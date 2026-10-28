import urllib.request, json, time

base = "http://localhost:4000"

def get(path):
    return json.loads(urllib.request.urlopen(base+"/api/"+path, timeout=5).read())

def post(path, body):
    req = urllib.request.Request(base+"/api/"+path,
        data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

def site(data, sid):
    return next((s for s in data["snapshot"]["sites"] if s["id"]==sid), None)

# Get all site IDs and scenarios from bootstrap
b = get("bootstrap")
all_sites = [s["id"] for s in b["snapshot"]["sites"]]
scenarios = ["bearing", "thermal", "quality", "surge", "baseline"]
print(f"Sites found: {all_sites}")
print(f"Scenarios  : {scenarios}")
print()

results = []

# ── PART 1: UI SIM MODE — all plants x all scenarios ─────────────────────────
print("="*65)
print("  PART 1: UI SIM MODE")
print("="*65)
post("stream-mode", {"source":"sim"})
time.sleep(1)

for sid in all_sites:
    for sc in scenarios:
        intensity = 85 if sc != "baseline" else 50
        post("simulate", {"siteId": sid, "scenario": sc, "intensity": intensity})
        time.sleep(2.5)  # wait for sim.step() tick
        s = site(get("bootstrap"), sid)
        if sc == "baseline":
            ok = s["scenario"] == "baseline" and s["status"] == "healthy"
        else:
            ok = s["scenario"] == sc and s["status"] == "warning"
        label = f"UI SIM [{sid}] scenario={sc}"
        detail = f"scenario={s['scenario']} status={s['status']}"
        results.append((label, ok, detail))
        icon = "PASS" if ok else "FAIL"
        print(f"  [{icon}] {label} => {detail}")

    # reset between sites
    post("simulate", {"siteId": sid, "scenario": "baseline", "intensity": 50})
    time.sleep(2)

# ── PART 2: KAFKA MODE — all plants x all scenarios ───────────────────────────
print()
print("="*65)
print("  PART 2: KAFKA MODE")
print("="*65)
resp = post("stream-mode", {"source":"kafka"})
print(f"  Toggle: sourceMode={resp.get('sourceMode')} sourceConnected={resp.get('sourceConnected')}")
time.sleep(1)

for sid in all_sites:
    for sc in scenarios:
        intensity = 85 if sc != "baseline" else 50
        # reset first
        post("simulate", {"siteId": sid, "scenario": "baseline", "intensity": 50})
        time.sleep(3)
        # inject
        post("simulate", {"siteId": sid, "scenario": sc, "intensity": intensity})
        time.sleep(7)  # wait for Kafka roundtrip
        s = site(get("bootstrap"), sid)
        if sc == "baseline":
            ok = s["scenario"] == "baseline"
        else:
            ok = s["scenario"] == sc and s["status"] == "warning"
        label = f"KAFKA  [{sid}] scenario={sc}"
        detail = f"scenario={s['scenario']} status={s['status']} vibration={s['robots'][0].get('vibration')}"
        results.append((label, ok, detail))
        icon = "PASS" if ok else "FAIL"
        print(f"  [{icon}] {label} => {detail}")

# ── FINAL RESET ───────────────────────────────────────────────────────────────
post("stream-mode", {"source":"sim"})
for sid in all_sites:
    post("simulate", {"siteId": sid, "scenario": "baseline", "intensity": 50})
time.sleep(3)

# ── SUMMARY ───────────────────────────────────────────────────────────────────
passed = sum(1 for _, ok, _ in results if ok)
failed = [(n, d) for n, ok, d in results if not ok]
print()
print("="*65)
print(f"  SUMMARY: {passed}/{len(results)} passed")
print("="*65)
if failed:
    print("  FAILURES:")
    for n, d in failed:
        print(f"    [FAIL] {n}")
        print(f"           {d}")
else:
    print("  All tests passed!")
print("="*65)
