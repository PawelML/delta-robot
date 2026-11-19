# Budget P1 single-axis bench — candidate fabrication package

**Status:** revised mounting layout verified in CAD, delivered-part fits and retention pending

**Date:** 2026-11-19

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
| Base plate | 500x280x10 mm, X = −240 to +260 mm |
| Base anchor holes | Ø13 mm at X = −210/+180 mm and Y = ±115 mm |
| Output support holes | Ø9 mm at X = 206/238 mm and Y = −120/−50 mm |
| Adjustable carrier | 104x220x12 mm |

The 0.5 kg visible mass is an envelope for bench loading, not proof that this
is the final physical mass shape. Use the
[P1 load and measurement specification](specs/p1-budget-bench-test.md) for
fixture inertia and time-domain load targets. The belt is a pitch-line envelope with a thin
visual section; individual teeth and running tooth contact are intentionally
not modelled.

## Validation evidence

- `forgecad run` passes six verifications at output angles -45, 0 and +80 deg;
- mechanical-integrity inspection passes at −45°, 0° and +80° for carrier
  adjustments −15, 0 and +3 mm with zero collisions in nine combinations;
- the fit-interference bundle sweeps 11 poses from −45° to +80° at nominal
  carrier adjustment and reports 0/11 colliding poses;
- the [XY section at Z = 5 mm](../artifacts/cad/inspections/p1-budget-single-axis-bench/base-section/section.png)
  shows the complete Ø9 mm outer bores with 17.5 mm of material before the
  plate edge and 10.8 mm between the relocated right anchor bore and the
  nearest carrier slot. The computed minimum gap from that anchor bore to
  the adjacent output-support bore is 15.5 mm;
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
The November audit found through-edge output mounting bores and a merged
anchor bore in that layout. Extending the positive X edge and moving the two
right anchors resolved those findings while preserving the axis datums.

To reproduce the section and motion check with ForgeCAD 0.10.3:

```bash
bench=cad/2026/07/22/p1-budget-single-axis-bench/main.forge.js
forgecad inspect section "$bench" --plane xy --offset 5 \
  --ray 'outer-front:225,-120:265,-120' --ray 'outer-rear:225,-50:265,-50' \
  --ray 'anchor-and-slot:140,-115:265,-115'
forgecad inspect fit interference "$bench" --joint-sweep 'output_angle=-45..80:11' --size 600
```

## Blocked fabrication details

Do not machine the bearing seats, pulley bores/keyways, shaft shoulders,
retainer grooves or supplier-specific motor holes directly from nominal
envelopes. Release them only after:

1. one motor, coupling, both pulleys, belt and the selected bearings are delivered;
2. critical diameters, widths, runout and hole patterns are measured;
3. shaft/housing fits and axial retention are calculated for the actual series;
4. the assembled belt plane and adjustment travel are checked on the bench;
5. actual arm, hub, pulley and shaft masses are entered back into the dynamics.
