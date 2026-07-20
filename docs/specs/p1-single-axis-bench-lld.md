# P1 single-axis bench — low-level design

**Status:** accepted for implementation
**Version:** 0.1
**Date:** 2026-07-20

## 1. Purpose

Define a parametric, assembly-aware CAD model for one representative delta-robot
shoulder axis. The CAD checks component envelopes, adjustment, output-arm travel
and obvious collisions. It is not manufacturing documentation and shall not
invent proprietary internal geometry for purchased parts.

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
| Centre adjustment | 25 mm minimum | Installation/tension allowance. |
| Input shaft | 9.525 mm | Published bore of selected small pulley. |
| Output shaft | 20 mm | Selected 1610 bushing bore and bearing family. |
| Output arm joint radius | 280 mm | Accepted robot geometry. |
| Output travel | -45 to +80 degrees | Required trajectory envelope plus inspection endpoints. |
| Representative tip mass | dynamic report output | Matches conservative equivalent joint inertia. |

## 3. Components and ownership

```text
bench assembly
├── base plate (fixed, fabricated)
├── servo + motor bracket (purchased envelope + fabricated bracket)
├── flexible coupling (purchased envelope)
├── adjustable input support
│   ├── two input bearings
│   ├── input jackshaft
│   └── 18T pulley between bearings
├── fixed output support
│   ├── two 6204 bearings
│   ├── output shaft
│   └── 90T pulley between bearings
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
4. Mount the servo and input bearing carrier on aligned longitudinal slots.
5. Connect the servo to the jackshaft without forcing axial or angular offset.
6. Install the 18T pulley between input bearings and align pulley mid-planes.
7. Fit the 600 mm belt with the carrier relaxed, slide to measured tension and
   tighten the carrier.
8. Set the representative mass at the modelled arm radius.
9. With power removed, sweep -45, 0 and +80 degrees and inspect clearances.
10. Begin powered commissioning only under the sequence in the P1 drive spec.

## 5. Collision and access rules

- No collision is allowed between arm/load and base, belt, pulley, shaft support
  or servo over the full output travel.
- Belt and pulley tooth form are visual envelopes, not manufacturable profiles.
- A visible keep-out envelope around the moving arm is an inspection aid and not
  a production safety guard.
- Bearing, bushing, coupling and pulley locking hardware must remain accessible.
- Input carrier slots must expose at least 25 mm usable translation without
  leaving insufficient bolt edge distance.

Unexpected overlap fails CAD validation. Intended shaft-in-bearing, shaft-in-hub
and fastener-through-hole fits are documented exceptions, not hidden collisions.

## 6. CAD outputs and acceptance

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
- changing arm length, centre distance or representative mass dimensions does
  not require editing unrelated component geometry.

The CAD validates layout, not strength, bearing life, belt tooth contact or
manufacturability. Those claims require calculations and physical evidence.
