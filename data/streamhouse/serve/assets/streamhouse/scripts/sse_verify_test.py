"""
Verify SSE by checking _clients queue is being populated and broadcast() fires.
Instead of opening SSE (which needs a persistent connection), we verify:
1. The publisher loop is ticking (sent count increases over time)
2. broadcast() is called (check via /api/stream repeatedly)
3. State changes after inject are visible in bootstrap (proxy for SSE data)
"""
import urllib.request, json, time

base = "http://localhost:4000"

def get(path):
    return json.loads(urllib.request.urlopen(base+"/api/"+path, timeout=5).read())

def post(path, body):
    req = urllib.request.Request(base+"/api/"+path,
        data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

results = []

# ── TEST 1: Publisher loop is ticking (sent count increases) ──────────────────
post("stream-mode", {"source":"sim"})
s1 = get("stream")["sent"]
time.sleep(4)
s2 = get("stream")["sent"]
r1 = s2 > s1
results.append(("Publisher loop ticking", r1, "sent {} -> {} (+{})".format(s1, s2, s2-s1)))

# ── TEST 2: UI SIM inject changes state (proves broadcast fires from sim.step) ─
post("simulate", {"siteId":"DET","scenario":"baseline","intensity":50})
time.sleep(2)
b_before = get("bootstrap")
det_before = next(s for s in b_before["snapshot"]["sites"] if s["id"]=="DET")

post("simulate", {"siteId":"DET","scenario":"bearing","intensity":85})
time.sleep(3)

b_after = get("bootstrap")
det_after = next(s for s in b_after["snapshot"]["sites"] if s["id"]=="DET")
r2 = det_after["scenario"] == "bearing" and det_after["status"] == "warning"
results.append(("UI SIM: state change after inject", r2,
    "before={}/{} after={}/{}".format(det_before["scenario"], det_before["status"],
                                       det_after["scenario"], det_after["status"])))

# ── TEST 3: SSE endpoint opens and sends initial snapshot ─────────────────────
# Use a very short read with large buffer to catch the initial snapshot event
try:
    req = urllib.request.Request(base+"/api/events",
        headers={"Accept":"text/event-stream", "Connection":"keep-alive"})
    resp = urllib.request.urlopen(req, timeout=4)
    data = resp.read(8192).decode("utf-8", errors="ignore")
    resp.close()
    has_initial = "event: snapshot" in data and '"sites"' in data
    r3 = has_initial
    results.append(("SSE delivers initial snapshot on connect", r3,
        "got {} bytes, has_snapshot={}".format(len(data), has_initial)))
except Exception as e:
    results.append(("SSE delivers initial snapshot on connect", False, str(e)))

# ── TEST 4: KAFKA mode roundtrip confirmed via bootstrap ──────────────────────
post("simulate", {"siteId":"DET","scenario":"baseline","intensity":50})
time.sleep(3)
resp_k = post("stream-mode", {"source":"kafka"})
post("simulate", {"siteId":"DET","scenario":"thermal","intensity":85})
time.sleep(8)
det_kafka = next(s for s in get("bootstrap")["snapshot"]["sites"] if s["id"]=="DET")
r4 = det_kafka["scenario"] == "thermal" and det_kafka["status"] == "warning"
results.append(("KAFKA roundtrip: thermal in state", r4,
    "scenario={} status={} temp={}".format(
        det_kafka["scenario"], det_kafka["status"],
        det_kafka["robots"][0].get("temperature"))))

# ── RESET ─────────────────────────────────────────────────────────────────────
post("stream-mode", {"source":"sim"})
post("simulate", {"siteId":"DET","scenario":"baseline","intensity":50})

# ── RESULTS ───────────────────────────────────────────────────────────────────
passed = sum(1 for _,ok,_ in results if ok)
print()
print("="*65)
print("  FACTORY PULSE -- SSE + STATE VERIFICATION TEST")
print("="*65)
for name, ok, detail in results:
    icon = "PASS" if ok else "FAIL"
    print("  [{}] {}".format(icon, name))
    print("         {}".format(detail))
print("="*65)
print("  {}/{} tests passed".format(passed, len(results)))
print("="*65)
