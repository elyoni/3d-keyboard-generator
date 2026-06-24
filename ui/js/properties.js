// Properties panel — shows fields for the selected component

import { COMPONENTS } from './components.js';

export class PropertiesPanel {
  constructor(container, app) {
    this.container = container;
    this.app = app;
  }

  render() {
    const activeId = document.activeElement?.id;
    const selEnd = document.activeElement?.selectionEnd;

    const { selected, components } = this.app.state;
    const comp = selected ? components.find(c => c.id === selected) : null;

    if (!comp) {
      this.container.innerHTML = `
        <div class="props-empty">
          <p>Click a component to select it, or pick a tool from the toolbar to place one.</p>
        </div>
      `;
      return;
    }

    const def = COMPONENTS[comp.type];

    // Build type options
    const typeOptions = Object.entries(COMPONENTS)
      .map(([key, d]) => `<option value="${key}" ${key === comp.type ? 'selected' : ''}>${d.displayName}</option>`)
      .join('');

    const hasRotation = comp.r !== 0;

    this.container.innerHTML = `
      <div class="props-header" style="background:${def.color2d}22; border-left: 3px solid ${def.color2d};">
        <span class="props-abbrev" style="background:${def.color2d}">${def.abbrev}</span>
        <span class="props-name">${def.displayName}</span>
      </div>

      <div class="props-body">
        <label class="prop-label">Type
          <select id="prop-type">${typeOptions}</select>
        </label>

        <div class="prop-row">
          <label class="prop-label">X (KU)
            <input type="number" id="prop-x" value="${round4(comp.absX)}" step="0.25" min="0">
          </label>
          <label class="prop-label">Y (KU)
            <input type="number" id="prop-y" value="${round4(comp.absY)}" step="0.25" min="0">
          </label>
        </div>

        <div class="prop-row">
          <label class="prop-label">W (KU)
            <input type="number" id="prop-w" value="${round4(comp.w)}" step="0.25" min="0.1">
          </label>
          <label class="prop-label">H (KU)
            <input type="number" id="prop-h" value="${round4(comp.h)}" step="0.25" min="0.1">
          </label>
        </div>

        <label class="prop-label">Rotation (°)
          <input type="number" id="prop-r" value="${round4(comp.r)}" step="15">
        </label>

        <div id="pivot-fields" style="${hasRotation ? '' : 'display:none'}">
          <div class="prop-row">
            <label class="prop-label">Pivot X
              <input type="number" id="prop-rx" value="${round4(comp.rx)}" step="0.25">
            </label>
            <label class="prop-label">Pivot Y
              <input type="number" id="prop-ry" value="${round4(comp.ry)}" step="0.25">
            </label>
          </div>
        </div>

        ${(comp.type === 'cherry' || comp.type === 'kailhchoc') ? `
        <label class="prop-label">Key Label
          <input type="text" id="prop-label" value="${escHtml(comp.label || '')}" placeholder="e.g. Q, Enter, Shift">
        </label>
        ` : ''}

        ${def.hasTextProp ? `
        <label class="prop-label">Engraved Text (p)
          <textarea id="prop-p" rows="3" placeholder="Line1\\nLine2">${escHtml(comp.p || '')}</textarea>
        </label>
        ` : ''}

        <div class="props-info">
          <span class="props-layer">Layer: ${def.layer}</span>
          <span class="props-tip">${def.tip}</span>
        </div>

        <button id="prop-delete" class="btn-danger">Delete Component</button>
      </div>
    `;

    this._bindEvents(comp);

    if (activeId) {
      const el = document.getElementById(activeId);
      if (el && this.container.contains(el)) {
        el.focus();
        if (selEnd !== undefined && el.setSelectionRange) {
          el.setSelectionRange(selEnd, selEnd);
        }
      }
    }
  }

  _bindEvents(comp) {
    const update = (key, val) => {
      this.app.updateComponent(comp.id, { [key]: val });
      this.app.pushHistory();
    };

    const bind = (id, key, parser = parseFloat) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('change', () => update(key, parser(el.value)));
    };

    // Type change: update and re-render panel
    const typeEl = document.getElementById('prop-type');
    if (typeEl) {
      typeEl.addEventListener('change', () => {
        const newType = typeEl.value;
        const newDef = COMPONENTS[newType];
        this.app.updateComponent(comp.id, {
          type: newType,
          w: newDef.defaultW,
          h: newDef.defaultH,
        });
        this.app.pushHistory();
        this.render(); // re-render panel to show/hide type-specific fields
      });
    }

    bind('prop-x', 'absX');
    bind('prop-y', 'absY');
    bind('prop-w', 'w');
    bind('prop-h', 'h');

    const rEl = document.getElementById('prop-r');
    if (rEl) {
      rEl.addEventListener('change', () => {
        const newR = parseFloat(rEl.value);
        this.app.updateComponent(comp.id, { r: newR });
        this.app.pushHistory();
        // Show/hide pivot fields
        const pivotDiv = document.getElementById('pivot-fields');
        if (pivotDiv) pivotDiv.style.display = newR !== 0 ? '' : 'none';
      });
    }

    bind('prop-rx', 'rx');
    bind('prop-ry', 'ry');

    const labelEl = document.getElementById('prop-label');
    if (labelEl) labelEl.addEventListener('input', () => update('label', labelEl.value));

    const pEl = document.getElementById('prop-p');
    if (pEl) pEl.addEventListener('input', () => update('p', pEl.value));

    const delBtn = document.getElementById('prop-delete');
    if (delBtn) delBtn.addEventListener('click', () => this.app.deleteSelected());
  }
}

function round4(n) { return Math.round(n * 10000) / 10000; }
function escHtml(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
