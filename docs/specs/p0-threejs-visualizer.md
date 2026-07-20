# P0 Three.js visualizer — specification

**Status:** accepted for implementation
**Version:** 0.2
**Date:** 2026-07-20

## 1. Problem

The Python model exports a classified Cartesian workspace, one complete robot
pose and a sampled 25-305-25 trajectory. This slice
shall provide a browser-based Three.js view in which a developer can orbit the
robot, see which regions are reachable, joint-limited or unreachable, and
inspect the pose and source assumptions without reading raw JSON.

The visualizer is a diagnostic instrument. It consumes authoritative Python
results and shall not solve IK, FK or workspace reachability in JavaScript.

## 2. Operating story

The user starts the local development server, opens the page and initially sees
the complete delta robot framed together with the sampled workspace. The robot
is visually dominant; the unreachable shell is intentionally faint so it does
not hide the reachable interior. A side panel explains the reference fixture,
reports counts and joint angles, and lets the user isolate each class. Mouse or
touch input rotates, pans and zooms the scene. A reset button restores the
automatically fitted engineering view.

If either artifact is missing or incompatible, the application shows a visible
error instead of drawing a plausible but incomplete robot.

## 3. Data boundary

The visualizer accepts exactly:

- `delta-robot-p0-workspace/v2`,
- `delta-robot-p0-pose/v1`,
- `delta-robot-p0-trajectory/v1`,
- SI units declared by every document,
- identical geometry, source label and assembly mode in all three documents.

It validates required arrays, finite numbers, positive workspace counts and the
identity `reachable + joint_limited + unreachable = total = points.length`.
Unknown extra fields are tolerated for backward-compatible Python additions;
missing or contradictory required fields fail visibly.

The production build copies the generated files from the repository
`artifacts/` directory. There is no hand-maintained JavaScript copy of these
values.

## 4. Coordinate mapping

The Python base frame remains the labelled engineering frame. Three.js uses Y
as its conventional screen-up axis, so every exported point is mapped by one
pure boundary function:

```text
Python/base:  (X, Y, Z)
Three/scene:  (X, Z, -Y)
```

This is right-handed: scene `X cross Y = Z`. The Python base plane `Z = 0`
becomes the horizontal scene plane `Y = 0`, and the normal workspace at Python
`Z < 0` appears below that plane. Axis labels show **model X, model Y and model
Z**, not unnamed Three.js axes.

## 5. Visible layers

### Workspace

Each classification is one independent point cloud so opacity and visibility
do not require altering source data:

| Class | Color | Default treatment | Meaning |
|---|---|---|---|
| `practically_usable` | green | visible, strongest | Reachable and above the exported P0 singularity threshold. |
| `weak_reachable` | purple | visible, strongest | Reachable but below the P0 singularity threshold. |
| `joint_limited` | amber | visible, medium | Link geometry closes but the demo angle window rejects it. |
| `unreachable` | red | visible, faint | No accepted solution on the supported branch. |

The three colors match the established status palette in
`station_configurator`. Point size is based on the smallest grid interval so a
new artifact remains legible without hard-coding the Williams scale. The UI can
toggle each cloud independently and stores those visibility choices in
`localStorage`.

### Robot pose

The pose layer contains:

- a thin base plate and three motor/shoulder markers,
- three upper arms from exported shoulder to exported knee points,
- six lower rods rendered as two rods around each exported virtual center line,
- three knee markers,
- a moving-platform plate and three attachment markers,
- a highlighted platform-center marker.

The exported center lines remain authoritative. Physical parallelogram width is
not yet in the model, so paired lower rods use a **display-only** separation of
four rendered lower-rod radii. This makes both rods distinguishable while each
pair stays centered on the verified line. Rod radius is derived from the
smaller link length and clamped to a visible engineering-diagram range; it is
not exported, measured or used by kinematics. The UI states this limitation.

Base and platform plates are context surfaces around the exported joint radii,
not manufacturing geometry. Their material is visually distinct and
semi-matte so nodes and rods remain readable.

### Context

The scene includes:

- a base-plane grid,
- labelled model axes,
- soft hemisphere and directional lighting,
- a dark neutral background,
- no factory cell, safety cage or conveyor in this slice.

## 6. UI and interaction

The left panel provides:

- data status and source label,
- checkboxes for robot and all three workspace classes,
- play/pause and restart controls for the trajectory,
- a reset-view action,
- orbit/pan/zoom instructions,
- an explicit warning that collision and dynamic feasibility remain unverified.

The right panel reports:

- total and per-class point counts and percentages,
- grid shape and bounds in millimetres,
- pose XYZ in millimetres,
- three joint angles in degrees,
- link lengths and joint radii in millimetres,
- schema identifiers.
- live trajectory time, segment, joint rates and joint accelerations.

The camera uses pointer controls matching the proven local configurator:
left-drag orbit, right-drag pan and wheel zoom. Its initial target and distance
are fitted from the workspace bounds and pose rather than copied from the other
project. Reset repeats that fit. The canvas resizes with the window and remains
usable on narrow screens by collapsing the stats panel below the controls.

## 7. Project and dependency boundary

The visualizer is a framework-free ES-module application under `visualizer/`.
Three.js is the only runtime dependency. Vite is the development/build tool,
as recommended by the official Three.js installation guide. `package-lock.json`
pins the resolved dependency graph; `node_modules/` and `dist/` are ignored.

Commands:

```text
cd visualizer
npm install
npm run dev
npm test
npm run build
```

The source separates artifact validation/mapping from Three.js scene code so
the data boundary can be tested with Node without WebGL or a browser.

## 8. Walk-through

1. Vite serves the app and copies the current generated artifacts.
2. The app fetches all three JSON documents concurrently.
3. A pure module validates schemas, units, summaries and shared metadata.
4. Any failure enters an error state and stops before scene construction.
5. Model coordinates are mapped to the right-handed scene frame.
6. Four point-cloud buffers are created directly from exported classifications
   and quality booleans.
7. Exported pose points build the robot diagram; no solver runs in JavaScript.
8. The camera fits the combined data bounds.
9. UI values are filled from the documents, and saved layer visibility is
   applied.
10. The animation loop interpolates corresponding exported joint coordinates,
    updates the existing meshes and runs orbit/resize handling.

## 9. Acceptance tests

This slice is complete when:

1. Pure tests accept the committed artifacts and reject wrong schema, units,
   summary cardinality, non-finite coordinates and mismatched shared metadata.
2. A mapping test proves base `(1, 2, 3)` becomes scene `(1, 3, -2)`.
3. Partitioning returns exactly the workspace summary counts without dropping
   or inventing points.
4. The Three.js scene draws three upper arms, six lower rods, both plates and
   all exported diagnostic nodes without disconnected endpoints.
5. The page exposes all layer toggles, status, counts, dimensions and angles.
6. A production build succeeds and contains all three versioned JSON artifacts.
7. The browser console has no application errors during a local smoke test.
8. A visual inspection confirms that the robot, all four workspace layers,
   model-axis orientation and UI are legible in the initial view.
9. Existing Ruff, strict Mypy and Pytest gates remain green.

## 10. Explicit exclusions and uncertainty

- The page does not edit dimensions or invoke Python. Regenerating artifacts is
  the source-of-truth path until a later configuration API is specified.
- JavaScript does not retime the path or calculate missing samples; it only
  interpolates adjacent exported coordinates for display.
- Paired lower-rod spacing and plate thickness are display conventions, not BOM
  dimensions.
- `practically_usable` still does not mean collision-free or dynamically
  feasible.
- The selected DIY geometry remains provisional until dynamics, CAD clearance
  and physical tests pass.

## 11. 25-305-25 animation contract

The trajectory adapter validates the complete 1,001-sample schema, ordered
times, eight segment records, all numeric vectors, three unique arms per sample
and summary extrema. A mismatch in geometry, source or assembly mode prevents
the scene from starting.

The scene adds a line showing the exported platform-centre path and loops the
one-second animation. At render time JavaScript linearly interpolates only
between corresponding coordinates in adjacent exported samples. It updates the
existing meshes for three upper arms, six display-only lower rods, platform and
nodes. It never reconstructs a point from angle or geometry.

`window.__deltaVisualizer` exposes playback state and current sample index for
a headless smoke test. One visual loop must visit source, destination and source
in the exported segment order while all links remain connected.
