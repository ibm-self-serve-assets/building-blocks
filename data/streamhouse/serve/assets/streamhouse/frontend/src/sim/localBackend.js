// ─────────────────────────────────────────────────────────────────────────────
// Browser-side stand-in for the Factory Pulse backend.
//
// Implements the same endpoints the UI calls (bootstrap, simulate, control,
// context) and the same live stream (snapshot / cloud events), so the whole app
// runs with no server: six plants × six robots of synthetic telemetry, fault
// scenarios on one robot, line stops, alerts, repair and rule-based answers.
//
// It is only used when /api is unreachable (or VITE_LOCAL_SIM=true); see api.js.
// ─────────────────────────────────────────────────────────────────────────────
import { PROFILES } from '../twin/plantProfiles.js';
import { TRIP_AT } from '../twin/lineControl.js';

export const LOCAL_SITES = [
  { id: 'DET', city: 'Detroit', state: 'MI', lat: 42.33, lng: -83.05, profile: 'automotive', name: 'Detroit Body Shop', lines: 3, oee: 91, throughput: 64 },
  { id: 'ATL', city: 'Atlanta', state: 'GA', lat: 33.75, lng: -84.39, profile: 'battery', name: 'Atlanta Battery Works', lines: 2, oee: 88, throughput: 48 },
  { id: 'AUS', city: 'Austin', state: 'TX', lat: 30.27, lng: -97.74, profile: 'electronics', name: 'Austin Electronics', lines: 4, oee: 93, throughput: 120 },
  { id: 'LOU', city: 'Louisville', state: 'KY', lat: 38.25, lng: -85.76, profile: 'appliance', name: 'Louisville Appliance Park', lines: 3, oee: 89, throughput: 72 },
  { id: 'STL', city: 'St. Louis', state: 'MO', lat: 38.63, lng: -90.2, profile: 'beverage', name: 'St. Louis Bottling', lines: 2, oee: 92, throughput: 180 },
  { id: 'SEA', city: 'Everett', state: 'WA', lat: 47.98, lng: -122.2, profile: 'aerospace', name: 'Everett Aerostructures', lines: 1, oee: 86, throughput: 12 },
];

const SCENARIO_NAME = { bearing: 'Bearing wear', thermal: 'Thermal excursion', quality: 'Quality drift', surge: 'Demand surge' };
const ROBOT_SCENARIOS = ['bearing', 'thermal', 'quality'];   // these start in one robot
const HISTORY = 55;

const r1 = (v) => Math.round(v * 10) / 10;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const noise = (a) => (Math.random() - 0.5) * 2 * a;
const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

export function createLocalBackend({ autoStart = true, tickMs = 1000 } = {}) {
  const byId = Object.fromEntries(PROFILES.map((p) => [p.id, p]));
  const listeners = new Set();
  const alerts = [];
  const cloud = { mode: 'browser', status: 'simulated', derivedConnected: false };
  let tick = 0, alertSeq = 0;

  const sites = LOCAL_SITES.map((def) => {
    const profile = byId[def.profile];
    const robots = profile.robots.map((r, i) => {
      const baseTemp = 38 + Math.random() * 7, baseVib = 1.6 + Math.random() * 0.8;
      return { id: `R${i + 1}`, name: r.task, baseTemp, baseVib, temperature: baseTemp, vibration: baseVib, status: 'running' };
    });
    return {
      def, profile, robots,
      scenario: 'baseline', intensity: 0, since: 0, target: -1,
      paused: false, stopped: false,
      oee: def.oee, throughput: def.throughput, quality: 99.3,
      history: [],
    };
  });
  const find = (id) => {
    const s = sites.find((x) => x.def.id === id);
    if (!s) throw new Error(`Unknown site ${id}`);
    return s;
  };

  function addAlert(s, message, severity, acknowledged = false) {
    alerts.unshift({ id: `local-${++alertSeq}`, timestamp: new Date().toISOString(), siteId: s.def.id, message, severity, acknowledged });
    alerts.length = Math.min(alerts.length, 60);
  }
  const openAlerts = (s) => alerts.filter((a) => a.siteId === s.def.id && !a.acknowledged).length;

  /* ── one simulation tick (1 s) ── */
  function stepSite(s) {
    const sev = s.intensity / 100;
    const elapsed = tick - s.since;
    const failing = s.scenario === 'bearing' || s.scenario === 'thermal';
    const target = s.robots[s.target];

    // same rule as the 3D twin: a robot failure at TRIP_AT or above trips after a short symptom phase
    if (failing && sev >= TRIP_AT && !s.stopped && !s.paused && elapsed >= Math.ceil(3.6 - 1.6 * sev)) {
      s.stopped = true;
      addAlert(s, `Line stopped: ${target.id} ${target.name} protective stop (${SCENARIO_NAME[s.scenario].toLowerCase()})`, 'critical');
    }
    const running = !s.paused && !s.stopped;

    s.robots.forEach((r, i) => {
      const hit = i === s.target;
      if (hit && s.stopped) return;                         // tripped robot: readings frozen at the trip
      let tT = r.baseTemp + noise(0.6), vT = r.baseVib + noise(0.15);
      if (s.scenario === 'surge') { tT += 9 * sev; vT += 0.7 * sev; }
      if (!running) { tT -= 4; vT *= 0.3; }                 // idle robots cool down and go quiet
      if (hit && s.scenario === 'bearing') { vT = r.baseVib + 2 + 8 * sev + noise(0.4); tT += 6 * sev; }
      if (hit && s.scenario === 'thermal') { tT = r.baseTemp + 12 + 45 * sev + noise(1); vT += 0.6; }
      const k = hit && s.scenario !== 'baseline' ? 0.6 : 0.3;   // the faulty robot ramps fast so it peaks around the trip
      r.temperature += (tT - r.temperature) * k;
      r.vibration += (vT - r.vibration) * (k + 0.05);
    });
    s.robots.forEach((r, i) => {
      const hit = i === s.target && ROBOT_SCENARIOS.includes(s.scenario) && elapsed >= 1;
      r.status = hit ? 'warning' : s.paused ? 'stopped' : 'running';
    });

    s.quality += ((s.scenario === 'quality' ? 99.2 - 16 * sev : 99.2) + noise(0.1) - s.quality) * 0.25;
    let oeeT = s.def.oee + noise(0.8);
    if (s.scenario === 'quality') oeeT -= 4 + 14 * sev;
    if (failing && !s.stopped) oeeT -= 3 + 8 * sev;          // degraded robot slows the line before it trips
    if (s.scenario === 'surge') oeeT -= 2 * sev;
    if (s.stopped) oeeT = 30;
    if (s.paused) oeeT = s.oee;                              // planned stop: OEE holds
    s.oee += (oeeT - s.oee) * (s.stopped ? 0.08 : 0.2);

    const rate = (s.scenario === 'surge' ? 1 + 0.45 * sev : 1) * (failing ? 1 - 0.3 * sev : 1) * (s.scenario === 'quality' ? 1 - 0.1 * sev : 1);
    const thT = running ? s.def.throughput * rate * (1 + noise(0.03)) : 0;
    s.throughput += (thT - s.throughput) * 0.35;

    s.history.push({
      tick,
      time: new Date().toLocaleTimeString(),
      oee: r1(s.oee),
      vibration: r1(Math.max(...s.robots.map((r) => r.vibration))),
      temperature: r1(Math.max(...s.robots.map((r) => r.temperature))),
      throughput: Math.round(s.throughput),
    });
    if (s.history.length > HISTORY) s.history.shift();
  }

  function step(emit = true) {
    tick++;
    sites.forEach(stepSite);
    if (emit) {
      const snap = snapshot();
      listeners.forEach((h) => h.snapshot?.(snap));
    }
  }

  function siteView(s) {
    const failingNow = s.stopped || ROBOT_SCENARIOS.includes(s.scenario);
    return {
      id: s.def.id, name: s.def.name, city: s.def.city, state: s.def.state, lat: s.def.lat, lng: s.def.lng,
      type: s.profile.name, asset: s.profile.line, lines: s.def.lines,
      status: s.paused ? 'idle' : failingNow ? 'warning' : 'healthy',
      scenario: s.scenario, intensity: s.intensity, paused: s.paused,
      alerts: openAlerts(s),
      oee: r1(s.oee), throughput: Math.round(s.throughput), quality: r1(s.quality),
      robots: s.robots.map((r) => ({ id: r.id, name: r.name, status: r.status, temperature: r1(r.temperature), vibration: r1(r.vibration) })),
      history: s.history.slice(),
    };
  }

  function snapshot() {
    const views = sites.map(siteView);
    const total = views.reduce((n, v) => n + v.throughput, 0);
    const running = sites.reduce((n, s) => n + s.robots.filter((r) => r.status !== 'stopped').length, 0);
    return {
      timestamp: new Date().toISOString(),
      tick,
      sites: views,
      summary: {
        throughput: total,
        oee: r1(views.reduce((n, v) => n + v.oee, 0) / views.length),
        activeAlerts: alerts.filter((a) => !a.acknowledged).length,
        eventsPerSecond: Math.round(running * 6 + noise(8)),
        assets: sites.reduce((n, s) => n + s.robots.length, 0),
      },
      alerts: alerts.slice(0, 50),
    };
  }

  /* ── endpoints ── */
  function restore(s) {
    s.scenario = 'baseline';
    s.intensity = 0;
    s.target = -1;
    s.stopped = false;
    s.since = tick;
  }

  function simulate({ siteId, scenario = 'baseline', intensity = 85 }) {
    const s = find(siteId);
    if (scenario === 'baseline') {
      restore(s);
      addAlert(s, 'Scenario cleared: healthy operations restored', 'info', true);
      return { ok: true };
    }
    s.scenario = scenario;
    s.intensity = clamp(Number(intensity) || 0, 0, 100);
    s.since = tick;
    s.stopped = false;
    s.target = ROBOT_SCENARIOS.includes(scenario) ? Math.floor(Math.random() * s.robots.length) : -1;
    const r = s.robots[s.target];
    const sev = s.intensity / 100;
    const msg = {
      bearing: () => `${r.id} ${r.name}: bearing wear, vibration rising`,
      thermal: () => `${r.id} ${r.name}: motor temperature rising`,
      quality: () => `${r.id} ${r.name}: process drifting out of tolerance, rejects rising`,
      surge: () => `Demand surge: line rate raised to ${Math.round((1 + 0.45 * sev) * 100)}%`,
    }[scenario];
    if (!msg) throw new Error(`Unknown scenario ${scenario}`);
    addAlert(s, msg(), scenario === 'surge' ? 'warning' : sev >= TRIP_AT && scenario !== 'quality' ? 'critical' : 'warning');
    return { ok: true };
  }

  function control({ siteId, action }) {
    const s = find(siteId);
    if (action === 'pause') { s.paused = true; addAlert(s, 'Line paused by operator', 'info', true); }
    else if (action === 'resume') { s.paused = false; addAlert(s, 'Line resumed by operator', 'info', true); }
    else if (action === 'maintenance') {
      const r = s.robots[s.target];
      restore(s);
      s.paused = false;
      alerts.forEach((a) => { if (a.siteId === s.def.id) a.acknowledged = true; });
      addAlert(s, r ? `Maintenance completed on ${r.id} ${r.name}; line restarted` : 'Maintenance check completed', 'info', true);
    } else if (action === 'acknowledge') {
      alerts.forEach((a) => { if (a.siteId === s.def.id) a.acknowledged = true; });
    } else throw new Error(`Unknown action ${action}`);
    step();                                   // reflect the change right away
    return { result: { action, siteId, webhookDispatched: false } };
  }

  function context({ siteId, question = '' }) {
    const s = find(siteId), v = siteView(s);
    const q = question.toLowerCase();
    const worst = [...v.robots].sort((a, b) => (b.vibration / 2.2 + b.temperature / 45) - (a.vibration / 2.2 + a.temperature / 45))[0];
    const source = 'BROWSER SIMULATION · RULE-BASED ANSWER';
    if (/mainten|robot|attention|bearing|vibrat/.test(q)) {
      const bad = v.robots.find((r) => r.status === 'warning') || worst;
      const healthy = bad.status !== 'warning' && bad.vibration < 4 && bad.temperature < 60;
      return {
        source,
        title: healthy ? `No robot needs urgent maintenance at ${v.city}` : `${bad.id} (${bad.name}) needs attention`,
        answer: healthy
          ? `All six robots are within normal limits. The highest reading is ${bad.id} at ${bad.vibration} mm/s and ${bad.temperature} °C.`
          : `${bad.id} is running at ${bad.vibration} mm/s vibration and ${bad.temperature} °C. ${s.stopped ? 'It has tripped and the line is held until it is repaired.' : 'If the trend continues it will trip and stop the line.'}`,
        evidence: [`Vibration ${bad.vibration} mm/s`, `Temperature ${bad.temperature} °C`, `Status ${bad.status}`, `OEE ${v.oee}%`],
        suggestion: healthy ? 'Inject a bearing or thermal scenario to see predictive alerts.' : 'Use "Simulate repair" in the digital twin or "Schedule maintenance" in Actions.',
      };
    }
    if (/quality|defect|reject|scrap/.test(q)) {
      return {
        source,
        title: v.quality < 97 ? `Quality risk is elevated at ${v.city}` : `Quality is stable at ${v.city}`,
        answer: v.quality < 97
          ? `First-pass yield has dropped to ${v.quality}%. The drift traces to ${v.robots.find((r) => r.status === 'warning')?.id || 'one station'}; defective parts are flagged by inspection and rejected.`
          : `First-pass yield is ${v.quality}% and no station is drifting.`,
        evidence: [`First-pass yield ${v.quality}%`, `OEE ${v.oee}%`, `${v.alerts} open alerts`],
        suggestion: v.quality < 97 ? 'Restore healthy operations or schedule maintenance on the drifting robot.' : 'Inject a quality drift scenario to see rejects in the twin.',
      };
    }
    if (/energy|power|kw|consum/.test(q)) {
      const kw = v.robots.map((r) => (r.status === 'stopped' ? 0.4 : 2.6 + (r.temperature - 38) * 0.05));
      const total = kw.reduce((a, b) => a + b, 0);
      const top = v.robots[kw.indexOf(Math.max(...kw))];
      return {
        source,
        title: `${v.city} robots are drawing about ${r1(total)} kW`,
        answer: `Average ${r1(total / kw.length)} kW per robot. ${top.id} draws the most at ${r1(Math.max(...kw))} kW${top.temperature > 60 ? ', consistent with its high motor temperature' : ''}.`,
        evidence: v.robots.map((r, i) => `${r.id} ${r1(kw[i])} kW`),
        suggestion: 'Energy per unit rises when a robot runs hot or the line is held; clear faults to bring it back down.',
      };
    }
    const state = s.paused ? 'paused by an operator' : s.stopped ? 'stopped by a robot fault' : s.scenario === 'baseline' ? 'running normally' : `running under ${SCENARIO_NAME[s.scenario].toLowerCase()}`;
    return {
      source,
      title: `Operations briefing: ${v.name}`,
      answer: `The ${v.asset.toLowerCase()} is ${state}. OEE is ${v.oee}% at ${v.throughput} units/min with ${v.alerts} open alerts.`,
      evidence: [`OEE ${v.oee}%`, `${v.throughput} units/min`, `${v.robots.filter((r) => r.status === 'running').length}/6 robots running`, `${v.alerts} open alerts`],
      suggestion: s.scenario === 'baseline' ? 'Try injecting a scenario from the digital twin.' : 'Open the digital twin to see the affected robot.',
    };
  }

  async function call(path, body) {
    switch (path) {
      case 'bootstrap': return { snapshot: snapshot(), cloud, lastDerived: null };
      case 'simulate': { const r = simulate(body || {}); step(); return r; }
      case 'control': return control(body || {});
      case 'context': await sleep(350); return context(body || {});
      case 'mcp/tools':
      case 'mcp/call':
        throw new Error('The MCP explorer needs the Factory Pulse backend; it is not available in the browser simulation.');
      default:
        throw new Error(`/api/${path} is not available in the browser simulation.`);
    }
  }

  function subscribe(handlers) {
    listeners.add(handlers);
    handlers.cloud?.(cloud);
    return () => listeners.delete(handlers);
  }

  for (let i = 0; i < HISTORY; i++) step(false);        // start with a full trend history
  let timer = null;
  if (autoStart) timer = setInterval(() => step(), tickMs);

  return { call, subscribe, stop: () => clearInterval(timer), _step: step, _sites: sites };
}
