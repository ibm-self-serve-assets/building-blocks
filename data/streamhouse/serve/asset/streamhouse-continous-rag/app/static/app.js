const state = { snapshot: null, config: null };

const views = {
  overview: ["Operations Overview", "A live manufacturing control tower powered by a continuous Confluent data backbone."],
  rag: ["Continuous RAG", "Ask against knowledge that changes as maintenance and operations change."],
  knowledge: ["Knowledge Stream", "Publish new factory knowledge as events and watch the retrieval layer refresh."],
  streamhouse: ["Streamhouse Architecture", "Operational streams, continuous knowledge, and analytical tables on one event backbone."],
  events: ["Live Events", "See the business change as events rather than waiting for the next batch refresh."],
  settings: ["Runtime Settings", "Configuration status without exposing credentials."],
};

function $(id){ return document.getElementById(id); }
function esc(value){ return String(value ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function fmtTime(value){ if(!value) return "—"; try { return new Date(value).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'}); } catch { return value; } }
function titleCase(value){ return String(value || "").replace(/_/g," ").replace(/\b\w/g, m => m.toUpperCase()); }

function toast(message, isError=false){
  const el = $("toast"); el.textContent = message; el.classList.toggle("error", isError); el.classList.add("show");
  clearTimeout(window.__toastTimer); window.__toastTimer = setTimeout(() => el.classList.remove("show"), 3200);
}

async function api(path, options={}){
  const headers = {"Content-Type":"application/json", ...(options.headers||{})};
  const apiKey = sessionStorage.getItem("fp_api_key") || localStorage.getItem("fp_api_key") || (window.DEMO_API_KEY || "");
  if(apiKey){
    headers["X-API-Key"] = apiKey;
  }
  const response = await fetch(path, {headers, ...options});
  const data = await response.json().catch(() => ({}));
  if(!response.ok) throw new Error(data.detail || `${response.status} ${response.statusText}`);
  return data;
}

function switchView(name){
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(v => v.classList.remove("active"));
  $("view-"+name).classList.add("active");
  document.querySelector(`.nav-item[data-view="${name}"]`)?.classList.add("active");
  $("pageTitle").textContent = views[name][0]; $("pageSubtitle").textContent = views[name][1];
  window.scrollTo({top:0, behavior:"smooth"});
}

document.querySelectorAll(".nav-item").forEach(btn => btn.addEventListener("click", () => switchView(btn.dataset.view)));
document.querySelectorAll("[data-jump-rag]").forEach(btn => btn.addEventListener("click", () => switchView("rag")));

document.querySelectorAll("[data-prompt]").forEach(btn => btn.addEventListener("click", () => { $("questionInput").value = btn.dataset.prompt; }));

document.querySelectorAll("[data-step]").forEach(btn => btn.addEventListener("click", async () => {
  btn.disabled = true;
  try {
    const result = await api(`/api/demo/step/${btn.dataset.step}`, {method:"POST"});
    toast(`Demo step: ${btn.dataset.step}`);
    if(result.knowledge_update) toast("Resolution note streamed into Continuous RAG knowledge.");
  } catch(err){ toast(err.message, true); }
  finally { btn.disabled = false; }
}));

$("seedButton").addEventListener("click", async () => {
  $("seedButton").disabled = true;
  try { const result = await api("/api/demo/seed-knowledge", {method:"POST"}); toast(`Seeded ${result.count} knowledge documents.`); }
  catch(err){ toast(err.message, true); }
  finally { $("seedButton").disabled = false; }
});

$("knowledgeForm").addEventListener("submit", async (event) => {
  event.preventDefault(); $("knowledgeStatus").textContent = "Publishing…";
  const body = {title: $("knowledgeTitle").value, text: $("knowledgeText").value, source:"operator-upload", asset_id: $("knowledgeAsset").value || null, metadata:{ui:true}};
  try { await api("/api/knowledge", {method:"POST", body:JSON.stringify(body)}); $("knowledgeStatus").textContent = "Published to Kafka"; toast("Knowledge event published. Index will refresh continuously."); }
  catch(err){ $("knowledgeStatus").textContent = "Publish failed"; toast(err.message, true); }
});

$("askButton").addEventListener("click", async () => {
  const question = $("questionInput").value.trim(); if(!question) return;
  $("askButton").disabled = true; $("askStatus").textContent = "Retrieving freshest evidence…";
  $("answerText").textContent = "Working…";
  try {
    const result = await api("/api/rag/ask", {method:"POST", body:JSON.stringify({question, top_k:4})});
    renderAnswer(result); $("askStatus").textContent = `${result.evidence.length} evidence chunks retrieved`; toast("Grounded answer generated from current knowledge.");
  } catch(err){ $("answerText").textContent = err.message; $("askStatus").textContent = "Request failed"; toast(err.message, true); }
  finally { $("askButton").disabled = false; }
});

function renderAnswer(result){
  $("answerText").textContent = result.answer;
  $("latencyBadge").textContent = `${result.latency_ms} ms`;
  $("retrievalMode").textContent = `Retrieval: ${result.retrieval_mode}`;
  $("generationMode").textContent = `Generation: ${result.generation_mode}`;
  renderDataTrace(result);
  const grid = $("evidenceGrid");
  if(!result.evidence?.length){ grid.innerHTML = '<div class="empty-state">No evidence matched this question.</div>'; return; }
  const nowMs = Date.now();
  grid.innerHTML = result.evidence.map((e, i) => {
    const updMs = e.updated_at ? new Date(e.updated_at).getTime() : 0;
    const isNew = updMs && (nowMs - updMs) < 60000;
    return `
    <article class="evidence-card${isNew?' evidence-new':''}">
      <span class="score">E${i+1} &middot; score ${esc(e.score)}${isNew?' <span class="badge-new">NEW</span>':''}</span>
      <h4>${esc(e.title)}</h4>
      <p>${esc(e.text.slice(0, 500))}${e.text.length>500?'&hellip;':''}</p>
      <footer>${esc(e.source)} &middot; ${esc(e.asset_id || 'enterprise knowledge')} &middot; ${fmtTime(e.updated_at)}</footer>
    </article>`;
  }).join("");
}

function renderDataTrace(result){
  const el = $("dataTrace");
  if(!el) return;
  const ev = result.evidence || [];
  const now = new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'});

  const steps = [
    {
      icon: "1",
      label: "Knowledge documents streamed to Kafka",
      topic: "rag.knowledge.raw",
      detail: ev.length
        ? ev.map((e,i) => `[E${i+1}] <strong>${esc(e.title)}</strong> &mdash; source: <code>${esc(e.source)}</code>, asset: <code>${esc(e.asset_id||'n/a')}</code>, indexed: ${fmtTime(e.updated_at)}`).join('<br>')
        : 'No evidence documents retrieved.',
      color: "blue"
    },
    {
      icon: "2",
      label: "Continuous indexer chunked + embedded documents",
      topic: "rag.knowledge.embeddings",
      detail: `Each document was split into chunks (size=850 chars, overlap=120) and embedded using the <code>${esc(result.retrieval_mode)}</code> pipeline. Chunks were produced to the compacted <code>rag.knowledge.embeddings</code> Kafka topic. The in-memory vector index was rebuilt by replaying this topic from offset 0 on app start.`,
      color: "cyan"
    },
    {
      icon: "3",
      label: `Question embedded &amp; top-${ev.length} chunks retrieved`,
      topic: "vector index",
      detail: `Question embedded using the same model as the knowledge chunks. Cosine similarity search over ${$("indexedChunks")?.textContent||'?'} indexed chunks returned ${ev.length} evidence chunk(s):`
        + (ev.length ? '<br>' + ev.map((e,i)=>`&nbsp;&nbsp;E${i+1}: score <strong>${esc(e.score)}</strong> &mdash; chunk_id <code>${esc(e.chunk_id.slice(0,16))}…</code> from doc <code>${esc(e.document_id)}</code>`).join('<br>') : ''),
      color: "green"
    },
    {
      icon: "4",
      label: "Answer generated by LLM with evidence as context",
      topic: result.generation_mode,
      detail: `Retrieved chunks were passed as grounded context to <code>${esc(result.generation_mode)}</code>. The model was instructed to cite evidence inline as [E1], [E2], etc., and answer only from retrieved content. Total round-trip: <strong>${esc(result.latency_ms)} ms</strong> (Kafka retrieval ~0 ms + LLM generation ~${esc(result.latency_ms)} ms).`,
      color: "purple"
    }
  ];

  el.innerHTML = steps.map((s,i) => `
    <div class="trace-step">
      <div class="trace-step-head">
        <span class="trace-num trace-${s.color}">${s.icon}</span>
        <span class="trace-label">${s.label}</span>
        <code class="trace-topic">${esc(s.topic)}</code>
      </div>
      <div class="trace-body">${s.detail}</div>
    </div>`).join('<div class="trace-connector"></div>');

  // stamp time
  const stamp = $("traceTimestamp");
  if(stamp) stamp.textContent = `Traced at ${now}`;
}

function renderSnapshot(snapshot){
  state.snapshot = snapshot; const s = snapshot.factory_state || {};
  $("lastUpdated").textContent = `UPDATED ${fmtTime(s.ts)}`;
  $("projectedUnits").textContent = s.projected_units ?? "—";
  $("vibration").textContent = s.vibration_mm_s ?? "—";
  $("cycleTime").textContent = s.cycle_time_sec ?? "—";
  $("defectRate").textContent = s.defect_rate_pct ?? "—";
  $("machineHealth").textContent = titleCase(s.machine_health || "waiting");
  $("rootSignal").textContent = s.root_signal || "Waiting for factory events…";
  $("recommendationText").textContent = s.recommendation || "Continue monitoring.";
  $("indexedChunks").textContent = snapshot.indexed_chunks ?? 0;
  $("ragFreshnessSub").textContent = `${snapshot.indexed_chunks ?? 0} chunks currently indexed`;
  $("documentCount").textContent = snapshot.documents?.length ?? 0;
  $("vibrationBar").style.width = `${Math.min(100, ((s.vibration_mm_s || 0) / 7) * 100)}%`;
  $("cycleDelta").textContent = s.cycle_time_sec ? `${Math.round(((s.cycle_time_sec-42)/42)*100)}% vs 42 s baseline` : "Baseline 42 s";
  $("qualityRisk").textContent = `Quality risk: ${titleCase(s.quality_risk || '—')}`;
  $("signalMachine").textContent = titleCase(s.machine_health || "—");
  $("signalProduction").textContent = titleCase(s.production_risk || "—");
  $("signalQuality").textContent = titleCase(s.quality_risk || "—");

  // Machine LED colour driven from machine_health
  const led = $("machineLed");
  if(led){
    const health = (s.machine_health || "").toLowerCase();
    led.className = "machine-led " + (
      health === "critical"    ? "led-critical" :
      health === "degraded"    ? "led-degraded" :
      health === "maintenance" ? "led-maintenance" :
      health === "resolved" || health === "healthy" ? "led-healthy" :
      "led-idle"
    );
  }

  const risk = (s.overall_risk || "low").toLowerCase(); const pill = $("riskPill"); pill.textContent = risk.toUpperCase(); pill.className = `risk-pill ${risk}`;
  $("heroRisk").textContent = risk === "critical" ? "Production and quality need action" : risk === "medium" || risk === "high" ? "Factory risk is building" : "Live production intelligence";

  renderExceptions(snapshot.exceptions || []); renderDocuments(snapshot.documents || []); renderEvents(snapshot.events || []); renderConfig(snapshot.config || {});
}

function renderExceptions(items){
  const el = $("exceptionList"); if(!items.length){ el.innerHTML = '<div class="empty-state">No recent exceptions.</div>'; return; }
  el.innerHTML = items.slice(0,6).map(item => `<div class="timeline-item"><span class="timeline-dot ${esc(item.severity)}"></span><div><strong>${esc(item.title)}</strong><p>${esc(item.description)}</p></div><time>${fmtTime(item.ts)}</time></div>`).join("");
}

function renderDocuments(items){
  const el = $("documentList"); if(!items.length){ el.innerHTML = '<div class="empty-state">No knowledge documents yet. Seed the demo or publish one.</div>'; return; }
  el.innerHTML = [...items].reverse().slice(0,10).map(item => `<div class="document-card"><strong>${esc(item.title)}</strong><p>${esc(item.source)} · ${esc(item.asset_id || 'all assets')} · ${fmtTime(item.updated_at)}</p></div>`).join("");
}

function renderEvents(items){
  const el = $("eventFeed"); if(!items.length){ el.innerHTML = '<div class="empty-state">Waiting for events.</div>'; return; }
  el.innerHTML = items.slice(0,30).map(item => { const d=item.data||{}; const summary = d.title || d.root_signal || d.document_id || d.machine_id || JSON.stringify(d).slice(0,100); const ts=d.ts||d.updated_at; return `<div class="event-row"><code>${esc(item.type)}</code><span>${esc(summary)}</span><time>${fmtTime(ts)}</time></div>`; }).join("");
}

function renderConfig(config){
  state.config=config;
  $("settingKafka").textContent = config.kafka_configured ? "Configured" : "Missing";
  const srActive = config.effective_serialization_mode === 'schema-registry-json';
  $("settingSchema").textContent = config.schema_registry_configured
    ? (srActive ? "Active (schema-registry-json)" : "Configured · plain-json override")
    : "Optional / missing";
  $("settingRag").textContent = titleCase(config.rag_pipeline_mode || "—");
  $("settingLlm").textContent = config.watsonx_configured ? "watsonx.ai" : titleCase(config.llm_provider || "grounded template");
  $("ragModeLabel").textContent = config.rag_pipeline_mode === 'flink' ? 'Flink AI embeddings' : 'Kafka-backed continuous index';
  if($("settingTableflow")) $("settingTableflow").textContent = config.tableflow_enabled ? "Enabled" : "Disabled (set TABLEFLOW_ENABLED=true)";
}

async function probeKafka(){
  const chip = $("kafkaChip");
  chip.innerHTML = '<span class="dot"></span>Checking…';
  try {
    const result = await api("/api/kafka/probe");
    if(result.connected){
      chip.innerHTML = `<span class="dot ok"></span>Confluent connected · ${esc(result.latency_ms)} ms · ${esc(result.factorypulse_topics)} topics`;
    } else {
      chip.innerHTML = `<span class="dot error"></span>Kafka unreachable: ${esc(result.error || 'probe failed')}`;
    }
  } catch(err){
    chip.innerHTML = `<span class="dot error"></span>Kafka probe error`;
  }
}

async function loadInitial(){
  try { const snapshot = await api("/api/dashboard"); renderSnapshot(snapshot); }
  catch(err){ toast(err.message, true); }
}

const source = new EventSource("/api/events/stream");
source.addEventListener("snapshot", event => { try { renderSnapshot(JSON.parse(event.data)); } catch(e) { console.error(e); } });
source.onerror = () => { $("kafkaChip").innerHTML='<span class="dot"></span>Live feed reconnecting'; };

// ── Auth (client-side session only — no server verification) ─────────────────
const AUTH_KEY  = "fp_session_user";
const SIDEBAR_KEY = "fp_sidebar_v2_collapsed"; // versioned key to discard old broken state

function getUser(){
  try { return JSON.parse(sessionStorage.getItem(AUTH_KEY)); } catch{ return null; }
}

function applyUser(user){
  $("userAvatar").textContent = user.initials;
  $("userName").textContent   = user.name;
  $("userRole").textContent   = user.role;
  $("loginOverlay").classList.add("hidden");
}

function doLogin(name, role, initials){
  name = (name || "").trim();
  if(!name) return;
  const user = {
    name,
    role: (role || "").trim() || "Operator",
    initials: initials || name.split(" ").map(w => w[0].toUpperCase()).slice(0,2).join("")
  };
  sessionStorage.setItem(AUTH_KEY, JSON.stringify(user));
  applyUser(user);
}

function doLogout(){
  sessionStorage.removeItem(AUTH_KEY);
  $("userAvatar").textContent = "?";
  $("userName").textContent   = "Not signed in";
  $("userRole").textContent   = "—";
  $("loginOverlay").classList.remove("hidden");
  $("loginName").value = "";
  $("loginRole").value = "";
}

document.querySelectorAll(".preset-btn").forEach(btn => {
  btn.addEventListener("click", () => doLogin(btn.dataset.name, btn.dataset.role, btn.dataset.initials));
});
$("loginSubmit").addEventListener("click", () => doLogin($("loginName").value, $("loginRole").value, ""));
["loginName","loginRole"].forEach(id => {
  $(id).addEventListener("keydown", e => { if(e.key==="Enter") doLogin($("loginName").value, $("loginRole").value, ""); });
});
$("logoutBtn").addEventListener("click", doLogout);

// Restore session (or show login modal if none)
(function initAuth(){
  const user = getUser();
  if(user) applyUser(user);
  // else login overlay is visible by default (no class="hidden" in HTML)
})();

// ── Sidebar collapse ──────────────────────────────────────────────────────────
function applySidebarState(collapsed){
  document.querySelector(".shell").classList.toggle("sidebar-collapsed", collapsed);
  if(collapsed) sessionStorage.setItem(SIDEBAR_KEY, "1");
  else          sessionStorage.removeItem(SIDEBAR_KEY);
}

$("sidebarToggle").addEventListener("click", () => {
  applySidebarState(!document.querySelector(".shell").classList.contains("sidebar-collapsed"));
});

applySidebarState(sessionStorage.getItem(SIDEBAR_KEY) === "1");

loadInitial();
probeKafka();
setInterval(probeKafka, 15000);
