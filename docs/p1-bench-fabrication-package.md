# P1 single-axis bench — prototype fabrication package

**Release:** candidate 0.2  
**Date:** 2026-07-20  
**Purpose:** one workshop P1 axis, not three robot axes

## Files

- Parametric source: `cad/2026/07/20/p1-single-axis-bench/main.forge.js`
- Assembly exchange model: `artifacts/cad/p1-single-axis-bench.step`
- 21+ page view/BOM report: `artifacts/cad/p1-single-axis-bench-report.pdf`
- Design contract: `docs/specs/p1-single-axis-bench-lld.md`

The STEP and PDF are generated outputs. Regenerate them after every accepted CAD
change; do not edit either file manually.

## Coordinate datums

ForgeCAD dimensions are millimetres. The base centre is `(0, 0, 0)`, the base
top face is datum A at `Z = 12`, shaft axes are parallel to global `Y`, and both
shaft centre lines lie at `Z = 160`. The fixed output axis is at `X = 100`.
At nominal belt centre distance the input axis is at `X = -54.366869`.

The adjustment parameter is the change in centre distance. `-21 mm` moves the
input axis 21 mm toward the output for belt installation; `+4 mm` moves it 4 mm
away from nominal for tensioning.

## Released custom-part geometry

### Base plate

- 6082-T6 or 6061-T6 aluminium, `600 × 360 × 12`;
- four bench holes: `Ø13` at `X = ±265`, `Y = ±145`;
- four output-housing holes: `Ø9` at `X = 64, 136`, `Y = -150, -80`;
- four fixed carrier slots, width `9`, end-centre travel `25`, overall length
  `34`; slot centres are:

| X | Y |
|---:|---:|
| -93.866869 | -165 |
| -93.866869 | 75 |
| 2.133131 | -165 |
| 2.133131 | 75 |

Deburr all holes and slots. The four slots are fixed base features and must not
be re-centred on the current carrier position.

### Adjustable input carrier

- 6082-T6 or 6061-T6 aluminium, `130 × 270 × 12`;
- local origin on the input shaft axis; plate extent `X = ±65`,
  `Y = -180…90`, `Z = -148…-136`;
- four base-clamp holes `Ø9` at local `X = ±48`, `Y = -165, 75`;
- four input-housing holes `Ø6.6` at local `X = ±21`, `Y = -145, -85`;
- four motor-bracket holes `Ø6.6` at local `X = ±40`, `Y = 20, 55`.

The housing, coupling and motor bracket are all referenced to this plate. Their
relative alignment must not depend on sliding separate parts on the base.

### Shaft/support stack

| Feature | Output | Input |
|---|---:|---:|
| Shaft | C45/1045, `Ø20 × 180` | C45/1045, `Ø9.525 × 132.5` |
| Bearing | `6204-2RS`, `20 × 47 × 14` | one supplier's `R6-2RS`, nominal `9.525 × 22.225 × 7.142` |
| Bearing-centre positions Y | `-150`, `-80` | `-145`, `-85` |
| Centre span | `70` | `60` |
| Retainer rings | four, `OD60 × ID20.4 × 3` | four, `OD30 × ID9.9 × 3` |
| Housing-to-base/carrier holes | `Ø9`, local `X=±36` at both bearing Y values | `Ø6.6`, local `X=±21` at both bearing Y values |

The CAD contains closed bearing seats and separate face retainers. Retainer
bolt circles, bearing-seat fits and shaft shoulders/collars are intentionally
not released until actual bearings are selected and measured.

The output shaft contains separate provisional `6.1 mm` keyway envelopes under
the pulley/bushing and arm hub. Their depth, length, end radius, key standard and
fatigue effect require a shaft drawing after the delivered hub and bushing are
confirmed. Do not machine the CAD envelope directly as a final keyway drawing.

### Motor and encoder brackets

The motor bracket has a 10 mm foot, 190 mm front plate and two side braces. Its
foot uses the four carrier holes above. The 27 mm shaft/coupling clearance is
modelled, but the servo-flange bolt pattern remains a blank-to-match feature.

The external encoder is reserved on the rear output-shaft extension and mounted
to a fixed bracket, never to the rotating arm. The CAD uses an E6 envelope and a
20 mm shaft bore. Its final bolt pattern, cable exit and centring-tool clearance
come from the quoted US Digital configuration.

## Required checks before releasing drawings to a workshop

The following are not optional details; the candidate package is not a final
machining release until they are closed:

1. measure the delivered servo flange, shaft projection and connector exits;
2. select exact R6 and 6204 series and calculate housing/shaft fits from the
   bearing manufacturer's current fit guidance and the chosen materials;
3. replace retainer placeholders with bolt circles, thread engagement and
   accessible fasteners;
4. define shaft shoulders, spacers/collars, keyway standard and axial locking;
5. quote the exact E6 configuration and update its mounting holes/cable path;
6. verify coupling length, clamp access and actual pulley/bushing dimensions;
7. measure base/carrier flatness and align both shaft axes within `0.10 mm` over
   150 mm; align pulley mid-planes within `0.20 mm`;
8. hand-sweep `-45°`, `0°`, `+80°` with power removed before commissioning.

These open items are why the package can be used to obtain feedback and quotes,
but should not yet be sent with the instruction “machine exactly as drawn”.
