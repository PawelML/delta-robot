import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  assertMatchingArtifacts,
  mapModelToScene,
  partitionWorkspacePoints,
  validatePose,
  validateWorkspace,
} from '../src/data-contract.js';

const artifactsDirectory = new URL('../../artifacts/', import.meta.url);
const workspace = JSON.parse(
  await readFile(new URL('workspace.json', artifactsDirectory), 'utf8'),
);
const pose = JSON.parse(await readFile(new URL('pose.json', artifactsDirectory), 'utf8'));

test('committed artifacts satisfy the complete visualizer contract', () => {
  assert.equal(validateWorkspace(workspace), workspace);
  assert.equal(validatePose(pose), pose);
  assert.doesNotThrow(() => assertMatchingArtifacts(workspace, pose));
});

test('model coordinates map to the right-handed scene convention', () => {
  assert.deepEqual(mapModelToScene([1, 2, 3]), [1, 3, -2]);
});

test('workspace partition preserves exact summary counts', () => {
  const partitions = partitionWorkspacePoints(workspace);

  assert.equal(partitions.reachable.length, workspace.summary.reachable);
  assert.equal(partitions.joint_limited.length, workspace.summary.joint_limited);
  assert.equal(partitions.unreachable.length, workspace.summary.unreachable);
  assert.equal(
    Object.values(partitions).reduce((total, points) => total + points.length, 0),
    workspace.summary.total,
  );
});

test('workspace validation rejects a wrong schema and contradictory count', () => {
  const wrongSchema = structuredClone(workspace);
  wrongSchema.schema = 'delta-robot-p0-workspace/v999';
  assert.throws(() => validateWorkspace(wrongSchema), /schema must be/);

  const wrongCount = structuredClone(workspace);
  wrongCount.summary.reachable += 1;
  assert.throws(() => validateWorkspace(wrongCount), /class counts must sum/);

  const wrongReason = structuredClone(workspace);
  wrongReason.points[0].reason = 'reachable';
  assert.throws(() => validateWorkspace(wrongReason), /reason contradicts/);
});

test('validation rejects wrong units and non-finite coordinates', () => {
  const wrongUnits = structuredClone(pose);
  wrongUnits.units.length = 'mm';
  assert.throws(() => validatePose(wrongUnits), /units must be/);

  const invalidCoordinate = structuredClone(pose);
  invalidCoordinate.pose.platform_center_m[2] = Number.NaN;
  assert.throws(() => validatePose(invalidCoordinate), /finite number/);
});

test('matching rejects artifacts from different geometry or sources', () => {
  const wrongSource = structuredClone(pose);
  wrongSource.source = 'different_fixture';
  assert.throws(
    () => assertMatchingArtifacts(workspace, wrongSource),
    /source differs/,
  );

  const wrongGeometry = structuredClone(pose);
  wrongGeometry.geometry.upper_arm_length_m += 0.001;
  assert.throws(
    () => assertMatchingArtifacts(workspace, wrongGeometry),
    /upper_arm_length_m differs/,
  );
});
