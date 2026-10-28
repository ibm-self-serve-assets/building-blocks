// ─────────────────────────────────────────────────────────────────────────────
// Plant simulation engine for the Factory Pulse digital twin.
//
// Pure three.js (no React). createPlant(profile) builds one production line —
// robots, conveyor, feeders and parts — and returns an object you drive with
// plant.update(dt, control) every frame.
//
//   control = {
//     paused: boolean,            // feed hold: everything ramps to a stop
//     rate:   number,             // line speed multiplier (demand surge)
//     robots: [{                  // one entry per robot, same order as profile.robots
//       issue: null | 'bearing' | 'thermal' | 'strain' | 'quality' | 'stopped' | 'fault',
//       severity: 0..1,
//       trip: boolean,            // true → protective stop after the symptom shows
//       defectRate: 0..1,         // quality drift: chance an operation goes wrong
//     }],
//   }
//
// Line logic: the belt indexes one station only when every robot has finished
// its program. A tripped robot freezes in place, so its station never reports
// done and the conveyor stays held (and ramps down if it was moving).
// ─────────────────────────────────────────────────────────────────────────────
import * as THREE from 'three';

export const BELT_TOP = 0.57;      // belt surface height (m)
export const PITCH = 3.0;          // one index move = one station
export const ROBOT_Z = 2.0;        // robot bases sit 2 m either side of the belt centre
export const FEED_TOP = 0.55;      // feeder table height
const SLOT_X0 = -13.5;             // slot k sits at SLOT_X0 + k·PITCH
const NUM_SLOTS = 9;               // −13.5 … 10.5 (13.5 is inside the outfeed hood)
const INDEX_TIME = 1.4;
const SETTLE = 0.2;
const BELT_LEN = 29.2;

// Arm dimensions. The meshes and the IK both read these, so the hinges you see are the ones that move.
const BASE_H = 0.3, H_S = 1.2, L1 = 1.4, L2A = 0.66, L2B = 0.49, L2 = L2A + L2B, FL = 0.16, TIP = 0.34, D = FL + TIP;
export const ARM = { BASE_H, H_S, L1, L2, FL, TIP, D };

const POINT_STYLE = {
  screw: { h: 0.016, geo: (k) => k.cyl(0.026, 0.026, 0.016, 12), mat: (k) => k.metal('#e5e7eb', 0.2) },
  bolt: { h: 0.02, geo: (k) => k.cyl(0.03, 0.03, 0.02, 6), mat: (k) => k.metal('#cbd5e1', 0.25) },
  rivet: { h: 0.01, geo: (k) => k.cyl(0.014, 0.02, 0.01, 10), mat: (k) => k.metal('#d1d5db', 0.2) },
  hole: { h: 0.003, geo: (k) => k.cyl(0.011, 0.011, 0.003, 10), mat: (k) => k.paint('#05080c', 0.9) },
};
const BEAD_GAP = { torch: 0.02, glue: 0.015, tape: 0.004 };   // tool tip height above a bead
const BEAD_SPEED = { torch: 0.9, glue: 0.8, tape: 1.0 };       // m/s along a seam

const DEFAULT_THEME = {
  bg: '#071827', floor: '#16293b', grid: '#1a3550', lane: '#19d2e6',
  robot: '#f97316', shell: '#d5dde5', joint: '#2b3644', accent: '#f97316',
  conveyor: '#2a3e52', rail: '#b2c2ce', belt: '#1a2635', cleat: '#2c4459', beltStyle: 'belt',
  hood: '#24384c', feeder: '#22364a', frame: '#0c1c2d', strip: '#cfe8ff',
  sun: '#f0f4ff', sunIntensity: 2.6, ambient: 0.7, hemiSky: '#c8e0ff', hemiGround: '#1c2b3d', hemi: 1.05,
  fill: '#ffa953', fence: false,
};

const C = {
  red: new THREE.Color('#ff2a1a'), heat: new THREE.Color('#ff4a12'), hotBase: new THREE.Color('#2a0c04'), amber: new THREE.Color('#ffb020'),
  green: '#24d7b4', blue: '#3b82f6', yellow: '#f1c21b', redHex: '#ff3b30',
};

/* ───────────────────────────── helpers ───────────────────────────── */
const V3 = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const minJerk = (u) => { u = clamp(u, 0, 1); return u * u * u * (10 + u * (-15 + 6 * u)); };
const approach = (v, target, rate, dt) => (v < target ? Math.min(target, v + rate * dt) : Math.max(target, v - rate * dt));
function seeded(seed) {
  let s = seed >>> 0 || 1;
  return () => { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
}

// Geometry/material factory with caching, so 9 parts × N items share GPU buffers.
function makeKit() {
  const geos = new Map(), mats = new Map();
  const memo = (map, key, make) => { if (!map.has(key)) map.set(key, make()); return map.get(key); };
  const add = (geo, mat, parent, pos = [0, 0, 0], rot = [0, 0, 0]) => {
    const m = new THREE.Mesh(geo, mat);
    m.position.set(pos[0], pos[1], pos[2]);
    m.rotation.set(rot[0], rot[1], rot[2]);
    m.castShadow = true;
    m.receiveShadow = true;
    if (parent) parent.add(m);
    return m;
  };
  const kit = {
    add,
    group(parent, pos = [0, 0, 0]) {
      const g = new THREE.Group();
      g.position.set(pos[0], pos[1], pos[2]);
      if (parent) parent.add(g);
      return g;
    },
    geo: (key, make) => memo(geos, key, make),
    mat: (key, make) => memo(mats, key, make),
    box: (x, y, z) => memo(geos, `box|${x}|${y}|${z}`, () => new THREE.BoxGeometry(x, y, z)),
    cyl: (rt, rb, h, s = 20) => memo(geos, `cyl|${rt}|${rb}|${h}|${s}`, () => new THREE.CylinderGeometry(rt, rb, h, s)),
    sphere: (r, s = 12) => memo(geos, `sph|${r}|${s}`, () => new THREE.SphereGeometry(r, s, s)),
    plane: (x, y) => memo(geos, `pln|${x}|${y}`, () => new THREE.PlaneGeometry(x, y)),
    ring: (a, b, s = 40) => memo(geos, `ring|${a}|${b}|${s}`, () => new THREE.RingGeometry(a, b, s)),
    torus: (r, t, rs = 8, ts = 32) => memo(geos, `tor|${r}|${t}|${rs}|${ts}`, () => new THREE.TorusGeometry(r, t, rs, ts)),
    paint: (c, r = 0.45) => memo(mats, `paint|${c}|${r}`, () => new THREE.MeshStandardMaterial({ color: c, metalness: 0.25, roughness: r })),
    metal: (c, r = 0.3) => memo(mats, `metal|${c}|${r}`, () => new THREE.MeshStandardMaterial({ color: c, metalness: 0.85, roughness: r })),
    glow: (c, i = 1.5) => memo(mats, `glow|${c}|${i}`, () => new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: i, roughness: 0.4 })),
    flat: (c, o = 1) => memo(mats, `flat|${c}|${o}`, () => new THREE.MeshBasicMaterial({ color: c, transparent: o < 1, opacity: o, side: THREE.DoubleSide, depthWrite: o >= 1 })),
  };
  // cylinder lying along local X — every pitch joint uses one, so the visible hinge axis is the real axis
  kit.hub = (r, len, mat, parent, pos) => add(kit.cyl(r, r, len, 24), mat, parent, pos, [0, 0, Math.PI / 2]);
  kit.decal = (geo, mat, parent, pos) => { const m = add(geo, mat, parent, pos, [-Math.PI / 2, 0, 0]); m.castShadow = false; return m; };
  kit.paintable = (mesh) => { mesh.userData.paint = true; return mesh; };
  return kit;
}

function makeParticles(parent, { color, size, opacity, count }) {
  const pos = new Float32Array(count * 3).fill(-50);
  const vel = new Float32Array(count * 3);
  const life = new Float32Array(count);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const mat = new THREE.PointsMaterial({ color, size, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false });
  const points = new THREE.Points(geo, mat);
  points.frustumCulled = false;
  parent.add(points);
  let next = 0, alive = 0;
  return {
    material: mat,
    emit(p, n, fn) {
      for (let c = 0; c < n; c++) {
        const i = next++ % count, o = i * 3;
        pos[o] = p.x; pos[o + 1] = p.y; pos[o + 2] = p.z;
        const v = fn();
        vel[o] = v[0]; vel[o + 1] = v[1]; vel[o + 2] = v[2];
        life[i] = v[3];
      }
      alive = count;
    },
    update(dt, gravity, drag, floorY, bounce) {
      if (!alive) return;
      let any = 0;
      const k = Math.max(0, 1 - drag * dt);
      for (let i = 0; i < count; i++) {
        if (life[i] <= 0) continue;
        any++;
        const o = i * 3;
        life[i] -= dt;
        vel[o] *= k; vel[o + 2] *= k; vel[o + 1] = vel[o + 1] * k - gravity * dt;
        pos[o] += vel[o] * dt; pos[o + 1] += vel[o + 1] * dt; pos[o + 2] += vel[o + 2] * dt;
        if (pos[o + 1] < floorY) {
          pos[o + 1] = floorY;
          if (bounce) { vel[o + 1] *= -0.3; vel[o] *= 0.5; vel[o + 2] *= 0.5; } else { vel[o] = vel[o + 1] = vel[o + 2] = 0; }
        }
        if (life[i] <= 0) pos[o + 1] = -50;
      }
      alive = any;
      geo.attributes.position.needsUpdate = true;
    },
  };
}

/* ───────────────────────────── environment ───────────────────────────── */
function buildEnvironment(kit, T, root) {
  root.add(new THREE.AmbientLight(T.sun, T.ambient));
  root.add(new THREE.HemisphereLight(T.hemiSky, T.hemiGround, T.hemi));
  const sun = new THREE.DirectionalLight(T.sun, T.sunIntensity);
  sun.position.set(4, 14, 8);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -17, right: 17, top: 11, bottom: -11, near: 1, far: 45 });
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.02;
  root.add(sun);
  const fill = new THREE.PointLight(T.fill, 6, 14);
  fill.position.set(8, 5, 5);
  root.add(fill);

  const floor = kit.add(kit.plane(40, 24), kit.paint(T.floor, 0.9), root, [0, 0, 0], [-Math.PI / 2, 0, 0]);
  floor.castShadow = false;
  const grid = new THREE.GridHelper(40, 80, T.grid, T.grid);
  grid.position.y = 0.003;
  grid.material.transparent = true;
  grid.material.opacity = 0.45;
  root.add(grid);
  [-0.98, 0.98].forEach((z) => kit.decal(kit.plane(29, 0.06), kit.flat(T.lane, 0.35), root, [0, 0.005, z]));

  // building structure on the far side only, so nothing crosses the camera's view of the line
  const steel = kit.metal(T.frame, 0.45);
  [-12.6, -4.2, 4.2, 12.6].forEach((x) => kit.add(kit.box(0.24, 7.2, 0.24), steel, root, [x, 3.6, -5.2]));
  kit.add(kit.box(25.6, 0.26, 0.26), steel, root, [0, 7.2, -5.2]);
  kit.add(kit.box(25.6, 0.12, 0.12), steel, root, [0, 3.2, -5.2]);
  [-8, 0, 8].forEach((x) => {
    const l = new THREE.PointLight(T.strip, 14, 14);
    l.position.set(x, 6.6, 0);
    root.add(l);
  });

  if (T.fence) {     // safety fence behind the far-side robots
    const post = kit.paint('#f1c21b', 0.5);
    const mesh = kit.flat('#9fb3c8', 0.1);
    for (let x = -12; x <= 12.01; x += 2) kit.add(kit.box(0.08, 1.6, 0.08), post, root, [x, 0.8, -3.4]);
    for (let x = -11; x <= 11.01; x += 2) {
      const p = kit.add(kit.box(1.92, 1.35, 0.02), mesh, root, [x, 0.85, -3.4]);
      p.castShadow = false;
    }
    kit.add(kit.box(24.2, 0.05, 0.05), post, root, [0, 1.6, -3.4]);
  }
}

function buildConveyor(kit, T, root) {
  const roller = T.beltStyle === 'roller';
  kit.add(kit.box(BELT_LEN, roller ? 0.14 : 0.18, 1.5), kit.paint(T.conveyor, 0.4), root, [0, roller ? 0.38 : 0.42, 0]);
  [-0.7, 0.7].forEach((z) => kit.add(kit.box(BELT_LEN, 0.22, 0.1), kit.metal(T.rail, 0.25), root, [0, 0.54, z]));
  for (let x = -14.25; x <= 14.25; x += 1.5) [-0.55, 0.55].forEach((z) => kit.add(kit.box(0.1, 0.34, 0.14), kit.paint('#384c62'), root, [x, 0.17, z]));

  let update;
  if (roller) {
    const R = 0.05, SP = 0.25, xs = [];
    for (let x = -14.5; x <= 14.5 + 1e-6; x += SP) xs.push(x);
    const rollers = new THREE.InstancedMesh(kit.cyl(R, R, 1.26, 16), kit.metal(T.belt, 0.25), xs.length);
    rollers.castShadow = true;
    rollers.receiveShadow = true;
    rollers.frustumCulled = false;
    root.add(rollers);
    const m = new THREE.Matrix4(), q = new THREE.Quaternion(), qs = new THREE.Quaternion(), p = V3(), s = V3(1, 1, 1);
    const align = new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), Math.PI / 2);
    const zAxis = V3(0, 0, 1);
    let last = NaN;
    update = (beltPos) => {
      if (beltPos === last) return;
      last = beltPos;
      qs.setFromAxisAngle(zAxis, -beltPos / R);       // rollers turn as the load moves
      q.multiplyQuaternions(qs, align);
      xs.forEach((x, i) => { p.set(x, BELT_TOP - R, 0); m.compose(p, q, s); rollers.setMatrixAt(i, m); });
      rollers.instanceMatrix.needsUpdate = true;
    };
  } else {
    kit.add(kit.box(BELT_LEN, 0.06, 1.26), kit.paint(T.belt, 0.9), root, [0, 0.54, 0]);
    const slat = T.beltStyle === 'slat';
    const SP = slat ? 0.15 : 0.6, xs = [];
    for (let x = -14.4; x <= 14.4 - SP + 1e-6; x += SP) xs.push(x);
    const ticks = new THREE.InstancedMesh(kit.plane(slat ? 0.025 : 0.05, 1.2), kit.flat(T.cleat, 0.75), xs.length);
    const m = new THREE.Matrix4(), q = new THREE.Quaternion().setFromAxisAngle(V3(1, 0, 0), -Math.PI / 2), s = V3(1, 1, 1);
    xs.forEach((x, i) => { m.compose(V3(x, 0.573, 0), q, s); ticks.setMatrixAt(i, m); });
    ticks.frustumCulled = false;
    const holder = kit.group(root);
    holder.add(ticks);
    update = (beltPos) => { holder.position.x = ((beltPos % SP) + SP) % SP; };
  }

  // infeed / outfeed hoods hide where parts appear and leave; the band shows line state
  const band = new THREE.MeshStandardMaterial({ color: C.green, emissive: C.green, emissiveIntensity: 0.6 });
  [-1, 1].forEach((s) => {
    kit.add(kit.box(3.0, 1.2, 1.9), kit.paint(T.hood, 0.5), root, [s * 13.1, 1.1, 0]);
    const opening = kit.add(kit.plane(1.5, 0.75), kit.flat('#03070c'), root, [s * 11.595, 0.955, 0], [0, -s * Math.PI / 2, 0]);
    opening.castShadow = false;
    const b = kit.add(kit.box(0.06, 0.08, 1.92), band, root, [s * 11.62, 1.62, 0]);
    b.castShadow = false;
  });
  return { update, band };
}

/* ───────────────────────────── tools (all point along +Y, tip at y = TIP) ───────────────────────────── */
function buildTool(kit, T, def, j6, ctx) {
  const k = kit, P = def.program;
  const kind = P.kind === 'place' ? 'cups' : P.kind === 'scan' ? 'scanner' : P.kind === 'spray' ? 'sprayer' : P.tool;
  const dark = k.paint('#2f3b48', 0.5);
  k.add(k.cyl(0.055, 0.055, 0.08, 14), k.metal('#3b4654', 0.3), j6, [0, 0.04, 0]);   // tool changer plate
  const tool = { kind, update() {}, tipLocal: V3(0, TIP, 0) };

  if (kind === 'torch') {
    k.add(k.cyl(0.045, 0.055, 0.16, 14), dark, j6, [0, 0.16, 0]);
    k.add(k.cyl(0.03, 0.045, 0.06, 14), k.metal('#c08a4a', 0.3), j6, [0, 0.27, 0]);
    k.add(k.cyl(0.006, 0.014, 0.04, 8), k.metal('#e2e8f0', 0.2), j6, [0, 0.32, 0]);
    const arcMat = new THREE.MeshBasicMaterial({ color: '#fff6c8', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
    const arc = k.add(k.sphere(0.05, 12), arcMat, j6, [0, TIP + 0.01, 0]);
    arc.castShadow = false;
    tool.update = (on) => { arcMat.opacity = on ? 0.7 + Math.random() * 0.3 : 0; arc.scale.setScalar(on ? 0.7 + Math.random() * 0.7 : 1); };
  } else if (kind === 'glue') {
    k.add(k.cyl(0.05, 0.06, 0.14, 16), k.paint('#d9dee5', 0.4), j6, [0, 0.15, 0]);
    k.add(k.cyl(0.006, 0.03, 0.1, 12), k.metal('#9aa8b6'), j6, [0, 0.27, 0]);
    k.add(k.cyl(0.004, 0.004, 0.02, 8), k.metal('#e5e7eb'), j6, [0, 0.33, 0]);
    const dot = k.add(k.sphere(0.014, 10), new THREE.MeshBasicMaterial({ color: ctx.beadColor || '#cbd5e1' }), j6, [0, TIP, 0]);
    dot.castShadow = false;
    dot.visible = false;
    tool.update = (on) => { dot.visible = on; };
  } else if (kind === 'tape') {
    k.add(k.box(0.05, 0.16, 0.14), dark, j6, [0, 0.16, 0]);
    const roll = k.group(j6, [0, 0.27, 0]);
    k.add(k.torus(0.05, 0.02, 10, 24), k.paint('#d9c08a', 0.6), roll);
    k.add(k.cyl(0.02, 0.02, 0.11, 12), k.paint('#111827', 0.6), j6, [0, 0.32, 0], [Math.PI / 2, 0, 0]);
    tool.update = (on, dt) => { if (on) roll.rotation.z -= dt * 9; };
  } else if (kind === 'cups') {
    const it = ctx.item;
    const [cx, cz] = it.grip ?? [clamp(it.w / 2 - 0.07, 0.06, 0.3), clamp(it.d / 2 - 0.07, 0.05, 0.22)];
    k.add(k.box(2 * cx + 0.1, 0.03, 2 * cz + 0.1), dark, j6, [0, 0.1, 0]);
    const cupMat = new THREE.MeshStandardMaterial({ color: '#111827', roughness: 0.8, emissive: T.accent, emissiveIntensity: 0 });
    [[-cx, -cz], [cx, -cz], [-cx, cz], [cx, cz]].forEach(([x, z]) => {
      k.add(k.cyl(0.012, 0.012, 0.175, 8), k.metal('#94a3b8'), j6, [x, 0.2025, z]);
      k.add(k.cyl(0.045, 0.028, 0.05, 14), cupMat, j6, [x, 0.315, z]);
    });
    tool.update = (on) => { cupMat.emissiveIntensity = on ? 1.4 : 0; };
  } else if (kind === 'scanner') {
    k.add(k.box(0.16, 0.12, 0.3), k.paint('#1e293b', 0.4), j6, [0, 0.2, 0]);
    k.add(k.box(0.05, 0.01, 0.24), k.glow('#c4b5fd', 1.5), j6, [0, 0.265, 0]);
    const L = 0.57, W = 0.4;
    const fanGeo = new THREE.BufferGeometry();
    fanGeo.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0, 0, L, -W, 0, L, W], 3));
    const fanMat = new THREE.MeshBasicMaterial({ color: '#a78bfa', transparent: true, opacity: 0.2, side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false });
    const fan = new THREE.Mesh(fanGeo, fanMat);
    fan.position.y = 0.27;
    j6.add(fan);
    const lineMat = new THREE.MeshBasicMaterial({ color: '#ede9fe' });
    const line = new THREE.Mesh(k.box(0.012, 0.006, 2 * W), lineMat);
    line.position.y = 0.27 + L;
    j6.add(line);
    fan.visible = line.visible = false;
    tool.update = (on, dt, time, fail) => {
      fan.visible = line.visible = on;
      fanMat.color.set(fail ? '#ff4d4f' : '#a78bfa');
      lineMat.color.set(fail ? '#ffd1d1' : '#ede9fe');
      fanMat.opacity = 0.16 + 0.06 * Math.sin(time * 40);
    };
  } else if (kind === 'driver' || kind === 'drill' || kind === 'riveter') {
    let bit = null;
    if (kind === 'driver') {
      k.add(k.cyl(0.055, 0.065, 0.16, 16), k.paint('#334155', 0.45), j6, [0, 0.16, 0]);
      k.add(k.cyl(0.03, 0.05, 0.04, 14), k.metal('#9aa8b6'), j6, [0, 0.26, 0]);
      bit = k.group(j6, [0, 0.28, 0]);
      k.add(k.cyl(0.009, 0.009, 0.06, 6), k.metal('#e5e7eb', 0.2), bit, [0, 0.03, 0]);
    } else if (kind === 'drill') {
      k.add(k.cyl(0.05, 0.06, 0.14, 16), k.paint('#3f3f46', 0.45), j6, [0, 0.15, 0]);
      k.add(k.cyl(0.02, 0.045, 0.05, 14), k.metal('#9aa8b6'), j6, [0, 0.245, 0]);
      bit = k.group(j6, [0, 0.27, 0]);
      k.add(k.cyl(0.006, 0.006, 0.07, 6), k.metal('#f5f5f4', 0.15), bit, [0, 0.035, 0]);
    } else {
      k.add(k.cyl(0.06, 0.065, 0.16, 16), k.paint('#27272a', 0.45), j6, [0, 0.16, 0]);
      k.add(k.cyl(0.018, 0.04, 0.08, 14), k.metal('#9aa8b6'), j6, [0, 0.28, 0]);
      k.add(k.cyl(0.012, 0.012, 0.02, 10), k.metal('#e5e7eb'), j6, [0, 0.33, 0]);
    }
    tool.update = (on, dt) => { if (on && bit) bit.rotation.y += dt * 45; };
  } else if (kind === 'sprayer') {
    k.add(k.box(0.08, 0.12, 0.09), dark, j6, [0, 0.14, 0]);
    k.add(k.cyl(0.02, 0.03, 0.09, 12), k.metal('#9aa8b6'), j6, [0, 0.245, 0]);
    k.add(k.cyl(0.01, 0.02, 0.05, 12), k.metal('#e5e7eb'), j6, [0, 0.315, 0]);
    const coneMat = new THREE.MeshBasicMaterial({ color: ctx.paintColor || '#93c5fd', transparent: true, opacity: 0.16, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
    const cone = k.add(k.cyl(0.16, 0.006, 0.3, 20), coneMat, j6, [0, TIP + 0.15, 0]);
    cone.castShadow = false;
    cone.visible = false;
    tool.update = (on) => { cone.visible = on; };
  }
  return tool;
}

/* ───────────────────────────── robot ───────────────────────────── */
function buildRobot(kit, T, def, x, z, ctx) {
  const k = kit, n = def.side;
  // per-robot materials so one robot can glow (fault / heat) without the others
  const body = new THREE.MeshStandardMaterial({ color: T.robot, metalness: 0.25, roughness: 0.42, emissive: '#000000', emissiveIntensity: 1 });
  const shell = T.shell === T.robot ? body : k.paint(T.shell, 0.4);
  const joint = new THREE.MeshStandardMaterial({ color: T.joint, metalness: 0.85, roughness: 0.35, emissive: '#000000', emissiveIntensity: 1 });
  const bearing = new THREE.MeshStandardMaterial({ color: T.joint, metalness: 0.85, roughness: 0.35, emissive: '#000000', emissiveIntensity: 1 });
  const bolt = k.metal('#9aa8b6', 0.25);

  const root = k.group(null, [x, 0, z]);
  root.rotation.y = n < 0 ? 0 : Math.PI;          // local +Z always faces the belt

  // fixed base
  k.add(k.cyl(0.56, 0.6, 0.06, 32), k.metal('#2a3a4c', 0.5), root, [0, 0.03, 0]);
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2 + 0.3;
    k.add(k.cyl(0.035, 0.035, 0.04, 8), bolt, root, [Math.cos(a) * 0.5, 0.08, Math.sin(a) * 0.5]);
  }
  k.add(k.cyl(0.42, 0.48, 0.24, 32), joint, root, [0, 0.18, 0]);
  k.add(k.torus(0.43, 0.018, 8, 40), k.glow(T.accent, 0.6), root, [0, 0.29, 0], [Math.PI / 2, 0, 0]);

  // J1 waist
  const j1 = k.group(root, [0, BASE_H, 0]);
  k.add(k.cyl(0.4, 0.42, 0.1, 32), body, j1, [0, 0.05, 0]);
  k.add(k.cyl(0.3, 0.36, 0.5, 24), body, j1, [0, 0.35, 0]);
  const SP = H_S - BASE_H;
  [-1, 1].forEach((s) => {
    k.add(k.box(0.12, 0.42, 0.44), body, j1, [s * 0.27, SP - 0.16, 0]);
    k.hub(0.22, 0.12, body, j1, [s * 0.27, SP, 0]);
  });
  k.hub(0.13, 0.22, joint, j1, [0.44, SP, 0]);
  k.hub(0.09, 0.02, k.glow(T.accent, 0.8), j1, [0.56, SP, 0]);

  // J2 shoulder + upper arm
  const j2 = k.group(j1, [0, SP, 0]);
  k.hub(0.19, 0.4, bearing, j2, [0, 0, 0]);               // the shoulder bearing (glows on bearing wear)
  k.add(k.box(0.3, L1 - 0.2, 0.26), body, j2, [0, L1 / 2, 0]);
  k.add(k.box(0.32, L1 * 0.5, 0.1), k.paint('#22303f', 0.5), j2, [0, L1 / 2, 0]);
  k.add(k.cyl(0.028, 0.028, L1 - 0.3, 8), k.paint('#1e3048', 0.7), j2, [0, L1 / 2, -0.17]);
  k.hub(0.17, 0.34, joint, j2, [0, L1, 0]);

  // J3 elbow + forearm
  const j3 = k.group(j2, [0, L1, 0]);
  k.hub(0.16, 0.42, body, j3, [0, 0, 0]);
  k.add(k.box(0.22, 0.26, 0.22), body, j3, [0, -0.2, 0]);
  k.add(k.cyl(0.12, 0.15, 0.56, 20), shell, j3, [0, 0.36, 0]);
  k.add(k.torus(0.13, 0.012, 8, 28), k.glow(T.accent, 0.9), j3, [0, L2A, 0], [Math.PI / 2, 0, 0]);

  // J4 forearm roll + wrist yoke
  const j4 = k.group(j3, [0, L2A, 0]);
  k.add(k.cyl(0.1, 0.115, 0.3, 18), shell, j4, [0, 0.15, 0]);
  [-1, 1].forEach((s) => k.add(k.box(0.035, 0.24, 0.16), shell, j4, [s * 0.11, L2B - 0.07, 0]));
  k.hub(0.08, 0.255, joint, j4, [0, L2B, 0]);

  // J5 wrist pitch + flange
  const j5 = k.group(j4, [0, L2B, 0]);
  k.add(k.cyl(0.065, 0.075, 0.12, 16), shell, j5, [0, 0.08, 0]);
  k.add(k.cyl(0.08, 0.08, 0.03, 20), k.metal('#3b4654', 0.3), j5, [0, FL - 0.015, 0]);
  k.add(k.torus(0.08, 0.008, 8, 24), k.glow('#fcd34d', 0.7), j5, [0, FL - 0.015, 0], [Math.PI / 2, 0, 0]);

  const j6 = k.group(j5, [0, FL, 0]);
  const tool = buildTool(k, T, def, j6, ctx);

  // three-lamp stack light: green / amber / red
  k.add(k.cyl(0.022, 0.022, 1.16, 8), k.metal(T.joint, 0.35), root, [-0.7, 0.58, -0.55]);
  const lamps = ['#24d7b4', '#f1c21b', '#ff3b30'].map((c, i) => {
    const mat = new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: 0.05, roughness: 0.4 });
    k.add(k.cyl(0.06, 0.06, 0.12, 16), mat, root, [-0.7, 1.22 + i * 0.13, -0.55]);
    return mat;
  });
  k.add(k.cyl(0.066, 0.066, 0.03, 16), k.metal(T.joint, 0.35), root, [-0.7, 1.565, -0.55]);

  // floor: safety ring (turns red on fault) + accent ring + bearing-vibration ripples
  const ringMat = new THREE.MeshBasicMaterial({ color: '#fcd34d', transparent: true, opacity: 0.28, side: THREE.DoubleSide, depthWrite: false });
  k.decal(k.ring(0.78, 0.9), ringMat, root, [0, 0.004, 0]);
  k.decal(k.ring(0.64, 0.67), k.flat(T.accent, 0.4), root, [0, 0.005, 0]);
  const ripples = [0, 1].map(() => {
    const mat = new THREE.MeshBasicMaterial({ color: '#ffb020', transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false });
    const m = k.decal(k.ring(0.62, 0.68, 48), mat, root, [0, 0.006, 0]);
    m.visible = false;
    return { m, mat };
  });

  return { root, j1, j2, j3, j4, j5, j6, tool, body, joint, bearing, lamps, ringMat, ripples };
}

/* ───────────────────────────── kinematics ───────────────────────────── */
const _ik = new THREE.Vector3();
function solveIK(arm, target, tilt, extraYaw = 0) {
  _ik.copy(target).applyMatrix4(arm.invRoot);
  const yaw = Math.atan2(_ik.x, _ik.z);
  const r = Math.hypot(_ik.x, _ik.z);
  const wu = r - D * Math.sin(tilt);                 // wrist pivot sits D back along the tool axis
  const wv = _ik.y - H_S + D * Math.cos(tilt);
  const dRaw = Math.hypot(wu, wv);
  const d = clamp(dRaw, Math.abs(L1 - L2) + 1e-4, L1 + L2 - 1e-4);
  arm.reachMargin = Math.min(arm.reachMargin ?? 9, L1 + L2 - dRaw);
  const gamma = Math.atan2(wu, wv);
  const alpha = Math.acos(clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1));
  const beta = Math.acos(clamp((L1 * L1 + L2 * L2 - d * d) / (2 * L1 * L2), -1, 1));
  const a2 = gamma - alpha;                           // elbow-up solution
  const a3 = Math.PI - beta;
  arm.j1.rotation.y = yaw;
  arm.j2.rotation.x = a2;
  arm.j3.rotation.x = a3;
  arm.j4.rotation.y = 0;
  arm.j5.rotation.x = Math.PI - tilt - a2 - a3;       // holds the tool at the requested angle
  arm.j6.rotation.y = yaw + extraYaw;                 // cancels waist yaw so grippers stay square to the belt
}

const _s = new THREE.Vector3();
function sample(keys, t) {
  if (t <= keys[0].t) return { p: _s.copy(keys[0].p), tilt: keys[0].tilt, on: keys[0].on };
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i], b = keys[i + 1];
    if (t < b.t) {
      const u = (t - a.t) / (b.t - a.t);
      const e = b.ease === 'lin' ? u : minJerk(u);   // minimum-jerk: smooth start and stop like a real controller
      return { p: _s.lerpVectors(a.p, b.p, e), tilt: a.tilt + (b.tilt - a.tilt) * e, on: a.on };
    }
  }
  const z = keys[keys.length - 1];
  return { p: _s.copy(z.p), tilt: z.tilt, on: z.on };
}

/* ───────────────────────────── motion programs ─────────────────────────────
   Each robot runs a list of tool-tip waypoints. on = tool active from that key;
   ev = event fired on arrival (pick, place, pass, pt0…).                          */
function timeline(start, tilt) {
  const keys = [{ t: 0, p: start.clone(), on: false, tilt }];
  let t = 0;
  const last = () => keys[keys.length - 1].p;
  const tl = {
    get t() { return t; },
    to(p, dur, o = {}) { t += dur; keys.push({ t, p: p.clone(), ...o }); return tl; },
    auto(p, o) { return tl.to(p, clamp(0.28 + last().distanceTo(p) * 0.4, 0.3, 0.95), o); },
    hold(dur, o) { return tl.to(last(), dur, o); },
    finish() {
      let on = false, tt = tilt;
      keys.forEach((k) => {
        if (k.on !== undefined) on = k.on;
        k.on = on;
        if (k.tilt !== undefined) tt = k.tilt;
        k.tilt = tt;
      });
      return keys;
    },
  };
  return tl;
}

export function programFeatures(P) {
  return P.kind === 'bead' ? P.features : [P.feature];
}

function buildProgram(def, ctx) {
  const P = def.program, n = def.side, S = ctx.S, product = ctx.product;
  const ready = S(P.kind === 'place' ? Math.sign(P.feeder.dx) * 0.3 : 0, 1.1, n * 0.9);
  const tl = timeline(ready, P.tilt ?? (P.tool === 'torch' ? 0.3 : 0));
  const out = { beads: null, spray: null, place: null, points: null };

  if (P.kind === 'bead') {
    const gap = BEAD_GAP[P.tool] ?? 0.02, speed = BEAD_SPEED[P.tool] ?? 0.85;
    out.beads = P.features.map((id) => {
      const f = product.features[id];
      const tipDy = f.from[1] + f.size[0] / 2 + gap;
      const a = S(f.from[0], tipDy, f.from[2]), b = S(f.to[0], tipDy, f.to[2]);
      tl.auto(a.clone().setY(a.y + 0.2));
      tl.to(a, 0.25, { on: true });
      const t0 = tl.t;
      tl.to(b, a.distanceTo(b) / speed, { ease: 'lin', on: false });
      const t1 = tl.t;
      tl.to(b.clone().setY(b.y + 0.2), 0.22);
      return { id, t0, t1 };
    });
  } else if (P.kind === 'place') {
    const f = product.features[P.feature], it = product.items[f.item];
    const F = V3(ctx.feeder.x, FEED_TOP + it.h, ctx.feeder.z);
    const Fup = F.clone().setY(F.y + 0.4);
    const tipDy = f.at[1] + it.h;
    const placeTip = S(f.at[0], tipDy, f.at[2]);
    const transferDy = Math.max(tipDy + 0.35, ctx.maxY + it.h + 0.15);    // carried item clears what is already built
    tl.auto(Fup);
    tl.to(F, 0.3, { on: true, ev: 'pick' });
    tl.hold(0.15);
    tl.to(Fup, 0.3);
    const tLift = tl.t;
    tl.auto(S(f.at[0], transferDy, f.at[2]));
    const tOver = tl.t;
    tl.to(placeTip, 0.42, { on: false, ev: 'place' });
    tl.hold(0.12);
    tl.to(S(f.at[0], tipDy + 0.3, f.at[2]), 0.3);
    out.place = { tLift, tOver, tAfter: tl.t };
  } else if (P.kind === 'scan') {
    const h = ctx.maxY + 0.5, span = (product.length ?? 1) / 2 + 0.05, z = P.z ?? 0;
    tl.auto(S(-span, h, z));
    tl.hold(0.2, { on: true });
    tl.to(S(span, h, z), 2.0);
    tl.hold(0.2, { on: false, ev: 'pass' });
  } else if (P.kind === 'points') {
    const f = product.features[P.feature], head = POINT_STYLE[f.style].h;
    const dwell = P.dwell ?? (P.tool === 'drill' ? 0.24 : P.tool === 'riveter' ? 0.2 : 0.3);
    out.points = f.points.length;
    f.points.forEach((p, i) => {
      const above = S(p[0], p[1] + 0.15, p[2]);
      tl.auto(above);
      tl.to(S(p[0], p[1] + head, p[2]), 0.18, { on: true, ev: `pt${i}` });
      tl.hold(dwell, { on: false });
      tl.to(above, 0.15);
    });
  } else if (P.kind === 'spray') {
    const h = ctx.maxY + 0.38, span = P.span ?? 0.5, zs = P.passes ?? [-0.2, 0, 0.2];
    let x = -span;
    tl.auto(S(x, h, zs[0]));
    tl.hold(0.1, { on: true });
    const t0 = tl.t;
    zs.forEach((z, j) => {
      if (j) tl.to(S(x, h, z), 0.3);
      x = -x;
      tl.to(S(x, h, z), (2 * span) / 0.85, { ease: 'lin' });
    });
    const t1 = tl.t;
    tl.hold(0.05, { on: false });
    out.spray = { id: P.feature, t0, t1 };
  }
  tl.auto(ready);
  return { keys: tl.finish(), end: tl.t, ...out };
}

/* ───────────────────────────── the plant ───────────────────────────── */
export function createPlant(profile, { seed = 7 } = {}) {
  const T = { ...DEFAULT_THEME, ...profile.theme };
  const kit = makeKit();
  const rand = seeded(seed);
  const root = new THREE.Group();
  root.name = `plant-${profile.id}`;
  buildEnvironment(kit, T, root);
  const conveyor = buildConveyor(kit, T, root);

  const product = profile.product;
  const stationX = profile.stations || [-7.5, -4.5, -1.5, 1.5, 4.5, 7.5];
  const stationSlot = stationX.map((x) => Math.round((x - SLOT_X0) / PITCH));
  const hasScanner = profile.robots.some((d) => d.program.kind === 'scan');
  const statusId = Object.keys(product.features).find((id) => product.features[id].kind === 'status');

  // which station produces each feature, and how tall the part is before a given station
  const featureStage = {};
  profile.robots.forEach((d) => programFeatures(d.program).forEach((id) => { featureStage[id] = d.station; }));
  const featureTop = (f) => {
    if (f.kind === 'bead') return f.from[1] + f.size[0] / 2;
    if (f.kind === 'item') return f.at[1] + product.items[f.item].h;
    if (f.kind === 'points') return Math.max(...f.points.map((p) => p[1])) + POINT_STYLE[f.style].h;
    return 0;
  };
  const maxYBefore = (stage) => Object.entries(product.features).reduce(
    (m, [id, f]) => (featureStage[id] !== undefined && featureStage[id] < stage ? Math.max(m, featureTop(f)) : m), product.baseTop);

  const beadGeo = {};
  for (const [id, f] of Object.entries(product.features)) {
    if (f.kind === 'bead') beadGeo[id] = new THREE.BoxGeometry(1, f.size[0], f.size[1]).translate(0.5, 0, 0);
  }

  /* ── parts ── */
  function makePart() {
    const g = kit.group(root, [0, BELT_TOP, 0]);
    product.base(kit, g);
    const feats = {};
    for (const [id, f] of Object.entries(product.features)) {
      if (f.kind === 'bead') {
        const holder = kit.group(g, f.from);
        const dx = f.to[0] - f.from[0], dz = f.to[2] - f.from[2], len = Math.hypot(dx, dz);
        holder.rotation.y = -Math.atan2(dz, dx);
        const mat = f.hot
          ? new THREE.MeshStandardMaterial({ color: f.color, metalness: 0.7, roughness: 0.45, emissive: '#ff7a1a', emissiveIntensity: 0 })
          : new THREE.MeshStandardMaterial({ color: f.color, metalness: 0.1, roughness: 0.6 });
        const base = new THREE.Color(f.color);
        const mesh = kit.add(beadGeo[id], mat, holder);
        mesh.visible = false;
        const st = { kind: 'bead', prog: 0, heat: 0 };
        st.set = (p) => { st.prog = p; mesh.visible = p > 0.001; mesh.scale.x = Math.max(p, 0.001) * len; };
        st.heatUp = () => { if (f.hot) { st.heat = 1; mat.emissiveIntensity = 3; } };
        st.cool = (dt) => { if (st.heat > 0) { st.heat = Math.max(0, st.heat - dt * 0.35); mat.emissiveIntensity = st.heat * 3; } };
        st.flaw = () => { mat.color.set('#2a2420'); };          // porous / burnt bead
        st.reset = () => { st.set(0); st.heat = 0; mat.emissiveIntensity = 0; mat.color.copy(base); };
        st.complete = () => { st.set(1); st.heat = 0; mat.emissiveIntensity = 0; };
        feats[id] = st;
      } else if (f.kind === 'item') {
        const mesh = product.items[f.item].make(kit);
        mesh.position.set(f.at[0], f.at[1], f.at[2]);
        mesh.visible = false;
        g.add(mesh);
        const st = { kind: 'item' };
        st.set = (v) => { mesh.visible = !!v; };
        st.misplace = (off, yaw) => { mesh.position.set(f.at[0] + off.x, f.at[1], f.at[2] + off.z); mesh.rotation.y = yaw; mesh.visible = true; };
        st.reset = () => { mesh.visible = false; mesh.position.set(f.at[0], f.at[1], f.at[2]); mesh.rotation.y = 0; };
        st.complete = () => { mesh.visible = true; };
        feats[id] = st;
      } else if (f.kind === 'points') {
        const style = POINT_STYLE[f.style];
        const meshes = f.points.map((p) => {
          const m = kit.add(style.geo(kit), style.mat(kit), g, [p[0], p[1] + style.h / 2, p[2]]);
          m.visible = false;
          return m;
        });
        const st = { kind: 'points' };
        st.show = (i) => { if (meshes[i]) meshes[i].visible = true; };
        st.skew = (i) => {                                   // cross-threaded fastener left proud
          const m = meshes[i];
          if (!m) return;
          m.visible = true;
          m.position.y += 0.014;
          m.rotation.z = 0.55;
        };
        st.reset = () => meshes.forEach((m, i) => {
          m.visible = false;
          m.position.y = f.points[i][1] + style.h / 2;
          m.rotation.z = 0;
        });
        st.complete = () => meshes.forEach((m) => { m.visible = true; });
        feats[id] = st;
      } else if (f.kind === 'status') {
        const mat = new THREE.MeshStandardMaterial({ color: '#fbbf24', emissive: '#fbbf24', emissiveIntensity: 1.2, roughness: 0.4 });
        kit.add(kit.sphere(0.035, 10), mat, g, f.at);
        const paint = (c) => { mat.color.set(c); mat.emissive.set(c); };
        const st = { kind: 'status' };
        st.set = (v) => paint(v === 'pass' ? '#22c55e' : v === 'fail' ? '#ff3b30' : '#fbbf24');
        st.reset = () => paint('#fbbf24');
        st.complete = () => paint('#22c55e');
        feats[id] = st;
      }
    }
    // paint features recolour every mesh flagged paintable in this part (materials cloned per part)
    for (const [id, f] of Object.entries(product.features)) {
      if (f.kind !== 'paint') continue;
      const targets = [];
      g.traverse((o) => {
        if (o.isMesh && o.userData.paint) {
          o.material = o.material.clone();
          targets.push({ mat: o.material, from: o.material.color.clone() });
        }
      });
      const to = new THREE.Color(f.color);
      const st = { kind: 'paint', prog: 0 };
      st.set = (p) => { st.prog = p; targets.forEach((t) => t.mat.color.copy(t.from).lerp(to, p)); };
      st.reset = () => st.set(0);
      st.complete = () => st.set(1);
      feats[id] = st;
    }
    return { g, feats, slot: 0, defect: false };
  }

  const parts = [];
  for (let k = 0; k < NUM_SLOTS; k++) {
    const p = makePart();
    p.slot = k;
    p.g.position.x = SLOT_X0 + k * PITCH;
    for (const [id, st] of Object.entries(p.feats)) {
      const s = featureStage[id];
      if (s !== undefined && stationSlot[s] < k) st.complete();
    }
    parts.push(p);
  }
  const partAt = (station) => parts.find((p) => p.slot === stationSlot[station]);
  function markDefect(part) {
    if (!part || part.defect) return;
    part.defect = true;
    if (!hasScanner && statusId) part.feats[statusId].set('fail');   // no vision station: flag it in-process
  }

  /* ── feeders ── */
  let simT = 0;
  function spawnFeed(feed, instant) {
    const obj = feed.item.make(kit);
    root.add(obj);
    const top = FEED_TOP, low = FEED_TOP - feed.item.h - 0.01;
    obj.position.set(feed.x, instant ? top : low, feed.z);
    feed.obj = obj;
    feed.rise = instant ? null : { t0: simT, low, top };
  }
  function buildFeeder(def, x) {
    const item = product.items[product.features[def.program.feature].item];
    const fx = x + def.program.feeder.dx, fz = def.side * def.program.feeder.dz;
    kit.add(kit.box(item.w + 0.2, FEED_TOP, item.d + 0.2), kit.paint(T.feeder, 0.55), root, [fx, FEED_TOP / 2, fz]);
    kit.decal(kit.plane(item.w + 0.04, item.d + 0.04), kit.flat('#04080d'), root, [fx, FEED_TOP + 0.002, fz]);
    const feed = { x: fx, z: fz, item, obj: null, rise: null, refillAt: null };
    spawnFeed(feed, true);
    return feed;
  }
  function updateFeeder(feed) {
    if (feed.refillAt !== null && simT >= feed.refillAt) { feed.refillAt = null; spawnFeed(feed, false); }
    if (feed.rise) {
      const u = (simT - feed.rise.t0) / 0.9;
      feed.obj.position.y = feed.rise.low + (feed.rise.top - feed.rise.low) * minJerk(u);
      if (u >= 1) feed.rise = null;
    }
  }

  /* ── robots ── */
  // each robot starts its cycle a little after the index, so the arms don't move in lockstep
  const startDelay = () => 0.08 + rand() * 0.5;
  const arms = profile.robots.map((def, index) => {
    const x = stationX[def.station], z = def.side * ROBOT_Z;
    const P = def.program;
    const ctx = {
      sx: x, side: def.side, product,
      S: (dx, dy, dz) => V3(x + dx, BELT_TOP + dy, dz),
      maxY: maxYBefore(def.station),
      item: P.kind === 'place' ? product.items[product.features[P.feature].item] : null,
      beadColor: P.kind === 'bead' ? product.features[P.features[0]].color : null,
      paintColor: P.kind === 'spray' ? product.features[P.feature].color : null,
    };
    const parts3d = buildRobot(kit, T, def, x, z, ctx);
    root.add(parts3d.root);
    parts3d.root.updateMatrix();
    const arm = {
      ...parts3d, def, index,
      invRoot: parts3d.root.matrix.clone().invert(),
      bodyBase: parts3d.body.color.clone(),
      t: -startDelay(), prevT: 0, speed: 1, decide: true,
      issue: null, issueSince: 0, severity: 0, defectRate: 0, tripped: false, symptom: null,
      heat: 0, shake: 0, defect: false, dOff: V3(), dYaw: 0, defBead: 0, defPoint: 0,
      carried: null, feed: null,
    };
    if (P.kind === 'place') { arm.feed = buildFeeder(def, x); ctx.feeder = arm.feed; }
    Object.assign(arm, buildProgram(def, ctx));
    return arm;
  });

  /* ── effects ── */
  const sparks = makeParticles(root, { color: '#ffc861', size: 0.05, opacity: 1, count: 120 });
  const mist = makeParticles(root, { color: '#9ec5ff', size: 0.07, opacity: 0.3, count: 160 });
  const heatFx = makeParticles(root, { color: '#ff7a2f', size: 0.13, opacity: 0.5, count: 160 });
  const sprayArm = arms.find((a) => a.spray);
  if (sprayArm) mist.material.color.set(product.features[sprayArm.spray.id].color);
  const weldLights = arms.filter((a) => a.tool.kind === 'torch').map((a) => {
    const l = new THREE.PointLight('#ffd27a', 0, 4, 2);
    root.add(l);
    return [a, l];
  });
  const faultLight = new THREE.PointLight('#ff3b30', 0, 7, 2);
  const heatLight = new THREE.PointLight('#ff6a2a', 0, 6, 2);
  root.add(faultLight, heatLight);

  const _w = V3(), _w2 = V3(), _off = V3();
  const tipPos = (a, out) => { out.copy(a.tool.tipLocal); a.j6.localToWorld(out); return root.worldToLocal(out); };

  /* ── line state ── */
  let phase = 'work', idxT = 0, settle = 0, beltSpeed = 1, beltPos = 0;
  let units = 0, rejects = 0, lastIndexAt = null, cycle = 0, ctlPaused = false, lineRate = 1;
  const nominalCycle = Math.max(...arms.map((a) => a.end)) + SETTLE + INDEX_TIME;

  function advanceSlots() {
    for (const p of parts) {
      p.slot++;
      if (p.slot >= NUM_SLOTS) {                     // left through the outfeed hood → recycle at the infeed
        if (p.defect) rejects++; else units++;
        Object.values(p.feats).forEach((f) => f.reset());
        p.defect = false;
        p.slot = 0;
      }
    }
  }

  function decideCycle(a) {                          // quality drift: does this robot botch this part?
    const kind = a.def.program.kind;
    a.defect = kind !== 'scan' && a.defectRate > 0 && rand() < a.defectRate;
    if (!a.defect) return;
    const sgn = () => (rand() < 0.5 ? -1 : 1);
    a.dOff.set(sgn() * (0.035 + rand() * 0.03), 0, (rand() - 0.5) * 0.05);
    a.dYaw = sgn() * (0.12 + rand() * 0.14);
    a.defBead = Math.floor(rand() * (a.beads?.length || 1));
    a.defPoint = Math.floor(rand() * (a.points || 1));
  }

  function placeBlend(a) {                           // how much of the misplacement offset applies right now
    const { tLift, tOver, tAfter } = a.place, t = a.t;
    if (t <= tLift) return 0;
    if (t < tOver) return minJerk((t - tLift) / (tOver - tLift));
    if (t <= tAfter) return 1;
    return 1 - minJerk((t - tAfter) / Math.max(0.01, a.end - tAfter));
  }

  function onEvent(a, ev) {
    const part = partAt(a.def.station), P = a.def.program;
    if (ev === 'pick') {
      const obj = a.feed.obj;
      if (!obj) return;
      a.j6.attach(obj);
      a.carried = obj;
      a.feed.obj = null;
      a.feed.rise = null;
      a.feed.refillAt = simT + 0.9;
    } else if (ev === 'place') {
      if (a.carried) { a.j6.remove(a.carried); a.carried = null; }
      if (!part) return;
      if (a.defect) { part.feats[P.feature].misplace(a.dOff, -a.dYaw); markDefect(part); } else part.feats[P.feature].set(true);
    } else if (ev === 'pass') {
      if (part) part.feats[P.feature].set(part.defect ? 'fail' : 'pass');
    } else if (ev.startsWith('pt')) {
      const i = Number(ev.slice(2));
      if (!part) return;
      if (a.defect && i === a.defPoint) { part.feats[P.feature].skew(i); markDefect(part); } else part.feats[P.feature].show(i);
    }
  }

  // returns false when the tool should be off (e.g. a weld that stopped short)
  function programHook(a, part) {
    const t = a.t;
    let toolOk = true;
    if (a.beads && part) {
      a.beads.forEach((b, i) => {
        if (t < b.t0) return;
        const st = part.feats[b.id];
        const cap = a.defect && i === a.defBead ? 0.6 : 1;
        const u = clamp((t - b.t0) / (b.t1 - b.t0), 0, 1);
        st.set(Math.max(st.prog, Math.min(cap, u)));
        const active = t <= b.t1;
        if (active && u < cap && a.speed > 0.15) st.heatUp();
        if (active && u >= cap) toolOk = false;
        if (cap < 1 && u >= cap && !part.defect) { st.flaw(); markDefect(part); }
      });
    }
    if (a.spray && part && t >= a.spray.t0) {
      const st = part.feats[a.spray.id];
      const cap = a.defect ? 0.5 : 1;                 // thin, patchy coat
      const u = clamp((t - a.spray.t0) / (a.spray.t1 - a.spray.t0), 0, 1);
      st.set(Math.max(st.prog, Math.min(cap, u)));
      if (cap < 1 && u >= 0.99) markDefect(part);
    }
    return toolOk;
  }

  function update(dt, ctl = {}) {
    simT += dt;
    const paused = !!ctl.paused;
    ctlPaused = paused;
    const rate = clamp(ctl.rate ?? 1, 0.25, 3);
    lineRate = rate;
    const conds = ctl.robots || [];

    // ── condition bookkeeping ──
    for (const a of arms) {
      const c = conds[a.index] || null;
      const issue = c?.issue || null;
      if (issue !== a.issue) { a.issue = issue; a.issueSince = simT; }
      a.severity = clamp(c?.severity ?? 0, 0, 1);
      a.defectRate = clamp(c?.defectRate ?? 0, 0, 1);
      const delay = issue === 'stopped' || issue === 'fault' ? 0 : 3.6 - 1.6 * a.severity;   // symptom shows before the trip
      a.tripped = !!issue && !!c?.trip && simT - a.issueSince >= delay;
      a.symptom = issue === 'bearing' || issue === 'thermal' || issue === 'strain' ? issue : null;
    }
    const tripped = arms.filter((a) => a.tripped);
    const halt = paused || tripped.length > 0;
    const blinkFast = (simT * 3) % 1 < 0.5, blinkSlow = (simT * 1.2) % 1 < 0.5;
    let hottest = null;

    // ── robots ──
    for (const a of arms) {
      if (a.decide) { decideCycle(a); a.decide = false; }
      const derate = a.symptom === 'bearing' ? 0.6 : a.symptom === 'thermal' ? 0.8 : 1;
      a.speed = approach(a.speed, paused || a.tripped ? 0 : derate, a.tripped ? 6 : 2.5, dt);
      if (phase === 'work') a.t = Math.min(a.end, a.t + dt * a.speed * rate);
      const k = sample(a.keys, a.t);

      let yawExtra = 0;
      if (a.defect && a.place) {
        const w = placeBlend(a);
        if (w > 0) { k.p.add(_off.copy(a.dOff).multiplyScalar(w)); yawExtra = a.dYaw * w; }
      }
      solveIK(a, k.p, k.tilt, yawExtra);

      // bearing wear: the arm shudders (stops when the brakes engage on a trip)
      a.shake = approach(a.shake, a.symptom === 'bearing' && !a.tripped ? 1 : 0, 3, dt);
      if (a.shake > 0) {
        const amp = a.shake * (0.012 + 0.026 * a.severity) * (0.45 + 0.55 * Math.min(1, a.speed / 0.6));
        a.j1.rotation.y += amp * 0.7 * Math.sin(simT * 41);
        a.j2.rotation.x += amp * Math.sin(simT * 57 + 1.3);
        a.j3.rotation.x += amp * 0.8 * Math.sin(simT * 49 + 2.1);
      }

      for (const key of a.keys) if (key.ev && key.t > a.prevT && key.t <= a.t) onEvent(a, key.ev);
      a.prevT = a.t;

      const part = partAt(a.def.station);
      const toolOk = phase === 'work' ? programHook(a, part) : true;
      const on = k.on && a.speed > 0.15 && toolOk;
      a.toolOn = on;
      a.tool.update(on, dt * Math.max(a.speed, 0.2) * rate, simT, a.tool.kind === 'scanner' && part?.defect);

      if (on && a.tool.kind === 'torch') {
        tipPos(a, _w);
        sparks.emit(_w, 2, () => {
          const ang = Math.random() * Math.PI * 2, s = 0.6 + Math.random() * 1.6;
          return [Math.cos(ang) * s, 0.4 + Math.random() * 1.6, Math.sin(ang) * s, 0.25 + Math.random() * 0.45];
        });
      }
      if (on && a.tool.kind === 'sprayer') {
        tipPos(a, _w);
        mist.emit(_w, 3, () => [(Math.random() - 0.5) * 0.5, -(0.7 + Math.random() * 0.6), (Math.random() - 0.5) * 0.5, 0.45 + Math.random() * 0.35]);
      }

      // thermal excursion: motors glow and heat shimmer rises off the arm
      const heatTarget = a.symptom === 'thermal' ? 0.45 + 0.55 * a.severity : a.symptom === 'strain' ? 0.35 : 0;
      a.heat = approach(a.heat, heatTarget, heatTarget > a.heat ? 0.35 : 0.25, dt);
      if (a.heat > 0.2) {
        if (!hottest || a.heat > hottest.heat) hottest = a;
        if (Math.random() < a.heat * 0.9) {
          a.j3.getWorldPosition(_w); root.worldToLocal(_w);
          a.j2.getWorldPosition(_w2); root.worldToLocal(_w2);
          _w.lerp(_w2, Math.random());
          heatFx.emit(_w, 1, () => [(Math.random() - 0.5) * 0.25, 0.35 + Math.random() * 0.4, (Math.random() - 0.5) * 0.25, 1.0 + Math.random() * 0.8]);
        }
      }

      // body glow: red-hot for heat (paint darkens so the glow reads as heat on any robot colour),
      // pulsing red for a tripped robot
      a.body.color.copy(a.bodyBase).lerp(C.hotBase, a.heat * 0.85);
      if (a.heat > 0.01) {
        a.body.emissive.copy(C.heat); a.body.emissiveIntensity = a.heat * 1.15;
        a.joint.emissive.copy(C.heat); a.joint.emissiveIntensity = a.heat * 1.8;
      } else if (a.tripped) {
        a.body.emissive.copy(C.red); a.body.emissiveIntensity = 0.22 + 0.18 * Math.sin(simT * 6);
        a.joint.emissiveIntensity = 0;
      } else {
        a.body.emissiveIntensity = 0;
        a.joint.emissiveIntensity = 0;
      }
      // the shoulder bearing itself: amber while wearing, red once tripped
      if (a.symptom === 'bearing') {
        a.bearing.emissive.copy(a.tripped ? C.red : C.amber);
        a.bearing.emissiveIntensity = a.tripped ? 1.6 : 0.8 + 0.8 * Math.abs(Math.sin(simT * 9));
      } else a.bearing.emissiveIntensity = 0;
      // vibration ripples on the floor
      a.ripples.forEach((r, i) => {
        const vis = a.shake > 0.05;
        r.m.visible = vis;
        if (!vis) return;
        const u = (simT * 1.4 + i * 0.5) % 1;
        r.m.scale.setScalar(1 + u * 1.6);
        r.mat.opacity = (1 - u) * 0.55 * a.shake;
      });

      // stack light
      let g = 0, y = 0, r = 0;
      if (a.tripped) r = blinkFast ? 2.6 : 0.15;
      else if (a.symptom) y = blinkFast ? 2.2 : 0.2;        // predictive alert: running but degraded
      else if (paused) y = blinkSlow ? 2.0 : 0.2;
      else if (tripped.length && a.t >= a.end) y = 1.6;     // finished its part, now waiting on the stopped station
      else if (a.issue === 'quality') { y = 1.2; g = 0.6; }
      else g = on ? 2.4 : 1.1;
      a.lamps[0].emissiveIntensity = 0.05 + g;
      a.lamps[1].emissiveIntensity = 0.05 + y;
      a.lamps[2].emissiveIntensity = 0.05 + r;
      a.ringMat.color.set(a.tripped ? C.redHex : a.symptom ? '#ffb020' : '#fcd34d');
      a.ringMat.opacity = a.tripped ? 0.45 + 0.3 * Math.sin(simT * 6) : 0.28;

      if (a.feed) updateFeeder(a.feed);
    }

    // ── weld light, fault light, heat light ──
    for (const [a, l] of weldLights) {
      if (a.toolOn) {
        tipPos(a, _w);
        l.position.copy(_w);
        l.intensity = 4 + Math.random() * 4;
      } else l.intensity = 0;
    }
    if (tripped.length) {
      tripped[0].root.getWorldPosition(_w); root.worldToLocal(_w);
      faultLight.position.set(_w.x, 2.4, _w.z);
      faultLight.intensity = 6 + 4 * Math.sin(simT * 6);
    } else faultLight.intensity = 0;
    if (hottest) {
      hottest.j3.getWorldPosition(_w); root.worldToLocal(_w);
      heatLight.position.copy(_w);
      heatLight.intensity = hottest.heat * (5 + Math.sin(simT * 3));
    } else heatLight.intensity = 0;

    // ── line control: index only when every station is done and nothing holds the line ──
    if (phase === 'work') {
      if (!halt && arms.every((a) => a.t >= a.end)) {
        settle += dt * rate;
        if (settle >= SETTLE) {
          phase = 'index';
          idxT = 0;
          settle = 0;
          if (lastIndexAt !== null) cycle = simT - lastIndexAt;
          lastIndexAt = simT;
        }
      } else settle = 0;
    }
    beltSpeed = approach(beltSpeed, halt ? 0 : 1, halt ? 3 : 2, dt);
    let e = 0;
    if (phase === 'index') {
      const prev = minJerk(idxT / INDEX_TIME);
      idxT = Math.min(INDEX_TIME, idxT + dt * beltSpeed * rate);
      e = minJerk(idxT / INDEX_TIME);
      beltPos += (e - prev) * PITCH;
      if (idxT >= INDEX_TIME) {
        advanceSlots();
        phase = 'work';
        e = 0;
        arms.forEach((a) => { a.t = -startDelay(); a.prevT = a.t; a.decide = true; });
      }
    }
    for (const p of parts) {
      p.g.position.x = SLOT_X0 + (p.slot + e) * PITCH;
      for (const f of Object.values(p.feats)) f.cool?.(dt);
    }
    conveyor.update(beltPos);
    sparks.update(dt, 9.8, 0, BELT_TOP + 0.08, true);
    mist.update(dt, 0.4, 1.6, BELT_TOP, false);
    heatFx.update(dt, -0.15, 0.6, 0, false);

    // hood bands show line state
    const band = conveyor.band;
    const bandColor = tripped.length ? (blinkFast ? C.redHex : '#3a0c0c') : paused ? C.yellow : rate > 1.05 ? C.blue : C.green;
    band.color.set(bandColor);
    band.emissive.set(bandColor);
  }

  function status() {
    return {
      state: arms.some((a) => a.tripped) ? 'stopped' : ctlPaused ? 'paused' : 'running',
      faulted: arms.filter((a) => a.tripped).map((a) => a.index),
      warnings: arms.filter((a) => a.symptom && !a.tripped).map((a) => a.index),
      units, rejects,
      cycle: cycle || nominalCycle,
      rate: lineRate,
      phase,
    };
  }

  function dispose() {
    const geos = new Set(), mats = new Set();
    root.traverse((o) => {
      if (o.geometry) geos.add(o.geometry);
      if (o.material) [].concat(o.material).forEach((m) => mats.add(m));
      if (o.isInstancedMesh) o.dispose();
    });
    geos.forEach((g) => g.dispose());
    mats.forEach((m) => m.dispose());
  }

  return {
    group: root,
    profile,
    update,
    status,
    dispose,
    nominalCycle,
    robots: arms.map((a) => ({
      index: a.index, task: a.def.task, station: a.def.station, side: a.def.side,
      label: [stationX[a.def.station], 3.15, a.def.side * ROBOT_Z],
    })),
    _debug: { arms, parts, partAt, stationSlot, maxYBefore, sample, get simT() { return simT; } },
  };
}
