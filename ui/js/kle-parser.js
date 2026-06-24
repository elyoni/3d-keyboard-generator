// KLE JSON string → internal flat model
// Implements the KLE cursor algorithm.
// Internal component = { id, type, absX, absY, w, h, r, rx, ry, label, p }

import { COMPONENTS, SM_TO_TYPE, LABEL_FALLBACKS } from './components.js';

let _idCounter = 0;
function genId() {
  return `comp_${++_idCounter}`;
}

// Preprocess KLE JSON string: bare property names → quoted, single-quoted strings → double-quoted.
// KLE JSON uses {sm:"cherry"} which is not valid JSON.
function preprocessKLE(raw) {
  // Remove JS-style comments (// ...)
  let s = raw.replace(/\/\/[^\n]*/g, '');
  // Replace bare property names: word characters followed by : (but not http://)
  s = s.replace(/([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)(\s*):/g, '$1"$2"$3:');
  // Replace single-quoted strings with double-quoted
  s = s.replace(/'([^'\\]*(\\.[^'\\]*)*)'/g, (_, inner) => '"' + inner.replace(/"/g, '\\"') + '"');
  return s;
}

// Resolve the component type from a pykle key's properties.
// Priority: sm field > label[4] (profile) > label[2] (top-right) > label[10] > label[0]
function resolveType(sm, labels, p) {
  // sm field takes priority
  if (sm && sm !== '') {
    const t = SM_TO_TYPE[sm];
    if (t) return t;
  }
  // Check label fallbacks
  for (const label of labels) {
    if (label && label !== '') {
      const t = LABEL_FALLBACKS[label.trim()];
      if (t) return t;
      // Check sm values directly
      if (SM_TO_TYPE[label.trim()]) return SM_TO_TYPE[label.trim()];
    }
  }
  // Default to cherry MX
  return 'cherry';
}

export function parseKLE(kleStr) {
  const components = [];
  const globalSettings = { split: false, switchType: 'cherrymx', borderSize: 0 };

  let processed;
  try {
    processed = preprocessKLE(kleStr);
    // Parse as JSON
  } catch (e) {
    throw new Error(`KLE preprocessing failed: ${e.message}`);
  }

  let rows;
  try {
    rows = JSON.parse(processed);
  } catch (e) {
    throw new Error(`KLE JSON parse error: ${e.message}`);
  }

  if (!Array.isArray(rows)) {
    throw new Error('KLE JSON must be an array of rows');
  }

  // KLE cursor state
  let curX = 0;
  let curY = 0;
  let curR = 0;
  let curRx = 0;
  let curRy = 0;
  let curW = 1;
  let curH = 1;
  let curSm = '';
  let curA = 4; // alignment
  let curP = ''; // profile (p field)

  // Check first element for metadata
  const firstRow = rows[0];
  if (Array.isArray(firstRow) && firstRow.length > 0 && typeof firstRow[0] === 'object' && firstRow[0] !== null) {
    const meta = firstRow[0];
    if (meta.meta) {
      const m = meta.meta;
      if (m.split) globalSettings.split = true;
      if (m.switchType) globalSettings.switchType = m.switchType;
      if (m.notes !== undefined) globalSettings.borderSize = parseInt(m.notes) || 0;
    }
    // The pykle_serial also stores meta in keyboard.meta — but we just check first element
  }

  for (const row of rows) {
    if (!Array.isArray(row)) continue;

    // Reset per-row cursor state
    // curX resets to curRx at the start of each row
    // curY advances by 1 (default key height) from previous row's ry
    // Note: curSm is sticky (persists across rows like r/rx/ry — matches pykle_serial behavior)
    curX = curRx;
    curY = curRy;
    curW = 1;
    curH = 1;
    curA = 4;
    curP = '';

    let isFirstInRow = true;

    for (const item of row) {
      if (item === null) continue;

      if (typeof item === 'object' && !Array.isArray(item)) {
        // Property block — update cursor state
        if ('r' in item) {
          curR = item.r;
          // When rotation changes, reset cursor to (rx, ry)
          // but only if rx/ry are also specified
        }
        if ('rx' in item) {
          curRx = item.rx;
          curX = curRx; // reset cursor x
        }
        if ('ry' in item) {
          curRy = item.ry;
          curY = curRy; // reset cursor y
        }
        if ('x' in item) curX += item.x;
        if ('y' in item) curY += item.y;
        if ('w' in item) curW = item.w;
        if ('h' in item) curH = item.h;
        if ('sm' in item) curSm = item.sm;
        if ('a' in item) curA = item.a;
        if ('p' in item) curP = item.p || '';
      } else if (typeof item === 'string') {
        // This is a key — place it
        const label = item;

        // Build labels array for type resolution
        // KLE alignment 'a' affects which label slots are active
        // We use labels[4] (profile) for type detection when sm is absent
        // For simplicity, put label in position 0 and p in position 4
        const labels = [];
        labels[0] = label;
        labels[4] = curP || label;
        labels[2] = label;
        labels[10] = label;

        const type = resolveType(curSm, labels, curP);
        const comp = COMPONENTS[type];

        // For keys, the label string is the key legend (not the type name)
        // Only preserve it if it looks like a real key label (not a component name)
        const isComponentLabel = LABEL_FALLBACKS[label] || SM_TO_TYPE[label];
        const displayLabel = (!isComponentLabel && type === 'cherry') || (!isComponentLabel && type === 'kailhchoc')
          ? label
          : '';

        components.push({
          id: genId(),
          type,
          absX: curX,
          absY: curY,
          w: curW,
          h: curH,
          r: curR,
          rx: curRx,
          ry: curRy,
          label: displayLabel,
          p: curP,
        });

        // Advance cursor by key width
        curX += curW;

        // Reset per-key one-shot properties (w, h, p reset; sm stays sticky like r/rx/ry)
        curW = 1;
        curH = 1;
        curP = '';
        isFirstInRow = false;
      }
    }

    // After each row, advance by 1 from the Y position used in this row
    // (not a simple +1 counter — y-deltas from property blocks accumulate)
    curRy = curY + 1;
    curX = curRx;
    curY = curRy;
  }

  return { components, globalSettings };
}
