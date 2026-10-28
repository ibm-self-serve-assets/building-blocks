// ─────────────────────────────────────────────────────────────────────────────
// Turns the backend's plant state (site.scenario, site.robots[].status, …) into
// what the 3D line should do.
//
// A real failure starts in one machine, so a scenario is always shown on ONE
// robot, even when the backend flags several (or none):
//   • exactly one robot flagged      → that robot
//   • several / none flagged         → the clearly worst one by the scenario's
//                                       sensor (vibration / temperature); if none
//                                       stands out, a stable per-plant choice
// The choice is held until the scenario changes, so the fault never hops between
// robots as sensor readings fluctuate.
// ─────────────────────────────────────────────────────────────────────────────

// Robot-failure scenarios trip the line once severity reaches TRIP_AT.
// Below it the robot keeps running with a predictive alert.
export const TRIP_AT = 0.6;
const ROBOT_FAILURES = ['bearing', 'thermal'];
export const ISSUE_TEXT = {
  bearing: 'Bearing wear', thermal: 'Over-temperature', strain: 'Overload',
  quality: 'Quality drift', stopped: 'Stopped', fault: 'Fault',
};

const num = (v) => (Number.isFinite(Number(v)) ? Number(v) : 0);
const clamp01 = (v) => Math.min(1, Math.max(0, v));
const hash = (s) => [...String(s)].reduce((h, c) => (Math.imul(h, 31) + c.charCodeAt(0)) >>> 0, 7);

export function severityOf(site, fallback) {
  const raw = site?.intensity ?? site?.severity ?? site?.scenarioIntensity ?? fallback ?? 85;
  const n = num(raw);
  return clamp01(n > 1 ? n / 100 : n);
}

function pickRobot(robots, flagged, scenario, siteId) {
  const pool = flagged.length ? flagged : robots.map((_, i) => i);
  const metric = scenario === 'bearing' ? 'vibration' : scenario === 'thermal' || scenario === 'surge' ? 'temperature' : null;
  if (metric) {
    const vals = pool.map((i) => num(robots[i]?.[metric]));
    const max = Math.max(...vals), min = Math.min(...vals);
    if (max - min > Math.max(0.05 * Math.abs(max), 0.5)) return pool[vals.indexOf(max)];   // one robot clearly worst
  }
  return pool[hash(`${siteId}|${scenario}`) % pool.length];
}

export function createLineController() {
  let memo = { key: null, index: -1 };

  return function lineControl(site, severityFallback) {
    const robots = site?.robots || [];
    const scenario = site?.scenario || 'baseline';
    const sev = severityOf(site, severityFallback);
    const paused = !!site?.paused || site?.status === 'idle';
    const conds = robots.map(() => null);
    const out = { robots: conds, paused, rate: scenario === 'surge' ? 1 + 0.45 * sev : 1, focus: -1 };
    if (!robots.length) return out;

    const flagged = robots.map((r, i) => (r?.status === 'warning' || r?.status === 'stopped' ? i : -1)).filter((i) => i >= 0);

    if (scenario === 'baseline') {
      memo = { key: null, index: -1 };
      // healthy operations: only an explicit robot stop (outside a line pause) counts as a failure
      if (!paused) {
        const s = robots.findIndex((r) => r?.status === 'stopped');
        if (s >= 0) { conds[s] = { issue: 'stopped', severity: 1, trip: true }; out.focus = s; }
      }
      return out;
    }
    if (scenario === 'surge' && !flagged.length) return out;      // pure throughput change: the whole line speeds up

    const key = `${site.id}|${scenario}`;
    const index = flagged.length === 1 ? flagged[0] : memo.key === key ? memo.index : pickRobot(robots, flagged, scenario, site.id);
    memo = { key, index };

    const r = robots[index];
    let c;
    if (r?.status === 'stopped' && !paused) c = { issue: 'stopped', severity: 1, trip: true };
    else if (ROBOT_FAILURES.includes(scenario)) c = { issue: scenario, severity: sev, trip: sev >= TRIP_AT && (flagged.length > 0 || site.status === 'warning') };
    else if (scenario === 'quality') c = { issue: 'quality', severity: sev, defectRate: 0.25 + 0.45 * sev };
    else if (scenario === 'surge') c = { issue: 'strain', severity: sev };
    else c = { issue: 'fault', severity: 1, trip: true };
    conds[index] = c;
    out.focus = index;
    return out;
  };
}
