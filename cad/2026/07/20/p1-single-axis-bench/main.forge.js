// P1 single-axis delta-robot shoulder bench.
// Purchased pulleys, belt and servo are catalogue envelopes, not production geometry.

const PITCH = 5;
const SMALL_TEETH = 18;
const LARGE_TEETH = 90;
const RATIO = LARGE_TEETH / SMALL_TEETH;
const SMALL_PITCH_RADIUS = SMALL_TEETH * PITCH / (2 * Math.PI);
const LARGE_PITCH_RADIUS = LARGE_TEETH * PITCH / (2 * Math.PI);
const BELT_LENGTH = 600;
const BELT_WIDTH = 15;
const BELT_THICKNESS = 1.04;
const NOMINAL_CENTRE = 154.36686875740537;
const RELAXED_ADJUSTMENT = -21;
const TENSIONED_ADJUSTMENT = 4;

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
  min: 220,
  max: 320,
  step: 5,
  unit: 'mm',
});
const representativeMass = param('Representative tip mass', 1.035, {
  min: 0,
  max: 1.5,
  step: 0.025,
  unit: 'kg',
});

const OUTPUT_X = 100;
const NOMINAL_INPUT_X = OUTPUT_X - NOMINAL_CENTRE;
const INPUT_X = OUTPUT_X - NOMINAL_CENTRE - beltAdjustment;
const SHAFT_Z = 160;
const BELT_Y = -115;
const ARM_Y = -205;
const CARRIER_HOLE_X = [-48, 48];
const CARRIER_HOLE_Y = [-165, 75];

const aluminium = { metalness: 0.55, roughness: 0.38 };
const steel = { metalness: 0.78, roughness: 0.25 };
const polymer = { metalness: 0.02, roughness: 0.72 };

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

function bearingBlock(yCenter, width, depth, bottomZ, topZ, boreRadius) {
  const body = box(width, depth, topZ - bottomZ).translate(0, yCenter, bottomZ);
  const bore = axialCylinder(depth + 4, boreRadius, yCenter);
  return difference(body, bore);
}

function verticalHole(height, radius, x, y, zBottom) {
  return cylinder(height, radius, undefined, 48).translate(x, y, zBottom);
}

function fixedCarrierSlot(localX, y) {
  const centreTravel = TENSIONED_ADJUSTMENT - RELAXED_ADJUSTMENT;
  const slotRadius = 4.5;
  const travelCentreX = NOMINAL_INPUT_X + localX
    - (RELAXED_ADJUSTMENT + TENSIONED_ADJUSTMENT) / 2;
  const left = travelCentreX - centreTravel / 2;
  const right = travelCentreX + centreTravel / 2;
  return union(
    box(centreTravel, slotRadius * 2, 18).translate(travelCentreX, y, -3),
    verticalHole(18, slotRadius, left, y, -3),
    verticalHole(18, slotRadius, right, y, -3),
  );
}

function slottedBasePlate() {
  let plate = box(600, 360, 12);
  for (const x of CARRIER_HOLE_X) {
    for (const y of CARRIER_HOLE_Y) {
      plate = difference(plate, fixedCarrierSlot(x, y));
    }
  }
  for (const x of [OUTPUT_X - 36, OUTPUT_X + 36]) {
    for (const y of [-150, -80]) {
      plate = difference(plate, verticalHole(18, 4.5, x, y, -3));
    }
  }
  for (const x of [-265, 265]) {
    for (const y of [-145, 145]) {
      plate = difference(plate, verticalHole(18, 6.5, x, y, -3));
    }
  }
  return plate
    .color('#6f7d8c')
    .material({ metalness: 0.4, roughness: 0.52 })
    .withConnectors({
      output_support: connector({
        origin: [OUTPUT_X, 0, SHAFT_Z],
        axis: [0, 0, 1],
        up: [1, 0, 0],
        kind: 'fixed',
      }),
      input_carrier: connector({
        origin: [INPUT_X, 0, SHAFT_Z],
        axis: [0, 0, 1],
        up: [1, 0, 0],
        kind: 'fixed',
      }),
      belt_datum: connector({
        origin: [OUTPUT_X, 0, SHAFT_Z],
        axis: [0, 0, 1],
        up: [1, 0, 0],
        kind: 'fixed',
      }),
    });
}

function inputCarrier() {
  let plate = box(130, 270, 12).translate(0, -45, -148);
  for (const x of CARRIER_HOLE_X) {
    for (const y of CARRIER_HOLE_Y) {
      plate = difference(plate, verticalHole(18, 4.5, x, y, -151));
    }
  }
  for (const x of [-21, 21]) {
    for (const y of [-145, -85]) {
      plate = difference(plate, verticalHole(18, 3.3, x, y, -151));
    }
  }
  for (const x of [-40, 40]) {
    for (const y of [20, 55]) {
      plate = difference(plate, verticalHole(18, 3.3, x, y, -151));
    }
  }
  return plate
    .color('#8a98a6')
    .material(aluminium)
    .withConnectors({
      base: fixedMount(),
      input_support: childMount(),
      servo_mount: childMount(),
    });
}

function outputSupport() {
  const frontBlock = bearingBlock(-150, 100, 14, -148, 24, 23.5)
    .color('#4c5968')
    .material(steel);
  const rearBlock = bearingBlock(-80, 100, 14, -148, 24, 23.5)
    .color('#4c5968')
    .material(steel);
  const frontBearing = axialRing(14, 23.5, 10.02, 0)
    .color('#a9b4c0')
    .material(steel);
  const rearBearing = axialRing(14, 23.5, 10.02, 0)
    .color('#a9b4c0')
    .material(steel);
  verify.clearanceBetween(
    'Output bearing is seated without positive interference in envelope CAD',
    frontBearing.translate(0, -150, 0),
    frontBlock,
    -0.01,
    0.05,
    2,
  );
  const crossbar = box(100, 92, 18).translate(0, -115, -148).material(steel);
  const retainer = () => axialRing(3, 30, 10.2, 0)
    .color('#788694')
    .material(steel)
    .withConnectors({ mount: fixedMount() });
  let housingShape = union(frontBlock, rearBlock, crossbar);
  for (const x of [-36, 36]) {
    for (const y of [-150, -80]) {
      housingShape = difference(housingShape, verticalHole(28, 4.5, x, y, -151));
    }
  }
  const housing = housingShape
    .color('#4c5968')
    .material(steel)
    .withConnectors({
      base: fixedMount(),
      output_axis: shaftConnector([0, -1, 0]),
      front_bearing: connector({ origin: [0, -150, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      rear_bearing: connector({ origin: [0, -80, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      front_outer_retainer: connector({ origin: [0, -158.5, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      front_inner_retainer: connector({ origin: [0, -141.5, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      rear_inner_retainer: connector({ origin: [0, -88.5, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      rear_outer_retainer: connector({ origin: [0, -71.5, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      encoder_bracket: connector({ origin: [0, -44, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
    });
  return {
    housing,
    frontBearing: frontBearing.withConnectors({ mount: fixedMount() }),
    rearBearing: rearBearing.withConnectors({ mount: fixedMount() }),
    frontOuterRetainer: retainer(),
    frontInnerRetainer: retainer(),
    rearInnerRetainer: retainer(),
    rearOuterRetainer: retainer(),
  };
}

function outputRotor() {
  const shaftBlank = axialCylinder(180, 10, -125);
  const pulleyKeyway = box(6.1, 32, 4).translate(0, BELT_Y, 7);
  const armKeyway = box(6.1, 20, 4).translate(0, ARM_Y, 7);
  const shaft = difference(shaftBlank, pulleyKeyway, armKeyway)
    .color('#b8c3ce')
    .material(steel);
  const pulleyBody = axialRing(25, 71.044, 28.52, 0)
    .color('#3c4652')
    .material(steel);
  const frontFlange = axialRing(2, 76, 28.52, -13.0)
    .color('#596675')
    .material(steel);
  const rearFlange = axialRing(2, 76, 28.52, 13.0)
    .color('#596675')
    .material(steel);
  const bushing = axialRing(25.4, 28.5, 10.02, 0)
    .color('#8793a0')
    .material(steel);
  const armBeam = box(armLength - 25, 14, 20)
    .translate((armLength + 25) / 2, 0, -10)
    .color('#d07b24')
    .material(aluminium);
  const armHub = axialRing(20, 30, 10.02, 0)
    .color('#bf6818')
    .material(aluminium);
  const loadRadius = 32 + representativeMass * 6;
  const tipLoad = axialCylinder(55, loadRadius, 0)
    .translate(armLength, 0, 0)
    .color('#805a3b')
    .material({ metalness: 0.62, roughness: 0.42 });
  const fabricatedArm = union(armBeam, armHub)
    .color('#d07b24')
    .material(aluminium);
  verify.intentionalOverlap(
    'Representative mass clamps around arm',
    fabricatedArm,
    tipLoad,
    'The adjustable mass is represented as a clamp around the fabricated arm.',
  );
  const pulley = union(pulleyBody, frontFlange, rearFlange)
    .color('#3c4652')
    .material(steel)
    .withConnectors({ mount: fixedMount() });
  return {
    shaft: shaft.withConnectors({
      axis: shaftConnector([0, 1, 0]),
      pulley_mount: connector({ origin: [0, BELT_Y, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      bushing_mount: connector({ origin: [0, BELT_Y, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      arm_mount: connector({ origin: [0, ARM_Y, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      mass_mount: connector({ origin: [0, ARM_Y, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
    }),
    pulley,
    bushing: bushing.withConnectors({ mount: fixedMount() }),
    arm: fabricatedArm.withConnectors({ mount: fixedMount() }),
    mass: tipLoad.withConnectors({ mount: fixedMount() }),
  };
}

function outputEncoderAssembly() {
  const bracketPlate = difference(
    box(80, 8, 172).translate(0, 0, -148),
    axialCylinder(12, 11.2, 0),
  );
  const bracketFoot = box(100, 58, 10).translate(0, 25, -148);
  const bracket = union(bracketPlate, bracketFoot)
    .color('#657383')
    .material(steel)
    .withConnectors({
      mount: fixedMount(),
      encoder_mount: connector({
        origin: [0, -14, 0],
        axis: [0, 0, 1],
        up: [1, 0, 0],
        kind: 'fixed',
      }),
    });
  const encoderBody = axialRing(20, 30.5, 10.15, 0)
    .color('#315f86')
    .material(polymer)
    .withConnectors({ mount: fixedMount() });
  return { bracket, encoderBody };
}

function inputSupport() {
  const frontBlock = bearingBlock(-145, 56, 7.142, -136, 16, 11.1125)
    .color('#566474')
    .material(steel);
  const rearBlock = bearingBlock(-85, 56, 7.142, -136, 16, 11.1125)
    .color('#566474')
    .material(steel);
  const frontBearing = axialRing(7.142, 11.1125, 9.525 / 2 + 0.02, 0)
    .color('#a9b4c0')
    .material(steel);
  const rearBearing = axialRing(7.142, 11.1125, 9.525 / 2 + 0.02, 0)
    .color('#a9b4c0')
    .material(steel);
  verify.clearanceBetween(
    'Input bearing is seated without positive interference in envelope CAD',
    frontBearing.translate(0, -145, 0),
    frontBlock,
    -0.01,
    0.05,
    2,
  );
  const crossbar = box(56, 78, 16).translate(0, -115, -136).material(steel);
  const retainer = () => axialRing(3, 15, 4.95, 0)
    .color('#788694')
    .material(steel)
    .withConnectors({ mount: fixedMount() });
  let housingShape = union(frontBlock, rearBlock, crossbar);
  for (const x of [-21, 21]) {
    for (const y of [-145, -85]) {
      housingShape = difference(housingShape, verticalHole(25, 3.3, x, y, -139));
    }
  }
  const housing = housingShape
    .color('#566474')
    .material(steel)
    .withConnectors({
      base: fixedMount(),
      input_axis: shaftConnector([0, -1, 0]),
      front_bearing: connector({ origin: [0, -145, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      rear_bearing: connector({ origin: [0, -85, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      front_outer_retainer: connector({ origin: [0, -150.071, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      front_inner_retainer: connector({ origin: [0, -139.929, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      rear_inner_retainer: connector({ origin: [0, -90.071, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      rear_outer_retainer: connector({ origin: [0, -79.929, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
    });
  return {
    housing,
    frontBearing: frontBearing.withConnectors({ mount: fixedMount() }),
    rearBearing: rearBearing.withConnectors({ mount: fixedMount() }),
    frontOuterRetainer: retainer(),
    frontInnerRetainer: retainer(),
    rearInnerRetainer: retainer(),
    rearOuterRetainer: retainer(),
  };
}

function inputRotor() {
  const shaft = axialCylinder(132.5, 9.525 / 2, -93.75)
    .color('#c2ccd5')
    .material(steel);
  const pulley = axialRing(19, 27.5082 / 2, 9.525 / 2 + 0.02, 0)
    .color('#a6adb5')
    .material(aluminium);
  const frontFlange = axialRing(1.6, 15.875, 9.525 / 2 + 0.02, -10.3)
    .color('#c1c7cd')
    .material(aluminium);
  const rearFlange = axialRing(1.6, 15.875, 9.525 / 2 + 0.02, 10.3)
    .color('#c1c7cd')
    .material(aluminium);
  const coupling = difference(
    axialCylinder(45, 17.5, 0),
    axialCylinder(23.5, 9.525 / 2 + 0.02, -10.75),
    axialCylinder(23.5, 7.02, 10.75),
  )
    .color('#2f78a8')
    .material(aluminium);
  const purchasedPulley = union(pulley, frontFlange, rearFlange)
    .color('#a6adb5')
    .material(aluminium)
    .withConnectors({ mount: fixedMount() });
  return {
    shaft: shaft.withConnectors({
      axis: shaftConnector([0, 1, 0]),
      pulley_mount: connector({ origin: [0, BELT_Y, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
      coupling_mount: connector({ origin: [0, -27.5, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
    }),
    pulley: purchasedPulley,
    coupling: coupling.withConnectors({ mount: fixedMount() }),
  };
}

function servoAssembly() {
  const body = box(60, 146.7, 79)
    .translate(0, 73.35, -39.5)
    .color('#252b33')
    .material({ metalness: 0.4, roughness: 0.38 });
  const frontPlate = box(70, 6, 190)
    .translate(0, -3, -136)
    .subtract(axialCylinder(10, 27, -3))
    .color('#657383')
    .material(steel);
  const bracketFoot = box(100, 75, 10).translate(0, 34.5, -136).material(steel);
  const leftBrace = box(8, 55, 100).translate(-35, 27.5, -126).material(steel);
  const rightBrace = box(8, 55, 100).translate(35, 27.5, -126).material(steel);
  const motorShaft = axialCylinder(22.5, 7, -11.25)
    .color('#c7d0d8')
    .material(steel);
  const brakeCap = axialCylinder(8, 31, 150.7)
    .color('#1f252c')
    .material(polymer);
  const motor = union(body, motorShaft, brakeCap)
    .color('#252b33')
    .material({ metalness: 0.4, roughness: 0.38 })
    .withConnectors({ mount: fixedMount() });
  let bracketShape = union(frontPlate, bracketFoot, leftBrace, rightBrace);
  for (const x of [-40, 40]) {
    for (const y of [20, 55]) {
      bracketShape = difference(bracketShape, verticalHole(16, 3.3, x, y, -139));
    }
  }
  const bracket = bracketShape
    .color('#657383')
    .material(steel)
    .withConnectors({
    base: fixedMount(),
    motor_mount: connector({ origin: [0, 0, 0], axis: [0, 0, 1], up: [1, 0, 0], kind: 'fixed' }),
  });
  return { motor, bracket };
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
    .material({ metalness: 0, roughness: 0.86 })
    .withConnectors({ base: fixedMount() });
}

const base = slottedBasePlate();
const carrier = inputCarrier();
const outputHousing = outputSupport();
const outputMoving = outputRotor();
const outputEncoder = outputEncoderAssembly();
const inputHousing = inputSupport();
const inputMoving = inputRotor();
const servo = servoAssembly();
const belt = beltEnvelope();

const bench = assembly('P1 single-axis bench')
  .addPart('Base plate', base, {
    material: '6082-T6 or 6061 aluminium',
    process: 'machined or accurately drilled prototype plate',
    massKg: 7.0,
  })
  .addPart('Adjustable input carrier', carrier, {
    material: '12 mm 6082-T6 or 6061-T6 aluminium',
    process: 'machined or accurately drilled prototype plate',
  })
  .addPart('Output housing', outputHousing.housing, { material: 'fabricated steel' })
  .addPart('Output front bearing', outputHousing.frontBearing, { material: 'purchased bearing' })
  .addPart('Output rear bearing', outputHousing.rearBearing, { material: 'purchased bearing' })
  .addPart('Output front outer retainer', outputHousing.frontOuterRetainer, { material: 'fabricated steel' })
  .addPart('Output front inner retainer', outputHousing.frontInnerRetainer, { material: 'fabricated steel' })
  .addPart('Output rear inner retainer', outputHousing.rearInnerRetainer, { material: 'fabricated steel' })
  .addPart('Output rear outer retainer', outputHousing.rearOuterRetainer, { material: 'fabricated steel' })
  .addPart('Output shaft', outputMoving.shaft, { material: 'steel' })
  .addPart('P90 pulley', outputMoving.pulley, { material: 'purchased ductile iron pulley' })
  .addPart('1610 bushing', outputMoving.bushing, { material: 'purchased steel bushing' })
  .addPart('Representative arm', outputMoving.arm, { material: 'fabricated aluminium' })
  .addPart('Representative mass', outputMoving.mass, { massKg: representativeMass })
  .addPart('Output encoder bracket', outputEncoder.bracket, { material: 'fabricated steel' })
  .addPart('US Digital E6 envelope', outputEncoder.encoderBody, { material: 'purchased encoder' })
  .addPart('Input housing', inputHousing.housing, { material: 'fabricated steel' })
  .addPart('Input front bearing', inputHousing.frontBearing, { material: 'purchased bearing' })
  .addPart('Input rear bearing', inputHousing.rearBearing, { material: 'purchased bearing' })
  .addPart('Input front outer retainer', inputHousing.frontOuterRetainer, { material: 'fabricated steel' })
  .addPart('Input front inner retainer', inputHousing.frontInnerRetainer, { material: 'fabricated steel' })
  .addPart('Input rear inner retainer', inputHousing.rearInnerRetainer, { material: 'fabricated steel' })
  .addPart('Input rear outer retainer', inputHousing.rearOuterRetainer, { material: 'fabricated steel' })
  .addPart('Input jackshaft', inputMoving.shaft, { material: 'steel' })
  .addPart('P18 pulley', inputMoving.pulley, { material: 'purchased aluminium pulley' })
  .addPart('Flexible coupling', inputMoving.coupling, { material: 'purchased coupling' })
  .addPart('Motor bracket', servo.bracket, { material: 'fabricated steel' })
  .addPart('Leadshine servo', servo.motor, { massKg: 1.65, material: 'purchased servo' })
  .addPart('600-5MGT-15 belt envelope', belt, { material: 'rubber synchronous belt' })
  .connect('Base plate.output_support', 'Output housing.base', { as: 'output_support_mount' })
  .connect('Output housing.front_bearing', 'Output front bearing.mount', { as: 'output_front_bearing_seat' })
  .connect('Output housing.rear_bearing', 'Output rear bearing.mount', { as: 'output_rear_bearing_seat' })
  .connect('Output housing.front_outer_retainer', 'Output front outer retainer.mount', { as: 'output_front_outer_retainer_mount' })
  .connect('Output housing.front_inner_retainer', 'Output front inner retainer.mount', { as: 'output_front_inner_retainer_mount' })
  .connect('Output housing.rear_inner_retainer', 'Output rear inner retainer.mount', { as: 'output_rear_inner_retainer_mount' })
  .connect('Output housing.rear_outer_retainer', 'Output rear outer retainer.mount', { as: 'output_rear_outer_retainer_mount' })
  .connect('Output housing.output_axis', 'Output shaft.axis', {
    as: 'output_angle',
    min: -45,
    max: 80,
    default: outputAngle,
    unit: 'deg',
  })
  .connect('Output shaft.pulley_mount', 'P90 pulley.mount', { as: 'p90_shaft_mount' })
  .connect('Output shaft.bushing_mount', '1610 bushing.mount', { as: 'bushing_shaft_mount' })
  .connect('Output shaft.arm_mount', 'Representative arm.mount', { as: 'arm_shaft_mount' })
  .connect('Output shaft.mass_mount', 'Representative mass.mount', { as: 'mass_shaft_mount' })
  .connect('Output housing.encoder_bracket', 'Output encoder bracket.mount', { as: 'encoder_bracket_mount' })
  .connect('Output encoder bracket.encoder_mount', 'US Digital E6 envelope.mount', { as: 'encoder_mount' })
  .connect('Base plate.input_carrier', 'Adjustable input carrier.base', { as: 'input_carrier_mount' })
  .connect('Adjustable input carrier.input_support', 'Input housing.base', { as: 'input_support_mount' })
  .connect('Input housing.front_bearing', 'Input front bearing.mount', { as: 'input_front_bearing_seat' })
  .connect('Input housing.rear_bearing', 'Input rear bearing.mount', { as: 'input_rear_bearing_seat' })
  .connect('Input housing.front_outer_retainer', 'Input front outer retainer.mount', { as: 'input_front_outer_retainer_mount' })
  .connect('Input housing.front_inner_retainer', 'Input front inner retainer.mount', { as: 'input_front_inner_retainer_mount' })
  .connect('Input housing.rear_inner_retainer', 'Input rear inner retainer.mount', { as: 'input_rear_inner_retainer_mount' })
  .connect('Input housing.rear_outer_retainer', 'Input rear outer retainer.mount', { as: 'input_rear_outer_retainer_mount' })
  .connect('Input housing.input_axis', 'Input jackshaft.axis', {
    as: 'input_angle',
    min: -225,
    max: 400,
    default: 0,
    unit: 'deg',
    follows: { joint: 'output_angle', ratio: RATIO, offset: 0 },
  })
  .connect('Input jackshaft.pulley_mount', 'P18 pulley.mount', { as: 'p18_shaft_mount' })
  .connect('Input jackshaft.coupling_mount', 'Flexible coupling.mount', { as: 'coupling_shaft_mount' })
  .connect('Adjustable input carrier.servo_mount', 'Motor bracket.base', { as: 'motor_bracket_mount' })
  .connect('Motor bracket.motor_mount', 'Leadshine servo.mount', { as: 'servo_mount' })
  .connect('Base plate.belt_datum', '600-5MGT-15 belt envelope.base', { as: 'belt_mount' });

bench.addAnimation('Full representative sweep', {
  duration: 4,
  loop: true,
  keyframes: [
    { values: { output_angle: -45 } },
    { values: { output_angle: 80 } },
    { values: { output_angle: -45 } },
  ],
});

bom(1, 'Leadshine iSV2-RS6040V48G integrated 48 V servo with brake');
bom(1, 'Gates P18-5MGT-15AL aluminium pulley, 3/8 inch bore');
bom(1, 'Gates P90-5MGT-15 pulley');
bom(1, 'Gates 1610 taper bushing, 20 mm finished bore');
bom(1, 'Gates 600-5MGT-15 synchronous belt');
bom(2, '6204-2RS sealed output bearing, dynamic rating at least 12 kN');
bom(2, 'R6-2RS-envelope input bearing, dynamic rating at least 2 kN');
bom(4, 'output bearing retainer ring, 60 x 20.4 x 3 mm; bolt pattern VERIFY FROM DELIVERED COMPONENT');
bom(4, 'input bearing retainer ring, 30 x 9.9 x 3 mm; bolt pattern VERIFY FROM DELIVERED COMPONENT');
bom(1, '14 mm to 3/8 inch zero-backlash flexible coupling, at least 5 Nm');
bom(1, '20 mm steel output shaft, 180 mm prototype length');
bom(1, '3/8 inch steel input jackshaft, 132.5 mm prototype length');
bom(1, '600 x 360 x 12 mm aluminium base plate', { material: '6082-T6 or 6061' });
bom(1, '130 x 270 x 12 mm adjustable input carrier', { material: '6082-T6 or 6061' });
bom(1, 'fabricated output bearing housing, 70 mm bearing-centre span');
bom(1, 'fabricated input bearing housing, 60 mm bearing-centre span');
bom(1, 'braced fabricated servo bracket; mounting pattern VERIFY FROM DELIVERED COMPONENT');
bom(1, '280 mm representative aluminium output arm and hub');
bom(4, 'M8 carrier clamp set with washer and prevailing locking method');
bom(1, 'US Digital E6, 10000 CPR, 20 mm bore, differential output');
bom(1, 'fabricated fixed E6 encoder bracket');
bom(representativeMass, 'adjustable representative test mass', { unit: 'kg' });

dim([INPUT_X, 0, SHAFT_Z], [OUTPUT_X, 0, SHAFT_Z], {
  label: 'Nominal pulley centre distance',
  color: '#18b6d9',
});
dim([OUTPUT_X, ARM_Y, SHAFT_Z], [OUTPUT_X + armLength, ARM_Y, SHAFT_Z], {
  label: 'Representative arm radius',
  color: '#f0a040',
});
dim([-300, -180, 0], [300, -180, 0], { label: 'Base width 600 mm' });
dim([INPUT_X - 65, 90, 24], [INPUT_X + 65, 90, 24], {
  label: 'Input carrier width 130 mm',
  color: '#72d38f',
});
dim([INPUT_X + 65, -180, 24], [INPUT_X + 65, 90, 24], {
  label: 'Input carrier length 270 mm',
  color: '#72d38f',
});
dim([OUTPUT_X, -150, SHAFT_Z], [OUTPUT_X, -80, SHAFT_Z], {
  label: 'Output bearing span 70 mm',
  color: '#18b6d9',
});
dim([INPUT_X, -145, SHAFT_Z], [INPUT_X, -85, SHAFT_Z], {
  label: 'Input bearing span 60 mm',
  color: '#18b6d9',
});
dim([OUTPUT_X, -215, SHAFT_Z], [OUTPUT_X, -35, SHAFT_Z], {
  label: 'Output shaft length 180 mm',
  color: '#c9d4df',
});
dim([INPUT_X, -160, SHAFT_Z], [INPUT_X, -27.5, SHAFT_Z], {
  label: 'Input shaft length 132.5 mm',
  color: '#c9d4df',
});
dim(
  [NOMINAL_INPUT_X, 105, SHAFT_Z],
  [NOMINAL_INPUT_X - RELAXED_ADJUSTMENT, 105, SHAFT_Z],
  { label: 'Relaxed installation travel 21 mm', color: '#72d38f' },
);
dim(
  [NOMINAL_INPUT_X, 125, SHAFT_Z],
  [NOMINAL_INPUT_X - TENSIONED_ADJUSTMENT, 125, SHAFT_Z],
  { label: 'Tensioning travel 4 mm', color: '#72d38f' },
);

verify.equal('Exact transmission ratio', RATIO, 5, 1e-12);
verify.equal('Nominal calculated centre distance', NOMINAL_CENTRE, 154.36686875740537, 1e-9);
verify.inRange('Output angle is inside accepted travel', outputAngle, -45, 80);
verify.inRange(
  'Input carrier remains inside fixed slots',
  beltAdjustment,
  RELAXED_ADJUSTMENT,
  TENSIONED_ADJUSTMENT,
);
verify.physicalComponentCount(
  'Bench is one installed physical connectivity component',
  1,
);

scene({
  background: { top: '#c3ccd7', bottom: '#566474' },
  camera: { position: [520, -700, 410], target: [10, -70, 105], fov: 38 },
  views: {
    hero: { camera: { position: [520, -700, 410], target: [10, -70, 105], up: [0, 0, 1], fov: 38 } },
    belt: { camera: { position: [30, -720, 180], target: [20, -110, 155], up: [0, 0, 1], fov: 30 } },
    side: { camera: { position: [680, -210, 210], target: [20, -80, 110], up: [0, 0, 1], fov: 32 } },
    arm_clearance: { camera: { position: [360, -620, 40], target: [160, -190, 20], up: [0, 0, 1], fov: 35 } },
  },
  environment: { preset: 'studio', intensity: 0.2, background: false },
  lights: [
    { type: 'ambient', color: '#efe7dc', intensity: 0.15 },
    { type: 'directional', position: [260, -320, 420], color: '#ffe2bf', intensity: 2.8, castShadow: true },
    { type: 'directional', position: [-260, 210, 220], color: '#d4e6fb', intensity: 0.85 },
    { type: 'hemisphere', skyColor: '#c7d3df', groundColor: '#495463', intensity: 0.15 },
  ],
  ground: { visible: true, color: '#3d4854', height: -180, receiveShadow: true },
  jointOverlay: { axisColor: '#13dfff', arcColor: '#ff7a1a' },
});

return bench;
