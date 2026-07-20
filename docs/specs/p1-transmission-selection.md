# P1 5:1 synchronous-belt transmission — specification

**Status:** accepted for implementation
**Version:** 0.1
**Date:** 2026-07-20

## 1. Problem and boundary

Select and calculate one representative 5:1 belt reduction for the P1 bench.
The result shall be detailed enough to build a parametric CAD envelope and a
purchase-level BOM, but it remains a prototype selection until measured belt
tension, alignment, temperature and lost motion pass the physical P1 gate.

The motor is the provisional Leadshine `iSV2-RS6040V48G`. Its shaft shall not
carry belt pull. A flexible zero-backlash coupling drives a separately supported
input jackshaft. Both belt pulleys sit between their respective support bearings.

## 2. Primary-source inputs

- Gates, *PowerGrip GT3 Drive Design Manual*:
  <https://www.gates.com/content/dam/documents-library/catalogs/powergrip-gt3-drive-design-manual-en.pdf>
- Gates, *Light Power and Precision Manual*:
  <https://www.gates.com/content/dam/gates/home/knowledge-center/resource-library/catalogs/light-power-and-precision-manual.pdf>
- Leadshine product page:
  <https://www.leadshine.com/product-detail/iSV2-RS6040V48G.html>
- Leadshine iSV2-RS user manual V2.01:
  <https://www.leadshine.com/upfiles/downloads/f85ab001e8edd4c7f05e5c32ea6671fd_1766721032370.pdf>

Published inputs used by the model:

| Input | Value |
|---|---:|
| Belt pitch | 5 mm (5MGT) |
| Available belt widths considered | 9, 15, 25 mm |
| Selected small pulley | Gates `P18-5MGT-15AL`, 18 teeth, aluminium |
| Small pulley published `WR²` | 0.000097 lb·ft² |
| Selected large pulley | Gates `P90-5MGT-15`, 90 teeth, ductile iron |
| Large pulley published `WR²` | 0.1358 lb·ft² |
| Large-pulley bushing | Gates 1610, 20 mm bore |
| Selected belt | `600-5MGT-15`, 600 mm pitch length, 15 mm width |
| 15 mm belt capacity at 18 teeth | 0.32 hp at 300 rpm; 0.40 hp at 400 rpm |
| 600 mm belt length factor | 0.95 |
| Gates minimum static tension for 15 mm span | 15 lbf |

Pulley product codes, bores and availability must be confirmed with the chosen
distributor before payment. The model does not turn catalogue data into an
availability claim.

## 3. Variants

The report compares these exact-ratio candidates:

| Variant | Pulley teeth | Belt | Intent |
|---|---:|---:|---|
| A | 16/80 | 535-5MGT-15 | Compact comparison; rejected if the small pulley has no applicable Gates rating or bore solution. |
| B | 18/90 | 600-5MGT-15 | Reference build candidate using published stock sprockets and rating-table data. |
| C | 20/100 | 625-5MGT-15 | Larger-tooth comparison; rejected for P1 if the 100-tooth sprocket is not a standard published item. |

Variant B is the provisional recommendation. No substitution may silently
change pitch, width, material, tooth count, bore or inertia.

## 4. Calculation contract

Use SI units internally. For pitch `p`, teeth `z`, pitch diameter `D`, belt
pitch length `L` and centre distance `C`:

```text
D = z p / pi
L = 2 C + pi (D_large + D_small) / 2
    + (D_large - D_small)^2 / (4 C)
```

Solve the second expression for its positive physical root. Calculate small
pulley wrap, teeth in mesh, belt speed, speed ratio, pitch-line force difference,
and equivalent reflected inertias. Convert published `WR²` to mass moment of
inertia using `1 lb·ft² = 0.0421401101 kg·m²`; do not treat `WR²` as mass.

The dynamic report supplies the actual instantaneous motor torque, speed and
power. Belt rating is checked using linear interpolation only inside the
published 300–400 rpm interval and the published 600 mm length factor. A
configurable 1.50 service factor is applied to trajectory power for the belt
capacity check. Extrapolation outside published data shall return an explicit
`not_evaluated` result.

Initial installation tension is `1.5 × 15 lbf = 100.1 N` per span. This is a
provisional start-stop test setting, not a universal Gates recommendation. The
conservative support-load screen is:

```text
delta_tension = absolute_transmitted_torque / small_pitch_radius
radial_upper_bound = 2 * installation_tension + delta_tension
```

It deliberately over-bounds the vector shaft load. The physical build must use
a Gates-approved sonic-frequency or force/deflection measurement and record the
actual value.

## 5. Shaft and support contract

- Motor: 14 mm shaft connected only through a flexible, zero-backlash coupling.
- Input jackshaft: 3/8 inch (9.525 mm) steel, two sealed bearings, pulley between
  bearings, bearing dynamic rating at least 2 kN.
- Output shaft: 20 mm steel, two `6204-2RS`-envelope bearings, pulley between
  bearings, bearing dynamic rating at least 12 kN.
- Coupling: 14 mm to 3/8 inch, at least 5 Nm rated torque and at least 1000 rpm.
- Output hub: Gates 1610 taper bushing with 20 mm finished bore.
- Centre distance: nominal value calculated from 600 mm pitch length, adjustable
  by at least 25 mm for installation and measured tensioning.
- Pulley-plane angular misalignment: at most 0.25 degrees.

Calculate simple bearing reactions and combined torsional/bending shaft stress.
These are screening calculations, not a fatigue or keyway stress-concentration
certification. Reject any candidate with fewer than six small-pulley teeth in
mesh or an unresolved shaft/bore mismatch.

## 6. Outputs and failure behaviour

`artifacts/p1_transmission_selection.json` shall contain source labels, all
input assumptions, each variant's geometry, speed, force, inertia, shaft screen,
belt-capacity status, rejection reasons and deterministic recommendation.

Invalid dimensions, non-physical centre solutions, zero/negative efficiency,
unsupported rating interpolation and non-finite results are rejected explicitly.
The implementation must not clip geometry into a passing state.

## 7. Acceptance evidence

- Selected ratio is exactly `5.0` within `1e-12`.
- Reconstructed belt length differs from 600 mm by less than `1e-9` m.
- Independent nominal hand calculation gives centre distance about 154.37 mm,
  small-pulley wrap about 136.42 degrees and about 6.82 teeth in mesh.
- Published pulley inertias convert to about `4.088e-6` and `5.723e-3 kg·m²`.
- Belt speed at 330.48 rpm is about 0.496 m/s.
- Tests cover invalid geometry, fewer-than-six-teeth rejection and power-rating
  interpolation boundaries.
- The JSON artifact is exactly reproducible from committed inputs.

## 8. Remaining uncertainty

The independent oracle covers catalogue dimensions and standard belt geometry.
It does not validate real tension, tooth stiffness, resonance, bearing fit,
machining runout or available Modbus sampling rate. Those remain physical P1
measurements; no software result may mark the physical gate as passed.
