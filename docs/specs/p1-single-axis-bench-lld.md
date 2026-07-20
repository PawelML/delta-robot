# P1 single-axis bench — low-level design

**Status:** accepted for implementation
**Version:** 0.2
**Date:** 2026-07-20

## 1. Purpose

Define a parametric, assembly-aware CAD model for one representative delta-robot
shoulder axis. The CAD checks component envelopes, adjustment, output-arm travel,
assembly access and obvious collisions. It also emits a prototype fabrication
package for the custom parts. It shall not invent proprietary internal geometry
for purchased parts; supplier-dependent fits remain release blockers.

## 2. Fixed parameters and units

ForgeCAD uses millimetres and degrees; Python remains authoritative in metres
and radians. The shaft axis is global `Y`, vertical is `Z`, and the arm moves in
the `XZ` plane. Output zero is a horizontal arm pointing in `+X`; positive angle
moves it toward `-Z`, matching the robot convention.

| Parameter | Initial value | Source / rationale |
|---|---:|---|
| Base plate | 600 × 360 × 12 mm | Prototype envelope with clamp/bolt margin; fabricated part. |
| Servo envelope | 60 × 79 × 146.7 mm plus 14 mm shaft | Leadshine mechanical drawing; purchased envelope only. |
| Belt centre distance | calculated near 154.37 mm | 18/90 teeth, 5 mm pitch, 600 mm belt. |
| Centre adjustment | -21 to +4 mm from nominal | Gates allowance for installing a 600 mm belt over two flanged 5 mm sprockets, plus tensioning travel. Total 25 mm. |
| Input shaft | 9.525 mm | Published bore of selected small pulley. |
| Output shaft | 20 mm × 180 mm provisional | Selected 1610 bushing bore, 6204 bearing family and rear encoder extension. |
| Output arm joint radius | 280 mm | Accepted robot geometry. |
| Output travel | -45 to +80 degrees | Required trajectory envelope plus inspection endpoints. |
| Representative tip mass | dynamic report output | Matches conservative equivalent joint inertia. |

## 3. Components and ownership

```text
bench assembly
├── base plate (fixed, fabricated)
├── fixed output support
│   ├── two 6204 bearings
│   ├── output shaft
│   ├── 90T pulley between bearings
│   └── external encoder and bracket on rear shaft extension
├── adjustable input carrier (one rigid translated datum)
│   ├── servo + braced motor bracket
│   ├── flexible coupling (purchased envelope)
│   ├── two input bearings
│   ├── input jackshaft
│   └── 18T pulley between bearings
├── synchronous-belt envelope
└── output rotor
    ├── 280 mm representative arm
    └── adjustable representative mass
```

Each part is created at its own modelling origin and positioned through named
connectors. The moving output subtree is attached through a revolute joint.
Input rotation follows the output angle at the documented 5:1 ratio for visual
inspection; Python remains the source of the commanded motion.

## 4. Assembly walk-through

1. Bolt or clamp the base plate to a stable bench.
2. Mount the output bearing blocks at the fixed datum.
3. Insert the 20 mm shaft, two bearing envelopes, 90T pulley/bushing and arm hub.
4. Assemble the servo bracket and both input bearing housings on one rigid input
   carrier. Their mutual shaft alignment is fixed by that carrier.
5. Place the carrier over four fixed longitudinal slots in the base and leave
   the M8 clamping bolts loose. The slots do not move with the carrier.
6. Connect the servo to the jackshaft without forcing axial or angular offset.
7. Install the 18T pulley between input bearings and align pulley mid-planes.
8. Fit the 600 mm belt with the carrier at the relaxed `-21 mm` position, slide
   to measured tension and tighten the carrier.
9. Fit the external encoder without using it as an axial shaft retainer.
10. Set the representative mass at the modelled arm radius.
11. With power removed, sweep -45, 0 and +80 degrees and inspect clearances.
12. Begin powered commissioning only under the sequence in the P1 drive spec.

## 5. Prototype fabrication contract

The first release is a machined/drilled workshop prototype using a 12 mm
6082-T6 (6061-T6 acceptable) base and input carrier, steel bearing supports and
steel shafts. Datum A is the base top face; datum B is the output-axis centre
plane; datum C is the belt mid-plane. The two shaft axes must be parallel within
`0.10 mm` over 150 mm and pulley mid-planes aligned within `0.20 mm` before a
powered run. These are assembly targets to measure, not unverified CAD claims.

Required custom-part information:

- base and carrier outside dimensions, fixed hole/slot positions and edge
  distances;
- full, closed bearing seats with removable axial retainers, not open half-bores;
- shaft lengths, bearing shoulders/spacers and separate pulley/arm keyway zones;
- a braced motor bracket with a load path to the carrier;
- accessible M8 carrier clamps and accessible pulley/bushing locking hardware;
- external-encoder bracket referenced to the fixed output housing.

Bearing-seat tolerances, circlip grooves, exact key lengths, servo mounting-hole
pattern and E6 bracket holes are marked `VERIFY FROM DELIVERED COMPONENT` until
the relevant manufacturer drawing and measured purchased part agree. The CAD
may reserve their envelopes but may not label invented dimensions shop-ready.

## 6. Collision and access rules

- No collision is allowed between arm/load and base, belt, pulley, shaft support
  or servo over the full output travel.
- Belt and pulley tooth form are visual envelopes, not manufacturable profiles.
- A visible keep-out envelope around the moving arm is an inspection aid and not
  a production safety guard.
- Bearing, bushing, coupling and pulley locking hardware must remain accessible.
- Fixed base slots must expose the complete `-21 to +4 mm` translation without
  leaving insufficient bolt edge distance.

Unexpected overlap fails CAD validation. Intended shaft-in-bearing, shaft-in-hub
and fastener-through-hole fits are documented exceptions, not hidden collisions.

## 7. CAD outputs and acceptance

The source lives at
`cad/2026/07/20/p1-single-axis-bench/main.forge.js` and returns an unsolved
ForgeCAD `Assembly`. It shall expose output angle and belt adjustment controls,
emit a BOM and key dimensions, and define a stable inspection scene.

Acceptance evidence:

- the model runs at -45, 0 and +80 degrees;
- rendered views make the supported input shaft and complete belt path visible;
- mechanical-integrity and interference inspections identify no unexpected
  collision at the three poses;
- physical-components inspection identifies the intended separate bodies;
- displayed dimensions agree with the transmission JSON within 0.1 mm;
- the four base slots remain fixed when the input carrier adjustment changes;
- servo shaft, coupling and jackshaft translate as one rigid carrier subtree;
- the bearing housings have closed seats and the output rear extension provides
  a non-contact external-encoder mounting zone;
- changing arm length, centre distance or representative mass dimensions does
  not require editing unrelated component geometry.

The fabrication package consists of the parametric source, a dimension/BOM
report and a STEP assembly reference. It is a release candidate until every
`VERIFY FROM DELIVERED COMPONENT` item is closed on the actual hardware.

The CAD validates layout, not strength, bearing life, belt tooth contact or
manufacturability. Those claims require calculations and physical evidence.
