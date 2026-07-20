# BOM — robot delta DIY

**Status:** provisional v0.3 — purchase parameters for one P1 bench axis

**Date:** 2026-07-20

**Purchase rule:** do not buy three drives before the P1 single-axis bench gate

This is a controlled list of candidates, not a frozen three-axis shopping list. The
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
  selected pulleys, shafts, bushing, coupling, belt and motor rotor inertia, the
  motor requirement is 2.576 Nm peak, 1.096 Nm RMS and 330.48 rpm.
- Gates `18/90` with a `600-5MGT-15` belt gives exactly 5.00:1, nominal centre
  distance 154.37 mm, 6.82 small-pulley teeth in mesh and about 0.496 m/s belt
  speed. Design belt power is 68.0 W versus 244.0 W interpolated catalogue
  capacity at the operating speed.
- The conservative support-load screen is 376.5 N. The 3/8 inch input and 20 mm
  output shaft screens give 61.2 MPa and 15.1 MPa von Mises respectively,
  before keyway/fatigue concentration factors.
- The old 2.0–2.2 Nm NEMA 23 closed-loop stepper proposal is rejected: its
  holding torque is already below the required dynamic peak before pulley
  inertia, friction and torque-speed droop.

## 2. P1 single-drive bench BOM

Only this section is in near-term scope. Catalogue codes are purchasing
parameters, not a claim of local stock. Confirm every bore, revision, included
flange/bushing and landed price with the selected distributor before payment.

### 2.1 Drive and transmission

| Item | Concrete purchase parameter | Qty now | Evidence / acceptance |
|---|---|---:|---|
| Integrated servo | Leadshine `iSV2-RS6040V48G`; 24–60 VDC, nominal 48 V; 400 W; 1.27/3.81 Nm rated/peak; 3000/4000 rpm rated/max; brake; Pulse+Direction and Modbus RTU | max. 1 | Exact `G` revision and current manual on delivery; <https://www.leadshine.com/product-detail/iSV2-RS6040V48G.html> |
| Small pulley | Gates `P18-5MGT-15AL`; 18 teeth, 5MGT, 15 mm belt, aluminium, finished 3/8 inch bore | 1 | Published pitch diameter 28.651 mm and `WR²=0.000097 lb·ft²`; no pulley on the servo shaft |
| Large pulley | Gates `P90-5MGT-15`; 90 teeth, 5MGT, 15 mm belt, ductile iron, 1610 bushing interface | 1 | Published pitch diameter 143.239 mm and `WR²=0.1358 lb·ft²` |
| Taper bushing | Gates 1610, finished 20 mm bore, compatible key and screws included/ordered | 1 | Confirm exact metric-bore suffix and key dimensions with distributor |
| Belt | Gates PowerGrip GT3 `600-5MGT-15`; 600 mm pitch length, 5 mm pitch, 15 mm width, 120 teeth | 1 installed + 1 optional spare | Do not substitute 9 mm width or a different length without regenerating selection artifact |
| Flexible coupling | Zero-backlash jaw or bellows coupling, bores 14.000 mm and 9.525 mm, rated torque ≥5 Nm, speed ≥1000 rpm | 1 | Document allowed angular/radial/axial misalignment and clamp-screw torque; no set-screw-only generic coupler |

Primary transmission evidence is `artifacts/p1_transmission_selection.json` and
the manufacturer method is the Gates GT3 design manual:
<https://www.gates.com/content/dam/documents-library/catalogs/powergrip-gt3-drive-design-manual-en.pdf>.

### 2.2 Shafts, bearings and fixture

| Item | Concrete purchase/fabrication parameter | Qty | Acceptance before powered test |
|---|---|---:|---|
| Input jackshaft | C45/1045 or equivalent steel, Ø9.525 mm, prototype length 132.5 mm in CAD; bearing/pulley journals straight and undamaged | 1 | Final length may follow selected coupling/retainers; pulley remains between bearings |
| Input bearings | Sealed `R6-2RS` envelope, 9.525 × 22.225 × 7.142 mm, dynamic rating ≥2 kN | 2 | Buy one matched supplier series and use its actual fit data in the housing drawing |
| Output shaft | C45/1045 or equivalent steel, Ø20 mm, prototype length 180 mm | 1 | Add real keyway/retention drawing before machining; pulley between bearings, arm outside support span |
| Output bearings | `6204-2RS`, 20 × 47 × 14 mm, dynamic rating ≥12 kN | 2 | Normal internal clearance unless supplier/fit calculation justifies otherwise |
| Base plate | 6082-T6 or 6061-T6 aluminium, 600 × 360 × 12 mm | 1 | Flat, clamped/bolted to bench edge so the +80° arm sweep remains unobstructed |
| Bearing housings | Fabricated or machined carriers matching the parametric CAD and actual bearing fits | 1 input + 1 output | CAD envelopes are not fabrication drawings; add shoulders, retainers and fasteners before machining |
| Output arm | 280 mm shaft centre to load centre; target complete arm/hub mass 0.250 kg | 1 | Weigh and enter actual mass before full-speed run |
| Adjustable load | 1.035 kg nominal at 280 mm radius, adjustable/removable in small increments | 1 set | This matches maximum calculated joint inertia only; secure mechanically and record actual radius/mass |
| Fasteners/retainers | Property class and dimensions derived from final housing drawings; prevailing locking method on rotating joints | 1 set | No unspecified friction-only retention for pulley, arm hub or test mass |

Parametric layout source:
`cad/2026/07/20/p1-single-axis-bench/main.forge.js`. It validates -45°, 0°
and +80° envelope poses but does not replace shaft keyway, bearing-fit or
fastener manufacturing drawings.

### 2.3 Electrical, braking and measurements

| Item | Concrete purchase parameter | Qty | Acceptance / uncertainty |
|---|---|---:|---|
| 48 VDC supply | Regulated 48 VDC, ≥600 W / ≥12.5 A continuous for the one-axis bench, current limiting, output overvoltage tolerance coordinated with braking | 1 | Provisional rating; confirm with drive distributor and measured regeneration before later multi-axis supply selection |
| Regenerative resistor | Non-inductive/chassis resistor 10 Ω, ≥100 W continuous nameplate, insulated terminals and ventilated mounting | 1 | Current manual's starting test value for RS6040; never below 5 Ω; monitor temperature, brake load `<80%` and driver `<60°C` during P1 |
| DC isolation/cutoff | 60 VDC minimum, ≥30 A DC-rated disconnect/contactor operated by a normally-closed mushroom circuit | 1 set | Workshop power cutoff only; verify DC interruption rating, fuse and wiring with an electrician if uncertain |
| Branch protection/wiring | Fuse/breaker and copper conductors rated for 60 VDC and the selected 12.5 A continuous supply, with PE bonding where applicable | 1 set | Size from actual cable length, installation and manufacturer terminal limits |
| Motion command source | 5 V differential Pulse+Direction line driver, capability ≥500 kHz, hardware servo-enable output | 1 | P1 tool, not a decision for the final robot controller |
| Modbus diagnostics | Galvanically isolated RS485 adapter supporting Modbus RTU plus correct CN5 cable/breakout | 1 | Verify address, baud, grounding and achievable polling rate on delivered drive |
| Configuration cable | Leadshine `CABLE-PC-1` or confirmed current equivalent for CN7/commissioning | 1 | Confirm connector compatibility for exact revision |
| Temperature measurement | Contact probe or calibrated IR method covering at least 0–120°C | 1 | Record driver, motor case and regenerative-resistor method/location |
| Lost-motion reference | External angular encoder with ≤0.02° resolution at output, or dial indicator geometry with equivalent ≤0.02° angular resolution | 1 | Required to judge the 0.10° target; internal encoder counts alone are insufficient |
| Belt tension measurement | Gates-compatible sonic-frequency measurement or documented span force/deflection tool | 1 | Initial model setting is 100.1 N per span; record actual span, frequency/force and method |

Manufacturer data used for the candidate: 24–60 VDC input, 10 Arms continuous
motor phase current, 28 A peak current, 3000 rpm rated, 4000 rpm maximum and
0.58 kg·cm² rotor inertia. Phase current is not treated as DC-supply input
current. Verify the exact delivered revision and datasheet before payment.

Resolved in software/documentation: exact belt geometry, published pulley
inertias, separately supported input shaft, current position/temperature/bus
register addresses, parametric layout and an automatic simulator-only P1 report.

Remaining blockers before ordering the single P1 set:

1. Confirm local availability, finished bores, exact servo revision, warranty,
   total landed price and return policy.
2. Obtain written supply/regeneration confirmation for the selected 48 V supply
   and 10 Ω / 100 W resistor combination.
3. Freeze actual bearing series, fits, shaft retention/keyways and fasteners in
   fabrication drawings based on delivered component dimensions.
4. Confirm the external angle/temperature/belt-tension measurement method.

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

1. Resolve the four remaining P1 purchasing blockers above.
2. Build one servo/belt/output-shaft bench axis and measure it.
3. Retain, reratio, upsize to 750 W or reject based on evidence.
4. Freeze BOM v1 and buy the remaining two drives only after the P1 gate.
5. Complete collision/stiffness CAD, build P2, then proceed to vacuum P3 and
   conveyor tracking P4.
