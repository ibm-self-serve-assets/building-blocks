// ─────────────────────────────────────────────────────────────────────────────
// Six plant profiles. Each one is a different factory: its own product, process,
// station layout, robot colour, conveyor and lighting.
//
// Coordinates are metres in the part's frame: x along the belt, z across it
// (far side negative), y up from the belt surface. Items are built with their
// origin at the bottom centre.
//
// robots[i] is driven by site.robots[i] from the backend (same order).
// side: −1 = far side of the belt, +1 = near (camera) side.
// ─────────────────────────────────────────────────────────────────────────────
import * as THREE from 'three';

// Pin a site to a plant here. Unpinned sites get the remaining plants in the order the backend lists them.
// (ATL, AUS, LOU, STL and SEA are the browser-simulation plants; harmless if your backend uses other IDs.)
export const SITE_PROFILE = {
  DET: 'automotive',
  ATL: 'battery',
  AUS: 'electronics',
  LOU: 'appliance',
  STL: 'beverage',
  SEA: 'aerospace',
};

// open-bottom carton / sleeve
function carton(w, h, d, { color = '#b98a5a', tape = true, band = null } = {}) {
  return {
    w, h, d,
    make(k) {
      const g = k.group();
      const m = k.paint(color, 0.85);
      k.add(k.box(w, 0.02, d), m, g, [0, h - 0.01, 0]);
      [-1, 1].forEach((s) => {
        k.add(k.box(w, h, 0.02), m, g, [0, h / 2, s * (d / 2 - 0.01)]);
        k.add(k.box(0.02, h, d - 0.04), m, g, [s * (w / 2 - 0.01), h / 2, 0]);
        if (band) k.add(k.box(w * 0.8, 0.09, 0.004), k.paint(band, 0.5), g, [0, h * 0.62, s * (d / 2 + 0.002)]);
      });
      if (tape) k.add(k.box(w + 0.01, 0.004, 0.1), k.paint('#e3cf9e', 0.6), g, [0, h + 0.002, 0]);
      return g;
    },
  };
}

/* ───────────────────────── 1 · Automotive body shop ───────────────────────── */
const weldGrey = '#6b7785';
const automotive = {
  id: 'automotive',
  name: 'Automotive body shop',
  line: 'Body-in-white subframe line',
  theme: {
    bg: '#0b1016', floor: '#1b222c', grid: '#2a3442', lane: '#fbbf24',
    robot: '#ff7a1a', shell: '#ff7a1a', joint: '#2b2f36', accent: '#ffb057',
    conveyor: '#353b44', rail: '#9aa4ae', belt: '#b5bec8', beltStyle: 'roller',
    hood: '#2d333c', feeder: '#2b313a', frame: '#11161d', strip: '#ffe2bf', sun: '#ffe9d1', fill: '#ff9f43',
    fence: true,
  },
  stations: [-7.5, -1.5, 4.5],             // three cells, two robots each
  product: {
    baseTop: 0.2, length: 1.2,
    base(k, g) {
      k.add(k.box(1.2, 0.08, 0.78), k.metal('#8f9aa6', 0.4), g, [0, 0.04, 0]);
      [-0.3, 0.3].forEach((z) => k.add(k.box(1.15, 0.12, 0.09), k.metal('#6f7b88', 0.35), g, [0, 0.14, z]));
    },
    items: {
      xmem: { w: 0.1, h: 0.12, d: 0.51, make(k) { const g = k.group(); k.add(k.box(0.1, 0.12, 0.51), k.metal('#7d8896', 0.35), g, [0, 0.06, 0]); return g; } },
    },
    features: {
      seamFar: { kind: 'bead', from: [-0.52, 0.095, -0.36], to: [0.52, 0.095, -0.36], size: [0.03, 0.03], color: weldGrey, hot: true },
      seamNear: { kind: 'bead', from: [-0.52, 0.095, 0.36], to: [0.52, 0.095, 0.36], size: [0.03, 0.03], color: weldGrey, hot: true },
      xmemA: { kind: 'item', item: 'xmem', at: [-0.32, 0.08, 0] },
      xmemB: { kind: 'item', item: 'xmem', at: [0.32, 0.08, 0] },
      jointAF: { kind: 'bead', from: [-0.39, 0.2125, -0.238], to: [-0.25, 0.2125, -0.238], size: [0.025, 0.025], color: weldGrey, hot: true },
      jointBF: { kind: 'bead', from: [0.25, 0.2125, -0.238], to: [0.39, 0.2125, -0.238], size: [0.025, 0.025], color: weldGrey, hot: true },
      jointAN: { kind: 'bead', from: [-0.39, 0.2125, 0.238], to: [-0.25, 0.2125, 0.238], size: [0.025, 0.025], color: weldGrey, hot: true },
      jointBN: { kind: 'bead', from: [0.39, 0.2125, 0.238], to: [0.25, 0.2125, 0.238], size: [0.025, 0.025], color: weldGrey, hot: true },
      qc: { kind: 'status', at: [0.56, 0.115, 0] },
    },
  },
  robots: [
    { station: 0, side: -1, task: 'Seam weld', program: { kind: 'bead', tool: 'torch', features: ['seamFar'] } },
    { station: 0, side: 1, task: 'Seam weld', program: { kind: 'bead', tool: 'torch', features: ['seamNear'] } },
    { station: 1, side: -1, task: 'Load cross-member', program: { kind: 'place', feature: 'xmemA', feeder: { dx: -1.3, dz: 1.45 } } },
    { station: 1, side: 1, task: 'Load cross-member', program: { kind: 'place', feature: 'xmemB', feeder: { dx: 1.3, dz: 1.45 } } },
    { station: 2, side: -1, task: 'Joint weld', program: { kind: 'bead', tool: 'torch', features: ['jointAF', 'jointBF'] } },
    { station: 2, side: 1, task: 'Joint weld', program: { kind: 'bead', tool: 'torch', features: ['jointBN', 'jointAN'] } },
  ],
};

/* ───────────────────────── 2 · EV battery modules ───────────────────────── */
const battery = {
  id: 'battery',
  name: 'EV battery plant',
  line: 'Battery module line',
  theme: {
    bg: '#06140f', floor: '#14261f', grid: '#1e3a30', lane: '#34d399',
    robot: '#eef2f6', shell: '#eef2f6', joint: '#1f2937', accent: '#22d3ee',
    conveyor: '#25323a', rail: '#9fb3bf', belt: '#14201c', cleat: '#2c4a40', beltStyle: 'belt',
    hood: '#22332d', feeder: '#1f2f2a', frame: '#0b1a16', strip: '#e6fbff', sun: '#eaf6ff', fill: '#5eead4',
  },
  product: {
    baseTop: 0.17, length: 1.16,
    base(k, g) {
      const wall = k.paint('#4b5563', 0.5);
      k.add(k.box(1.16, 0.05, 0.72), k.paint('#3a4048', 0.55), g, [0, 0.025, 0]);
      [-1, 1].forEach((s) => {
        k.add(k.box(1.16, 0.12, 0.03), wall, g, [0, 0.11, s * 0.345]);
        k.add(k.box(0.03, 0.12, 0.66), wall, g, [s * 0.565, 0.11, 0]);
      });
    },
    items: {
      cells: {
        w: 0.46, h: 0.26, d: 0.6,
        make(k) {
          const g = k.group();
          [-0.1725, -0.0575, 0.0575, 0.1725].forEach((x, i) => k.add(k.box(0.105, 0.26, 0.6), k.paint(i % 2 ? '#1e40af' : '#2563eb', 0.35), g, [x, 0.13, 0]));
          return g;
        },
      },
      busbar: { w: 0.92, h: 0.02, d: 0.12, make(k) { const g = k.group(); k.add(k.box(0.92, 0.02, 0.12), k.metal('#c27c3e', 0.3), g, [0, 0.01, 0]); return g; } },
    },
    features: {
      paste1: { kind: 'bead', from: [-0.46, 0.062, -0.2], to: [0.46, 0.062, -0.2], size: [0.024, 0.05], color: '#c9ced6' },
      paste2: { kind: 'bead', from: [0.46, 0.062, 0], to: [-0.46, 0.062, 0], size: [0.024, 0.05], color: '#c9ced6' },
      paste3: { kind: 'bead', from: [-0.46, 0.062, 0.2], to: [0.46, 0.062, 0.2], size: [0.024, 0.05], color: '#c9ced6' },
      cellsA: { kind: 'item', item: 'cells', at: [-0.235, 0.05, 0] },
      cellsB: { kind: 'item', item: 'cells', at: [0.235, 0.05, 0] },
      busbar: { kind: 'item', item: 'busbar', at: [0, 0.31, 0] },
      bolts: { kind: 'points', style: 'bolt', points: [[-0.38, 0.33, 0], [-0.13, 0.33, 0], [0.13, 0.33, 0], [0.38, 0.33, 0]] },
      eol: { kind: 'status', at: [0.565, 0.205, 0] },
    },
  },
  robots: [
    { station: 0, side: -1, task: 'Dispense thermal paste', program: { kind: 'bead', tool: 'glue', features: ['paste1', 'paste2', 'paste3'] } },
    { station: 1, side: -1, task: 'Place cell stack', program: { kind: 'place', feature: 'cellsA', feeder: { dx: 1.3, dz: 1.5 } } },
    { station: 2, side: -1, task: 'Place cell stack', program: { kind: 'place', feature: 'cellsB', feeder: { dx: 1.3, dz: 1.5 } } },
    { station: 3, side: 1, task: 'Place busbar', program: { kind: 'place', feature: 'busbar', feeder: { dx: 1.35, dz: 1.45 } } },
    { station: 4, side: 1, task: 'Bolt busbar', program: { kind: 'points', tool: 'driver', feature: 'bolts' } },
    { station: 5, side: 1, task: 'End-of-line test', program: { kind: 'scan', feature: 'eol' } },
  ],
};

/* ───────────────────────── 3 · Electronics assembly ───────────────────────── */
const electronics = {
  id: 'electronics',
  name: 'Electronics assembly',
  line: 'Control-unit (ECU) line',
  theme: {
    bg: '#090c18', floor: '#191f30', grid: '#283152', lane: '#818cf8',
    robot: '#2f6bf0', shell: '#dfe6ee', joint: '#1e2433', accent: '#93c5fd',
    conveyor: '#2a3142', rail: '#aab4cc', belt: '#3a4560', cleat: '#55628a', beltStyle: 'slat',
    hood: '#262d40', feeder: '#232a3d', frame: '#0b1020', strip: '#e0e7ff', sun: '#eef2ff', fill: '#818cf8',
  },
  product: {
    baseTop: 0.05, length: 1.0,
    base(k, g) {
      k.add(k.box(1.0, 0.05, 0.7), k.paint('#2b2f36', 0.6), g, [0, 0.025, 0]);
      [[-0.46, -0.31], [0.46, -0.31], [-0.46, 0.31], [0.46, 0.31]].forEach(([x, z]) => k.add(k.cyl(0.015, 0.015, 0.04, 10), k.metal('#cbd5e1'), g, [x, 0.07, z]));
    },
    items: {
      pcb: {
        w: 0.82, h: 0.042, d: 0.56,
        make(k) {
          const g = k.group();
          k.add(k.box(0.82, 0.03, 0.56), k.paint('#1f7a4d', 0.5), g, [0, 0.015, 0]);
          [[0.1, -0.15], [0.22, -0.15], [0.1, 0.12], [0.25, 0.1], [0.32, -0.05]].forEach(([x, z]) => k.add(k.box(0.06, 0.012, 0.04), k.paint('#111827', 0.5), g, [x, 0.036, z]));
          k.add(k.box(0.06, 0.012, 0.3), k.metal('#d4a94a', 0.3), g, [-0.37, 0.036, 0]);
          return g;
        },
      },
      chip: {
        w: 0.2, h: 0.035, d: 0.2,
        make(k) { const g = k.group(); k.add(k.box(0.2, 0.03, 0.2), k.paint('#0f172a', 0.4), g, [0, 0.015, 0]); k.add(k.box(0.12, 0.005, 0.12), k.metal('#94a3b8', 0.3), g, [0, 0.0325, 0]); return g; },
      },
      heatsink: {
        w: 0.24, h: 0.14, d: 0.24,
        make(k) {
          const g = k.group(), al = k.metal('#b8c2cc', 0.35);
          k.add(k.box(0.24, 0.02, 0.24), al, g, [0, 0.01, 0]);
          for (let i = 0; i < 7; i++) k.add(k.box(0.012, 0.12, 0.24), al, g, [-0.108 + i * 0.036, 0.08, 0]);
          return g;
        },
      },
      cover: {
        w: 0.88, h: 0.24, d: 0.62,
        make(k) {
          const g = k.group();
          k.add(k.box(0.88, 0.24, 0.62), k.paint('#3d4a5c', 0.45), g, [0, 0.12, 0]);
          k.add(k.box(0.3, 0.004, 0.18), k.paint('#e5e7eb', 0.6), g, [0.2, 0.242, 0.12]);
          for (let i = 0; i < 5; i++) k.add(k.box(0.04, 0.004, 0.3), k.paint('#1f2937', 0.7), g, [-0.32 + i * 0.07, 0.242, -0.05]);
          return g;
        },
      },
    },
    features: {
      pcb: { kind: 'item', item: 'pcb', at: [0, 0.05, 0] },
      chip: { kind: 'item', item: 'chip', at: [-0.18, 0.08, 0] },
      heatsink: { kind: 'item', item: 'heatsink', at: [-0.18, 0.115, 0] },
      screws: { kind: 'points', style: 'screw', points: [[-0.36, 0.08, -0.23], [0.36, 0.08, -0.23], [0.36, 0.08, 0.23], [-0.36, 0.08, 0.23]] },
      aoi: { kind: 'status', at: [0, 0.085, 0.335] },
      cover: { kind: 'item', item: 'cover', at: [0, 0.05, 0] },
    },
  },
  robots: [
    { station: 0, side: -1, task: 'Load PCB', program: { kind: 'place', feature: 'pcb', feeder: { dx: 1.3, dz: 1.45 } } },
    { station: 1, side: -1, task: 'Place processor', program: { kind: 'place', feature: 'chip', feeder: { dx: 1.2, dz: 1.4 } } },
    { station: 2, side: -1, task: 'Fit heatsink', program: { kind: 'place', feature: 'heatsink', feeder: { dx: 1.2, dz: 1.4 } } },
    { station: 3, side: -1, task: 'Fasten PCB', program: { kind: 'points', tool: 'driver', feature: 'screws' } },
    { station: 4, side: -1, task: 'AOI inspection', program: { kind: 'scan', feature: 'aoi' } },
    { station: 5, side: -1, task: 'Fit cover', program: { kind: 'place', feature: 'cover', feeder: { dx: 1.35, dz: 1.45 } } },
  ],
};

/* ───────────────────────── 4 · Appliance assembly ───────────────────────── */
const appliance = {
  id: 'appliance',
  name: 'Appliance plant',
  line: 'Washer final-assembly line',
  theme: {
    bg: '#0f1216', floor: '#22272e', grid: '#333b46', lane: '#facc15',
    robot: '#f2c418', shell: '#f2c418', joint: '#2a2d33', accent: '#fde68a',
    conveyor: '#2f3640', rail: '#aeb6c0', belt: '#1d232b', cleat: '#3a4452', beltStyle: 'belt',
    hood: '#2b323b', feeder: '#2a3038', frame: '#12161b', strip: '#fff6d8', sun: '#fff7e6', fill: '#fbbf24',
  },
  product: {
    baseTop: 0.06, length: 1.0,
    base(k, g) { k.add(k.box(1.0, 0.06, 0.66), k.metal('#a0a8b2', 0.4), g, [0, 0.03, 0]); },
    items: {
      motor: {
        w: 0.36, h: 0.25, d: 0.36, grip: [0.075, 0.075],
        make(k) {
          const g = k.group();
          k.add(k.box(0.36, 0.03, 0.36), k.paint('#4b5563', 0.5), g, [0, 0.015, 0]);
          k.add(k.cyl(0.14, 0.14, 0.22, 24), k.paint('#374151', 0.45), g, [0, 0.14, 0]);
          k.add(k.cyl(0.05, 0.05, 0.03, 16), k.metal('#cbd5e1'), g, [0, 0.265, 0]);
          return g;
        },
      },
      housing: {
        w: 0.92, h: 0.4, d: 0.58,
        make(k) {
          const g = k.group();
          k.paintable(k.add(k.box(0.92, 0.4, 0.58), k.paint('#e8ecf0', 0.4), g, [0, 0.2, 0]));
          k.add(k.cyl(0.13, 0.13, 0.012, 32), k.paint('#1f2937', 0.2), g, [-0.15, 0.2, 0.292], [Math.PI / 2, 0, 0]);
          k.add(k.torus(0.13, 0.016, 10, 36), k.metal('#c7cdd4', 0.25), g, [-0.15, 0.2, 0.296]);
          k.add(k.box(0.28, 0.05, 0.012), k.paint('#111827', 0.5), g, [0.25, 0.33, 0.292]);
          return g;
        },
      },
      carton: carton(1.12, 0.56, 0.78),
    },
    features: {
      motor: { kind: 'item', item: 'motor', at: [0, 0.06, 0] },
      bolts: { kind: 'points', style: 'bolt', points: [[-0.15, 0.09, -0.15], [0.15, 0.09, -0.15], [0.15, 0.09, 0.15], [-0.15, 0.09, 0.15]] },
      housing: { kind: 'item', item: 'housing', at: [0, 0.06, 0] },
      coat: { kind: 'paint', color: '#3f6f9f' },
      qc: { kind: 'status', at: [0.47, 0.095, 0.3] },
      carton: { kind: 'item', item: 'carton', at: [0, 0, 0] },
    },
  },
  robots: [
    { station: 0, side: -1, task: 'Load motor', program: { kind: 'place', feature: 'motor', feeder: { dx: 1.3, dz: 1.45 } } },
    { station: 1, side: 1, task: 'Bolt motor', program: { kind: 'points', tool: 'driver', feature: 'bolts' } },
    { station: 2, side: -1, task: 'Fit cabinet', program: { kind: 'place', feature: 'housing', feeder: { dx: 1.35, dz: 1.5 } } },
    { station: 3, side: 1, task: 'Powder coat', program: { kind: 'spray', feature: 'coat', passes: [-0.2, 0, 0.2], span: 0.5 } },
    { station: 4, side: -1, task: 'Final inspection', program: { kind: 'scan', feature: 'qc' } },
    { station: 5, side: 1, task: 'Box unit', program: { kind: 'place', feature: 'carton', feeder: { dx: 1.45, dz: 1.55 } } },
  ],
};

/* ───────────────────────── 5 · Food & beverage case packing ───────────────────────── */
const bottleGrid = [];
for (const x of [-0.075, 0.075]) for (const z of [-0.225, -0.075, 0.075, 0.225]) bottleGrid.push([x, z]);
const beverage = {
  id: 'beverage',
  name: 'Beverage bottling',
  line: 'Case-packing line',
  theme: {
    bg: '#0b1618', floor: '#26343a', grid: '#33464e', lane: '#e2e8f0',
    robot: '#14b8a6', shell: '#e2e8f0', joint: '#334155', accent: '#5eead4',
    conveyor: '#9aa5ad', rail: '#d5dde3', belt: '#d6dde2', cleat: '#b4bec6', beltStyle: 'slat',
    hood: '#8b979f', feeder: '#7b878f', frame: '#14232a', strip: '#f0fdfa', sun: '#f0fdfa', fill: '#2dd4bf',
  },
  product: {
    baseTop: 0.1, length: 0.76,
    base(k, g) {
      const m = k.paint('#b98a5a', 0.85);
      k.add(k.box(0.76, 0.02, 0.66), m, g, [0, 0.01, 0]);
      [-1, 1].forEach((s) => {
        k.add(k.box(0.76, 0.1, 0.015), m, g, [0, 0.05, s * 0.3225]);
        k.add(k.box(0.015, 0.1, 0.63), m, g, [s * 0.3725, 0.05, 0]);
      });
    },
    items: {
      bottles: {
        w: 0.274, h: 0.335, d: 0.574, grip: [0.075, 0.225],
        make(k) {
          const g = k.group();
          const glass = k.mat('bottle-glass', () => new THREE.MeshStandardMaterial({ color: '#7a3e12', metalness: 0.1, roughness: 0.15 }));
          const geo = k.geo('bottle', () => new THREE.LatheGeometry(
            [[0, 0], [0.058, 0], [0.062, 0.012], [0.062, 0.2], [0.05, 0.24], [0.024, 0.28], [0.022, 0.31], [0, 0.31]].map(([r, y]) => new THREE.Vector2(r, y)), 18));
          const bottles = new THREE.InstancedMesh(geo, glass, bottleGrid.length);
          const caps = new THREE.InstancedMesh(k.cyl(0.026, 0.026, 0.025, 12), k.paint('#dc2626', 0.4), bottleGrid.length);
          const m = new THREE.Matrix4();
          bottleGrid.forEach(([x, z], i) => {
            bottles.setMatrixAt(i, m.makeTranslation(x, 0, z));
            caps.setMatrixAt(i, m.makeTranslation(x, 0.3225, z));
          });
          [bottles, caps].forEach((o) => { o.castShadow = true; o.receiveShadow = true; o.frustumCulled = false; g.add(o); });
          return g;
        },
      },
      sleeve: carton(0.8, 0.4, 0.7, { tape: false, band: '#0f766e' }),
      label: {
        w: 0.26, h: 0.006, d: 0.16, grip: [0.06, 0.04],
        make(k) {
          const g = k.group();
          k.add(k.box(0.26, 0.006, 0.16), k.paint('#f8fafc', 0.6), g, [0, 0.003, 0]);
          for (let i = 0; i < 9; i++) k.add(k.box(0.006 + (i % 3) * 0.004, 0.002, 0.07), k.paint('#111827', 0.7), g, [-0.08 + i * 0.016, 0.007, -0.02]);
          return g;
        },
      },
    },
    features: {
      packA: { kind: 'item', item: 'bottles', at: [-0.16, 0.02, 0] },
      packB: { kind: 'item', item: 'bottles', at: [0.16, 0.02, 0] },
      inspect: { kind: 'status', at: [0.3, 0.135, 0.29] },
      sleeve: { kind: 'item', item: 'sleeve', at: [0, 0, 0] },
      tape: { kind: 'bead', from: [-0.4, 0.403, 0], to: [0.4, 0.403, 0], size: [0.006, 0.09], color: '#d9c08a' },
      label: { kind: 'item', item: 'label', at: [-0.18, 0.4, 0.2] },
    },
  },
  robots: [
    { station: 0, side: 1, task: 'Load bottle pack', program: { kind: 'place', feature: 'packA', feeder: { dx: 1.3, dz: 1.45 } } },
    { station: 1, side: -1, task: 'Load bottle pack', program: { kind: 'place', feature: 'packB', feeder: { dx: 1.3, dz: 1.45 } } },
    { station: 2, side: 1, task: 'Fill-level vision', program: { kind: 'scan', feature: 'inspect' } },
    { station: 3, side: -1, task: 'Sleeve case', program: { kind: 'place', feature: 'sleeve', feeder: { dx: 1.35, dz: 1.5 } } },
    { station: 4, side: 1, task: 'Tape seal', program: { kind: 'bead', tool: 'tape', features: ['tape'] } },
    { station: 5, side: -1, task: 'Apply label', program: { kind: 'place', feature: 'label', feeder: { dx: 1.2, dz: 1.4 } } },
  ],
};

/* ───────────────────────── 6 · Aerospace structures ───────────────────────── */
const rivetRows = [
  [-0.45, 0.097, 0.217], [-0.15, 0.097, 0.217], [0.15, 0.097, 0.217], [0.45, 0.097, 0.217],
  [0.45, 0.097, -0.217], [0.15, 0.097, -0.217], [-0.15, 0.097, -0.217], [-0.45, 0.097, -0.217],
];
const aerospace = {
  id: 'aerospace',
  name: 'Aerospace structures',
  line: 'Wing-panel riveting line',
  theme: {
    bg: '#0d1012', floor: '#24282c', grid: '#353b41', lane: '#a3e635',
    robot: '#5b6470', shell: '#d1d5db', joint: '#1f2328', accent: '#a3e635',
    conveyor: '#2c3136', rail: '#a1a8b0', belt: '#1b1f23', cleat: '#3a4048', beltStyle: 'belt',
    hood: '#3a3f2a', feeder: '#2a2f33', frame: '#101315', strip: '#f1f5e8', sun: '#f5f7f0', fill: '#bef264',
    fence: true,
  },
  product: {
    baseTop: 0.085, length: 1.24,
    base(k, g) {
      [-0.5, 0.5].forEach((x) => k.add(k.box(0.1, 0.06, 0.7), k.paint('#30363d', 0.6), g, [x, 0.03, 0]));
      k.paintable(k.add(k.box(1.24, 0.025, 0.76), k.metal('#c3cad3', 0.35), g, [0, 0.0725, 0]));
    },
    items: {
      stringer: {
        w: 1.16, h: 0.072, d: 0.1, grip: [0.3, 0],
        make(k) {
          const g = k.group(), m = k.metal('#b8c0ca', 0.35);
          k.paintable(k.add(k.box(1.16, 0.012, 0.1), m, g, [0, 0.006, 0]));
          k.paintable(k.add(k.box(1.16, 0.06, 0.025), m, g, [0, 0.042, 0]));
          k.paintable(k.add(k.box(1.16, 0.012, 0.05), m, g, [0, 0.066, 0]));
          return g;
        },
      },
    },
    features: {
      seal1: { kind: 'bead', from: [-0.56, 0.093, 0.18], to: [0.56, 0.093, 0.18], size: [0.016, 0.05], color: '#4b5563' },
      seal2: { kind: 'bead', from: [0.56, 0.093, -0.18], to: [-0.56, 0.093, -0.18], size: [0.016, 0.05], color: '#4b5563' },
      stringerA: { kind: 'item', item: 'stringer', at: [0, 0.085, 0.18] },
      stringerB: { kind: 'item', item: 'stringer', at: [0, 0.085, -0.18] },
      holes: { kind: 'points', style: 'hole', points: rivetRows },
      rivets: { kind: 'points', style: 'rivet', points: rivetRows },
      primer: { kind: 'paint', color: '#b5c449' },
      qc: { kind: 'status', at: [0.58, 0.12, 0.33] },
    },
  },
  robots: [
    { station: 0, side: 1, task: 'Apply sealant', program: { kind: 'bead', tool: 'glue', features: ['seal1', 'seal2'] } },
    { station: 1, side: 1, task: 'Load stringer', program: { kind: 'place', feature: 'stringerA', feeder: { dx: 1.45, dz: 1.45 } } },
    { station: 2, side: 1, task: 'Load stringer', program: { kind: 'place', feature: 'stringerB', feeder: { dx: 1.45, dz: 1.45 } } },
    { station: 3, side: -1, task: 'Drill', program: { kind: 'points', tool: 'drill', feature: 'holes' } },
    { station: 4, side: -1, task: 'Rivet', program: { kind: 'points', tool: 'riveter', feature: 'rivets' } },
    { station: 5, side: -1, task: 'Prime', program: { kind: 'spray', feature: 'primer', passes: [-0.25, 0, 0.25], span: 0.6 } },
  ],
};

export const PROFILES = [automotive, battery, electronics, appliance, beverage, aerospace];
const BY_ID = Object.fromEntries(PROFILES.map((p) => [p.id, p]));

const hash = (s) => [...String(s)].reduce((h, c) => (Math.imul(h, 31) + c.charCodeAt(0)) >>> 0, 7);

// Pinned sites get their plant; every other site gets a different unpinned plant, in list order.
export function profileForSite(site, sites = []) {
  if (!site) return PROFILES[0];
  const pinned = SITE_PROFILE[site.id];
  if (pinned && BY_ID[pinned]) return BY_ID[pinned];
  // only plants pinned to sites that are actually in this list are taken
  const used = new Set((sites.length ? sites : [site]).map((s) => SITE_PROFILE[s.id]).filter(Boolean));
  const free = PROFILES.filter((p) => !used.has(p.id));
  const pool = free.length ? free : PROFILES;
  const unpinned = (sites.length ? sites : [site]).filter((s) => !SITE_PROFILE[s.id]);
  const i = unpinned.findIndex((s) => s.id === site.id);
  return pool[(i >= 0 ? i : hash(site.id)) % pool.length];
}
