export const WORKSPACE_SCHEMA = 'delta-robot-p0-workspace/v2';
export const POSE_SCHEMA = 'delta-robot-p0-pose/v1';
export const WORKSPACE_CLASSES = ['reachable', 'joint_limited', 'unreachable'];

const REASONS_BY_CLASS = {
  reachable: ['reachable'],
  joint_limited: ['joint_limit'],
  unreachable: [
    'geometric_unreachable',
    'degenerate_boundary',
    'assembly_constraint',
    'ambiguous_assembly',
  ],
};

const GEOMETRY_FIELDS = [
  'base_joint_radius_m',
  'platform_joint_radius_m',
  'upper_arm_length_m',
  'lower_arm_length_m',
  'min_joint_angle_rad',
  'max_joint_angle_rad',
];

function fail(message) {
  throw new Error(`Invalid visualizer artifact: ${message}`);
}

function requireObject(value, path) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) {
    fail(`${path} must be an object`);
  }
  return value;
}

function requireFiniteNumber(value, path) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    fail(`${path} must be a finite number`);
  }
  return value;
}

function requireNonNegativeInteger(value, path) {
  if (!Number.isInteger(value) || value < 0) {
    fail(`${path} must be a non-negative integer`);
  }
  return value;
}

function requireVector3(value, path) {
  if (!Array.isArray(value) || value.length !== 3) {
    fail(`${path} must be a three-element array`);
  }
  value.forEach((component, index) => requireFiniteNumber(component, `${path}[${index}]`));
  return value;
}

function validateCommon(document, expectedSchema) {
  const artifact = requireObject(document, 'document');
  if (artifact.schema !== expectedSchema) {
    fail(`schema must be ${expectedSchema}`);
  }
  const units = requireObject(artifact.units, 'units');
  if (units.length !== 'm' || units.angle !== 'rad') {
    fail('units must be length=m and angle=rad');
  }
  if (typeof artifact.source !== 'string' || artifact.source.trim() === '') {
    fail('source must be a non-empty string');
  }
  if (artifact.assembly_mode !== 'knee_out_platform_below') {
    fail('assembly_mode must be knee_out_platform_below');
  }

  const geometry = requireObject(artifact.geometry, 'geometry');
  GEOMETRY_FIELDS.forEach((field) => requireFiniteNumber(geometry[field], `geometry.${field}`));
  for (const field of GEOMETRY_FIELDS.slice(0, 4)) {
    if (geometry[field] <= 0) fail(`geometry.${field} must be positive`);
  }
  if (geometry.min_joint_angle_rad >= geometry.max_joint_angle_rad) {
    fail('geometry joint limits must be ordered');
  }
  return artifact;
}

function validateBounds(bounds) {
  const validated = requireObject(bounds, 'grid.bounds_m');
  for (const axis of ['x', 'y', 'z']) {
    const interval = validated[axis];
    if (!Array.isArray(interval) || interval.length !== 2) {
      fail(`grid.bounds_m.${axis} must contain minimum and maximum`);
    }
    const minimum = requireFiniteNumber(interval[0], `grid.bounds_m.${axis}[0]`);
    const maximum = requireFiniteNumber(interval[1], `grid.bounds_m.${axis}[1]`);
    if (minimum > maximum) fail(`grid.bounds_m.${axis} must be ordered`);
  }
}

export function validateWorkspace(document) {
  const artifact = validateCommon(document, WORKSPACE_SCHEMA);
  const grid = requireObject(artifact.grid, 'grid');
  validateBounds(grid.bounds_m);
  const shape = requireObject(grid.shape, 'grid.shape');
  for (const axis of ['x', 'y', 'z']) {
    if (requireNonNegativeInteger(shape[axis], `grid.shape.${axis}`) < 1) {
      fail(`grid.shape.${axis} must be positive`);
    }
  }

  const summary = requireObject(artifact.summary, 'summary');
  const total = requireNonNegativeInteger(summary.total, 'summary.total');
  const expectedCounts = Object.fromEntries(
    WORKSPACE_CLASSES.map((classification) => [
      classification,
      requireNonNegativeInteger(summary[classification], `summary.${classification}`),
    ]),
  );
  const summed = Object.values(expectedCounts).reduce((sum, count) => sum + count, 0);
  if (summed !== total) fail('workspace class counts must sum to summary.total');
  const practicallyUsable = requireNonNegativeInteger(
    summary.practically_usable,
    'summary.practically_usable',
  );
  const weakReachable = requireNonNegativeInteger(
    summary.weak_reachable,
    'summary.weak_reachable',
  );
  if (practicallyUsable + weakReachable !== summary.reachable) {
    fail('workspace quality counts must sum to summary.reachable');
  }

  if (!Array.isArray(artifact.points) || artifact.points.length !== total) {
    fail('points length must equal summary.total');
  }
  const actualCounts = Object.fromEntries(WORKSPACE_CLASSES.map((name) => [name, 0]));
  let actualPracticallyUsable = 0;
  let actualWeakReachable = 0;
  artifact.points.forEach((pointValue, index) => {
    const point = requireObject(pointValue, `points[${index}]`);
    if (!WORKSPACE_CLASSES.includes(point.classification)) {
      fail(`points[${index}].classification is unknown`);
    }
    if (!REASONS_BY_CLASS[point.classification].includes(point.reason)) {
      fail(`points[${index}].reason contradicts its classification`);
    }
    requireVector3(point.position_m, `points[${index}].position_m`);
    if (typeof point.practically_usable !== 'boolean') {
      fail(`points[${index}].practically_usable must be boolean`);
    }
    const marginFields = ['parallel_margin', 'serial_margin', 'singularity_margin'];
    if (point.classification === 'unreachable') {
      if (point.practically_usable) {
        fail(`points[${index}] unreachable point cannot be practically usable`);
      }
      for (const field of marginFields) {
        if (point[field] !== null) fail(`points[${index}].${field} must be null`);
      }
    } else {
      for (const field of marginFields) {
        const margin = requireFiniteNumber(point[field], `points[${index}].${field}`);
        if (margin < 0 || margin > 1) fail(`points[${index}].${field} must be in [0, 1]`);
      }
      if (point.singularity_margin > point.parallel_margin + Number.EPSILON) {
        fail(`points[${index}].singularity_margin exceeds parallel margin`);
      }
      if (point.singularity_margin > point.serial_margin + Number.EPSILON) {
        fail(`points[${index}].singularity_margin exceeds serial margin`);
      }
      if (point.classification === 'joint_limited' && point.practically_usable) {
        fail(`points[${index}] joint-limited point cannot be practically usable`);
      }
    }
    if (point.practically_usable) actualPracticallyUsable += 1;
    if (point.classification === 'reachable' && !point.practically_usable) {
      actualWeakReachable += 1;
    }
    actualCounts[point.classification] += 1;
  });
  for (const classification of WORKSPACE_CLASSES) {
    if (actualCounts[classification] !== expectedCounts[classification]) {
      fail(`point count for ${classification} contradicts summary`);
    }
  }
  if (actualPracticallyUsable !== practicallyUsable) {
    fail('point count for practically_usable contradicts summary');
  }
  if (actualWeakReachable !== weakReachable) {
    fail('point count for weak_reachable contradicts summary');
  }

  const shapeCardinality = shape.x * shape.y * shape.z;
  if (shapeCardinality !== total) fail('grid shape cardinality must equal summary.total');
  return artifact;
}

export function validatePose(document) {
  const artifact = validateCommon(document, POSE_SCHEMA);
  if (artifact.classification !== 'reachable') {
    fail('pose classification must be reachable');
  }
  const pose = requireObject(artifact.pose, 'pose');
  requireVector3(pose.platform_center_m, 'pose.platform_center_m');
  requireVector3(pose.joint_angles_rad, 'pose.joint_angles_rad');
  if (!Array.isArray(pose.arms) || pose.arms.length !== 3) {
    fail('pose.arms must contain exactly three arms');
  }
  const armIndices = new Set();
  pose.arms.forEach((armValue, index) => {
    const arm = requireObject(armValue, `pose.arms[${index}]`);
    if (!Number.isInteger(arm.arm_index) || arm.arm_index < 1 || arm.arm_index > 3) {
      fail(`pose.arms[${index}].arm_index must be 1, 2 or 3`);
    }
    armIndices.add(arm.arm_index);
    requireVector3(arm.shoulder_m, `pose.arms[${index}].shoulder_m`);
    requireVector3(arm.knee_m, `pose.arms[${index}].knee_m`);
    requireVector3(
      arm.platform_attachment_m,
      `pose.arms[${index}].platform_attachment_m`,
    );
  });
  if (armIndices.size !== 3) fail('pose arm indices must be unique');
  return artifact;
}

export function assertMatchingArtifacts(workspace, pose) {
  for (const field of ['source', 'assembly_mode']) {
    if (workspace[field] !== pose[field]) fail(`${field} differs between artifacts`);
  }
  for (const field of GEOMETRY_FIELDS) {
    if (workspace.geometry[field] !== pose.geometry[field]) {
      fail(`geometry.${field} differs between artifacts`);
    }
  }
}

export function mapModelToScene(vector) {
  requireVector3(vector, 'model vector');
  return [vector[0], vector[2], -vector[1]];
}

export function partitionWorkspacePoints(workspace) {
  const partitions = Object.fromEntries(WORKSPACE_CLASSES.map((name) => [name, []]));
  for (const point of workspace.points) {
    partitions[point.classification].push(point.position_m);
  }
  return partitions;
}

export function partitionWorkspaceQualityPoints(workspace) {
  const partitions = {
    practically_usable: [],
    weak_reachable: [],
    joint_limited: [],
    unreachable: [],
  };
  for (const point of workspace.points) {
    if (point.practically_usable) {
      partitions.practically_usable.push(point.position_m);
    } else if (point.classification === 'reachable') {
      partitions.weak_reachable.push(point.position_m);
    } else {
      partitions[point.classification].push(point.position_m);
    }
  }
  return partitions;
}
