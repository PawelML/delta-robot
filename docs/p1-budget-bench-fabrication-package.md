# Budget P1 single-axis bench — candidate fabrication package

**Status:** layout validated; delivered-part fits and retention not released  
**Date:** 2026-07-22

## Controlled source and outputs

- ForgeCAD source: `cad/2026/07/22/p1-budget-single-axis-bench/main.forge.js`;
- STEP: `artifacts/cad/p1-budget-single-axis-bench.step`;
- PDF with BOM and dimensions:
  `artifacts/cad/p1-budget-single-axis-bench-report.pdf`;
- overview, belt and jackshaft PNG renders in `artifacts/cad/`;
- exact interference and physical-component manifests in
  `artifacts/cad/inspections/p1-budget-single-axis-bench/`.

## Controlled layout dimensions

| Dimension | Candidate value |
|---|---:|
| HTD transmission | 20/60 teeth, 5 mm pitch, 15 mm width |
| Belt pitch length | 450 mm |
| Nominal shaft-centre distance | 120.8064669 mm |
| Input carrier adjustment | -15 to +3 mm |
| Input shaft | Ø8 x 100 mm prototype blank |
| Input bearing envelope | 608, 8x22x7 mm |
| Input bearing-centre span | 50 mm |
| Coupling envelope | BKL/3/8/8, Ø25 x 32 mm |
| Output shaft | provisional Ø12 x 130 mm blank |
| Output bearing | selected SKF 6001-2RSH CN, 12x28x8 mm; fits pending |
| Output bearing-centre span | 60 mm |
| Representative arm | 280 mm shaft centre to nominal load point |
| Base plate | 480x280x10 mm |
| Adjustable carrier | 104x220x12 mm |

The 0.5 kg visible mass is an envelope for bench loading, not proof that this
is the final physical mass shape. The belt is a pitch-line envelope with a thin
visual section; individual teeth and running tooth contact are intentionally
not modelled.

## Validation evidence

- `forgecad run` passes six verifications at output angles -45, 0 and +80 deg;
- the assembly audit with exact geometry and an eight-step joint sweep reports
  zero errors and zero warnings;
- mechanical-integrity inspection passes at -45, 0 and +80 deg with zero
  collisions;
- the independent fit-interference bundle sweeps six poses from -45 to +80 deg
  and reports 0/6 colliding poses;
- the physical-component inspection records the current envelope assembly.

The mechanical-integrity graph reports six contact components because
fasteners, retainers and shaft keys are intentionally not yet frozen. This is
not treated as proof of a ready-to-fabricate stack. Exact assembly constraints
are represented by connectors; physical connection details must be added from
the delivered parts.

The first plausible CAD layout did fail the exact sweep because the arm crossed
the base at +80 deg. The output axis was moved to the bench edge and the arm
plane outside the plate before the clean evidence above was generated. This is
why the sweep is a release check rather than an optional visual review.

## Blocked fabrication details

Do not machine the bearing seats, pulley bores/keyways, shaft shoulders,
retainer grooves or supplier-specific motor holes directly from nominal
envelopes. Release them only after:

1. one motor, coupling, both pulleys, belt and the selected bearings are delivered;
2. critical diameters, widths, runout and hole patterns are measured;
3. shaft/housing fits and axial retention are calculated for the actual series;
4. the assembled belt plane and adjustment travel are checked on the bench;
5. actual arm, hub, pulley and shaft masses are entered back into the dynamics.
