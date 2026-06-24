# Keyboard Generator — Architecture & Component Reference

## Coordinate Systems

| System | X | Y | Z | Unit |
|---|---|---|---|---|
| KLE JSON | right → | down ↓ | — | Key Units (KU) |
| Python / OpenSCAD | right → | up ↑ | out of board ↑ | mm |
| Three.js viewer | right → | up ↑ | out of board ↑ | mm |

**KLE → mm conversion:** multiply KU by the switch spacing.
- Cherry MX: `1 KU = 19.05 mm`
- Kailh Choc: `1 KU = 19.05 mm` (same in this project)

**KLE Y → mm Y:** flip sign. KLE absY=0 is the top; mm Y=0 is the bottom-left reference.

---

## Layer Stack (bottom-up)

```
 Z = (LAYER_THICKNESS + GAP) * 2  ┌──────────────────────────────┐  PLATE (light gray)
                                   │  key holes (14.03×14.03 mm)  │  2.16 mm thick
                                   │  + pin boss posts             │
                                   └──────────────────────────────┘
 Z = (LAYER_THICKNESS + GAP) * 1  ┌──────────────────────────────┐  PCB (dark green)
                                   │  hotswap socket footprints   │  2.16 mm thick
                                   │  + Arduino + TRRS body       │
                                   │  pin screw holes              │
                                   └──────────────────────────────┘
 Z = 0                             ┌──────────────────────────────┐  BOTTOM (dark gray)
                                   │  Arduino USB cutout           │  2.16 mm thick
                                   │  TRRS barrel opening          │
                                   │  pin screw holes              │
                                   │  camera mount boss (below)    │
                                   │  tilt legs (below)            │
                                   └──────────────────────────────┘
```

`BASIC_LAYER_THICKNESS = 2.16 mm`  
`BORDER_RADIUS = 2 mm` (rounded corners on all three layers)

---

## Board Outline (Convex Hull)

All three layers share the same 2D outline, computed as the convex hull of all component corners, then rounded with `BORDER_RADIUS`.

**Python method:** `Keyboard._draw_base_plate()` collects all four corners of each part (using the part's **physical size**, after applying rotation and border expansion), feeds them to `scipy.spatial.ConvexHull`, then calls `round2d(r=2)`.

**Physical sizes used for hull** (NOT the KLE w/h values):

| Component | Physical size (mm) |
|---|---|
| cherry / kailhchoc | `w * 19.05` × `h * 19.05` (KLE-scaled) |
| arduino | `19 × 39` (fixed) |
| trrs | `8.2 × 14.6` (fixed — socket body + barrel) |
| pinplate / pinpcb / pinb2t | `4 × 4` (outer diameter) |
| hole (wire pass-through) | `w * 14.03` × `h * 14.03` (KLE-scaled, uses 14.03mm hole spacing) |
| platetext | `1 × 1` (tiny, rarely affects hull) |
| cameramount_selftap / heatset | `14 × 14` (BOSS_OUTER_DIAMETER) |
| tiltleg | `10 × 10` (LEG_DIAMETER) |

> **Important:** Parts whose KLE `w` or `h` differ from their physical footprint must use physical size for the hull, NOT `w * 19.05`.

---

## Component-by-Layer Matrix

### CherryMxKey / KailhChocKey

| Layer | What happens |
|---|---|
| **Plate** | Switch hole `14.03 × 14.03 mm` cut through. Ring of reinforcement added around hole. |
| **PCB** | Hotswap socket footprint `14.03 × 14.03 mm` subtracted. STL model of hotswap socket embedded (offset +0.56 mm for Cherry). |
| **Bottom** | Nothing. |

### Arduino

Physical size: `19 mm × 39 mm`  
Orientation: long axis along Y. Top edge points toward the split connector side.

| Layer | What happens |
|---|---|
| **Plate** | Nothing (footprint_plate = None). |
| **PCB** | Full footprint `19 × 39 mm` subtracted (slot for the board). Two rows of 12 pin holes (d=1.5 mm, spaced 2.54 mm, starting 2.5 mm from edge, 15 mm apart). |
| **Bottom** | Header opening: `12 × (13+10) mm` slot cut through, offset toward USB end. |

### TRRS Jack (PJ-320A)

Physical size: `8.2 × 14.6 mm` (body: 6.2 × 12.4 mm + 2.2 mm barrel space)  
Often placed at `r=90` so the barrel points outward from the board edge.

| Layer | What happens |
|---|---|
| **Plate** | Nothing. |
| **PCB** | Full footprint `8.2 × 14.6 mm` subtracted. Barrel hole (d=5.3 mm, h=2.2 mm) cut through one side. PCB part rendered as socket body box + cavity. |
| **Bottom** | Body opening `6.2 × 6.2 mm` cut through (so the jack can be inserted from below). |

### PinPlate (plate ↔ PCB spacer)

Physical size: `4 mm diameter` cylinder post; contributes 4×4 mm to hull.

| Layer | What happens |
|---|---|
| **Plate** | Boss post added on TOP surface (solid 4mm OD cylinder, height = PCB spacing, with 2mm ID hole). Fills the cell gap in the board. |
| **PCB** | 2mm hole cut through (receives the pin shaft). Screw chamfer recess on PCB surface. |
| **Bottom** | Nothing. |

### PinPcb (PCB ↔ bottom spacer)

| Layer | What happens |
|---|---|
| **Plate** | Nothing. |
| **PCB** | Boss post added on TOP surface. 2mm hole cut through for screw. |
| **Bottom** | Screw chamfer recess + 2mm through-hole. |

### PinFromBottomToPlate / pinb2t (bottom ↔ plate)

Combines PinPlate and PinPcb. Puts a boss on both PCB (for spacer) and plate, and screw recesses on both PCB and bottom.

### Hole (wire pass-through)

Physical size: `w * 14.03 × h * 14.03 mm`

| Layer | What happens |
|---|---|
| **Plate** | Nothing. |
| **PCB** | Slot cut through. |
| **Bottom** | Nothing. |

### PlateText (engraved text)

Physical size: `1 × 1 mm` (does not significantly affect hull).

| Layer | What happens |
|---|---|
| **Plate** | Text engraved (subtracted) from plate surface using `text3d`. |
| **PCB** | Nothing. |
| **Bottom** | Nothing. |

### CameraMount (self-tap or heat-set)

Physical size: `14 mm diameter` boss; contributes 14×14 mm to hull.

Protrudes **downward** from the bottom layer outer face (toward the desk).

| Layer | What happens |
|---|---|
| **Plate** | Nothing. |
| **PCB** | Nothing. |
| **Bottom** | Boss added below: 4 mm conical chamfer flare at board surface + main cylinder (d=14 mm, h=6-10 mm) + blind screw hole (d=5.5 mm for self-tap, d=7 mm for heat-set). |

### TiltLeg

Physical size: `10 mm diameter` cylinder; contributes 10×10 mm to hull.  
Height is **auto-calculated** by the Python code from the tilt plane defined by:
`leg_height = boss_height × |leg_x − outer_edge_x| / |boss_x − outer_edge_x|`

| Layer | What happens |
|---|---|
| **Plate** | Nothing. |
| **PCB** | Nothing. |
| **Bottom** | Leg added below: 4 mm conical chamfer + straight shaft + hemisphere tip (d=10 mm). |

---

## Part Placement: Rotation

All parts support optional rotation from KLE `r`, `rx`, `ry`:

```
absX, absY  → top-left of part cell in KU (KLE coordinates)
rx, ry      → rotation pivot in KU
r           → rotation angle in degrees (KLE: clockwise when Y-down)
```

**Python:** the center point is first computed as `(absX, absY) + physicalSize/2` (in mm), then rotated around `(rx, ry) * spacing` using a standard 2D rotation matrix.

**Critical:** the center that gets rendered is the **post-rotation** center. The convex hull is also computed using the **post-rotation corners** of each part.

---

## Python Rotation Pipeline (Exact Math)

### Coordinate convention

Python receives KLE values directly — **no Y-axis flip**. So Python's Y increases downward (same as KLE), even though OpenSCAD normally uses Y-up. The resulting SCAD geometry is "upside-down" relative to OpenSCAD convention, but since all parts share the same convention the relative positions are correct.

### Step-by-step for every part

**Input** (from pykle_serial / JS parser):
| Field | Meaning |
|---|---|
| `absX / part.x` | Top-left corner X of the key cell, in KU |
| `absY / part.y` | Top-left corner Y of the key cell, in KU (Y-down) |
| `r / rotation_angle` | Rotation angle in degrees |
| `rx / rotation_x` | Rotation pivot X, in KU |
| `ry / rotation_y` | Rotation pivot Y, in KU |
| `w, h / width, height` | Key cell size in KU |

**Step 1 — Convert to mm**
```
pos_mm    = (absX * spacing,  absY * spacing)       # top-left in mm
pivot_mm  = (rx * spacing,    ry * spacing)          # pivot in mm
```

**Step 2 — Determine physical size**

If the class has a `spacing` attribute (CherryMxKey, KailhChocKey), size depends on the KLE cell:
```
size_mm = (w * class.spacing.x,  h * class.spacing.y)
```
If the class has a **fixed** size (Arduino, TRRS, pins, camera mount, tilt leg):
```
size_mm = class.size   # e.g. XY(19, 39) for Arduino — KLE w/h are IGNORED
```

**Step 3 — Compute unrotated center**
```
center_pre = (pos_mm.x + size_mm.w / 2,  pos_mm.y + size_mm.h / 2)
```

**Step 4 — Rotate center around pivot**

Python uses the standard 2D rotation matrix:
```
R = [[cos(r°), -sin(r°)],
     [sin(r°),  cos(r°)]]

center_post = R @ (center_pre - pivot_mm) + pivot_mm
```

Because Python's Y is down (KLE convention) and this matrix is the "CCW in Y-up" matrix, it acts **clockwise** visually — which matches KLE's `r` field semantics.

**Step 5 — Draw at local origin, then rotate and translate**
```python
# In every draw_*_part / draw_*_footprint method:
result = self._draw_*()         # build shape centered at (0, 0, 0)
result = result.rotate(self.angle_rotation)           # rotate in place (Z-axis, CW in Y-down)
result = result.translate(center_post.x, center_post.y, 0)  # move to final position
```

**Key invariant**: `center_post` (called `center_point` in Python) is the only position stored. Every draw call uses `.rotate(angle).translate(center_point.x, center_point.y)`.

---

## Per-Component Geometry at Local Origin

Each component's `_draw_*` methods build geometry **centered at (0, 0)** before rotation/translation.

### CherryMxKey / KailhChocKey

| Method | Geometry at origin |
|---|---|
| `_draw_plate_footprint` | 14.03 × 14.03 × 5 mm cube (hole cut-out) + 14.03+3 reinforcement ring |
| `_draw_pcb_footprint` | 19.05 × 19.05 × 5 mm cube (full cell footprint cut-out) |
| `_draw_pcb_part` | STL hotswap socket model, offset +0.56 mm in Z for Cherry |

### Arduino

Fixed size 19 × 39 mm. Long axis = Y. USB end is at the −Y side (smaller Y in KLE space).

| Method | Geometry at origin |
|---|---|
| `_draw_pcb_footprint` | 19 × 39 × 5 mm cube |
| `_draw_pcb_part` | 12 pin holes × 2 rows (d=1.5 mm, spacing 2.54 mm, rows 15 mm apart) |
| `_draw_bottom_part_addition_sub` | 12 × (13+10) mm slot near the −Y (USB) end |

### TRRSJack (PJ-320A)

Fixed size 8.2 × 14.6 mm. Default rotation r=90 (barrel points in X direction).

| Method | Geometry at origin |
|---|---|
| `_draw_pcb_footprint` | 8.2 × 14.6 × 5 mm cube |
| `_draw_pcb_part` | socket body box (6.2 × 12.4 × 5.2) + barrel cylinder (d=5.3, h=2.2) on Y− side |
| `_draw_bottom_part_addition_sub` | ≈6.2 × 6.2 mm slot centered at origin |

### Pin (PinPlate / PinPcb / PinFromBottomToPlate)

Fixed size 4 × 4 mm. All three are cylinders centered at (0,0).

| Param | Value |
|---|---|
| Outer diameter | 4 mm (r=2 mm) |
| Inner hole diameter | 2 mm (r=1 mm) |
| Boss height | varies (≈ PCB layer gap) |

### CameraMount (self-tap / heat-set)

Fixed size 14 × 14 mm. Protrudes **downward** (−Z) from the bottom layer.

| Param | Value |
|---|---|
| BOSS_OUTER_DIAMETER | 14 mm |
| boss_height | 10 mm (self-tap), 6 mm (heat-set) |
| Screw hole d | 5.5 mm (self-tap), 7 mm (heat-set) |
| Conical chamfer | 4 mm at the board surface |

### TiltLeg

Fixed size 10 × 10 mm. Protrudes **downward** (−Z). Height auto-calculated from tilt plane:
```
leg_height = boss_height × |leg_x − outer_edge_x| / |boss_x − outer_edge_x|
```

| Param | Value |
|---|---|
| LEG_DIAMETER | 10 mm |
| Tip shape | hemisphere |
| Conical chamfer | 4 mm at board surface |

---

## How the JS 3D Viewer Maps This

### Center position

```js
function getCompCenterMm(comp) {
  const { w, h } = getPhysSize(comp);  // physical mm, NOT comp.w * SPACING
  let cx = comp.absX * SPACING + w / 2;
  let cy = comp.absY * SPACING + h / 2;
  if (comp.r !== 0) {
    const rad = comp.r * Math.PI / 180;
    const px = comp.rx * SPACING, py = comp.ry * SPACING;
    // Same R matrix as Python — CW in Y-down
    const r = rotatePoint(cx, cy, px, py, rad);
    cx = r.x; cy = r.y;
  }
  return { mmX: cx, mmY: cy };  // KLE mm coords (Y-down)
}
```

This is mathematically identical to Python's `center_point` computation.

### Three.js mesh placement

```js
const { mmX, mmY } = getCompCenterMm(comp);
const sx = mmX - shapeCx;           // center X in shape space
const sy = -(mmY - shapeCy);        // Y-flip: KLE Y-down → Three.js Y-up
mesh.position.set(sx, sy, z);
mesh.rotation.z = -comp.r * Math.PI / 180;  // negate because Y-flip reverses CW/CCW
```

Why negate the rotation: flipping Y transforms a CW rotation (in KLE Y-down) into a CCW rotation (in Three.js Y-up). Negating `rotation.z` compensates, making the mesh appear correctly oriented.

### Switch holes / rectangular cutouts

Rectangular holes in the board layers (key switch holes, TRRS slot, Arduino opening) are drawn in local space around `(0, 0)`, then rotated by `comp.r` **around their own center**, then translated to `(mmX, mmY)`:

```js
// CORRECT: rotate corners around own center, then translate
function addRectHole(shape, cx_mm, cy_mm, hw, hh, rotRad, shapeCx, shapeCy) {
  const cos = rotRad ? Math.cos(rotRad) : 1;
  const sin = rotRad ? Math.sin(rotRad) : 0;
  const raw = [[-hw,-hh],[-hw,hh],[hw,hh],[hw,-hh]];
  const pts = raw.map(([x, y]) => ({
    x: cx_mm + x*cos - y*sin,
    y: cy_mm + x*sin + y*cos,
  }));
  // ...add as THREE.Path hole to shape
}
```

**Common mistake**: passing `(comp.rx * SPACING, comp.ry * SPACING)` as pivot to `rotatePoint` after already using `getCompCenterMm` produces a **double rotation** — the pre-rotated center gets rotated a second time around the KLE pivot, placing the hole at a completely wrong position.

---

## Differences Between Website Output and OpenSCAD

The following bugs exist in the Three.js viewer (`ui/js/viewer3d.js`):

| Bug | Effect | Root cause |
|---|---|---|
| Rotated parts placed at unrotated center | TRRS, thumb keys appear at wrong position in 3D | Viewer uses `(absX + w/2) * 19.05` without rotating around pivot |
| Non-key parts use KLE w/h for size | Arduino, TRRS, pins, camera mount, tilt leg render at wrong size | Should use fixed physical sizes (see table above) |
| Pin cylinder radius 3.5–4 mm | Pins appear 2× too large | Should be OD=2 mm radius (d=4 mm), ID=1 mm radius (d=2 mm) |
| Convex hull uses KLE cell size | Board outline may be slightly off | Hull corners should use physical part size, not `w * 19.05` |
| Camera mount / tilt leg extrude upward into board | Geometry bleeds through the bottom layer | Should extrude downward from `z = LAYER_THICKNESS` |
