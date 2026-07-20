# P0 conveyor footprint coverage

**Status:** accepted for implementation  
**Version:** 0.1  
**Date:** 2026-07-20

## 1. Problem and decision

The accepted useful workspace is a vertical cylinder with radius `0.200 m`,
height `0.150 m` and centre at `z = -0.347 m`. The existing conveyor is
`0.200 m` wide. Before treating that cylinder as sufficient for the application,
the model shall explicitly verify the rectangular pick area used by the planned
25-305-25 motion:

- length along global `X`: `0.305 m`;
- conveyor width along global `Y`: `0.200 m`;
- centre: `x = 0`, `y = 0`;
- vertical interval: the full accepted useful-cylinder height.

This is a P0 geometric requirement. It does not claim that a gripper, product,
camera or moving-conveyor tracking process fits the same area.

## 2. Inputs, coordinates and units

Python uses metres and radians. The delta base centre is `X = Y = 0`, positive
`Z` points upward, and the tool works below the base. The footprint is centred
and axis-aligned only to make its relationship to the accepted 305 mm trajectory
explicit. A centred rectangle has the same corner radius after any rotation, so
orientation does not change containment inside a circular workspace.

The farthest footprint point in `XY` is a corner:

```text
sqrt((0.305 / 2)^2 + (0.200 / 2)^2) = 0.182363 m
radial reserve to the accepted 0.200 m cylinder = 0.017637 m
```

## 3. Output artifact and classifications

`scripts/generate_conveyor_coverage.py` shall write
`artifacts/conveyor_coverage.json` with schema
`delta-robot-p0-conveyor-coverage/v1`. It shall contain:

- the footprint and accepted cylinder dimensions;
- analytical corner radius and radial reserve;
- sampling counts and total evaluated points;
- reachability-class counts without redefining existing classes;
- minimum joint-limit margin and minimum singularity margin;
- the worst sampled points for both margins;
- an overall `passes` result.

Each sampled point is evaluated by the authoritative Python IK and differential
kinematics. Unreachable, joint-limited, ambiguous or numerically invalid points
remain explicit failures; no clipping or projection is allowed.

## 4. Deterministic evidence

The rectangular prism is sampled inclusively at `31 × 21 × 16 = 10,416`
points. This gives 10.17 mm spacing in `X`, 10 mm in `Y` and 10 mm in `Z` and
always includes all corners, the boundary and the centre axes.

Acceptance tests shall demonstrate:

1. the analytical corner radius and reserve match the values above;
2. all four XY corners lie inside the accepted useful cylinder;
3. all 10,416 sampled points are geometrically reachable and pass the existing
   practical joint-limit and singularity criteria;
4. changing the width to a value whose corner radius exceeds `0.200 m` fails
   containment rather than silently reducing the area;
5. the generated JSON is deterministic and finite.

The corner calculation proves continuous `XY` containment of the rectangle in
the accepted cylinder. The kinematic margins inside that cylinder remain
numerical evidence from the existing workspace screening and this denser,
application-shaped sample; they are not physical accuracy evidence.

## 5. Outside this slice

- conveyor frame, belt thickness and collision geometry;
- tool diameter and wrist orientation;
- camera field of view and calibration;
- dynamic cycle time, product interception and conveyor tracking;
- production guarding or safety architecture.
