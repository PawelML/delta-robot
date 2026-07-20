# BOM — robot delta DIY

**Status:** provisional v0.2 after P0 kinematics and first P1 dynamic model

**Date:** 2026-07-20

**Purchase rule:** do not buy three drives before the P1 single-axis bench gate

This is a controlled list of candidates, not a frozen shopping list. The
authoritative requirements are in `poc_plan.md`, numerical evidence in
`artifacts/geometry_comparison.json` and `artifacts/dynamic_sizing.json`, and
the representative drive contract in `docs/specs/p1-single-drive.md`.

## 1. Evidence that changed the initial BOM

- Selected kinematic geometry: base joint radius 180 mm, platform joint radius
  65 mm, upper arms 280 mm and lower arms 450 mm.
- The complete sampled Ø400×150 mm cylinder passes with minimum singularity
  margin 0.571 and minimum joint-limit reserve 11.96°.
- Conservative 0.50 kg / 1 Hz dynamic case requires 8.190 Nm peak and
  3.507 Nm RMS at the output joint.
- With 5:1 and 90% provisional efficiency, after a 30% load factor and the
  candidate motor's rotor inertia, the motor requirement is 2.401 Nm peak,
  1.026 Nm RMS and 330.48 rpm.
- The old 2.0–2.2 Nm NEMA 23 closed-loop stepper proposal is rejected: its
  holding torque is already below the required dynamic peak before pulley
  inertia, friction and torque-speed droop.

## 2. P1 single-drive bench BOM

Only this section is in near-term scope. Even these parts wait for confirmation
of the current Modbus register map and a completed belt-drive selection.

| Item | Candidate / requirement | Qty now | Status |
|---|---|---:|---|
| Integrated servo | Leadshine `iSV2-RS6040V48G`, 48 VDC, 400 W, 1.27 Nm rated, 3.81 Nm peak, 17-bit encoder, Pulse+Direction + Modbus RTU, brake | max. 1 | Provisional candidate; primary source: <https://www.leadshine.com/product-detail/iSV2-RS6040V48G.html> |
| Reduction | 5.00:1 synchronous belt; Gates PowerGrip GT3 or engineering equivalent, initially 5M pitch and at least 15 mm width | 1 set | Tooth counts, belt length and width must pass the Gates design procedure |
| Pulleys/hubs | Metal motor pulley; metal or structurally verified output pulley; keyed or clamping hubs | 1 set | No printed torque-carrying 100T pulley for P1 |
| Output shaft support | Shaft, two bearings, rigid housing and representative output arm/inertia | 1 set | Must permit external lost-motion measurement |
| 48 V bench supply | Nominal 48 VDC, at least the drive's published 10 A continuous requirement | 1 | Exact supply blocked by peak-current and regenerative-energy confirmation |
| Physical power cutoff | NC mushroom switch operating a correctly rated DC contactor/disconnect | 1 set | Workshop minimum; verify DC interruption rating |
| Command/diagnostic interface | Pulse+Direction source plus isolated RS485 adapter for Modbus diagnostics | 1 set | Controller architecture for the full robot remains open |
| External measurement | Dial indicator or external angular reference adequate to resolve 0.10° output lost motion | 1 | Required P1 evidence, not optional tooling |

Manufacturer data used for the candidate: 24–60 VDC input, 10 Arms continuous,
28 A peak, 3000 rpm rated, 4000 rpm maximum, 0.58 kg·cm² rotor inertia. Verify
the exact delivered revision and datasheet before payment.

Open blockers before ordering the P1 set:

1. Obtain the current iSV2-RS register manual or distributor confirmation that
   actual encoder position can be read over Modbus at a useful update rate.
2. Confirm DC-bus regeneration/overvoltage handling for repeated 1 Hz reversal.
3. Select exact belt, pulley diameters, centre distance and width using the
   manufacturer procedure, including motor-shaft overhung load:
   <https://www.gates.com/content/dam/documents-library/catalogs/powergrip-gt3-drive-design-manual-en.pdf>.
4. Confirm local availability, warranty, total landed price and compatible
   tuning/communication cables.

## 3. Mechanical candidate BOM for P2

These quantities describe the selected model geometry but remain blocked until
the P1 axis is retained.

| Item | Requirement | Qty | Status / measurement plan |
|---|---|---:|---|
| Lower rods | Carbon tube, 450 mm joint-centre length; current mass model starts from Ø12×10 mm | 6 | Final tube and insert design must keep all six rod/joint assemblies at or below the conservative 0.360 kg assumption, or rerun dynamics |
| Lower joints | Twelve low-clearance joints with articulation covering the full selected cylinder | 12 | igus KBRM/KGLM remains a candidate, not a validated selection; CAD and articulation test required |
| Upper arms | 280 mm shoulder-to-knee, rigid hub and link | 3 | Each complete arm assumed 0.200 kg nominal / 0.250 kg conservative; weigh representative P1/P2 part |
| Base joint layout | Three shoulder centres on radius 180 mm at the accepted arm azimuths | 1 set | CAD source of truth still required |
| Moving platform | Three virtual attachment centres on radius 65 mm | 1 | Platform + vacuum tooling assumed 0.250 kg nominal / 0.300 kg conservative |
| Parallelogram spacing | Rigid paired-rod spacers and hardware | 6 ends | Width, collisions and bearing angles not yet modelled |
| Frame | Aluminium extrusion/plate structure around the selected geometry | 1 | Size only after CAD collision and stiffness check; old “3 m of 3030” estimate is not validated |

Every completed mechanical assembly is weighed. A mass above any conservative
value triggers regeneration of `dynamic_sizing.json` before powered full-speed
testing.

## 4. Full robot drives and control — blocked

| Item | Future quantity | Current decision |
|---|---:|---|
| Two additional servo axes | 2 | Buy only after one axis completes 1,000 reversals, temperature, bus-voltage, position-error and lost-motion tests |
| Full three-axis DC supply / bus | 1 | Size after measured single-axis power and regeneration; the former 350 W supply is withdrawn |
| Motion controller | 1 | Not selected. P0/P1 do not justify freezing Klipper, ROS2+MCU or a commercial motion controller |
| Homing sensors | 3 | Type and mounting wait for P2 CAD |
| Supervisory computer | 1 | Existing computer/Raspberry Pi may be reused; do not buy solely from the old BOM |

The previous statement that Klipper `rotary_delta` and Moonraker are already the
chosen stack is withdrawn. Software architecture will be decided after the
representative servo's command and feedback interfaces are verified.

## 5. Vacuum, perception and conveyor — later gates

These remain P3/P4 candidates and are not justified purchases during P1:

| Subsystem | Candidate requirement | Gate |
|---|---|---|
| Vacuum source and valve | 12/24 V source, fast release, sized for the actual test part | P3 |
| Suction cups and tubing | Selected from part surface and mass | P3 |
| Vacuum switch | Independent grip confirmation | P3 |
| Camera and lighting | Calibratable view of the conveyor | P4 |
| Conveyor encoder | Resolution and interface derived from tracking error budget | P4 |

## 6. Cost status

The former `2,200–4,400 PLN` total is invalid because it assumed three cheap
steppers, a GT2 transmission and a 350 W supply that the dynamic model no longer
supports. Do not use it as a budget commitment.

Rebuild the cost table only after:

1. the exact one-axis servo, belt and supply are confirmed,
2. landed prices and warranty are checked on the purchase date,
3. P1 decides whether 400 W / 5:1 is retained,
4. CAD determines real frame, shafts, bearings and machined parts.

## 7. Build order

1. Resolve the four P1 purchasing blockers above.
2. Build one servo/belt/output-shaft bench axis and measure it.
3. Retain, reratio, upsize to 750 W or reject based on evidence.
4. Freeze BOM v1 and buy the remaining two drives only after the P1 gate.
5. Complete collision/stiffness CAD, build P2, then proceed to vacuum P3 and
   conveyor tracking P4.
