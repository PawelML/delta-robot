// Budget P1 single-axis bench for HTD 5M 20/60 transmission.
// Catalogue envelopes and provisional fabricated parts; final fits wait for delivered parts.

const PITCH = 5;
const SMALL_TEETH = 20;
const LARGE_TEETH = 60;
const RATIO = LARGE_TEETH / SMALL_TEETH;
const SMALL_PITCH_RADIUS = SMALL_TEETH * PITCH / (2 * Math.PI);
const LARGE_PITCH_RADIUS = LARGE_TEETH * PITCH / (2 * Math.PI);
const NOMINAL_CENTRE = 120.80646690657736;
const BELT_LENGTH = 450;
const BELT_WIDTH = 15;
// A 0.5 mm visual envelope keeps the belt outside catalogue pulley OD; the
// pitch-line geometry remains authoritative and tooth contact is not modelled.
const BELT_THICKNESS = 0.5;
const RELAXED_ADJUSTMENT = -15;
const TENSIONED_ADJUSTMENT = 3;

const outputAngle = param('Output angle', 0, {
  min: -45,
  max: 80,
  step: 1,
  unit: 'deg',
});
const beltAdjustment = param('Input carrier adjustment', 0, {
  min: RELAXED_ADJUSTMENT,
  max: TENSIONED_ADJUSTMENT,
  step: 0.5,
  unit: 'mm',
});
const armLength = param('Representative arm length', 280, {
  min: 260,
  max: 300,
  step: 5,
  unit: 'mm',
});
const representativeMass = param('Representative test mass', 0.5, {
  min: 0.1,
  max: 1.0,
  step: 0.05,
  unit: 'kg',
});

// The shoulder axis sits at the bench edge so the +80 deg arm pose clears the
// plate instead of sweeping through it.
const OUTPUT_X = 222;
const INPUT_X = OUTPUT_X - NOMINAL_CENTRE - beltAdjustment;
const NOMINAL_INPUT_X = OUTPUT_X - NOMINAL_CENTRE;
const SHAFT_Z = 135;
const BELT_Y = -85;
const ARM_Y = -155;
const INPUT_BEARING_Y = [-110, -60];
const OUTPUT_BEARING_Y = [-115, -55];

const aluminium = { metalness: 0.52, roughness: 0.4 };
const steel = { metalness: 0.76, roughness: 0.27 };
const polymer = { metalness: 0.02, roughness: 0.78 };

function fixedMount() {
  return connector({
    origin: [0, 0, 0],
    axis: [0, 0, -1],
    up: [1, 0, 0],
    kind: 'fixed',
  });
}

function childMount() {
  return connector({
    origin: [0, 0, 0],
    axis: [0, 0, 1],
    up: [1, 0, 0],
    kind: 'fixed',
  });
}

function shaftConnector(axis) {
  return connector({
    origin: [0, 0, 0],
    axis,
    up: [0, 0, 1],
    kind: 'revolute',
  });
}

function axialCylinder(length, radius, yCenter) {
  return cylinder(length, radius, undefined, 64)
    .pointAlong([0, 1, 0])
    .translate(0, yCenter - length / 2, 0);
}

function axialRing(length, outerRadius, innerRadius, yCenter) {
  return difference(
    axialCylinder(length, outerRadius, yCenter),
    axialCylinder(length + 2, innerRadius, yCenter),
  );
}

function verticalHole(height, radius, x, y, zBottom) {
  return cylinder(height, radius, undefined, 48).translate(x, y, zBottom);
}

function bearingBlock(yCenter, width, depth, bottomZ, topZ, boreRadius) {
  return difference(
    box(width, depth, topZ - bottomZ).translate(0, yCenter, bottomZ),
    axialCylinder(depth + 4, boreRadius, yCenter),
  );
}

function carrierSlot(x, y) {
  const travel = TENSIONED_ADJUSTMENT - RELAXED_ADJUSTMENT;
  const radius = 4.5;
  const centre = x - (RELAXED_ADJUSTMENT + TENSIONED_ADJUSTMENT) / 2;
  return union(
    box(travel, radius * 2, 16).translate(centre, y, -2),
    verticalHole(16, radius, centre - travel / 2, y, -2),
    verticalHole(16, radius, centre + travel / 2, y, -2),
  );
}

function basePlate() {
  let plate = box(480, 280, 10);
  for (const localX of [-42, 42]) {
    for (const y of [-115, 65]) {
      plate = difference(plate, carrierSlot(NOMINAL_INPUT_X + localX, y));
    }
  }
  for (const x of [OUTPUT_X - 16, OUTPUT_X + 16]) {
    for (const y of [-120, -50]) {
      plate = difference(plate, verticalHole(16, 4.5, x, y, -2));
    }
  }
  for (const x of [-210, 210]) {
    for (const y of [-115, 115]) {
      plate = difference(plate, verticalHole(16, 6.5, x, y, -2));
    }
  }
  return plate
    .color('#718092')
    .material(aluminium)
    .withConnectors({
      output_support: connector({ origin: [OUTPUT_X, 0, SHAFT_Z], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      input_carrier: connector({ origin: [INPUT_X, 0, SHAFT_Z], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      belt_datum: connector({ origin: [OUTPUT_X, 0, SHAFT_Z], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
    });
}

function adjustableCarrier() {
  let plate = box(104, 220, 12).translate(0, -25, -125);
  for (const x of [-42, 42]) {
    for (const y of [-115, 65]) {
      plate = difference(plate, verticalHole(18, 4.5, x, y, -128));
    }
  }
  return plate
    .color('#8e9cab')
    .material(aluminium)
    .withConnectors({
      base: fixedMount(),
      input_support: childMount(),
      motor_bracket: childMount(),
    });
}

function inputSupport() {
  const blocks = INPUT_BEARING_Y.map((y) => bearingBlock(y, 54, 10, -113, 18, 11.02));
  const bridge = box(54, 60, 14).translate(0, -85, -113);
  let housingShape = union(blocks[0], blocks[1], bridge);
  for (const x of [-20, 20]) {
    for (const y of [-112, -58]) {
      housingShape = difference(housingShape, verticalHole(20, 3.3, x, y, -116));
    }
  }
  const bearing = () => axialRing(7, 11, 4.05, 0)
    .color('#b9c3cd')
    .material(steel)
    .withConnectors({ mount: fixedMount() });
  verify.clearanceBetween(
    'Input 608 envelope is seated without positive housing interference',
    axialRing(7, 11, 4.05, 0).translate(0, INPUT_BEARING_Y[0], 0),
    blocks[0],
    -0.01,
    0.05,
    2,
  );
  const housing = housingShape
    .color('#526172')
    .material(steel)
    .withConnectors({
      base: fixedMount(),
      axis: shaftConnector([0, -1, 0]),
      front_bearing: connector({ origin: [0, INPUT_BEARING_Y[0], 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      rear_bearing: connector({ origin: [0, INPUT_BEARING_Y[1], 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
    });
  return { housing, frontBearing: bearing(), rearBearing: bearing() };
}

function inputRotor() {
  const shaft = axialCylinder(100, 4, -70)
    .color('#c7d0d8')
    .material(steel);
  const toothBody = axialRing(20.5, 30.69 / 2, 4.1, 0);
  const hub = axialRing(5.5, 23 / 2, 4.1, 13);
  const flanges = union(
    axialRing(1.7, 18, 4.1, -10.9),
    axialRing(1.7, 18, 4.1, 15.9),
  );
  const pulley = union(toothBody, hub, flanges)
    .color('#aeb6be')
    .material(steel)
    .withConnectors({ mount: fixedMount() });
  return {
    shaft: shaft.withConnectors({
      axis: shaftConnector([0, 1, 0]),
      pulley_mount: connector({ origin: [0, BELT_Y, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      coupling_mount: connector({ origin: [0, 0, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
    }),
    pulley,
  };
}

function coupling() {
  const shell = axialRing(32, 12.5, 4.08, -22);
  const grooves = union(
    axialRing(1.5, 12.8, 10.7, -31),
    axialRing(1.5, 12.8, 10.7, -26),
    axialRing(1.5, 12.8, 10.7, -18),
    axialRing(1.5, 12.8, 10.7, -13),
  );
  return difference(shell, grooves)
    .color('#327eae')
    .material(aluminium)
    .withConnectors({ mount: fixedMount() });
}

function motorAndBracket() {
  const body = box(57, 122, 57)
    .translate(0, 61, -28.5)
    .color('#273039')
    .material({ metalness: 0.42, roughness: 0.38 });
  const frontBoss = axialCylinder(2, 19, -1)
    .color('#aeb7c0')
    .material(steel);
  const motorShaft = axialCylinder(20, 4, -10)
    .color('#c6cfd7')
    .material(steel);
  const motor = union(body, frontBoss, motorShaft)
    .color('#273039')
    .material({ metalness: 0.42, roughness: 0.38 })
    .withConnectors({ mount: fixedMount() });
  const face = difference(
    box(76, 6, 148).translate(0, -3, -113),
    axialCylinder(10, 20, -3),
  );
  const foot = box(104, 72, 10).translate(0, 34, -113);
  const braces = union(
    box(8, 58, 82).translate(-34, 29, -103),
    box(8, 58, 82).translate(34, 29, -103),
  );
  let bracketShape = union(face, foot, braces);
  for (const x of [-42, 42]) {
    for (const y of [16, 52]) {
      bracketShape = difference(bracketShape, verticalHole(16, 3.3, x, y, -116));
    }
  }
  const bracket = bracketShape
    .color('#617183')
    .material(steel)
    .withConnectors({ base: fixedMount(), motor_mount: childMount() });
  return { motor, bracket };
}

function outputSupport() {
  const blocks = OUTPUT_BEARING_Y.map((y) => bearingBlock(y, 44, 12, -125, 23, 14.02));
  const bridge = box(44, 72, 16).translate(0, -85, -125);
  let housingShape = union(blocks[0], blocks[1], bridge);
  for (const x of [-16, 16]) {
    for (const y of [-120, -50]) {
      housingShape = difference(housingShape, verticalHole(20, 4.5, x, y, -128));
    }
  }
  const bearing = () => axialRing(8, 14, 6.05, 0)
    .color('#b9c3cd')
    .material(steel)
    .withConnectors({ mount: fixedMount() });
  verify.clearanceBetween(
    'Output bearing envelope is seated without positive housing interference',
    axialRing(8, 14, 6.05, 0).translate(0, OUTPUT_BEARING_Y[0], 0),
    blocks[0],
    -0.01,
    0.05,
    2,
  );
  const housing = housingShape
    .color('#4c5a69')
    .material(steel)
    .withConnectors({
      base: fixedMount(),
      axis: shaftConnector([0, -1, 0]),
      front_bearing: connector({ origin: [0, OUTPUT_BEARING_Y[0], 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      rear_bearing: connector({ origin: [0, OUTPUT_BEARING_Y[1], 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
    });
  return { housing, frontBearing: bearing(), rearBearing: bearing() };
}

function outputRotor() {
  const shaft = axialCylinder(130, 6, -90)
    .color('#c4ced7')
    .material(steel);
  const toothBody = axialRing(20.5, 94.35 / 2, 6.1, 0);
  const hub = axialRing(9.7, 25, 6.1, 15);
  const pulley = union(toothBody, hub)
    .color('#b8a26d')
    .material(aluminium)
    .withConnectors({ mount: fixedMount() });
  const armBeam = box(armLength - 21, 12, 18)
    .translate((armLength + 21) / 2, 0, -9);
  const armHub = axialRing(12, 22, 6.1, 0);
  const arm = union(armBeam, armHub)
    .color('#df7b24')
    .material(aluminium)
    .withConnectors({ mount: fixedMount() });
  const loadRadius = 20 + representativeMass * 8;
  const mass = axialCylinder(42, loadRadius, 0)
    .translate(armLength + loadRadius, 0, 0)
    .color('#74533d')
    .material(steel)
    .withConnectors({ mount: fixedMount() });
  return {
    shaft: shaft.withConnectors({
      axis: shaftConnector([0, 1, 0]),
      pulley_mount: connector({ origin: [0, BELT_Y, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      arm_mount: connector({ origin: [0, ARM_Y, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      mass_mount: connector({ origin: [0, ARM_Y, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
    }),
    pulley,
    arm,
    mass,
  };
}

function beltEnvelope() {
  const drive = lib.beltDrive({
    pulleys: [
      { name: 'input', center: [-NOMINAL_CENTRE - beltAdjustment, 0], pitchRadius: SMALL_PITCH_RADIUS },
      { name: 'output', center: [0, 0], pitchRadius: LARGE_PITCH_RADIUS },
    ],
    beltWidth: BELT_WIDTH,
    beltThickness: BELT_THICKNESS,
  });
  return drive.belt
    .rotateX(90)
    .translate(0, BELT_Y + BELT_WIDTH / 2, 0)
    .color('#20252b')
    .material(polymer)
    .withConnectors({ base: fixedMount() });
}

const base = basePlate();
const carrier = adjustableCarrier();
const inputFixed = inputSupport();
const inputMoving = inputRotor();
const motor = motorAndBracket();
const outputFixed = outputSupport();
const outputMoving = outputRotor();
const bkl3 = coupling();
const belt = beltEnvelope();

const bench = assembly('Budget P1 single-axis bench')
  .addPart('Base plate', base, { material: 'aluminium plate', process: 'drilled workshop prototype' })
  .addPart('Adjustable input carrier', carrier, { material: '12 mm aluminium plate' })
  .addPart('Input bearing housing', inputFixed.housing, { material: 'fabricated aluminium or steel' })
  .addPart('Input front 608 bearing', inputFixed.frontBearing, { material: 'purchased SKF 608-2RS envelope' })
  .addPart('Input rear 608 bearing', inputFixed.rearBearing, { material: 'purchased SKF 608-2RS envelope' })
  .addPart('Input jackshaft', inputMoving.shaft, { material: 'C45 steel' })
  .addPart('HTD 20T pulley', inputMoving.pulley, { material: 'purchased steel pulley' })
  .addPart('R+W BKL3 coupling', bkl3, { material: 'purchased bellows coupling', massKg: 0.027 })
  .addPart('Motor bracket', motor.bracket, { material: 'fabricated steel' })
  .addPart('23HS40 closed-loop stepper', motor.motor, { material: 'purchased motor', massKg: 1.65 })
  .addPart('Output bearing housing', outputFixed.housing, { material: 'fabricated aluminium or steel' })
  .addPart('Output front bearing', outputFixed.frontBearing, { material: 'purchased 12x28x8 bearing envelope' })
  .addPart('Output rear bearing', outputFixed.rearBearing, { material: 'purchased 12x28x8 bearing envelope' })
  .addPart('Output shaft', outputMoving.shaft, { material: 'C45 steel' })
  .addPart('HTD 60T pulley', outputMoving.pulley, { material: 'purchased aluminium pulley' })
  .addPart('Representative upper arm', outputMoving.arm, { material: 'fabricated aluminium' })
  .addPart('Representative test mass', outputMoving.mass, { massKg: representativeMass })
  .addPart('450-5M-15 belt envelope', belt, { material: 'rubber synchronous belt' })
  .connect('Base plate.input_carrier', 'Adjustable input carrier.base', { as: 'carrier_mount' })
  .connect('Adjustable input carrier.input_support', 'Input bearing housing.base', { as: 'input_support_mount' })
  .connect('Input bearing housing.front_bearing', 'Input front 608 bearing.mount', { as: 'input_front_bearing_seat' })
  .connect('Input bearing housing.rear_bearing', 'Input rear 608 bearing.mount', { as: 'input_rear_bearing_seat' })
  .connect('Input bearing housing.axis', 'Input jackshaft.axis', {
    as: 'input_angle',
    min: -240,
    max: 400,
    default: 0,
    unit: 'deg',
    follows: { joint: 'output_angle', ratio: RATIO, offset: 0 },
  })
  .connect('Input jackshaft.pulley_mount', 'HTD 20T pulley.mount', { as: 'input_pulley_mount' })
  .connect('Input jackshaft.coupling_mount', 'R+W BKL3 coupling.mount', { as: 'coupling_axis_mount' })
  .connect('Adjustable input carrier.motor_bracket', 'Motor bracket.base', { as: 'motor_bracket_mount' })
  .connect('Motor bracket.motor_mount', '23HS40 closed-loop stepper.mount', { as: 'motor_mount' })
  .connect('Base plate.output_support', 'Output bearing housing.base', { as: 'output_support_mount' })
  .connect('Output bearing housing.front_bearing', 'Output front bearing.mount', { as: 'output_front_bearing_seat' })
  .connect('Output bearing housing.rear_bearing', 'Output rear bearing.mount', { as: 'output_rear_bearing_seat' })
  .connect('Output bearing housing.axis', 'Output shaft.axis', {
    as: 'output_angle',
    min: -45,
    max: 80,
    default: outputAngle,
    unit: 'deg',
  })
  .connect('Output shaft.pulley_mount', 'HTD 60T pulley.mount', { as: 'output_pulley_mount' })
  .connect('Output shaft.arm_mount', 'Representative upper arm.mount', { as: 'arm_mount' })
  .connect('Output shaft.mass_mount', 'Representative test mass.mount', { as: 'mass_mount' })
  .connect('Base plate.belt_datum', '450-5M-15 belt envelope.base', { as: 'belt_mount' });

bench.addAnimation('Accepted shoulder sweep', {
  duration: 4,
  loop: true,
  keyframes: [
    { values: { output_angle: -45 } },
    { values: { output_angle: 80 } },
    { values: { output_angle: -45 } },
  ],
});

bom(1, 'StepperOnline 23HS40-5004D-E1000 motor and CL57Y-V20 driver allocation');
bom(1, 'HTD 20-5M-15 steel pulley, finished 8 mm bore and positive retention');
bom(1, 'HTD 60-5M-15 aluminium pulley, finish-machined hub/retention');
bom(1, '450-5M-15 synchronous belt');
bom(1, 'R+W BKL/3/8/8 bellows coupling, 3 Nm');
bom(2, 'SKF 608-2RS/2RSH-envelope bearing, 8 x 22 x 7 mm');
bom(1, 'C45 input jackshaft, 8 mm x 100 mm prototype blank');
bom(2, '12 x 28 x 8 mm sealed output bearing; exact series VERIFY BEFORE PURCHASE');
bom(1, 'C45 output shaft, 12 mm x 130 mm prototype blank');
bom(1, '480 x 280 x 10 mm aluminium base plate');
bom(1, '104 x 220 x 12 mm adjustable input carrier');
bom(1, 'fabricated input housing, 50 mm bearing-centre span');
bom(1, 'fabricated output housing, 60 mm bearing-centre span');
bom(1, 'braced NEMA 23 bracket; hole pattern VERIFY FROM DELIVERED MOTOR');
bom(1, '280 mm representative upper arm and positive shaft hub');
bom(representativeMass, 'removable representative test mass', { unit: 'kg' });

dim([INPUT_X, 0, SHAFT_Z], [OUTPUT_X, 0, SHAFT_Z], {
  label: 'Pulley centre distance',
  color: '#19bddd',
});
dim([INPUT_X, INPUT_BEARING_Y[0], SHAFT_Z], [INPUT_X, INPUT_BEARING_Y[1], SHAFT_Z], {
  label: 'Input bearing span 50 mm',
  color: '#77d792',
});
dim([OUTPUT_X, OUTPUT_BEARING_Y[0], SHAFT_Z], [OUTPUT_X, OUTPUT_BEARING_Y[1], SHAFT_Z], {
  label: 'Output bearing span 60 mm',
  color: '#19bddd',
});
dim([OUTPUT_X, ARM_Y, SHAFT_Z], [OUTPUT_X + armLength, ARM_Y, SHAFT_Z], {
  label: 'Representative arm radius',
  color: '#f4a041',
});
dim([-240, -140, 0], [240, -140, 0], { label: 'Base width 480 mm' });
dim([NOMINAL_INPUT_X, 105, SHAFT_Z], [NOMINAL_INPUT_X - RELAXED_ADJUSTMENT, 105, SHAFT_Z], {
  label: 'Relaxed installation travel 15 mm',
  color: '#77d792',
});
dim([NOMINAL_INPUT_X, 122, SHAFT_Z], [NOMINAL_INPUT_X - TENSIONED_ADJUSTMENT, 122, SHAFT_Z], {
  label: 'Tensioning travel 3 mm',
  color: '#77d792',
});

verify.equal('Exact budget transmission ratio', RATIO, 3, 1e-12);
verify.equal('Calculated nominal centre distance', NOMINAL_CENTRE, 120.80646690657736, 1e-9);
verify.inRange('Output angle stays inside accepted shoulder range', outputAngle, -45, 80);
verify.inRange('Input carrier stays inside slots', beltAdjustment, RELAXED_ADJUSTMENT, TENSIONED_ADJUSTMENT);

scene({
  background: { top: '#c5d0db', bottom: '#556475' },
  camera: { position: [740, -860, 490], target: [150, -55, 90], fov: 47 },
  views: {
    hero: { camera: { position: [740, -860, 490], target: [150, -55, 90], up: [0, 0, 1], fov: 47 } },
    belt: { camera: { position: [120, -720, 180], target: [160, -85, 135], up: [0, 0, 1], fov: 40 } },
    side: { camera: { position: [610, -170, 210], target: [20, -55, 95], up: [0, 0, 1], fov: 34 } },
    jackshaft: { camera: { position: [-180, -390, 230], target: [INPUT_X, -60, 130], up: [0, 0, 1], fov: 28 } },
  },
  environment: { preset: 'studio', intensity: 0.22, background: false },
  lights: [
    { type: 'ambient', color: '#eee6dc', intensity: 0.16 },
    { type: 'directional', position: [260, -330, 410], color: '#ffe0b9', intensity: 2.7, castShadow: true },
    { type: 'directional', position: [-250, 210, 230], color: '#d4e8ff', intensity: 0.9 },
    { type: 'hemisphere', skyColor: '#c7d4e0', groundColor: '#465363', intensity: 0.16 },
  ],
  ground: { visible: true, color: '#3c4856', height: -155, receiveShadow: true },
  jointOverlay: { axisColor: '#12dff0', arcColor: '#ff7b1f' },
});

return bench;
