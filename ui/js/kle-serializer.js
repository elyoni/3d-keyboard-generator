// Internal flat model → KLE JSON string
// Converts the flat array of components (absolute positions) to KLE JSON format.

import { COMPONENTS } from './components.js';

const EPSILON = 0.01; // tolerance for floating-point comparisons

function round4(n) {
  return Math.round(n * 10000) / 10000;
}

function approxEqual(a, b) {
  return Math.abs(a - b) < EPSILON;
}

// Group components into "rows" by their absY value (within tolerance).
// Returns array of rows, each row sorted by absX.
function groupIntoRows(components) {
  if (components.length === 0) return [];

  // Separate rotated components (they form their own groups)
  const rotated = components.filter(c => !approxEqual(c.r, 0));
  const straight = components.filter(c => approxEqual(c.r, 0));

  const rows = [];

  // Group straight components by Y
  const usedStraight = new Set();
  const sortedStraight = [...straight].sort((a, b) => a.absY - b.absY || a.absX - b.absX);

  for (const comp of sortedStraight) {
    if (usedStraight.has(comp.id)) continue;
    const row = [comp];
    usedStraight.add(comp.id);
    for (const other of sortedStraight) {
      if (!usedStraight.has(other.id) && approxEqual(other.absY, comp.absY)) {
        row.push(other);
        usedStraight.add(other.id);
      }
    }
    row.sort((a, b) => a.absX - b.absX);
    rows.push({ type: 'straight', y: comp.absY, items: row });
  }

  rows.sort((a, b) => a.y - b.y);

  // Group rotated components by (r, rx, ry) group
  // Each unique (r, rx, ry) combination is a rotation group; within it, group by Y
  const rotGroups = new Map();
  for (const comp of rotated) {
    const key = `${round4(comp.r)},${round4(comp.rx)},${round4(comp.ry)}`;
    if (!rotGroups.has(key)) rotGroups.set(key, []);
    rotGroups.get(key).push(comp);
  }

  for (const [key, group] of rotGroups) {
    const [r, rx, ry] = key.split(',').map(Number);
    // Within this rotation group, further group by absY
    const byY = new Map();
    for (const comp of group) {
      const yKey = round4(comp.absY);
      if (!byY.has(yKey)) byY.set(yKey, []);
      byY.get(yKey).push(comp);
    }
    const sortedYs = [...byY.keys()].sort((a, b) => a - b);
    for (const yKey of sortedYs) {
      const rowItems = byY.get(yKey).sort((a, b) => a.absX - b.absX);
      rows.push({ type: 'rotated', y: yKey, r, rx, ry, items: rowItems });
    }
  }

  // Sort all rows: straight rows by Y, rotated rows interleaved by Y position
  rows.sort((a, b) => {
    const ay = a.type === 'rotated' ? a.ry : a.y;
    const by_ = b.type === 'rotated' ? b.ry : b.y;
    return ay - by_;
  });

  return rows;
}

export function serializeKLE(components, globalSettings) {
  const { split, switchType, borderSize } = globalSettings;

  const kleRows = [];

  // First row: metadata (optional, only if non-default settings)
  if (split || switchType !== 'cherrymx' || borderSize > 0) {
    const meta = {};
    if (split) meta.split = true;
    if (switchType !== 'cherrymx') meta.switchType = switchType;
    if (borderSize > 0) meta.notes = String(borderSize);
    kleRows.push([{ meta }]);
  }

  if (components.length === 0) {
    return JSON.stringify(kleRows, null, 2);
  }

  const rows = groupIntoRows(components);

  let prevR = 0;
  let prevRx = 0;
  let prevRy = 0;
  let globalCursorY = 0; // tracks the KLE cursor Y for straight rows

  for (const row of rows) {
    const kleRow = [];

    if (row.type === 'rotated') {
      // Emit a row with r/rx/ry header
      const props = {};
      if (!approxEqual(row.r, prevR)) { props.r = round4(row.r); prevR = row.r; }
      props.rx = round4(row.rx);
      props.ry = round4(row.ry);

      // y offset within the rotation group: absY - ry
      // The first component's absY relative to ry
      const firstComp = row.items[0];
      const yInGroup = round4(firstComp.absY - row.ry);
      if (!approxEqual(yInGroup, 0)) props.y = yInGroup;

      // x offset: absX - rx for the first component
      const xInGroup = round4(firstComp.absX - row.rx);
      if (!approxEqual(xInGroup, 0)) props.x = xInGroup;

      // Add component-specific properties for first item
      addCompProps(props, firstComp);
      kleRow.push(props);
      kleRow.push(firstComp.label || firstComp.p || getDefaultLabel(firstComp.type));

      // Remaining components in row — r is already set in the row header, never repeat it
      let cursorX = firstComp.absX + firstComp.w;
      for (const comp of row.items.slice(1)) {
        const p = {};
        const xDelta = round4(comp.absX - cursorX);
        if (!approxEqual(xDelta, 0)) p.x = xDelta;
        addCompProps(p, comp, /* skipR */ true);
        if (Object.keys(p).length > 0) kleRow.push(p);
        kleRow.push(comp.label || comp.p || getDefaultLabel(comp.type));
        cursorX = comp.absX + comp.w;
      }

      prevRx = row.rx;
      prevRy = row.ry;
    } else {
      // Straight row
      // Compute y delta from the global cursor
      const yDelta = round4(row.y - globalCursorY);

      let cursorX = 0;
      let isFirst = true;

      for (const comp of row.items) {
        const p = {};

        if (isFirst) {
          // y offset for the row
          if (!approxEqual(yDelta, 0)) p.y = yDelta;
          // Reset rotation if it was set
          if (!approxEqual(prevR, 0)) { p.r = 0; prevR = 0; }
          if (!approxEqual(prevRx, 0)) { p.rx = 0; prevRx = 0; }
          if (!approxEqual(prevRy, 0)) { p.ry = 0; prevRy = 0; }
        }

        const xDelta = round4(comp.absX - cursorX);
        if (!approxEqual(xDelta, 0)) p.x = xDelta;
        addCompProps(p, comp);

        if (Object.keys(p).length > 0) kleRow.push(p);
        kleRow.push(comp.label || comp.p || getDefaultLabel(comp.type));
        cursorX = comp.absX + comp.w;
        isFirst = false;
      }

      globalCursorY = row.y + 1; // advance by default row height
    }

    kleRows.push(kleRow);
  }

  return JSON.stringify(kleRows, null, 2);
}

function addCompProps(p, comp, skipR = false) {
  const def = COMPONENTS[comp.type];
  if (def.smValue && def.smValue !== 'cherry') {
    p.sm = def.smValue;
  }
  if (!approxEqual(comp.w, 1)) p.w = round4(comp.w);
  if (!approxEqual(comp.h, 1)) p.h = round4(comp.h);
  if (!skipR && !approxEqual(comp.r, 0) && !('r' in p)) {
    p.r = round4(comp.r);
  }
}

function getDefaultLabel(type) {
  const abbrevs = {
    cherry: '', kailhchoc: '', arduino: 'Arduino', trrs: 'trrs',
    pinplate: 'PPlate', pinpcb: 'PinPcb', pinb2t: 'PB2T',
    hole: 'Hole', platetext: 'Text',
    cameramount_selftap: 'Mount', cameramount_heatset: 'Mount', tiltleg: 'Leg',
  };
  return abbrevs[type] || '';
}
