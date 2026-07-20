import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

import {
  assertMatchingArtifacts,
  mapModelToScene,
  partitionWorkspaceQualityPoints,
  validatePose,
  validateTrajectory,
  validateWorkspace,
} from './data-contract.js';

const COLORS = {
  background: 0x080c12,
  base: 0x283548,
  platform: 0x3d789f,
  upperArm: 0x72b8ff,
  lowerRod: 0xc7d5e5,
  shoulder: 0x4c98d8,
  knee: 0xe8edf4,
  attachment: 0x54d7c5,
  center: 0xffdf75,
  reachable: 0x42d69a,
  practically_usable: 0x42d69a,
  weak_reachable: 0xd765ff,
  joint_limited: 0xffb454,
  unreachable: 0xff6670,
};

const POINT_STYLE = {
  practically_usable: { opacity: 0.72, sizeFactor: 0.22 },
  weak_reachable: { opacity: 0.82, sizeFactor: 0.25 },
  joint_limited: { opacity: 0.5, sizeFactor: 0.18 },
  unreachable: { opacity: 0.14, sizeFactor: 0.14 },
};

const $ = (id) => document.getElementById(id);
const sceneCanvas = $('scene');
const loadingOverlay = $('loading-overlay');
const errorBanner = $('error-banner');
const errorMessage = $('error-message');

let renderer;
let scene;
let camera;
let controls;
let robotGroup;
let layerGroups;
let trajectory;
let playbackStartMs;
let playbackTimeS = 0;
let playbackRunning = true;

function formatMillimetres(valueMetres, digits = 0) {
  return `${(valueMetres * 1000).toFixed(digits)} mm`;
}

function formatInterval(interval) {
  return `${formatMillimetres(interval[0])} … ${formatMillimetres(interval[1])}`;
}

function formatPercent(count, total) {
  return `${count.toLocaleString('pl-PL')} · ${((100 * count) / total).toFixed(1)}%`;
}

function setStatus(kind, title, detail) {
  $('status-dot').className = `status-dot ${kind}`;
  $('status-title').textContent = title;
  $('status-detail').textContent = detail;
}

async function fetchArtifact(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path}: HTTP ${response.status}`);
  }
  return response.json();
}

function mappedVector(modelVector) {
  return new THREE.Vector3(...mapModelToScene(modelVector));
}

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function setCylinderBetween(cylinder, start, end) {
  const direction = new THREE.Vector3().subVectors(end, start);
  const length = direction.length();
  cylinder.position.copy(start).add(end).multiplyScalar(0.5);
  cylinder.quaternion.setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    direction.normalize(),
  );
  cylinder.scale.set(1, length, 1);
}

function createCylinderBetween(start, end, radius, material, radialSegments = 14) {
  const geometry = new THREE.CylinderGeometry(radius, radius, 1, radialSegments);
  const cylinder = new THREE.Mesh(geometry, material);
  setCylinderBetween(cylinder, start, end);
  cylinder.castShadow = true;
  return cylinder;
}

function createNode(position, radius, color, group) {
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(radius, 18, 12),
    new THREE.MeshStandardMaterial({ color, metalness: 0.08, roughness: 0.4 }),
  );
  mesh.position.copy(position);
  mesh.castShadow = true;
  group.add(mesh);
  return mesh;
}

function createRobot(poseArtifact) {
  const group = new THREE.Group();
  group.name = 'authoritative-pose';
  const geometry = poseArtifact.geometry;
  const minimumLink = Math.min(
    geometry.upper_arm_length_m,
    geometry.lower_arm_length_m,
  );
  const upperRadius = clamp(minimumLink * 0.012, 0.003, 0.012);
  const lowerRadius = clamp(minimumLink * 0.0065, 0.0025, 0.007);
  const pairSpacing = 4 * lowerRadius;
  const nodeRadius = Math.max(upperRadius * 1.35, pairSpacing * 0.62);
  const baseThickness = upperRadius * 1.5;
  const platformThickness = upperRadius * 1.35;

  const baseMaterial = new THREE.MeshStandardMaterial({
    color: COLORS.base,
    metalness: 0.16,
    roughness: 0.62,
    transparent: true,
    opacity: 0.92,
  });
  const platformMaterial = new THREE.MeshStandardMaterial({
    color: COLORS.platform,
    metalness: 0.18,
    roughness: 0.45,
  });
  const upperMaterial = new THREE.MeshStandardMaterial({
    color: COLORS.upperArm,
    metalness: 0.22,
    roughness: 0.35,
  });
  const lowerMaterial = new THREE.MeshStandardMaterial({
    color: COLORS.lowerRod,
    metalness: 0.35,
    roughness: 0.3,
  });

  const basePlate = new THREE.Mesh(
    new THREE.CylinderGeometry(
      geometry.base_joint_radius_m * 1.32,
      geometry.base_joint_radius_m * 1.32,
      baseThickness,
      64,
    ),
    baseMaterial,
  );
  basePlate.position.y = baseThickness * 0.15;
  basePlate.receiveShadow = true;
  group.add(basePlate);

  const platformCenter = mappedVector(poseArtifact.pose.platform_center_m);
  const platformPlate = new THREE.Mesh(
    new THREE.CylinderGeometry(
      geometry.platform_joint_radius_m * 1.4,
      geometry.platform_joint_radius_m * 1.4,
      platformThickness,
      48,
    ),
    platformMaterial,
  );
  platformPlate.position.copy(platformCenter);
  platformPlate.castShadow = true;
  group.add(platformPlate);

  let upperArmCount = 0;
  let lowerRodCount = 0;
  const armViews = [];
  for (const arm of poseArtifact.pose.arms) {
    const shoulder = mappedVector(arm.shoulder_m);
    const knee = mappedVector(arm.knee_m);
    const attachment = mappedVector(arm.platform_attachment_m);
    const upperArm = createCylinderBetween(shoulder, knee, upperRadius, upperMaterial);
    group.add(upperArm);
    upperArmCount += 1;

    const radialLength = Math.hypot(arm.shoulder_m[0], arm.shoulder_m[1]);
    const tangentModel = [
      -arm.shoulder_m[1] / radialLength,
      arm.shoulder_m[0] / radialLength,
      0,
    ];
    const lowerRods = [];
    for (const direction of [-1, 1]) {
      const offsetModel = tangentModel.map(
        (component) => component * direction * pairSpacing * 0.5,
      );
      const rodKnee = mappedVector(
        arm.knee_m.map((component, index) => component + offsetModel[index]),
      );
      const rodAttachment = mappedVector(
        arm.platform_attachment_m.map(
          (component, index) => component + offsetModel[index],
        ),
      );
      const lowerRod = createCylinderBetween(
        rodKnee,
        rodAttachment,
        lowerRadius,
        lowerMaterial,
        12,
      );
      group.add(lowerRod);
      lowerRods.push(lowerRod);
      lowerRodCount += 1;
    }

    const shoulderNode = createNode(shoulder, nodeRadius, COLORS.shoulder, group);
    const kneeNode = createNode(knee, nodeRadius, COLORS.knee, group);
    const attachmentNode = createNode(
      attachment,
      nodeRadius * 0.8,
      COLORS.attachment,
      group,
    );

    const motorBlock = new THREE.Mesh(
      new THREE.BoxGeometry(nodeRadius * 3.1, nodeRadius * 2.4, nodeRadius * 2.4),
      new THREE.MeshStandardMaterial({
        color: 0x365672,
        metalness: 0.3,
        roughness: 0.5,
      }),
    );
    motorBlock.position.copy(shoulder);
    motorBlock.position.y += nodeRadius * 1.45;
    motorBlock.castShadow = true;
    group.add(motorBlock);
    armViews.push({
      attachmentNode,
      kneeNode,
      lowerRods,
      motorBlock,
      shoulderNode,
      upperArm,
    });
  }

  const centerNode = createNode(platformCenter, nodeRadius * 0.72, COLORS.center, group);
  group.userData = {
    armViews,
    centerNode,
    lowerRodCount,
    pairSpacing,
    platformPlate,
    upperArmCount,
  };
  return group;
}

function interpolateVector(start, end, fraction) {
  return start.map((value, index) => value + (end[index] - value) * fraction);
}

function updateRobotFromSamples(group, before, after, fraction) {
  const platformCenterModel = interpolateVector(
    before.platform_center_m,
    after.platform_center_m,
    fraction,
  );
  const platformCenter = mappedVector(platformCenterModel);
  group.userData.platformPlate.position.copy(platformCenter);
  group.userData.centerNode.position.copy(platformCenter);

  before.arms.forEach((arm, index) => {
    const nextArm = after.arms[index];
    const view = group.userData.armViews[index];
    const shoulderModel = interpolateVector(arm.shoulder_m, nextArm.shoulder_m, fraction);
    const kneeModel = interpolateVector(arm.knee_m, nextArm.knee_m, fraction);
    const attachmentModel = interpolateVector(
      arm.platform_attachment_m,
      nextArm.platform_attachment_m,
      fraction,
    );
    const shoulder = mappedVector(shoulderModel);
    const knee = mappedVector(kneeModel);
    const attachment = mappedVector(attachmentModel);
    setCylinderBetween(view.upperArm, shoulder, knee);
    view.shoulderNode.position.copy(shoulder);
    view.kneeNode.position.copy(knee);
    view.attachmentNode.position.copy(attachment);

    const radialLength = Math.hypot(shoulderModel[0], shoulderModel[1]);
    const tangentModel = [-shoulderModel[1] / radialLength, shoulderModel[0] / radialLength, 0];
    [-1, 1].forEach((direction, rodIndex) => {
      const offset = tangentModel.map(
        (component) => component * direction * group.userData.pairSpacing * 0.5,
      );
      setCylinderBetween(
        view.lowerRods[rodIndex],
        mappedVector(kneeModel.map((component, axis) => component + offset[axis])),
        mappedVector(
          attachmentModel.map((component, axis) => component + offset[axis]),
        ),
      );
    });
  });
}

function createTrajectoryPath(trajectoryArtifact) {
  const points = trajectoryArtifact.samples.map((sample) => mappedVector(sample.platform_center_m));
  const path = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints(points),
    new THREE.LineBasicMaterial({ color: 0x8bd7ff, transparent: true, opacity: 0.75 }),
  );
  path.name = 'authoritative-trajectory-path';
  scene.add(path);
}

function minimumGridInterval(workspace) {
  const intervals = ['x', 'y', 'z']
    .map((axis) => {
      const bounds = workspace.grid.bounds_m[axis];
      const count = workspace.grid.shape[axis];
      return count > 1 ? (bounds[1] - bounds[0]) / (count - 1) : Number.POSITIVE_INFINITY;
    })
    .filter(Number.isFinite);
  return Math.min(...intervals);
}

function createWorkspaceLayers(workspace) {
  const partitions = partitionWorkspaceQualityPoints(workspace);
  const pointInterval = minimumGridInterval(workspace);
  const groups = {};
  for (const [classification, points] of Object.entries(partitions)) {
    const positions = new Float32Array(points.length * 3);
    points.forEach((point, index) => {
      const mapped = mapModelToScene(point);
      positions.set(mapped, index * 3);
    });
    const buffer = new THREE.BufferGeometry();
    buffer.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    buffer.computeBoundingSphere();
    const style = POINT_STYLE[classification];
    const material = new THREE.PointsMaterial({
      color: COLORS[classification],
      depthWrite: false,
      opacity: style.opacity,
      size: pointInterval * style.sizeFactor,
      sizeAttenuation: true,
      transparent: true,
    });
    const cloud = new THREE.Points(buffer, material);
    cloud.name = `workspace-${classification}`;
    cloud.renderOrder = classification === 'unreachable' ? 0 : 1;
    scene.add(cloud);
    groups[classification] = cloud;
  }
  return groups;
}

function createTextSprite(label, color) {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 96;
  const context = canvas.getContext('2d');
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.font = '700 42px system-ui';
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillStyle = color;
  context.fillText(label, canvas.width / 2, canvas.height / 2);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: texture, depthTest: false, transparent: true }),
  );
  sprite.scale.set(0.14, 0.0525, 1);
  sprite.renderOrder = 5;
  return sprite;
}

function createContext(workspace) {
  const group = new THREE.Group();
  const bounds = workspace.grid.bounds_m;
  const span = Math.max(
    bounds.x[1] - bounds.x[0],
    bounds.y[1] - bounds.y[0],
    bounds.z[1] - bounds.z[0],
  );
  const gridSize = span * 1.45;
  const divisions = Math.max(workspace.grid.shape.x - 1, 10);
  const grid = new THREE.GridHelper(gridSize, divisions, 0x33435a, 0x172131);
  grid.material.transparent = true;
  grid.material.opacity = 0.68;
  group.add(grid);

  const axisLength = span * 0.28;
  const origin = new THREE.Vector3(0, 0.018, 0);
  const axes = [
    { label: 'X', direction: new THREE.Vector3(1, 0, 0), color: 0xff6262 },
    { label: 'Y', direction: new THREE.Vector3(0, 0, -1), color: 0x67a2ff },
    { label: 'Z', direction: new THREE.Vector3(0, 1, 0), color: 0x61da8b },
  ];
  for (const axis of axes) {
    const arrow = new THREE.ArrowHelper(
      axis.direction,
      origin,
      axisLength,
      axis.color,
      axisLength * 0.12,
      axisLength * 0.06,
    );
    group.add(arrow);
    const label = createTextSprite(axis.label, `#${axis.color.toString(16).padStart(6, '0')}`);
    label.position.copy(origin).addScaledVector(axis.direction, axisLength * 1.12);
    group.add(label);
  }
  scene.add(group);
}

function configureScene(workspace, pose, trajectoryArtifact) {
  renderer = new THREE.WebGLRenderer({
    canvas: sceneCanvas,
    antialias: true,
    powerPreference: 'high-performance',
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(COLORS.background);
  scene.fog = new THREE.Fog(COLORS.background, 3.8, 7.5);

  camera = new THREE.PerspectiveCamera(44, 1, 0.01, 100);
  controls = new OrbitControls(camera, sceneCanvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.07;
  controls.screenSpacePanning = true;

  scene.add(new THREE.HemisphereLight(0xbfd7ff, 0x111822, 1.45));
  const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
  keyLight.position.set(2.4, 3.2, 2.0);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.set(2048, 2048);
  keyLight.shadow.camera.near = 0.1;
  keyLight.shadow.camera.far = 8;
  scene.add(keyLight);
  const fillLight = new THREE.DirectionalLight(0x6ba8ff, 0.85);
  fillLight.position.set(-2.0, -0.4, -1.8);
  scene.add(fillLight);

  createContext(workspace);
  layerGroups = createWorkspaceLayers(workspace);
  createTrajectoryPath(trajectoryArtifact);
  robotGroup = createRobot(pose);
  scene.add(robotGroup);
  fitCamera();
  resize();
}

function fitCamera() {
  const box = new THREE.Box3();
  for (const layer of Object.values(layerGroups)) box.expandByObject(layer);
  box.expandByObject(robotGroup);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const maximumDimension = Math.max(size.x, size.y, size.z);
  const fieldOfViewRadians = THREE.MathUtils.degToRad(camera.fov);
  const distance = (maximumDimension / (2 * Math.tan(fieldOfViewRadians / 2))) * 1.35;
  const direction = new THREE.Vector3(1.2, 0.72, 1.35).normalize();
  controls.target.copy(center);
  camera.position.copy(center).addScaledVector(direction, distance);
  camera.near = Math.max(maximumDimension / 1000, 0.001);
  camera.far = maximumDimension * 20;
  camera.updateProjectionMatrix();
  controls.minDistance = maximumDimension * 0.25;
  controls.maxDistance = maximumDimension * 8;
  controls.update();
  controls.saveState();
}

function resize() {
  if (!renderer || !camera) return;
  renderer.setSize(window.innerWidth, window.innerHeight, false);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}

function readVisibilitySettings() {
  const defaults = {
    robot: true,
    usable: true,
    weak: true,
    limited: true,
    unreachable: true,
  };
  try {
    return { ...defaults, ...JSON.parse(localStorage.getItem('deltaVisualizerLayers') || '{}') };
  } catch {
    return defaults;
  }
}

function bindLayerControls() {
  const settings = readVisibilitySettings();
  const bindings = [
    ['toggle-robot', 'robot', robotGroup],
    ['toggle-usable', 'usable', layerGroups.practically_usable],
    ['toggle-weak', 'weak', layerGroups.weak_reachable],
    ['toggle-limited', 'limited', layerGroups.joint_limited],
    ['toggle-unreachable', 'unreachable', layerGroups.unreachable],
  ];
  for (const [id, key, object] of bindings) {
    const input = $(id);
    input.checked = Boolean(settings[key]);
    object.visible = input.checked;
    input.addEventListener('change', () => {
      object.visible = input.checked;
      settings[key] = input.checked;
      try {
        localStorage.setItem('deltaVisualizerLayers', JSON.stringify(settings));
      } catch {
        // Visibility still works when browser storage is unavailable.
      }
    });
  }
  $('reset-view').addEventListener('click', () => controls.reset());
  $('toggle-playback').addEventListener('click', () => {
    playbackRunning = !playbackRunning;
    if (playbackRunning) {
      playbackStartMs = performance.now() - playbackTimeS * 1000;
    }
    $('toggle-playback').textContent = playbackRunning ? 'Pauza' : 'Wznów';
  });
  $('restart-playback').addEventListener('click', () => {
    playbackTimeS = 0;
    playbackStartMs = performance.now();
    updateTrajectoryDisplay(0);
  });
}

function populateInterface(workspace, pose, trajectoryArtifact) {
  const summary = workspace.summary;
  $('source-label').textContent = workspace.source;
  $('workspace-schema').textContent = workspace.schema;
  $('pose-schema').textContent = pose.schema;
  $('trajectory-schema').textContent = trajectoryArtifact.schema;
  $('total-points').textContent = `${summary.total.toLocaleString('pl-PL')} punktów`;
  $('count-usable-short').textContent = summary.practically_usable.toLocaleString('pl-PL');
  $('count-weak-short').textContent = summary.weak_reachable.toLocaleString('pl-PL');
  $('count-limited-short').textContent = summary.joint_limited.toLocaleString('pl-PL');
  $('count-unreachable-short').textContent = summary.unreachable.toLocaleString('pl-PL');
  $('metric-reachable').textContent = formatPercent(summary.reachable, summary.total);
  $('metric-usable').textContent = formatPercent(summary.practically_usable, summary.total);
  $('metric-weak').textContent = formatPercent(summary.weak_reachable, summary.total);
  $('metric-limited').textContent = formatPercent(summary.joint_limited, summary.total);
  $('metric-unreachable').textContent = formatPercent(summary.unreachable, summary.total);
  const shape = workspace.grid.shape;
  $('metric-shape').textContent = `${shape.x} × ${shape.y} × ${shape.z}`;
  for (const axis of ['x', 'y', 'z']) {
    $(`metric-bound-${axis}`).textContent = formatInterval(workspace.grid.bounds_m[axis]);
  }

  const position = pose.pose.platform_center_m.map((value) => (value * 1000).toFixed(0));
  $('metric-position').textContent = `${position.join(' / ')} mm`;
  pose.pose.joint_angles_rad.forEach((angle, index) => {
    $(`metric-angle-${index + 1}`).textContent = `${THREE.MathUtils.radToDeg(angle).toFixed(2)}°`;
  });
  const geometry = pose.geometry;
  $('metric-base-radius').textContent = formatMillimetres(geometry.base_joint_radius_m, 1);
  $('metric-platform-radius').textContent = formatMillimetres(
    geometry.platform_joint_radius_m,
    1,
  );
  $('metric-upper-length').textContent = formatMillimetres(geometry.upper_arm_length_m, 1);
  $('metric-lower-length').textContent = formatMillimetres(geometry.lower_arm_length_m, 1);
  $('metric-cycle-duration').textContent = `${trajectoryArtifact.cycle.duration_s.toFixed(3)} s`;
  $('metric-cycle-samples').textContent = trajectoryArtifact.cycle.sample_count.toLocaleString('pl-PL');
  $('metric-min-singularity').textContent = trajectoryArtifact.summary.minimum_singularity_margin.toFixed(3);
  $('metric-max-joint-speed').textContent = `${Math.max(...trajectoryArtifact.summary.maximum_abs_joint_rates_rad_s).toFixed(2)} rad/s`;
  $('metric-max-joint-acceleration').textContent = `${Math.max(...trajectoryArtifact.summary.maximum_abs_joint_accelerations_rad_s2).toFixed(2)} rad/s²`;
}

function updateTrajectoryDisplay(timeS) {
  const duration = trajectory.cycle.duration_s;
  const wrappedTime = ((timeS % duration) + duration) % duration;
  const floatingIndex = wrappedTime / trajectory.cycle.sample_period_s;
  const beforeIndex = Math.min(Math.floor(floatingIndex), trajectory.samples.length - 1);
  const afterIndex = Math.min(beforeIndex + 1, trajectory.samples.length - 1);
  const fraction = floatingIndex - beforeIndex;
  const before = trajectory.samples[beforeIndex];
  const after = trajectory.samples[afterIndex];
  updateRobotFromSamples(robotGroup, before, after, fraction);

  const position = interpolateVector(before.platform_center_m, after.platform_center_m, fraction);
  const angles = interpolateVector(before.joint_angles_rad, after.joint_angles_rad, fraction);
  const rates = interpolateVector(before.joint_rates_rad_s, after.joint_rates_rad_s, fraction);
  const accelerations = interpolateVector(
    before.joint_accelerations_rad_s2,
    after.joint_accelerations_rad_s2,
    fraction,
  );
  $('metric-position').textContent = `${position
    .map((value) => (value * 1000).toFixed(1))
    .join(' / ')} mm`;
  angles.forEach((angle, index) => {
    $(`metric-angle-${index + 1}`).textContent = `${THREE.MathUtils.radToDeg(angle).toFixed(2)}°`;
    $(`metric-rate-${index + 1}`).textContent = `${rates[index].toFixed(2)} rad/s`;
    $(`metric-acceleration-${index + 1}`).textContent = `${accelerations[index].toFixed(1)} rad/s²`;
  });
  $('metric-trajectory-time').textContent = `${wrappedTime.toFixed(3)} s`;
  $('metric-segment').textContent = before.segment;
  if (window.__deltaVisualizer) {
    window.__deltaVisualizer.currentSampleIndex = beforeIndex;
    window.__deltaVisualizer.playbackRunning = playbackRunning;
  }
}

function animate(timestampMs) {
  requestAnimationFrame(animate);
  if (playbackStartMs === undefined) playbackStartMs = timestampMs;
  if (playbackRunning) {
    playbackTimeS = (timestampMs - playbackStartMs) / 1000;
  }
  updateTrajectoryDisplay(playbackTimeS);
  controls.update();
  renderer.render(scene, camera);
}

function showFailure(error) {
  loadingOverlay.classList.add('hidden');
  errorMessage.textContent = error instanceof Error ? error.message : String(error);
  errorBanner.hidden = false;
  setStatus('error', 'Błąd danych', 'Scena nie została zbudowana');
  window.__deltaVisualizer = { ready: false, error };
  console.error(error);
}

async function start() {
  try {
    const [workspaceDocument, poseDocument, trajectoryDocument] = await Promise.all([
      fetchArtifact('./workspace.json'),
      fetchArtifact('./pose.json'),
      fetchArtifact('./trajectory_25_305_25.json'),
    ]);
    const workspace = validateWorkspace(workspaceDocument);
    const pose = validatePose(poseDocument);
    trajectory = validateTrajectory(trajectoryDocument);
    assertMatchingArtifacts(workspace, pose, trajectory);
    configureScene(workspace, pose, trajectory);
    bindLayerControls();
    populateInterface(workspace, pose, trajectory);
    setStatus(
      'ready',
      'Dane zweryfikowane',
      `${workspace.summary.practically_usable} użytecznych · poza osiągalna`,
    );
    loadingOverlay.classList.add('hidden');
    window.__deltaVisualizer = {
      ready: true,
      workspace,
      pose,
      trajectory,
      robotStats: robotGroup.userData,
      scene,
      currentSampleIndex: 0,
      playbackRunning,
    };
    window.dispatchEvent(new CustomEvent('delta-visualizer-ready'));
    requestAnimationFrame(animate);
  } catch (error) {
    showFailure(error);
  }
}

window.addEventListener('resize', resize);
start();
