// HTML5 Canvas 2D grid editor

import { COMPONENTS } from './components.js';

const GRID_SIZE_PX = 60;  // pixels per key unit at scale=1
const CORNER_RADIUS = 4;  // px

export class Editor {
  constructor(canvas, app) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.app = app;

    this.scale = 1;
    this.panX = 30;
    this.panY = 30;

    this._dirty = true;
    this._dragging = null;
    this._panning = false;
    this._panStart = null;

    this._bindEvents();
    new ResizeObserver(() => this._onResize()).observe(canvas.parentElement);
    this._onResize();
    requestAnimationFrame(() => this._loop());
  }

  _onResize() {
    const p = this.canvas.parentElement;
    this.canvas.width = p.clientWidth;
    this.canvas.height = p.clientHeight;
    this._dirty = true;
  }

  markDirty() { this._dirty = true; }

  _loop() {
    if (this._dirty) { this._render(); this._dirty = false; }
    requestAnimationFrame(() => this._loop());
  }

  // ── Coordinate helpers ───────────────────────────────────────────────────────

  _pxToKU(px, py) {
    return {
      x: (px - this.panX) / (GRID_SIZE_PX * this.scale),
      y: (py - this.panY) / (GRID_SIZE_PX * this.scale),
    };
  }

  _snap(v) {
    const s = this.app.state.snapSize || 0.25;
    return Math.round(v / s) * s;
  }

  // ── Event binding ────────────────────────────────────────────────────────────

  _bindEvents() {
    this.canvas.addEventListener('mousedown', e => this._onMouseDown(e));
    this.canvas.addEventListener('mousemove', e => this._onMouseMove(e));
    this.canvas.addEventListener('mouseup',   e => this._onMouseUp(e));
    this.canvas.addEventListener('mouseleave',e => this._onMouseUp(e));
    this.canvas.addEventListener('wheel', e => this._onWheel(e), { passive: false });
    this.canvas.addEventListener('contextmenu', e => e.preventDefault());
    window.addEventListener('keydown', e => this._onKeyDown(e));
  }

  _getMouseKU(e) {
    const r = this.canvas.getBoundingClientRect();
    return this._pxToKU(e.clientX - r.left, e.clientY - r.top);
  }

  // ── Hit testing ──────────────────────────────────────────────────────────────

  _hitTest(ku) {
    const comps = this.app.state.components;
    for (let i = comps.length - 1; i >= 0; i--) {
      if (this._pointInComp(ku.x, ku.y, comps[i])) return comps[i];
    }
    return null;
  }

  _pointInComp(kx, ky, comp) {
    if (comp.r === 0) {
      return kx >= comp.absX && kx <= comp.absX + comp.w &&
             ky >= comp.absY && ky <= comp.absY + comp.h;
    }
    // Rotate point into component's local space
    const rad = -comp.r * Math.PI / 180;
    const dx = kx - comp.rx;
    const dy = ky - comp.ry;
    const rx = dx * Math.cos(rad) - dy * Math.sin(rad) + comp.rx;
    const ry = dx * Math.sin(rad) + dy * Math.cos(rad) + comp.ry;
    return rx >= comp.absX && rx <= comp.absX + comp.w &&
           ry >= comp.absY && ry <= comp.absY + comp.h;
  }

  // ── Mouse events ─────────────────────────────────────────────────────────────

  _onMouseDown(e) {
    const ku = this._getMouseKU(e);

    if (e.button === 1 || (e.button === 0 && e.altKey)) {
      this._panning = true;
      this._panStart = { mx: e.clientX, my: e.clientY, px: this.panX, py: this.panY };
      e.preventDefault();
      return;
    }

    if (e.button === 0) {
      if (this.app.state.activeTool) {
        this._placeComponent(ku);
        return;
      }
      const hit = this._hitTest(ku);
      if (hit) {
        this.app.selectComponent(hit.id);
        // Store start positions for drag — including rx/ry so rotated items drag correctly
        this._dragging = {
          comp: hit,
          startAbsX: hit.absX,
          startAbsY: hit.absY,
          startRx: hit.rx,
          startRy: hit.ry,
          mouseStartX: ku.x,
          mouseStartY: ku.y,
        };
      } else {
        this.app.selectComponent(null);
      }
    }
  }

  _onMouseMove(e) {
    const r = this.canvas.getBoundingClientRect();
    const px = e.clientX - r.left;
    const py = e.clientY - r.top;

    if (this._panning && this._panStart) {
      this.panX = this._panStart.px + (e.clientX - this._panStart.mx);
      this.panY = this._panStart.py + (e.clientY - this._panStart.my);
      this._dirty = true;
      return;
    }

    if (this._dragging) {
      const ku = this._pxToKU(px, py);
      const dx = ku.x - this._dragging.mouseStartX;
      const dy = ku.y - this._dragging.mouseStartY;

      const newX = this._snap(this._dragging.startAbsX + dx);
      const newY = this._snap(this._dragging.startAbsY + dy);
      const actualDx = newX - this._dragging.startAbsX;
      const actualDy = newY - this._dragging.startAbsY;

      // Also move the rotation pivot so rotated components move correctly
      const updates = {
        absX: newX,
        absY: newY,
        rx: this._dragging.startRx + actualDx,
        ry: this._dragging.startRy + actualDy,
      };
      this.app.updateComponent(this._dragging.comp.id, updates);
      return;
    }

    const ku = this._pxToKU(px, py);
    const hit = this._hitTest(ku);
    this.canvas.style.cursor = this.app.state.activeTool ? 'crosshair' : hit ? 'move' : 'default';
  }

  _onMouseUp(e) {
    if (this._panning) { this._panning = false; this._panStart = null; return; }
    if (this._dragging) { this.app.pushHistory(); this.app._saveToStorage(); this._dragging = null; }
  }

  _onWheel(e) {
    e.preventDefault();
    const r = this.canvas.getBoundingClientRect();
    const mx = e.clientX - r.left;
    const my = e.clientY - r.top;
    const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
    const ns = Math.max(0.15, Math.min(5, this.scale * factor));
    this.panX = mx - (mx - this.panX) * (ns / this.scale);
    this.panY = my - (my - this.panY) * (ns / this.scale);
    this.scale = ns;
    this._dirty = true;
  }

  _onKeyDown(e) {
    if (['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)) return;
    if ((e.key === 'Delete' || e.key === 'Backspace') && this.app.state.selected) {
      this.app.deleteSelected(); e.preventDefault();
    }
    if (e.key === 'Escape') { this.app.setActiveTool(null); this.app.selectComponent(null); }
    if ((e.ctrlKey || e.metaKey) && e.key === 'z') { e.preventDefault(); this.app.undo(); }
    if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.shiftKey && e.key === 'z'))) { e.preventDefault(); this.app.redo(); }
  }

  // ── Component placement ──────────────────────────────────────────────────────

  _placeComponent(ku) {
    const type = this.app.state.activeTool;
    const def = COMPONENTS[type];
    const x = Math.max(0, this._snap(ku.x - def.defaultW / 2));
    const y = Math.max(0, this._snap(ku.y - def.defaultH / 2));

    this.app.addComponent({
      type,
      absX: x, absY: y,
      w: def.defaultW, h: def.defaultH,
      r: def.defaultR || 0,
      rx: x + def.defaultW / 2,
      ry: y + def.defaultH / 2,
      label: '', p: '',
    });
  }

  fitToWindow() {
    const comps = this.app.state.components;
    if (comps.length === 0) { this.scale = 1; this.panX = 40; this.panY = 40; this._dirty = true; return; }
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const c of comps) {
      // Account for rotation by using all 4 corners
      const corners = this._getWorldCorners(c);
      for (const p of corners) {
        minX = Math.min(minX, p.x); minY = Math.min(minY, p.y);
        maxX = Math.max(maxX, p.x); maxY = Math.max(maxY, p.y);
      }
    }
    const pad = 1.5;
    const kuW = (maxX - minX) + pad * 2;
    const kuH = (maxY - minY) + pad * 2;
    this.scale = Math.min(this.canvas.width / (kuW * GRID_SIZE_PX), this.canvas.height / (kuH * GRID_SIZE_PX), 2);
    this.panX = -((minX - pad) * GRID_SIZE_PX * this.scale);
    this.panY = -((minY - pad) * GRID_SIZE_PX * this.scale);
    this._dirty = true;
  }

  // ── Convex hull helpers ──────────────────────────────────────────────────────

  _getWorldCorners(comp) {
    const corners = [
      { x: comp.absX,          y: comp.absY },
      { x: comp.absX + comp.w, y: comp.absY },
      { x: comp.absX + comp.w, y: comp.absY + comp.h },
      { x: comp.absX,          y: comp.absY + comp.h },
    ];
    if (comp.r === 0) return corners;
    const rad = comp.r * Math.PI / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    return corners.map(p => {
      const dx = p.x - comp.rx;
      const dy = p.y - comp.ry;
      return { x: comp.rx + dx * cos - dy * sin, y: comp.ry + dx * sin + dy * cos };
    });
  }

  _convexHull(points) {
    if (points.length < 3) return points;
    // Find bottom-left
    let start = 0;
    for (let i = 1; i < points.length; i++) {
      if (points[i].y > points[start].y ||
          (points[i].y === points[start].y && points[i].x < points[start].x)) start = i;
    }
    const hull = [];
    let cur = start;
    do {
      hull.push(points[cur]);
      let next = (cur + 1) % points.length;
      for (let i = 0; i < points.length; i++) {
        const cross = (points[next].x - points[cur].x) * (points[i].y - points[cur].y) -
                      (points[next].y - points[cur].y) * (points[i].x - points[cur].x);
        if (cross < 0) next = i;
      }
      cur = next;
    } while (cur !== start);
    return hull;
  }

  // ── Render ───────────────────────────────────────────────────────────────────

  _render() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    ctx.save();
    ctx.translate(this.panX, this.panY);
    ctx.scale(this.scale, this.scale);

    this._drawGrid();
    this._drawOutline();
    this._drawComponents();

    ctx.restore();
  }

  _drawGrid() {
    const ctx = this.ctx;
    const gs = GRID_SIZE_PX;
    const sc = this.scale;
    const W = this.canvas.width;
    const H = this.canvas.height;

    const x0 = Math.floor(-this.panX / (gs * sc)) - 1;
    const y0 = Math.floor(-this.panY / (gs * sc)) - 1;
    const x1 = Math.ceil((W - this.panX) / (gs * sc)) + 1;
    const y1 = Math.ceil((H - this.panY) / (gs * sc)) + 1;

    const snap = this.app.state.snapSize || 0.25;

    // Fine grid at snap size
    if (snap < 1 && gs * sc * snap > 4) {
      ctx.strokeStyle = 'rgba(255,255,255,0.04)';
      ctx.lineWidth = 0.5 / sc;
      const steps = Math.round(1 / snap);
      for (let xi = x0 * steps; xi <= x1 * steps; xi++) {
        if (xi % steps === 0) continue;
        const px = xi * gs * snap;
        ctx.beginPath(); ctx.moveTo(px, y0 * gs); ctx.lineTo(px, y1 * gs); ctx.stroke();
      }
      for (let yi = y0 * steps; yi <= y1 * steps; yi++) {
        if (yi % steps === 0) continue;
        const py = yi * gs * snap;
        ctx.beginPath(); ctx.moveTo(x0 * gs, py); ctx.lineTo(x1 * gs, py); ctx.stroke();
      }
    }

    // Main 1 KU grid
    ctx.strokeStyle = 'rgba(255,255,255,0.13)';
    ctx.lineWidth = 1 / sc;
    for (let x = x0; x <= x1; x++) {
      ctx.beginPath(); ctx.moveTo(x * gs, y0 * gs); ctx.lineTo(x * gs, y1 * gs); ctx.stroke();
    }
    for (let y = y0; y <= y1; y++) {
      ctx.beginPath(); ctx.moveTo(x0 * gs, y * gs); ctx.lineTo(x1 * gs, y * gs); ctx.stroke();
    }

    // Origin cross
    ctx.strokeStyle = 'rgba(255,255,255,0.35)';
    ctx.lineWidth = 2 / sc;
    const m = 0.35 * gs;
    ctx.beginPath(); ctx.moveTo(-m, 0); ctx.lineTo(m, 0); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, -m); ctx.lineTo(0, m); ctx.stroke();
  }

  // Draw keyboard outline — convex hull of all component corners + border margin
  _drawOutline() {
    const comps = this.app.state.components;
    if (comps.length === 0) return;

    const allPoints = [];
    for (const c of comps) {
      allPoints.push(...this._getWorldCorners(c));
    }
    const hull = this._convexHull(allPoints);
    if (hull.length < 3) return;

    // Expand hull outward by borderSize (mm → KU = mm / 19.05)
    const border = (this.app.state.globalSettings.borderSize || 0) / 19.05;
    let expanded = hull;
    if (border > 0) {
      const cx = hull.reduce((s, p) => s + p.x, 0) / hull.length;
      const cy = hull.reduce((s, p) => s + p.y, 0) / hull.length;
      expanded = hull.map(p => {
        const dx = p.x - cx;
        const dy = p.y - cy;
        const len = Math.sqrt(dx * dx + dy * dy) || 1;
        return { x: p.x + (dx / len) * border, y: p.y + (dy / len) * border };
      });
    }

    const ctx = this.ctx;
    const gs = GRID_SIZE_PX;

    // Filled translucent board area
    ctx.fillStyle = 'rgba(255, 200, 100, 0.04)';
    ctx.beginPath();
    ctx.moveTo(expanded[0].x * gs, expanded[0].y * gs);
    for (const p of expanded.slice(1)) ctx.lineTo(p.x * gs, p.y * gs);
    ctx.closePath();
    ctx.fill();

    // Dashed outline
    ctx.strokeStyle = 'rgba(255, 200, 100, 0.55)';
    ctx.lineWidth = 1.5 / this.scale;
    ctx.setLineDash([6 / this.scale, 4 / this.scale]);
    ctx.beginPath();
    ctx.moveTo(expanded[0].x * gs, expanded[0].y * gs);
    for (const p of expanded.slice(1)) ctx.lineTo(p.x * gs, p.y * gs);
    ctx.closePath();
    ctx.stroke();
    ctx.setLineDash([]);

    // Corner dot markers
    ctx.fillStyle = 'rgba(255, 200, 100, 0.7)';
    for (const p of expanded) {
      ctx.beginPath();
      ctx.arc(p.x * gs, p.y * gs, 2.5 / this.scale, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  _drawComponents() {
    const ctx = this.ctx;
    const gs = GRID_SIZE_PX;
    const selectedId = this.app.state.selected;

    for (const comp of this.app.state.components) {
      const def = COMPONENTS[comp.type];
      const isSelected = comp.id === selectedId;

      ctx.save();
      if (comp.r !== 0) {
        ctx.translate(comp.rx * gs, comp.ry * gs);
        ctx.rotate(comp.r * Math.PI / 180);
        ctx.translate(-comp.rx * gs, -comp.ry * gs);
      }

      const x = comp.absX * gs;
      const y = comp.absY * gs;
      const w = comp.w * gs;
      const h = comp.h * gs;
      const cr = Math.min(CORNER_RADIUS, w / 4, h / 4);

      ctx.fillStyle = def.color2d + (isSelected ? 'ff' : 'cc');
      roundRect(ctx, x + 2, y + 2, w - 4, h - 4, cr);
      ctx.fill();

      ctx.strokeStyle = isSelected ? '#ffffff' : def.color2d;
      ctx.lineWidth = (isSelected ? 2 : 1) / this.scale;
      ctx.setLineDash(isSelected ? [4 / this.scale, 4 / this.scale] : []);
      roundRect(ctx, x + 2, y + 2, w - 4, h - 4, cr);
      ctx.stroke();
      ctx.setLineDash([]);

      // Type abbreviation label
      const minDim = Math.min(w, h);
      const fs = Math.max(6, Math.min(minDim * 0.3, 14)) / this.scale;
      ctx.fillStyle = '#ffffff';
      ctx.font = `bold ${fs}px monospace`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(def.abbrev, x + w / 2, y + h / 2 - (comp.label || comp.p ? fs * 0.6 : 0));

      // Key label
      if ((comp.type === 'cherry' || comp.type === 'kailhchoc') && comp.label) {
        ctx.fillStyle = 'rgba(255,255,255,0.75)';
        ctx.font = `${Math.max(5, fs * 0.65)}px monospace`;
        ctx.fillText(comp.label, x + w / 2, y + h * 0.72);
      }

      // Plate text preview
      if (comp.type === 'platetext' && comp.p) {
        ctx.fillStyle = 'rgba(255,255,255,0.75)';
        ctx.font = `${Math.max(4, fs * 0.55)}px monospace`;
        ctx.fillText(comp.p.split('\n')[0].substring(0, 8), x + w / 2, y + h * 0.72);
      }

      // Rotation pivot dot
      if (comp.r !== 0) {
        ctx.fillStyle = 'rgba(255,255,80,0.9)';
        ctx.beginPath();
        ctx.arc(comp.rx * gs, comp.ry * gs, 3.5 / this.scale, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = 'rgba(0,0,0,0.5)';
        ctx.lineWidth = 1 / this.scale;
        ctx.stroke();
      }

      ctx.restore();
    }
  }
}

function roundRect(ctx, x, y, w, h, r) {
  r = Math.max(0, r);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.arcTo(x + w, y, x + w, y + r, r);
  ctx.lineTo(x + w, y + h - r);
  ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
  ctx.lineTo(x + r, y + h);
  ctx.arcTo(x, y + h, x, y + h - r, r);
  ctx.lineTo(x, y + r);
  ctx.arcTo(x, y, x + r, y, r);
  ctx.closePath();
}
