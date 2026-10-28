"""
Browser-path simulation test — mimics exactly what the browser does:
1. Fetches /api/bootstrap (as the browser would on first load)
2. Opens /api/events SSE and collects snapshots for 10 seconds
3. Posts /api/simulate (bearing, 85%) and watches for state change via SSE
4. Checks the snapshot arrives via SSE (not local sim)
5. Toggles to KAFKA, injects, waits for Kafka roundtrip via SSE
"""
import urllib.request, json, time, threading

base = "http://localhost:4000"

def get(path):
    return json.loads(urllib.request.urlopen(base+"/api/"+path, timeout=5).read())

def post(path, body):
    req = urllib.request.Request(base+"/api/"+path,
        data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

results = []

# ── TEST 1: Fresh bootstrap returns sourceMode=sim ───────────────────────────
b = get("bootstrap")
cloud = b["cloud"]
r1 = cloud.get("sourceMode") == "sim"
r1b = cloud.get("status") == "connected"
r1c = cloud.get("mode") == "kafka"
results.append(("Bootstrap: sourceMode=sim", r1, f"sourceMode={cloud.get('sourceMode')}"))
results.append(("Bootstrap: cloud connected", r1b, f"status={cloud.get('status')} mode={cloud.get('mode')}"))
results.append(("Bootstrap: mode=kafka (not browser sim)", r1c, f"mode={cloud.get('mode')}"))

# ── TEST 2: SSE stream delivers snapshot events ───────────────────────────────
# Open SSE and collect events for 5 seconds
post("stream-mode", {"source":"sim"})
post("simulate", {"siteId":"DET","scenario":"baseline","intensity":50})
time.sleep(2)

snapshots = []
errors = []

def collect_sse(duration=5):
    try:
        req = urllib.request.Request(base+"/api/events",
            headers={"Accept":"text/event-stream","Cache-Control":"no-cache"})
        resp = urllib.request.urlopen(req, timeout=duration+2)
        deadline = time.monotonic() + duration
        buf = ""
        while time.monotonic() < deadline:
            chunk = resp.read(1024).decode("utf-8", errors="ignore")
            if not chunk:
                break
            buf += chunk
            for line in buf.split("\n"):
                if line.startswith("data:"):
                    try:
                        snapshots.append(json.loads(line[5:].strip()))
                    except Exception:
                        pass
            buf = ""
    except Exception as e:
        errors.append(str(e))

t = threading.Thread(target=collect_sse, args=(5,))
t.start()
t.join(8)

r2 = len(snapshots) >= 2  # should receive multiple ticks in 5 seconds
results.append(("SSE /api/events delivers snapshots", r2, f"snapshots_received={len(snapshots)} errors={errors}"))

# ── TEST 3: Inject in UI SIM mode — snapshot reflects change via SSE ─────────
snapshots_after = []

def collect_after_inject(duration=5):
    try:
        req = urllib.request.Request(base+"/api/events",
            headers={"Accept":"text/event-stream","Cache-Control":"no-cache"})
        resp = urllib.request.urlopen(req, timeout=duration+2)
        deadline = time.monotonic() + duration
        buf = ""
        while time.monotonic() < deadline:
            chunk = resp.read(1024).decode("utf-8", errors="ignore")
            if not chunk:
                break
            buf += chunk
            for line in buf.split("\n"):
                if line.startswith("data:"):
                    try:
                        snapshots_after.append(json.loads(line[5:].strip()))
                    except Exception:
                        pass
            buf = ""
    except Exception:
        pass

t2 = threading.Thread(target=collect_after_inject, args=(5,))
t2.start()
time.sleep(0.3)
post("simulate", {"siteId":"DET","scenario":"bearing","intensity":85})
t2.join(7)

bearing_snaps = [s for s in snapshots_after
                 if any(site.get("scenario")=="bearing"
                        for site in s.get("sites",[]) if site.get("id")=="DET")]
r3 = len(bearing_snaps) >= 1
results.append(("UI SIM: bearing scenario arrives via SSE", r3,
    f"bearing_snapshots={len(bearing_snaps)} total_snapshots={len(snapshots_after)}"))

# ── TEST 4: KAFKA mode — Kafka roundtrip arrives via SSE ─────────────────────
post("simulate", {"siteId":"DET","scenario":"baseline","intensity":50})
time.sleep(3)
resp_toggle = post("stream-mode", {"source":"kafka"})
r4a = resp_toggle.get("sourceConnected") == True
results.append(("KAFKA toggle: sourceConnected", r4a, f"sourceConnected={resp_toggle.get('sourceConnected')}"))

kafka_snaps = []

def collect_kafka_snaps(duration=9):
    try:
        req = urllib.request.Request(base+"/api/events",
            headers={"Accept":"text/event-stream","Cache-Control":"no-cache"})
        resp = urllib.request.urlopen(req, timeout=duration+2)
        deadline = time.monotonic() + duration
        buf = ""
        while time.monotonic() < deadline:
            chunk = resp.read(1024).decode("utf-8", errors="ignore")
            if not chunk:
                break
            buf += chunk
            for line in buf.split("\n"):
                if line.startswith("data:"):
                    try:
                        kafka_snaps.append(json.loads(line[5:].strip()))
                    except Exception:
                        pass
            buf = ""
    except Exception:
        pass

t3 = threading.Thread(target=collect_kafka_snaps, args=(9,))
t3.start()
time.sleep(0.5)
post("simulate", {"siteId":"DET","scenario":"bearing","intensity":85})
t3.join(12)

kafka_bearing = [s for s in kafka_snaps
                 if any(site.get("scenario")=="bearing" and site.get("status")=="warning"
                        for site in s.get("sites",[]) if site.get("id")=="DET")]
r4b = len(kafka_bearing) >= 1
results.append(("KAFKA: bearing arrives via SSE roundtrip", r4b,
    f"bearing_snaps={len(kafka_bearing)} total_snaps={len(kafka_snaps)}"))

# ── RESET ─────────────────────────────────────────────────────────────────────
post("stream-mode", {"source":"sim"})
post("simulate", {"siteId":"DET","scenario":"baseline","intensity":50})

# ── PRINT RESULTS ─────────────────────────────────────────────────────────────
passed = sum(1 for _,ok,_ in results if ok)
print()
print("="*65)
print("  FACTORY PULSE -- BROWSER PATH TEST")
print("="*65)
for name, ok, detail in results:
    icon = "PASS" if ok else "FAIL"
    print(f"  [{icon}] {name}")
    print(f"         {detail}")
print("="*65)
print(f"  {passed}/{len(results)} tests passed")
print("="*65)
