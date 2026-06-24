// Central application state and wiring

import { COMPONENTS, CATEGORIES } from './components.js';
import { serializeKLE } from './kle-serializer.js';
import { parseKLE } from './kle-parser.js';
import { Editor } from './editor.js';
import { PropertiesPanel } from './properties.js';
import { JsonPanel } from './json-panel.js';
import { Viewer3D } from './viewer3d.js';
import { PRESETS } from './presets.js';

const STORAGE_KEY = 'kbdgen_v1';

let _idCounter = 1000;
function genId() { return `comp_${++_idCounter}`; }

class App {
  constructor() {
    this.state = {
      components: [],
      selected: null,
      activeTool: null,
      snapSize: 0.25,           // configurable snap grid in KU
      globalSettings: { split: false, switchType: 'cherrymx', borderSize: 0 },
      viewMode: 'editor',
      layerVisible: [true, true, true], // [bottom, pcb, plate]
    };

    this._history = [];
    this._historyIndex = -1;
    this._maxHistory = 80;

    this._editor = null;
    this._properties = null;
    this._jsonPanel = null;
    this._viewer3d = null;
  }

  init() {
    this._buildToolbar();
    this._buildGlobalSettings();
    this._buildViewTabs();
    this._buildPresetSelector();

    const editorCanvas = document.getElementById('editor-canvas');
    this._editor = new Editor(editorCanvas, this);

    const propsContainer = document.getElementById('properties-panel');
    this._properties = new PropertiesPanel(propsContainer, this);

    const jsonContainer = document.getElementById('json-section');
    this._jsonPanel = new JsonPanel(jsonContainer, this);

    const viewerContainer = document.getElementById('viewer-3d');
    this._viewer3d = new Viewer3D(viewerContainer, this);

    document.getElementById('btn-fit').addEventListener('click', () => this._editor.fitToWindow());

    // Restore from localStorage or start empty
    if (!this._loadFromStorage()) {
      this.pushHistory();
    }

    this._properties.render();
    this._updateJSON();
  }

  // ── State mutations ──────────────────────────────────────────────────────────

  addComponent(compData) {
    const comp = { ...compData, id: genId() };
    this.state.components = [...this.state.components, comp];
    this.state.selected = comp.id;
    // activeTool is intentionally NOT cleared — user stays in placement mode
    this._afterMutation();
    this.pushHistory();
    this._saveToStorage();
  }

  updateComponent(id, changes) {
    this.state.components = this.state.components.map(c =>
      c.id === id ? { ...c, ...changes } : c
    );
    this._afterMutation();
    this._saveToStorage();
  }

  deleteSelected() {
    if (!this.state.selected) return;
    this.state.components = this.state.components.filter(c => c.id !== this.state.selected);
    this.state.selected = null;
    this._afterMutation();
    this.pushHistory();
    this._saveToStorage();
  }

  selectComponent(id) {
    this.state.selected = id;
    this._properties.render();
    this._editor.markDirty();
  }

  setActiveTool(type) {
    this.state.activeTool = type;
    this._updateToolbarActive();
    // Don't clear selection when switching tools
    this._properties.render();
    this._editor.markDirty();
  }

  clearLayout() {
    this.state.components = [];
    this.state.selected = null;
    this.state.activeTool = null;
    this._updateToolbarActive();
    this._afterMutation();
    this.pushHistory();
    this._saveToStorage();
  }

  loadLayout(components, globalSettings) {
    this.state.components = components.map(c => ({ ...c, id: genId() }));
    this.state.selected = null;
    this.state.globalSettings = { ...this.state.globalSettings, ...globalSettings };
    this._syncGlobalSettingsUI();
    this._afterMutation();
    this.pushHistory();
    this._saveToStorage();
    this._editor.fitToWindow();
  }

  setLayerVisible(index, visible) {
    this.state.layerVisible = this.state.layerVisible.map((v, i) => i === index ? visible : v);
    this._viewer3d.setLayerVisibility(this.state.layerVisible);
  }

  // ── Persistence ──────────────────────────────────────────────────────────────

  _saveToStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        components: this.state.components,
        globalSettings: this.state.globalSettings,
        snapSize: this.state.snapSize,
      }));
    } catch (e) { /* quota error — ignore */ }
  }

  _loadFromStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return false;
      const data = JSON.parse(raw);
      if (data.components && data.components.length > 0) {
        this.state.components = data.components.map(c => ({ ...c, id: genId() }));
        this.state.globalSettings = { ...this.state.globalSettings, ...(data.globalSettings || {}) };
        this.state.snapSize = data.snapSize || 0.25;
        this._syncGlobalSettingsUI();
        this._syncSnapUI();
        this._afterMutation();
        this.pushHistory();
        // Defer fitToWindow until editor canvas is sized
        setTimeout(() => this._editor.fitToWindow(), 50);
        return true;
      }
    } catch (e) { /* corrupted storage */ }
    return false;
  }

  // ── History ──────────────────────────────────────────────────────────────────

  pushHistory() {
    const snapshot = JSON.stringify(this.state.components);
    this._history = this._history.slice(0, this._historyIndex + 1);
    this._history.push(snapshot);
    if (this._history.length > this._maxHistory) this._history.shift();
    this._historyIndex = this._history.length - 1;
  }

  undo() {
    if (this._historyIndex <= 0) return;
    this._historyIndex--;
    this.state.components = JSON.parse(this._history[this._historyIndex]);
    this.state.selected = null;
    this._afterMutation();
    this._saveToStorage();
  }

  redo() {
    if (this._historyIndex >= this._history.length - 1) return;
    this._historyIndex++;
    this.state.components = JSON.parse(this._history[this._historyIndex]);
    this.state.selected = null;
    this._afterMutation();
    this._saveToStorage();
  }

  // ── Internal update pipeline ─────────────────────────────────────────────────

  _afterMutation() {
    this._properties.render();
    this._editor.markDirty();
    this._updateJSON();
    if (this.state.viewMode === '3d') {
      this._viewer3d.rebuild(this.state.components);
    }
  }

  _updateJSON() {
    const kle = serializeKLE(this.state.components, this.state.globalSettings);
    this._jsonPanel.update(kle);
  }

  // ── Toolbar ──────────────────────────────────────────────────────────────────

  _buildToolbar() {
    const toolbar = document.getElementById('toolbar');
    toolbar.innerHTML = '';

    for (const cat of CATEGORIES) {
      const entries = Object.entries(COMPONENTS).filter(([, d]) => d.category === cat);
      if (entries.length === 0) continue;

      const section = document.createElement('div');
      section.className = 'toolbar-section';
      const header = document.createElement('div');
      header.className = 'toolbar-section-header';
      header.textContent = cat;
      section.appendChild(header);

      for (const [key, def] of entries) {
        const btn = document.createElement('button');
        btn.className = 'tool-btn';
        btn.dataset.type = key;
        btn.title = def.tip;
        btn.innerHTML = `
          <span class="tool-color" style="background:${def.color2d}"></span>
          <span class="tool-label">${def.displayName}</span>
        `;
        btn.addEventListener('click', () => {
          const isSame = this.state.activeTool === key;
          this.setActiveTool(isSame ? null : key);
        });
        section.appendChild(btn);
      }

      toolbar.appendChild(section);
    }
  }

  _updateToolbarActive() {
    document.querySelectorAll('.tool-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.type === this.state.activeTool);
    });
  }

  // ── Preset selector ──────────────────────────────────────────────────────────

  _buildPresetSelector() {
    const sel = document.getElementById('preset-select');
    if (!sel) return;

    for (const preset of PRESETS) {
      const opt = document.createElement('option');
      opt.value = preset.id;
      opt.textContent = preset.name;
      opt.title = preset.description;
      sel.appendChild(opt);
    }

    document.getElementById('btn-load-preset').addEventListener('click', () => {
      const id = sel.value;
      if (id === 'empty') { this.clearLayout(); return; }
      const preset = PRESETS.find(p => p.id === id);
      if (!preset) return;
      if (this.state.components.length > 0 &&
          !confirm(`Load "${preset.name}"? This will replace the current layout.`)) return;
      try {
        const { components, globalSettings } = parseKLE(preset.kle);
        const merged = { ...globalSettings, split: preset.split };
        this.loadLayout(components, merged);
      } catch (e) {
        alert(`Failed to load preset: ${e.message}`);
      }
    });
  }

  // ── Global settings ──────────────────────────────────────────────────────────

  _buildGlobalSettings() {
    const splitCb = document.getElementById('setting-split');
    const switchSel = document.getElementById('setting-switch-type');
    const borderInp = document.getElementById('setting-border');
    const snapInp = document.getElementById('setting-snap');

    if (splitCb) {
      splitCb.checked = this.state.globalSettings.split;
      splitCb.addEventListener('change', () => {
        this.state.globalSettings.split = splitCb.checked;
        this._updateJSON();
        this._saveToStorage();
      });
    }
    if (switchSel) {
      switchSel.value = this.state.globalSettings.switchType;
      switchSel.addEventListener('change', () => {
        this.state.globalSettings.switchType = switchSel.value;
        this._updateJSON();
        this._saveToStorage();
      });
    }
    if (borderInp) {
      borderInp.value = this.state.globalSettings.borderSize;
      borderInp.addEventListener('change', () => {
        this.state.globalSettings.borderSize = parseInt(borderInp.value) || 0;
        this._updateJSON();
        this._editor.markDirty();
        this._saveToStorage();
      });
    }
    if (snapInp) {
      snapInp.value = this.state.snapSize;
      snapInp.addEventListener('change', () => {
        const v = parseFloat(snapInp.value);
        if (v > 0) { this.state.snapSize = v; this._saveToStorage(); }
      });
    }
  }

  _syncGlobalSettingsUI() {
    const gs = this.state.globalSettings;
    const el = (id) => document.getElementById(id);
    if (el('setting-split')) el('setting-split').checked = gs.split;
    if (el('setting-switch-type')) el('setting-switch-type').value = gs.switchType;
    if (el('setting-border')) el('setting-border').value = gs.borderSize;
  }

  _syncSnapUI() {
    const snapInp = document.getElementById('setting-snap');
    if (snapInp) snapInp.value = this.state.snapSize;
  }

  // ── View tabs ────────────────────────────────────────────────────────────────

  _buildViewTabs() {
    const editorTab = document.getElementById('tab-editor');
    const viewerTab = document.getElementById('tab-3d');
    const editorSection = document.getElementById('editor-section');
    const viewerSection = document.getElementById('viewer-section');

    const switchTo = (mode) => {
      this.state.viewMode = mode;
      editorSection.hidden = mode !== 'editor';
      viewerSection.hidden = mode !== '3d';
      editorTab.classList.toggle('active', mode === 'editor');
      viewerTab.classList.toggle('active', mode === '3d');
      if (mode === '3d') {
        this._viewer3d.rebuild(this.state.components);
      }
    };

    editorTab.addEventListener('click', () => switchTo('editor'));
    viewerTab.addEventListener('click', () => switchTo('3d'));
  }
}

// Boot
const app = new App();
window.__app = app;
window.addEventListener('DOMContentLoaded', () => app.init());
