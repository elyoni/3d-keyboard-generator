// Three.js 3D visualization using real extruded geometry.
// Matches the Python/OpenSCAD output: convex-hull board outline, rounded corners,
// key-switch holes, pin posts, Arduino below PCB, camera mount boss, tilt legs.

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { COMPONENTS, CHERRY_MX_SPACING, LAYER_THICKNESS, CHERRY_MX_HOLE } from './components.js';

const SPACING  = CHERRY_MX_SPACING;   // 19.05 mm/KU

// ── Python-mirrored constants ─────────────────────────────────────────────────
// Each constant is sourced directly from the Python file noted in the comment.

// constants.py
const BORDER_R           = 2;     // BORDER_RADIUS
const PIN_BOSS_HEIGHT    = 5;     // CHERRY_MX_PCB_HEIGHT — pin boss height = plate↔PCB gap

// camera_mount.py
const BOSS_OUTER_D       = 14.0;  // BOSS_OUTER_DIAMETER
const BOSS_HEIGHT        = 10.0;  // BOSS_DEFAULT_HEIGHT
const CHAMFER_SIZE       = 4.0;   // CHAMFER_SIZE (boss and leg base flare width)
const SELFTAP_HOLE_D     = 5.5;   // SELF_TAP_HOLE_DIAMETER
const HEATSET_HOLE_D     = 7.0;   // HEAT_SET_HOLE_DIAMETER
const LEG_D              = 10.0;  // LEG_DIAMETER

// pins.py
const PIN_OUTER_D        = 4.0;   // diameter_outer (boss OD)
const PIN_INNER_D        = 2.0;   // diameter_inner (screw through-hole)
const PIN_SCREW_D        = 2.5;   // scraws_outer_diameter (countersink at bottom)

// split_keyboard_connectors.py → TRRSJack
const TRRS_BODY_W        = 6.2;   // socket_body_size.x
const TRRS_BODY_H        = 12.4;  // socket_body_size.y
const TRRS_SIZE_W        = TRRS_BODY_W + 2;            // size.x  = 8.2
const TRRS_SIZE_H        = TRRS_BODY_H + 2.2;          // size.y  = 14.6
const TRRS_BARREL_D      = 5.3;   // socket_hold_size_diameter
const TRRS_BARREL_H      = 2.2;   // socket_hole_size_height
const TRRS_BOTTOM_SLOT_W = TRRS_BODY_W * 2.5;          // 15.5 mm
const TRRS_BOTTOM_SLOT_H = TRRS_BODY_H * 2.5;          // 31.0 mm

// arduino.py
const ARD_W              = 19;    // size.x
const ARD_H              = 39;    // size.y
const ARD_PCB_THICKNESS  = 1;     // pcb_size z
const ARD_PIN_D          = 1.5;   // pins_diameter
const ARD_PINS_ROW_SPACE = 15;    // pins_row_space (mm between rows)
const ARD_PINS_N         = 12;    // pins_number per side
const ARD_PINS_SPACE     = 2.54;  // pins_space (mm pitch)
const ARD_PINS_FIRST     = 2.5;   // first_pin_position (mm from edge)
const ARD_HEADER_W       = 12;    // arduino_header[0]
const ARD_HEADER_H       = 13;    // arduino_header[1]
const ARD_HEADER_Z       = 6;     // arduino_header[2] (slot depth)
const ARD_BORDER         = 10;    // border_size
// Derived slot dimensions (matching _draw_bottom_part_addition_sub):
//   arduino_header + (0, border_size, 0) → (12, 23, 6)
const ARD_SLOT_W         = ARD_HEADER_W;                                          // 12
const ARD_SLOT_H         = ARD_HEADER_H + ARD_BORDER;                             // 23
//   y_offset = -border_size/2 - size.y/2 + arduino_header[Y]/2 = -5 - 19.5 + 6.5 = -18
const ARD_SLOT_Y         = -ARD_BORDER / 2 - ARD_H / 2 + ARD_HEADER_H / 2;       // -18 mm
//   z_offset = -arduino_header[Z] + BASIC_LAYER_THICKNESS * 2/3
const ARD_SLOT_Z         = -ARD_HEADER_Z + LAYER_THICKNESS * 2 / 3;              // ≈ -4.56 mm
// Pin start y (from component center): size.y/2 - pins_space*(N-1) - first_pin_position
const ARD_PINS_Y_START   = ARD_H / 2 - ARD_PINS_SPACE * (ARD_PINS_N - 1) - ARD_PINS_FIRST;

// Visual layer separation (extra gap so components in the gap are visible)
// Using PIN_BOSS_HEIGHT (5 mm) so the plate↔PCB gap matches the physical pin boss height.
const GAP = PIN_BOSS_HEIGHT;

// Physical footprint sizes for hull/positioning — mirrors Part.size in Python
const PHYS = {
  cherry:              (w, h) => ({ w: w * SPACING,     h: h * SPACING }),
  kailhchoc:           (w, h) => ({ w: w * SPACING,     h: h * SPACING }),
  arduino:             ()      => ({ w: ARD_W,           h: ARD_H }),
  trrs:                ()      => ({ w: TRRS_SIZE_W,     h: TRRS_SIZE_H }),
  pinplate:            ()      => ({ w: PIN_OUTER_D,     h: PIN_OUTER_D }),
  pinpcb:              ()      => ({ w: PIN_OUTER_D,     h: PIN_OUTER_D }),
  pinb2t:              ()      => ({ w: PIN_OUTER_D,     h: PIN_OUTER_D }),
  hole:                (w, h) => ({ w: w * CHERRY_MX_HOLE, h: h * CHERRY_MX_HOLE }),
  platetext:           ()      => ({ w: 1,               h: 1 }),
  cameramount_selftap: ()      => ({ w: BOSS_OUTER_D,    h: BOSS_OUTER_D }),
  cameramount_heatset: ()      => ({ w: BOSS_OUTER_D,    h: BOSS_OUTER_D }),
  tiltleg:             ()      => ({ w: LEG_D,           h: LEG_D }),
};

function getPhysSize(comp) {
  const fn = PHYS[comp.type];
  return fn ? fn(comp.w, comp.h) : { w: comp.w * SPACING, h: comp.h * SPACING };
}

// Layer base Z: bottom=0, pcb, plate
const LAYER_BASE_Z = [0, LAYER_THICKNESS + GAP, (LAYER_THICKNESS + GAP) * 2];
const LAYER_NAMES  = ['Bottom', 'PCB', 'Plate'];
const LAYER_COLORS = [0x2c3e50, 0x145a32, 0x607d8b];

// ── Geometry helpers ─────────────────────────────────────────────────────────

function mmToShapeVec(mmX, mmY, cx, cy) {
  return new THREE.Vector2(mmX - cx, -(mmY - cy));
}

function rotatePoint(px, py, pivotX, pivotY, rad) {
  const dx = px - pivotX, dy = py - pivotY;
  return {
    x: pivotX + dx * Math.cos(rad) - dy * Math.sin(rad),
    y: pivotY + dx * Math.sin(rad) + dy * Math.cos(rad),
  };
}

// Get 4 corners (in mm) of a component's physical footprint, after rotation around pivot.
function getCompCornersMm(comp) {
  const { w, h } = getPhysSize(comp);
  const x0 = comp.absX * SPACING, y0 = comp.absY * SPACING;
  const corners = [
    { x: x0,     y: y0 },
    { x: x0 + w, y: y0 },
    { x: x0 + w, y: y0 + h },
    { x: x0,     y: y0 + h },
  ];
  if (comp.r === 0) return corners;
  const rad = comp.r * Math.PI / 180;
  const px = comp.rx * SPACING, py = comp.ry * SPACING;
  return corners.map(p => rotatePoint(p.x, p.y, px, py, rad));
}

// Compute center of component in mm, after rotation around pivot.
// Returns { mmX, mmY } in world mm coords (Y increases downward, matching KLE).
function getCompCenterMm(comp) {
  const { w, h } = getPhysSize(comp);
  let cx = comp.absX * SPACING + w / 2;
  let cy = comp.absY * SPACING + h / 2;
  if (comp.r !== 0) {
    const rad = comp.r * Math.PI / 180;
    const px = comp.rx * SPACING, py = comp.ry * SPACING;
    const r = rotatePoint(cx, cy, px, py, rad);
    cx = r.x; cy = r.y;
  }
  return { mmX: cx, mmY: cy };
}

// Convert world mm center to Three.js shape-space coords (centered, Y-flipped).
function shapePos(mmX, mmY, shapeCx, shapeCy) {
  return { x: mmX - shapeCx, y: -(mmY - shapeCy) };
}

// Jarvis March (gift-wrap) convex hull
function convexHull(pts) {
  if (pts.length < 3) return pts;
  let start = 0;
  for (let i = 1; i < pts.length; i++)
    if (pts[i].y > pts[start].y || (pts[i].y === pts[start].y && pts[i].x < pts[start].x))
      start = i;
  const hull = [];
  let cur = start;
  do {
    hull.push(pts[cur]);
    let nxt = (cur + 1) % pts.length;
    for (let i = 0; i < pts.length; i++) {
      const cross = (pts[nxt].x - pts[cur].x) * (pts[i].y - pts[cur].y) -
                    (pts[nxt].y - pts[cur].y) * (pts[i].x - pts[cur].x);
      if (cross < 0) nxt = i;
    }
    cur = nxt;
  } while (cur !== start);
  return hull;
}

// Expand hull outward from centroid by `dist` mm
function expandHull(hull, dist) {
  if (dist <= 0) return hull;
  const cx = hull.reduce((s, p) => s + p.x, 0) / hull.length;
  const cy = hull.reduce((s, p) => s + p.y, 0) / hull.length;
  return hull.map(p => {
    const dx = p.x - cx, dy = p.y - cy;
    const len = Math.sqrt(dx * dx + dy * dy) || 1;
    return { x: p.x + dx / len * dist, y: p.y + dy / len * dist };
  });
}

// Build a THREE.Shape from a convex polygon with rounded corners
function roundedPolygonShape(polygon, roundR, cx, cy) {
  const n = polygon.length;
  const shape = new THREE.Shape();
  for (let i = 0; i < n; i++) {
    const a = polygon[(i + n - 1) % n];
    const b = polygon[i];
    const c = polygon[(i + 1) % n];
    const abX = b.x - a.x, abY = b.y - a.y;
    const bcX = c.x - b.x, bcY = c.y - b.y;
    const abL = Math.sqrt(abX * abX + abY * abY) || 1;
    const bcL = Math.sqrt(bcX * bcX + bcY * bcY) || 1;
    const r = Math.min(roundR, abL / 2, bcL / 2);
    const p1 = mmToShapeVec(b.x - abX / abL * r, b.y - abY / abL * r, cx, cy);
    const bv = mmToShapeVec(b.x, b.y, cx, cy);
    const p2 = mmToShapeVec(b.x + bcX / bcL * r, b.y + bcY / bcL * r, cx, cy);
    if (i === 0) shape.moveTo(p1.x, p1.y);
    else shape.lineTo(p1.x, p1.y);
    shape.quadraticCurveTo(bv.x, bv.y, p2.x, p2.y);
  }
  shape.closePath();
  return shape;
}

// Add a rectangular hole path to a shape.
// cx_mm/cy_mm is the ALREADY-ROTATED center (from getCompCenterMm).
// rotRad only controls the orientation of the rectangle around its own center.
// Do NOT pass the KLE pivot here — that would cause a double rotation.
function addRectHole(shape, cx_mm, cy_mm, hw, hh, rotRad, shapeCx, shapeCy) {
  const cos = rotRad ? Math.cos(rotRad) : 1;
  const sin = rotRad ? Math.sin(rotRad) : 0;
  const raw = [[-hw, -hh], [-hw, hh], [hw, hh], [hw, -hh]];
  const pts = raw.map(([x, y]) => ({
    x: cx_mm + x * cos - y * sin,
    y: cy_mm + x * sin + y * cos,
  }));
  const hole = new THREE.Path();
  hole.moveTo(...mmToShapeVec(pts[0].x, pts[0].y, shapeCx, shapeCy).toArray());
  for (let i = 1; i < pts.length; i++)
    hole.lineTo(...mmToShapeVec(pts[i].x, pts[i].y, shapeCx, shapeCy).toArray());
  hole.closePath();
  shape.holes.push(hole);
}

// Add a circular hole path to a shape
function addCircleHole(shape, cx_mm, cy_mm, r, shapeCx, shapeCy) {
  const hole = new THREE.Path();
  const sv = mmToShapeVec(cx_mm, cy_mm, shapeCx, shapeCy);
  hole.absarc(sv.x, sv.y, r, 0, Math.PI * 2, false);
  shape.holes.push(hole);
}

function makeMesh(geo, color, opacity = 1) {
  const transparent = opacity < 1;
  const mat = new THREE.MeshLambertMaterial({ color, transparent, opacity });
  return new THREE.Mesh(geo, mat);
}

// Render text to a canvas and return a Three.js CanvasTexture.
// physW/physH are the physical dimensions in mm (used to set canvas aspect ratio).
function makeTextTexture(text, physW, physH, bgColor, textColor) {
  const scale = 10;
  const cW = Math.max(Math.round(physW * scale), 32);
  const cH = Math.max(Math.round(physH * scale), 32);
  const canvas = document.createElement('canvas');
  canvas.width = cW;
  canvas.height = cH;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = bgColor;
  ctx.fillRect(0, 0, cW, cH);
  ctx.fillStyle = textColor;
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
  if (lines.length === 0) return new THREE.CanvasTexture(canvas);
  const maxLen = Math.max(...lines.map(l => l.length), 1);
  const fontSize = Math.min(cW / (maxLen * 0.62 + 0.5), cH / (lines.length * 1.3 + 0.2));
  ctx.font = `bold ${Math.round(fontSize)}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const lineH = cH / lines.length;
  lines.forEach((line, i) => ctx.fillText(line, cW / 2, (i + 0.5) * lineH));
  return new THREE.CanvasTexture(canvas);
}

// Place a flat plane with text just above the given z level.
function addTextPlane(group, sx, sy, z, physW, physH, rotRad, text, bgColor, textColor, comp = null) {
  const tex = makeTextTexture(text, physW, physH, bgColor, textColor);
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: false });
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(physW, physH), mat);
  plane.position.set(sx, sy, z);
  if (rotRad) plane.rotation.z = -rotRad;
  if (comp) plane.userData = { compId: comp.id, compType: comp.type };
  group.add(plane);
}

// ── Layer builders ────────────────────────────────────────────────────────────

function buildPlate(components, hull, borderMm, shapeCx, shapeCy) {
  const group = new THREE.Group();
  const shape = roundedPolygonShape(hull, BORDER_R, shapeCx, shapeCy);

  // Key switch holes in plate (14.03 × 14.03 mm)
  for (const comp of components) {
    if (comp.type !== 'cherry' && comp.type !== 'kailhchoc') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const rad = comp.r * Math.PI / 180;
    const hw = CHERRY_MX_HOLE / 2;
    addRectHole(shape, mmX, mmY, hw, hw, rad, shapeCx, shapeCy);
  }

  // Pin screw holes through plate — diameter_inner / 2
  for (const comp of components) {
    if (!comp.type.startsWith('pin')) continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    addCircleHole(shape, mmX, mmY, PIN_INNER_D / 2, shapeCx, shapeCy);
  }

  const extGeo = new THREE.ExtrudeGeometry(shape, { depth: LAYER_THICKNESS, bevelEnabled: false });
  group.add(makeMesh(extGeo, LAYER_COLORS[2]));
  group.add(new THREE.LineSegments(
    new THREE.EdgesGeometry(extGeo),
    new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.15 })
  ));

  // Pin standoffs below plate — boss fills the plate↔PCB gap (height = PIN_BOSS_HEIGHT)
  for (const comp of components) {
    if (comp.type !== 'pinplate' && comp.type !== 'pinb2t') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const sx = mmX - shapeCx, sy = -(mmY - shapeCy);
    const color = COMPONENTS[comp.type]?.color3d ?? 0x9B59B6;
    const pinGeo = new THREE.CylinderGeometry(PIN_OUTER_D / 2, PIN_OUTER_D / 2, PIN_BOSS_HEIGHT, 16);
    pinGeo.rotateX(Math.PI / 2);
    const pin = makeMesh(pinGeo, color);
    pin.userData = { compId: comp.id, compType: comp.type };
    pin.position.set(sx, sy, -PIN_BOSS_HEIGHT / 2);
    group.add(pin);
    const screwGeo = new THREE.CylinderGeometry(PIN_INNER_D / 2, PIN_INNER_D / 2, PIN_BOSS_HEIGHT + 2, 12);
    screwGeo.rotateX(Math.PI / 2);
    const screw = makeMesh(screwGeo, 0x0a0a0a);
    screw.userData = { compId: comp.id, compType: comp.type };
    screw.position.copy(pin.position);
    group.add(screw);
  }

  // Key legends — small label plane centered inside each switch hole
  for (const comp of components) {
    if (comp.type !== 'cherry' && comp.type !== 'kailhchoc') continue;
    if (!comp.label) continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const sx = mmX - shapeCx, sy = -(mmY - shapeCy);
    const sz = CHERRY_MX_HOLE * 0.85;  // slightly smaller than hole
    addTextPlane(group, sx, sy, LAYER_THICKNESS + 0.1, sz, sz,
      comp.r * Math.PI / 180, comp.label, '#1e2a3a', '#e8f4ff', comp);
  }

  // Plate text — render actual text content on plate surface
  for (const comp of components) {
    if (comp.type !== 'platetext') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const sx = mmX - shapeCx, sy = -(mmY - shapeCy);
    const physW = comp.w * SPACING;
    const physH = comp.h * SPACING;
    const text = comp.p || '?';
    addTextPlane(group, sx, sy, LAYER_THICKNESS + 0.1, physW, physH,
      comp.r * Math.PI / 180, text, '#7d5a00', '#fff8dc', comp);
  }

  return group;
}

function buildPcb(components, hull, borderMm, shapeCx, shapeCy) {
  const group = new THREE.Group();
  const shape = roundedPolygonShape(hull, BORDER_R, shapeCx, shapeCy);

  // Key switch holes in PCB
  for (const comp of components) {
    if (comp.type !== 'cherry' && comp.type !== 'kailhchoc') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const rad = comp.r * Math.PI / 180;
    const hw = CHERRY_MX_HOLE / 2;
    addRectHole(shape, mmX, mmY, hw, hw, rad, shapeCx, shapeCy);
  }

  // Screw holes through PCB — holes.py: cuboid([spacing*w, spacing*h, thickness+2])
  for (const comp of components) {
    if (comp.type !== 'hole') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const { w, h } = getPhysSize(comp);
    addRectHole(shape, mmX, mmY, w / 2, h / 2, comp.r * Math.PI / 180, shapeCx, shapeCy);
  }

  // Pin screw holes through PCB — diameter_inner / 2
  for (const comp of components) {
    if (!comp.type.startsWith('pin')) continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    addCircleHole(shape, mmX, mmY, PIN_INNER_D / 2, shapeCx, shapeCy);
  }

  // Arduino footprint cut through PCB — pcb_size = (ARD_W, ARD_H, 1)
  for (const comp of components) {
    if (comp.type !== 'arduino') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    addRectHole(shape, mmX, mmY, ARD_W / 2, ARD_H / 2, comp.r * Math.PI / 180, shapeCx, shapeCy);
  }

  // TRRS footprint cut through PCB — footprint_pcb = size = (TRRS_SIZE_W, TRRS_SIZE_H)
  for (const comp of components) {
    if (comp.type !== 'trrs') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    addRectHole(shape, mmX, mmY, TRRS_SIZE_W / 2, TRRS_SIZE_H / 2, comp.r * Math.PI / 180, shapeCx, shapeCy);
  }

  const extGeo = new THREE.ExtrudeGeometry(shape, { depth: LAYER_THICKNESS, bevelEnabled: false });
  group.add(makeMesh(extGeo, LAYER_COLORS[1]));
  group.add(new THREE.LineSegments(
    new THREE.EdgesGeometry(extGeo),
    new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.13 })
  ));

  // Hotswap sockets on PCB underside — 3.5mm thick, roughly key-hole sized
  for (const comp of components) {
    if (comp.type !== 'cherry' && comp.type !== 'kailhchoc') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const sx = mmX - shapeCx, sy = -(mmY - shapeCy);
    const sockSz = CHERRY_MX_HOLE * 0.85;
    const sockD = 3.5;
    const sock = makeMesh(new THREE.BoxGeometry(sockSz, sockSz, sockD), COMPONENTS.cherry.color3d);
    sock.userData = { compId: comp.id, compType: comp.type };
    sock.position.set(sx, sy, -(sockD / 2));
    if (comp.r !== 0) sock.rotation.z = -comp.r * Math.PI / 180;
    group.add(sock);
  }

  // Arduino board on PCB underside — pcb_size = (ARD_W, ARD_H, ARD_PCB_THICKNESS)
  for (const comp of components) {
    if (comp.type !== 'arduino') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const sx = mmX - shapeCx, sy = -(mmY - shapeCy);
    const board = makeMesh(
      new THREE.BoxGeometry(ARD_W, ARD_H, ARD_PCB_THICKNESS), COMPONENTS.arduino.color3d);
    board.userData = { compId: comp.id, compType: comp.type };
    board.position.set(sx, sy, -(ARD_PCB_THICKNESS / 2 + 0.1));
    if (comp.r !== 0) board.rotation.z = -comp.r * Math.PI / 180;
    group.add(board);

    // Pin headers — pins_number × 2 rows, pins_row_space apart, pins_space pitch
    // y_start mirrors Python: size.y/2 - pins_space*(N-1) - first_pin_position
    const pinH = 4;
    const rad = comp.r * Math.PI / 180;
    for (const side of [-1, 1]) {
      for (let i = 0; i < ARD_PINS_N; i++) {
        const pinGeo = new THREE.CylinderGeometry(ARD_PIN_D / 2, ARD_PIN_D / 2, pinH, 8);
        pinGeo.rotateX(Math.PI / 2);
        const pin = makeMesh(pinGeo, 0xd4af37);
        pin.userData = { compId: comp.id, compType: comp.type };
        const localX = side * (ARD_PINS_ROW_SPACE / 2);
        const localY = -(ARD_PINS_Y_START + i * ARD_PINS_SPACE);
        const rx2 = localX * Math.cos(-rad) - localY * Math.sin(-rad);
        const ry2 = localX * Math.sin(-rad) + localY * Math.cos(-rad);
        pin.position.set(sx + rx2, sy + ry2, -(ARD_PCB_THICKNESS + pinH / 2));
        group.add(pin);
      }
    }
  }

  // TRRS jack on PCB underside — socket_body_size + barrel
  for (const comp of components) {
    if (comp.type !== 'trrs') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const sx = mmX - shapeCx, sy = -(mmY - shapeCy);
    // Body: socket_body_size × 5.2mm depth (_draw_pcb_part: cube anchored FWD, up 0.2)
    const bD = 5.2;
    const bodyZ = -(bD / 2 + 0.2);
    const body = makeMesh(
      new THREE.BoxGeometry(TRRS_BODY_W, TRRS_BODY_H, bD), COMPONENTS.trrs.color3d);
    body.userData = { compId: comp.id, compType: comp.type };
    body.position.set(sx, sy, bodyZ);
    if (comp.r !== 0) body.rotation.z = -comp.r * Math.PI / 180;
    group.add(body);

    // Barrel: cylinder(d=TRRS_BARREL_D) protruding in component local +Y direction
    // Using same rotation convention as addRectHole: local +Y → world direction via +rad
    const barrelR  = TRRS_BARREL_D / 2;
    const barrelLen = 14; // protrudes ~14mm from body face
    const barrelGeo = new THREE.CylinderGeometry(barrelR, barrelR, barrelLen, 12);
    const barrel = makeMesh(barrelGeo, 0x888888);
    barrel.userData = { compId: comp.id, compType: comp.type };
    const barrelLocalY = TRRS_BODY_H / 2 + barrelLen / 2;
    const rad = comp.r * Math.PI / 180;
    const bx = -barrelLocalY * Math.sin(rad);
    const by =  barrelLocalY * Math.cos(rad);
    barrel.position.set(sx + bx, sy + by, bodyZ);
    barrel.rotation.z = rad;
    group.add(barrel);
  }

  // Pin through-hole rings in PCB layer — diameter_outer / 2
  for (const comp of components) {
    if (!comp.type.startsWith('pin')) continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const sx = mmX - shapeCx, sy = -(mmY - shapeCy);
    const color = COMPONENTS[comp.type]?.color3d ?? 0x9B59B6;
    const ringGeo = new THREE.CylinderGeometry(PIN_OUTER_D / 2, PIN_OUTER_D / 2, LAYER_THICKNESS, 20);
    ringGeo.rotateX(Math.PI / 2);
    const ring = makeMesh(ringGeo, color, 0.85);
    ring.userData = { compId: comp.id, compType: comp.type };
    ring.position.set(sx, sy, LAYER_THICKNESS / 2);
    group.add(ring);
    const innerGeo = new THREE.CylinderGeometry(PIN_INNER_D / 2, PIN_INNER_D / 2, LAYER_THICKNESS + 0.5, 12);
    innerGeo.rotateX(Math.PI / 2);
    const inner = makeMesh(innerGeo, 0x0a0a0a);
    inner.userData = { compId: comp.id, compType: comp.type };
    inner.position.copy(ring.position);
    group.add(inner);
  }

  // Pin standoffs below PCB — boss fills PCB↔bottom gap (height = PIN_BOSS_HEIGHT)
  for (const comp of components) {
    if (comp.type !== 'pinpcb' && comp.type !== 'pinb2t') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const sx = mmX - shapeCx, sy = -(mmY - shapeCy);
    const color = COMPONENTS[comp.type]?.color3d ?? 0x9B59B6;
    const pinGeo = new THREE.CylinderGeometry(PIN_OUTER_D / 2, PIN_OUTER_D / 2, PIN_BOSS_HEIGHT, 16);
    pinGeo.rotateX(Math.PI / 2);
    const pin = makeMesh(pinGeo, color);
    pin.userData = { compId: comp.id, compType: comp.type };
    pin.position.set(sx, sy, -PIN_BOSS_HEIGHT / 2);
    group.add(pin);
    const screwGeo = new THREE.CylinderGeometry(PIN_INNER_D / 2, PIN_INNER_D / 2, PIN_BOSS_HEIGHT + 2, 12);
    screwGeo.rotateX(Math.PI / 2);
    const screw = makeMesh(screwGeo, 0x0a0a0a);
    screw.userData = { compId: comp.id, compType: comp.type };
    screw.position.copy(pin.position);
    group.add(screw);
  }

  return group;
}

function buildBottom(components, hull, borderMm, shapeCx, shapeCy) {
  const group = new THREE.Group();
  const shape = roundedPolygonShape(hull, BORDER_R, shapeCx, shapeCy);

  // Pin screw holes in bottom — scraws_outer_diameter / 2 (pinpcb and pinb2t only)
  for (const comp of components) {
    if (comp.type !== 'pinpcb' && comp.type !== 'pinb2t') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    addCircleHole(shape, mmX, mmY, PIN_SCREW_D / 2, shapeCx, shapeCy);
  }

  const extGeo = new THREE.ExtrudeGeometry(shape, { depth: LAYER_THICKNESS, bevelEnabled: false });
  group.add(makeMesh(extGeo, LAYER_COLORS[0]));
  group.add(new THREE.LineSegments(
    new THREE.EdgesGeometry(extGeo),
    new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.13 })
  ));

  // Camera mount bosses — _draw_bottom_part_addition_add in camera_mount.py
  // Protrude below local z=0 (desk-facing surface of bottom layer) toward desk.
  for (const comp of components) {
    if (comp.type !== 'cameramount_selftap' && comp.type !== 'cameramount_heatset') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const sx = mmX - shapeCx, sy = -(mmY - shapeCy);
    const color = COMPONENTS[comp.type].color3d;
    const bossR  = BOSS_OUTER_D / 2;
    const chamfer = Math.min(CHAMFER_SIZE, BOSS_HEIGHT * 0.4);  // matches Python min()
    const mainH  = BOSS_HEIGHT - chamfer;
    const holeD  = comp.type === 'cameramount_heatset' ? HEATSET_HOLE_D : SELFTAP_HOLE_D;

    // Conical flare: d1=(BOSS_OUTER_D + 2*chamfer) at plate surface, d2=BOSS_OUTER_D going down
    const flareGeo = new THREE.CylinderGeometry(bossR + chamfer, bossR, chamfer, 20);
    flareGeo.rotateX(Math.PI / 2);
    const flare = makeMesh(flareGeo, color);
    flare.userData = { compId: comp.id, compType: comp.type };
    flare.position.set(sx, sy, -(chamfer / 2));
    group.add(flare);

    // Main cylinder: d=BOSS_OUTER_D, h=BOSS_HEIGHT-chamfer
    const bossGeo = new THREE.CylinderGeometry(bossR, bossR, mainH, 20);
    bossGeo.rotateX(Math.PI / 2);
    const boss = makeMesh(bossGeo, color);
    boss.userData = { compId: comp.id, compType: comp.type };
    boss.position.set(sx, sy, -(chamfer + mainH / 2));
    group.add(boss);

    // Blind screw hole: d=hole_diameter, h=BOSS_HEIGHT+0.5 (stops at plate surface)
    const holeGeo = new THREE.CylinderGeometry(holeD / 2, holeD / 2, BOSS_HEIGHT + 0.5, 12);
    holeGeo.rotateX(Math.PI / 2);
    const screwHole = makeMesh(holeGeo, 0x0a0a0a);
    screwHole.userData = { compId: comp.id, compType: comp.type };
    screwHole.position.set(sx, sy, -(BOSS_HEIGHT / 2));
    group.add(screwHole);
  }

  // Tilt legs — _draw_bottom_part_addition_add in camera_mount.py (TiltLeg)
  // Height is auto-calculated by Python; show a representative value here.
  for (const comp of components) {
    if (comp.type !== 'tiltleg') continue;
    const { mmX, mmY } = getCompCenterMm(comp);
    const sx = mmX - shapeCx, sy = -(mmY - shapeCy);
    const color = COMPONENTS.tiltleg.color3d;
    const legR  = LEG_D / 2;
    const totalH = 15;  // representative; Python auto-calculates from tilt plane
    const chamfer = Math.min(CHAMFER_SIZE, (totalH - legR) * 0.4);  // matches Python min()
    const shaftH  = totalH - legR - chamfer;

    // Conical flare: d1=(LEG_D + 2*chamfer) at plate surface, d2=LEG_D going down
    const flareGeo = new THREE.CylinderGeometry(legR + chamfer, legR, chamfer, 16);
    flareGeo.rotateX(Math.PI / 2);
    const flare = makeMesh(flareGeo, color);
    flare.userData = { compId: comp.id, compType: comp.type };
    flare.position.set(sx, sy, -(chamfer / 2));
    group.add(flare);

    // Straight shaft
    const shaftGeo = new THREE.CylinderGeometry(legR, legR, shaftH, 16);
    shaftGeo.rotateX(Math.PI / 2);
    const shaft = makeMesh(shaftGeo, color);
    shaft.userData = { compId: comp.id, compType: comp.type };
    shaft.position.set(sx, sy, -(chamfer + shaftH / 2));
    group.add(shaft);

    // Hemispherical tip: dome points -Z (toward desk), flat face at shaft end
    const tipGeo = new THREE.SphereGeometry(legR, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2);
    tipGeo.rotateX(-Math.PI / 2);  // dome → -Z; flat face stays at local z=0
    const tip = makeMesh(tipGeo, color);
    tip.userData = { compId: comp.id, compType: comp.type };
    tip.position.set(sx, sy, -(chamfer + shaftH));  // flat face at shaft bottom
    group.add(tip);
  }

  return group;
}

// ── Viewer class ─────────────────────────────────────────────────────────────

export class Viewer3D {
  constructor(container, app) {
    this.container = container;
    this.app = app;
    this._exploded = false;
    this._animating = false;
    this._targetSep = 0;
    this._currentSep = 0;
    this._meshMap = new Map();
    this._tooltip = null;
    this._initialized = false;
    this._currentComponents = [];
  }

  _ensureInit() {
    if (this._initialized) return;
    this._initialized = true;

    const W = Math.max(this.container.clientWidth, 400);
    const H = Math.max(this.container.clientHeight, 300);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(W, H);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setClearColor(0x1a1a2e, 1);
    this.container.appendChild(this.renderer.domElement);

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, W / H, 0.1, 10000);
    this.camera.position.set(0, -200, 140);
    this.camera.up.set(0, 0, 1);
    this.camera.lookAt(0, 0, 8);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.target.set(0, 0, 8);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;

    this.scene.add(new THREE.AmbientLight(0xffffff, 0.65));
    const dir = new THREE.DirectionalLight(0xffffff, 0.9);
    dir.position.set(60, -120, 220); this.scene.add(dir);
    const fill = new THREE.DirectionalLight(0x8899bb, 0.4);
    fill.position.set(-80, 100, -60); this.scene.add(fill);

    this.layerGroups = [new THREE.Group(), new THREE.Group(), new THREE.Group()];
    this.layerGroups.forEach(g => this.scene.add(g));

    this._tooltip = document.createElement('div');
    this._tooltip.className = 'viewer-tooltip';
    this._tooltip.style.display = 'none';
    this.container.style.position = 'relative';
    this.container.appendChild(this._tooltip);

    this._raycaster = new THREE.Raycaster();
    this._mouse = new THREE.Vector2();
    this._mouseDownXY = null;
    this.renderer.domElement.addEventListener('mousemove', e => this._onMouseMove(e));
    this.renderer.domElement.addEventListener('mousedown', e => { this._mouseDownXY = { x: e.clientX, y: e.clientY }; });
    this.renderer.domElement.addEventListener('click', e => {
      if (!this._mouseDownXY) return;
      const dx = e.clientX - this._mouseDownXY.x, dy = e.clientY - this._mouseDownXY.y;
      if (Math.sqrt(dx * dx + dy * dy) > 5) return; // was a drag
      this._onMouseClick(e);
    });

    new ResizeObserver(() => this._onResize()).observe(this.container);
    this._bindControls();
    this._loop();
  }

  _onResize() {
    if (!this.renderer) return;
    const W = this.container.clientWidth, H = this.container.clientHeight;
    if (!W || !H) return;
    this.camera.aspect = W / H;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(W, H);
  }

  _bindControls() {
    document.getElementById('exploded-toggle')?.addEventListener('change', e => {
      this._exploded = e.target.checked;
      this._targetSep = this._exploded ? 45 : 0;
      this._animating = true;
    });
    document.getElementById('reset-camera')?.addEventListener('click', () => {
      if (this._currentComponents.length > 0) this.rebuild(this._currentComponents);
      else { this.camera.position.set(0, -200, 140); this.controls.target.set(0, 0, 8); this.controls.update(); }
    });
    ['bottom', 'pcb', 'plate'].forEach((name, i) => {
      const cb = document.getElementById(`layer-vis-${name}`);
      if (cb) { cb.checked = true; cb.addEventListener('change', () => this.app.setLayerVisible(i, cb.checked)); }
    });
  }

  setLayerVisibility(vis) {
    if (!this._initialized) return;
    this.layerGroups.forEach((g, i) => { g.visible = vis[i]; });
  }

  _loop() {
    requestAnimationFrame(() => this._loop());
    if (this._animating) {
      this._currentSep += (this._targetSep - this._currentSep) * 0.10;
      if (Math.abs(this._currentSep - this._targetSep) < 0.05) {
        this._currentSep = this._targetSep; this._animating = false;
      }
      this.layerGroups.forEach((g, i) => { g.position.z = i * this._currentSep; });
    }
    this.controls?.update();
    this.renderer?.render(this.scene, this.camera);
  }

  rebuild(components) {
    this._ensureInit();
    this._currentComponents = components;

    this.layerGroups.forEach(g => { while (g.children.length) g.remove(g.children[0]); });
    this._meshMap.clear();
    this.layerGroups.forEach((g, i) => { g.visible = this.app.state.layerVisible[i]; });

    if (components.length === 0) return;

    // Compute bounding box and convex hull using physical part sizes
    const allPts = [];
    for (const c of components) allPts.push(...getCompCornersMm(c));
    // Jarvis March produces CCW in KLE/screen Y-down space.
    // mmToShapeVec flips Y, making it CW in Three.js space (which expects CCW for outer boundary).
    // Reversing the hull makes it CW in KLE space → CCW in Three.js after Y-flip.
    const hull = convexHull(allPts).reverse();
    const border = this.app.state.globalSettings.borderSize || 0;
    const expandedHull = expandHull(hull, border);

    const minX = Math.min(...allPts.map(p => p.x));
    const maxX = Math.max(...allPts.map(p => p.x));
    const minY = Math.min(...allPts.map(p => p.y));
    const maxY = Math.max(...allPts.map(p => p.y));
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;

    const plate  = buildPlate(components, expandedHull, border, cx, cy);
    const pcb    = buildPcb(components, expandedHull, border, cx, cy);
    const bottom = buildBottom(components, expandedHull, border, cx, cy);

    const positionGroup = (group, layerIdx) => {
      group.position.z = LAYER_BASE_Z[layerIdx];
      this.layerGroups[layerIdx].add(group);
      group.traverse(mesh => {
        if (!mesh.isMesh) return;
        const cd = mesh.userData?.compId ? mesh.userData : null;
        if (cd) {
          const def = COMPONENTS[cd.compType];
          this._meshMap.set(mesh, {
            layerName: LAYER_NAMES[layerIdx],
            compId: cd.compId,
            compType: cd.compType,
            displayName: def?.displayName ?? cd.compType,
          });
        } else {
          this._meshMap.set(mesh, { layerName: LAYER_NAMES[layerIdx] });
        }
      });
    };
    positionGroup(bottom, 0);
    positionGroup(pcb,    1);
    positionGroup(plate,  2);

    this.layerGroups.forEach((g, i) => { g.position.z = i * this._currentSep; });

    // Layer name sprites
    for (let i = 0; i < 3; i++) this._addLabel(LAYER_NAMES[i], -(maxX - minX) / 2 - border - 6, 0, LAYER_BASE_Z[i] + LAYER_THICKNESS / 2, i);

    // Fit camera to board
    const maxDim = Math.max(maxX - minX + border * 2, maxY - minY + border * 2);
    const dist = maxDim * 1.55;
    this.camera.position.set(0, -dist * 0.65, dist * 0.55 + 15);
    this.controls.target.set(0, 0, LAYER_BASE_Z[1] + LAYER_THICKNESS / 2);
    this.controls.update();
  }

  _addLabel(text, x, y, z, layerIdx) {
    const c = document.createElement('canvas');
    c.width = 256; c.height = 48;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 26px sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(text, 244, 34);
    const mat = new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true, opacity: 0.6 });
    const sprite = new THREE.Sprite(mat);
    sprite.scale.set(44, 9, 1);
    sprite.position.set(x - 20, y, z);
    this.layerGroups[layerIdx].add(sprite);
  }

  _onMouseClick(e) {
    if (!this.renderer) return;
    const rect = this.renderer.domElement.getBoundingClientRect();
    this._mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    this._mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    this._raycaster.setFromCamera(this._mouse, this.camera);
    const hits = this._raycaster.intersectObjects([...this._meshMap.keys()]);
    if (hits.length > 0) {
      const info = this._meshMap.get(hits[0].object);
      if (info?.compId) {
        this.app.selectComponent(info.compId);
      }
    }
  }

  _onMouseMove(e) {
    if (!this._tooltip || !this.renderer) return;
    const rect = this.renderer.domElement.getBoundingClientRect();
    this._mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    this._mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    this._raycaster.setFromCamera(this._mouse, this.camera);
    const hits = this._raycaster.intersectObjects([...this._meshMap.keys()]);
    if (hits.length > 0) {
      const info = this._meshMap.get(hits[0].object);
      if (info) {
        this._tooltip.textContent = info.displayName
          ? `${info.displayName} — ${info.layerName}`
          : info.layerName;
        this._tooltip.style.display = 'block';
        this._tooltip.style.left = (e.clientX - rect.left + 12) + 'px';
        this._tooltip.style.top  = (e.clientY - rect.top  - 28) + 'px';
        this.renderer.domElement.style.cursor = info.compId ? 'pointer' : 'default';
        return;
      }
    }
    this._tooltip.style.display = 'none';
    this.renderer.domElement.style.cursor = 'default';
  }
}
