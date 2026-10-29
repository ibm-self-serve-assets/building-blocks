// ─────────────────────────────────────────────────────────────────────────────
// Single entry point for every /api call and the live event stream.
//
// • Backend reachable  → behaves exactly as before (fetch + EventSource).
// • Backend not there   → switches to the browser simulation in localBackend.js
//                         the first time /api/bootstrap can't be reached.
//
// Override with an env var in .env:
//   VITE_LOCAL_SIM=true   always use the browser simulation
//   VITE_LOCAL_SIM=false  never fall back (backend only)
// ─────────────────────────────────────────────────────────────────────────────
import { createLocalBackend } from './localBackend.js';

const pref = import.meta.env?.VITE_LOCAL_SIM;
let mode = pref === 'true' ? 'local' : 'auto';       // auto → remote or local after the first call
let local = null;
const browserSim = () => (local ??= createLocalBackend());

export const getMode = () => mode;

class Unreachable extends Error {}

async function remote(path, body) {
  let res;
  const token = typeof window !== 'undefined' ? sessionStorage.getItem('fp-token') : null;
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  try {
    res = await fetch(`/api/${path}`, {
      method: body === undefined ? 'GET' : 'POST',
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (e) {
    throw new Unreachable(e.message);
  }
  let data;
  try { data = await res.json(); } catch { throw new Unreachable(`/api/${path} answered ${res.status} without JSON`); }
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

export async function call(path, body) {
  if (mode === 'local') return browserSim().call(path, body);
  try {
    const data = await remote(path, body);
    mode = 'remote';
    return data;
  } catch (e) {
    // Only fall back to the browser simulation if:
    //   1. The backend was genuinely unreachable (not just a slow response)
    //   2. We have never successfully reached the backend (mode !== 'remote')
    //   3. The user has not explicitly disabled fallback (pref !== 'false')
    // Once mode='remote' is set by a successful bootstrap, we NEVER fall back —
    // this prevents the browser sim from taking over after a momentary blip.
    if (e instanceof Unreachable && mode !== 'remote' && pref !== 'false') {
      if (mode !== 'local') console.info('[Factory Pulse] Backend not reachable, running the browser simulation.');
      mode = 'local';
      return browserSim().call(path, body);
    }
    // If mode is already 'remote' and we get an error, re-throw so the UI
    // shows the real error rather than silently switching to local sim.
    throw e;
  }
}

// While on the browser simulation, keep checking for the backend. As soon as /api/bootstrap
// answers, switch to it (live data wins) and hand the fresh bootstrap to onFound.
export function watchForBackend(onFound, everyMs = 15000) {
  if (pref === 'true') return () => {};
  const id = setInterval(async () => {
    if (mode !== 'local') return;
    try {
      const data = await remote('bootstrap');
      mode = 'remote';
      local?.stop();
      local = null;
      clearInterval(id);
      console.info('[Factory Pulse] Backend is now reachable, switched to live data.');
      onFound(data);
    } catch { /* still unreachable: stay on the simulation */ }
  }, everyMs);
  return () => clearInterval(id);
}

// handlers: { snapshot, cloud, flink, error } — returns a function that closes the stream
export function openStream(handlers) {
  // Only use the browser sim if we are firmly in local mode.
  // If mode is 'remote' or 'auto' (bootstrap succeeded), always use the real SSE endpoint.
  if (mode === 'local') return browserSim().subscribe(handlers);
  const es = new EventSource('/api/events');
  es.addEventListener('snapshot', (e) => handlers.snapshot?.(JSON.parse(e.data)));
  es.addEventListener('cloud', (e) => handlers.cloud?.(JSON.parse(e.data)));
  es.addEventListener('flink', (e) => handlers.flink?.(JSON.parse(e.data)));
  es.onerror = () => handlers.error?.();
  return () => es.close();
}
