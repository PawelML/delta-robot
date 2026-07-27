# P1 budget mechanical and cost closure

**Status:** implementation specification  
**Version:** 1.1
**Date:** 2026-07-27

## 1. Problem and decision boundary

The proxy performance sweep selected the catalogue HTD 5M `20/60`, 15 mm,
450 mm transmission for the active `budget_demonstrator`, but deliberately left
belt preload, shaft support, representative CAD and the complete 5--6 kPLN
cost envelope open. This slice shall close those digital questions without
claiming that P1 has passed and without authorising a purchase.

The retained `industrial_reference` calculations, BOM and CAD are regression
evidence and shall not be overwritten. The accepted delta geometry, useful
workspace and P0 trajectory remain unchanged.

## 2. Inputs and units

Python calculations use SI units. ForgeCAD receives millimetres and degrees at
the model boundary.

Fixed inputs:

- transmission: HTD 5M, 20/60 teeth, 15 mm width, 450 mm pitch length;
- nominal shaft-centre distance: the existing belt-geometry solver result;
- proxy design points: 0.50 kg / 1.50 s and 0.30 kg / 1.25 s;
- application load factor: 1.30;
- motor shaft dynamic radial-load limit: 75 N at 20 mm from the motor face;
- Gates minimum installation tension for a 15 mm-wide 5M HTD belt:
  13.5 lbf per span, converted with exactly 4.4482216152605 N/lbf;
- input shaft: provisional C45 steel, 8 mm diameter and 100 mm model length;
- input support: two SKF 608-2RSH-envelope bearings, 8x22x7 mm, with the 20T
  pulley centred in a 50 mm bearing span;
- coupling: R+W BKL/3/8/8 envelope, 3 Nm rated torque, 25 mm diameter, 32 mm
  length and 0.027 kg catalogue mass;
- provisional shaft yield strength for screening: 300 MPa, not a material
  certificate;
- keyway/fatigue stress multiplier: 1.50;
- minimum calculated shaft yield safety factor: 2.0;
- minimum coupling rated-torque factor: 1.3;
- bearing load screen uses the 3.32 kN SKF 608 basic dynamic rating; bearing
  life is not frozen until speed, fit, lubrication and duty are physical data.

Primary technical evidence:

- Gates design manual:
  <https://www.gates.com/content/dam/documents-library/catalogs/powergrip-gt3-drive-design-manual-en.pdf>;
- SKF E2 deep-groove bearing brochure:
  <https://www.skf.com/binaries/pub12/Images/PUB%20BU_P2%206692_3%20EN_E2%20DGBB%20brochure_LoResSingles_tcm_12-234805.pdf>;
- R+W BKL product data: <https://www.rw-america.com/product/bkl/>;
- exact stepper candidate and drawing link are stored in the design-profile
  artifact.

## 3. Belt and shaft calculation

Let `Te` be the peak effective belt-tension difference from the authoritative
trajectory/dynamics model, `F0` the installation tension in each span and
`beta = pi - small_pulley_wrap` the angle between the two outgoing span-force
vectors.

The direct motor-shaft layout is rejected if `Te > 75 N`; this deliberately
strong test does not need an assumed preload. The supported-shaft design load
uses:

```text
Te_design = 1.30 * Te
F_tight = F0 + Te_design
F_slack = F0
F_radial = sqrt(F_tight^2 + F_slack^2
                + 2 * F_tight * F_slack * cos(beta))
```

For a pulley centred between two bearings, each bearing reaction is
`F_radial / 2` and maximum simply-supported bending moment is
`F_radial * bearing_span / 4`. The shaft screen combines bending and torsion:

```text
sigma_b = 32 M / (pi d^3)
tau_t = 16 T / (pi d^3)
sigma_vm = 1.50 * sqrt(sigma_b^2 + 3 tau_t^2)
yield_safety_factor = 300 MPa / sigma_vm
```

`T` is the calculated peak required motor torque after the 1.30 application
factor. These equations are deliberately conservative screens, not fatigue or
fit approval.

The input-shaft and coupling inertias shall be added to the existing dynamic
model. Shaft inertia is derived from its steel cylinder. Coupling inertia uses
the conservative full-cylinder upper bound `0.5*m*r^2`; no hidden zero-inertia
components remain in the selected budget candidate.

## 4. Budget CAD contract

A new date-based ForgeCAD model shall represent one budget axis and shall not
modify the industrial bench. It must expose output angle from -45 to +80
degrees and belt centre adjustment from -15 to +3 mm.

The model shall visibly include:

- NEMA 23 motor envelope and 8 mm motor shaft;
- 8/8 mm bellows coupling;
- a separate 8 mm input jackshaft, two 608 bearings and rigid carrier;
- 20T and 60T pulleys, a 450 mm belt envelope and adjustment slots;
- provisional 12 mm output shaft, two bearing supports and the 280 mm arm;
- a representative removable test mass and base plate;
- distinct solids with bores/clearance where physical parts pass through one
  another.

ForgeCAD shall output a structured BOM and controlled dimensions. Minimum,
nominal and maximum output-angle poses must run. Unexpected solid interference
is a failure; deliberately touching interfaces must be described separately.
The model remains a layout/fabrication candidate: final bearing fits, keyways,
retainers and supplier hole patterns wait for delivered-part measurement.

## 5. Complete-demonstrator cost contract

The active cost report shall cover all three robot axes plus the minimum
mechanics, frame, electrical/control, vacuum and conveyor-observation hardware
needed for the demonstrator. It shall separate:

- exact dated catalogue candidates;
- capped allowances that need an RFQ or fabrication choice;
- contingency;
- excluded optional equipment and reusable workshop/computer resources.

Every line stores gross PLN cost, quantity, evidence state, gate and source or
measurement plan. The report is acceptable when its base total plus contingency
is between 5,000 and 6,000 PLN and no required category is silently assigned a
zero price. A cost envelope is not a shopping authorisation. One P1 axis still
precedes fabrication or purchase of the other two transmission sets.

The low-cost plan may omit industrial metrology from ownership cost only if it
states how the needed evidence will be borrowed, rented or replaced with a
calibrated lower-cost measurement. It may reuse an existing PC and workshop
tools, but must list that assumption. Camera and controlled lighting are
owner-supplied and shall not be costed. No 3D printer is assumed: printed
prototypes are an explicit outsourced-fabrication allowance, while critical
drive supports remain metal parts unless separately validated.

## 6. Outputs and failure behaviour

Owned generated evidence:

- `artifacts/budget_mechanical_closure.json`;
- `artifacts/budget_bom.json`;
- budget CAD renders plus STEP/report when the installed ForgeCAD licence
  permits export.

The Python API rejects non-finite/non-positive dimensions and invalid force or
price data. JSON generation uses `allow_nan=False`. No failed mechanical screen
may be hidden by clipping or relabelled as a physical pass.

## 7. Acceptance tests

- An independent hand-equation test proves that `Te > 75 N` rejects direct
  motor-shaft mounting before preload.
- Zero effective tension with equal span tensions produces the standard
  two-vector resultant.
- Increasing installation tension increases calculated radial load.
- The chosen supported shaft has yield safety factor at least 2.0, each bearing
  reaction below 10% of the SKF dynamic rating and coupling factor at least 1.3.
- The selected-candidate performance result remains `not_rejected_by_proxy` at
  0.50 kg / 1.50 s after shaft/coupling inertia is included.
- Mechanical and BOM documents are finite, deterministic and exactly match
  committed artifacts.
- The complete cost is within 5,000--6,000 PLN and every required category has
  a positive subtotal.
- ForgeCAD runs and is inspected at -45, 0 and +80 degrees, with no unexpected
  collisions.
- The industrial artifacts and accepted P0 trajectory do not change.

## 8. Explicit remaining uncertainty

- exact-kit torque curve, temperature and following error require physical P1;
- belt installation tension must be set and checked on hardware;
- actual pulley bores, bearing fits, shaft retention and part masses remain
  delivery/fabrication measurements;
- price and stock are a dated Polish-market snapshot, not a quotation;
- the 500 W kit supply and driver over-voltage behaviour must be observed under
  deceleration before three-axis duty is accepted;
- full delta-frame stiffness and arm/joint collision CAD remain later work.

## 9. Implemented result

The generated evidence rejects direct 20T mounting because the unpreloaded
effective tension difference is 92.813 N versus the 75 N motor-shaft limit.
With the 1.30 application factor and 60.051 N installation tension per span,
the supported input sees a 234.417 N radial resultant, or 117.209 N per 608
bearing. The provisional Ø8 mm shaft screen gives yield safety factor 2.978,
bearing-rating utilization 3.53% and BKL3 rated-torque factor 1.549.

Adding the shaft and conservative coupling inertia changes worst proxy-curve
utilization at 0.50 kg / 1.50 s only from 0.85279 to 0.85296, so the point
remains `not_rejected_by_proxy`. It is still not a physical pass.

The complete-demonstrator base estimate is 5,171.97 PLN gross plus 650 PLN
explicit contingency, total 5,821.97 PLN. The budget ForgeCAD bench passes the
exact six-pose interference sweep with zero colliding poses and the
mechanical-integrity checks at -45, 0 and +80 degrees.

On 2026-07-27 the unchanged 250 PLN camera/lighting allowance was reassigned to
batched outsourced FDM printing because those vision components are already
owned and no 3D printer is available. The total cost therefore remains
5,821.97 PLN rather than hiding a printer purchase outside the project budget.
