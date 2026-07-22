# BOM — robot delta DIY

**Status:** retained industrial reference v0.4 — inactive purchase plan

**Date:** 2026-07-20

**Purchase rule:** do not order from this document while the budget profile is active

This is the preserved `industrial_reference` list, not the active shopping list
for the 5--6 kPLN `budget_demonstrator`. It remains useful for comparison and a
future upgrade. The active provisional list is now `BOM_budget_delta.md`; its
20/60 transmission is digitally screened and costed but still requires a
physical single-axis P1 before the other two mechanical axes are released. The
authoritative requirements are in `poc_plan.md`, numerical evidence in
`artifacts/geometry_comparison.json`, `artifacts/dynamic_sizing.json` and
`artifacts/budget_performance_envelope.json`, and
the representative drive contract in `docs/specs/p1-single-drive.md`.
Operacyjna kolejność ofert, zakupów, pomiarów i zwolnienia rysunków znajduje się
w `docs/p1-procurement-checklist.md`.

## 1. Evidence that changed the initial BOM

- Selected kinematic geometry: base joint radius 180 mm, platform joint radius
  65 mm, upper arms 280 mm and lower arms 450 mm.
- The complete sampled Ø400×150 mm cylinder passes with minimum singularity
  margin 0.571 and minimum joint-limit reserve 11.96°.
- The centred 305×200 mm conveyor footprint has 17.64 mm radial reserve inside
  that cylinder; all 10,416 full-height samples pass the design margins.
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

## 2. Industrial-reference P1 single-drive bench BOM

This section is retained reference scope, not near-term purchasing scope.
Catalogue codes are purchasing
parameters, not a claim of local stock. Confirm every bore, revision, included
flange/bushing and landed price with the selected distributor before payment.

### 2.1 Drive and transmission

| Item | Concrete purchase parameter | Qty now | Evidence / acceptance |
|---|---|---:|---|
| Integrated servo | Leadshine `iSV2-RS6040V48G`; 24–60 VDC, nominal 48 V; 400 W; 1.27/3.81 Nm rated/peak; 3000/4000 rpm rated/max; brake; Pulse+Direction and Modbus RTU | max. 1 | Exact `G` revision and current manual on delivery; <https://www.leadshine.com/product-detail/iSV2-RS6040V48G.html> |
| Small pulley | Gates `P18-5MGT-15AL`, no. `7845-1518`; 18 teeth, 5MGT, 15 mm belt, aluminium; final bore 3/8 inch required | 1 | Published pitch diameter 28.651 mm and `WR²=0.000097 lb·ft²`; catalogue bore range is not proof of a finished 3/8 inch bore, so confirm machining and retention; no pulley on the servo shaft |
| Large pulley | Gates `P90-5MGT-15`, no. `7709-1090`; 90 teeth, 5MGT, 15 mm belt, ductile iron, 1610 bushing interface | 1 | Published pitch diameter 143.239 mm and `WR²=0.1358 lb·ft²` |
| Taper bushing | Gates `1610-20MM`, no. `7858-1620`, finished 20 mm bore, compatible key and screws included/ordered | 1 | Confirm key dimensions and direct compatibility with the quoted P90; a generic 1610-20 is not an automatic substitute |
| Belt | Gates PowerGrip GT3 `600-5MGT3-15`, no. `9400-55202`; 600 mm pitch length, 5 mm pitch, 15 mm width, 120 teeth | 1 installed + 1 optional spare | Current catalogue name for the selected 600-5MGT-15 geometry; do not substitute 9 mm width or a different length without regenerating selection artifact |
| Flexible coupling | Zero-backlash jaw or bellows coupling, bores 14.000 mm and 9.525 mm, rated torque ≥5 Nm, speed ≥1000 rpm | 1 | Document allowed angular/radial/axial misalignment and clamp-screw torque; no set-screw-only generic coupler. Regenerate CAD for the real envelope: the first qualifying Ruland candidate is Ø41.3 × 51.7 mm versus the Ø35 × 45 mm placeholder |

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
| Adjustable input carrier | 6082-T6 or 6061-T6 aluminium, 12 mm plate; carries servo bracket and both input supports as one rigid datum | 1 | Four fixed M8 base slots provide -21 to +4 mm centre-distance adjustment; verify edge distance and clamp access |
| Bearing housings | Fabricated or machined carriers matching the parametric CAD and actual bearing fits | 1 input + 1 output | Candidate package has closed seats and separate face retainers; calculate final fits and add retainer bolt circles from delivered bearings before machining |
| Output arm | 280 mm shaft centre to load centre; target complete arm/hub mass 0.250 kg | 1 | Weigh and enter actual mass before full-speed run |
| Adjustable load | 1.035 kg nominal at 280 mm radius, adjustable/removable in small increments | 1 set | This matches maximum calculated joint inertia only; secure mechanically and record actual radius/mass |
| Fasteners/retainers | Property class and dimensions derived from final housing drawings; prevailing locking method on rotating joints | 1 set | No unspecified friction-only retention for pulley, arm hub or test mass |

Parametric layout source:
`cad/2026/07/20/p1-single-axis-bench/main.forge.js`. It validates -45°, 0°
and +80° envelope poses. The STEP/report and controlled custom-part dimensions
are listed in `docs/p1-bench-fabrication-package.md`; open fit, keyway and
supplier-pattern items remain explicitly blocked from final machining release.

### 2.3 Electrical, braking and measurements

| Item | Concrete purchase parameter | Qty | Acceptance / uncertainty |
|---|---|---:|---|
| 48 VDC supply | Regulated 48 VDC, ≥600 W / ≥12.5 A continuous for the one-axis bench, current limiting, output overvoltage tolerance coordinated with braking | 1 | Provisional rating; confirm with drive distributor and measured regeneration before later multi-axis supply selection |
| Regenerative resistor | Non-inductive/chassis resistor 10 Ω, ≥100 W continuous nameplate, insulated terminals and ventilated mounting | 1 | Current manual's starting test value for RS6040; never below 5 Ω; monitor temperature, brake load `<80%` and driver `<60°C` during P1 |
| DC isolation/cutoff | 60 VDC minimum, ≥30 A DC-rated disconnect/contactor operated by a normally-closed mushroom circuit | 1 set | Workshop power cutoff only; verify DC interruption rating, fuse and wiring with an electrician if uncertain |
| Branch protection/wiring | Fuse/breaker and copper conductors rated for 60 VDC and the selected 12.5 A continuous supply, with PE bonding where applicable | 1 set | Size from actual cable length, installation and manufacturer terminal limits |
| Motion command and encoder capture | Mesa `7I96S`, used with Ethernet-connected LinuxCNC >=2.8.4; five 5 V differential step/dir channels, encoder input and isolated I/O | 1 | P1 tool, not a final controller decision. Manufacturer store showed out of stock, while a European supplier listed stock on 2026-07-20; confirm genuine traceable revision and delivered price |
| Mesa/encoder logic supply | Regulated 5.0 VDC, at least 1 A continuous, within 4.75–5.25 V at the 7I96S terminals | 1 | Separate purchasing item; include the 7I96S consumption, E6 load and wiring drop, and never feed P4 from 48 V |
| Modbus diagnostics | Waveshare `USB TO RS485 (C)`, SKU 34620, isolated FT232RNL adapter, plus correct CN5 cable/breakout | 1 | Verify address, baud, A/B/GND reference and measured polling rate on delivered drive |
| Configuration cable | Leadshine `CABLE-PC-1` or confirmed current equivalent for CN7/commissioning | 1 | Confirm connector compatibility for exact revision |
| Temperature logger | Pico Technology `USB TC-08`, order code `PP222`, 8 channels, Linux SDK, plus at least four suitable type-K surface/ambient probes | 1 set | Log servo/drive housing, output-bearing housing, regenerative resistor and ambient; confirm probe attachment and temperature range |
| Lost-motion reference | US Digital `E6`, 10,000 CPR, 20 mm bore, 5 V differential quadrature, index preferred; correct cover/base/cable and centring tool | 1 set | 40,000 counts/rev gives 0.009°/count. Capture at the rear output-shaft extension; internal encoder alone is insufficient |
| Belt tension measurement | Mark-10 `M3-5`, 25 N range, 0.02 N resolution, calibration certificate; fabricated full-width belt contact and fixed deflection stop | 1 set | Nominal tangent span is 143.34 mm and Gates deflection is 2.240 mm. Record actual span/force; the simple 100.1 N string estimate of about 6.26 N is not the acceptance range |

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
4. Obtain a combined quote for the exact E6 configuration, TC-08 probes and
   calibrated force gauge; confirm genuine 7I96S availability or pause purchase.

The dated market snapshot, supplier links and RFQ text are recorded in
`docs/p1-supplier-research-poland-2026-07-20.md`. Public stock is not written
confirmation and does not close any purchasing blocker.

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

1. Resolve the four remaining P1 purchasing blockers and complete the quotation
   phase in `docs/p1-procurement-checklist.md`.
2. Buy at most one set of catalogue/reference components for P1.
3. Measure delivered parts, close fits, keyways, retention and supplier-specific
   holes, then release updated fabrication drawings.
4. Fabricate and assemble one servo/belt/output-shaft bench axis.
5. Run the physical 1,000-reversal P1 gate and retain, reratio, upsize to 750 W
   or reject based on evidence.
6. Freeze BOM v1 and buy the remaining two drives only after the P1 gate.
7. Complete collision/stiffness CAD, build P2, then proceed to vacuum P3 and
   conveyor tracking P4.
