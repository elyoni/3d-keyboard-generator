// JSON panel — live KLE JSON output, copy/download/load

import { parseKLE } from './kle-parser.js';

export class JsonPanel {
  constructor(container, app) {
    this.container = container;
    this.app = app;

    this._textarea = container.querySelector('#kle-json-output');
    this._errorDiv = container.querySelector('#json-error');
    this._userEditing = false;

    this._bindButtons();
    this._bindTextarea();
  }

  update(kleJson) {
    if (this._userEditing) return;
    this._textarea.value = kleJson;
    this._clearError();
  }

  _bindButtons() {
    this.container.querySelector('#btn-copy').addEventListener('click', () => {
      navigator.clipboard.writeText(this._textarea.value)
        .then(() => this._flash('#btn-copy', 'Copied!'))
        .catch(() => this._showError('Clipboard access denied. Please copy the text manually.'));
    });

    this.container.querySelector('#btn-download').addEventListener('click', () => {
      const blob = new Blob([this._textarea.value], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'keyboard-layout.json';
      a.click();
      URL.revokeObjectURL(url);
    });

    this.container.querySelector('#btn-load').addEventListener('click', () => {
      this._loadFromTextarea();
    });

    this.container.querySelector('#btn-clear').addEventListener('click', () => {
      if (confirm('Clear the layout? This will remove all components.')) {
        this.app.clearLayout();
      }
    });
  }

  _bindTextarea() {
    this._textarea.addEventListener('focus', () => { this._userEditing = true; });
    this._textarea.addEventListener('blur', () => { this._userEditing = false; });
    this._textarea.addEventListener('keydown', e => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this._loadFromTextarea();
      }
    });
  }

  _loadFromTextarea() {
    const text = this._textarea.value.trim();
    if (!text) return;
    try {
      const { components, globalSettings } = parseKLE(text);
      this.app.loadLayout(components, globalSettings);
      this._clearError();
      this._userEditing = false;
    } catch (e) {
      this._showError(`Parse error: ${e.message}`);
    }
  }

  _showError(msg) {
    this._errorDiv.textContent = msg;
    this._errorDiv.hidden = false;
    this._textarea.classList.add('error');
    setTimeout(() => { this._textarea.classList.remove('error'); }, 1500);
  }

  _clearError() {
    this._errorDiv.textContent = '';
    this._errorDiv.hidden = true;
    this._textarea.classList.remove('error');
  }

  _flash(id, text) {
    const btn = this.container.querySelector(`#${id}`);
    if (!btn) return;
    const orig = btn.textContent;
    btn.textContent = text;
    setTimeout(() => { btn.textContent = orig; }, 1500);
  }
}
