import urllib.request, json, time

base = "http://localhost:4000"

def get(path):
    return json.loads(urllib.request.urlopen(base+"/api/"+path, timeout=5).read())

def post(path, body):
    req = urllib.request.Request(base+"/api/"+path,
        data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

def site(data, sid="DET"):
    return next(s for s in data["snapshot"]["sites"] if s["id"]==sid)

results = []

# TEST 1: Bootstrap returns correct sourceMode
b = get("bootstrap")
sm = b["cloud"].get("sourceMode")
r1 = sm == "sim"
results.append(("Bootstrap sourceMode=sim on load", r1, f"sourceMode={sm}"))

# TEST 2: UI SIM mode - inject thermal, state updates directly
post("stream-mode", {"source":"sim"})
post("simulate", {"siteId":"DET","scenario":"baseline","intensity":50})
time.sleep(2)
post("simulate", {"siteId":"DET","scenario":"thermal","intensity":85})
time.sleep(3)
s = site(get("bootstrap"))
r2 = s["scenario"] == "thermal" and s["status"] == "warning"
results.append(("UI SIM: thermal inject updates state", r2,
    f"scenario={s['scenario']} status={s['status']} temp={s['robots'][0].get('temperature')}"))

# TEST 3: Toggle to KAFKA, consumer starts on-demand
resp = post("stream-mode", {"source":"kafka"})
r3 = resp.get("sourceMode") == "kafka" and resp.get("sourceConnected") == True
results.append(("KAFKA toggle: sourceConnected=True", r3,
    f"sourceMode={resp.get('sourceMode')} sourceConnected={resp.get('sourceConnected')}"))

# TEST 4: Reset to baseline
post("simulate", {"siteId":"DET","scenario":"baseline","intensity":50})
time.sleep(3)
s0 = site(get("bootstrap"))
r4 = s0["scenario"] == "baseline"
results.append(("Reset to baseline", r4,
    f"scenario={s0['scenario']} vibration={s0['robots'][0].get('vibration')}"))

# TEST 5: KAFKA mode - inject bearing, wait for roundtrip
sent_before = get("stream")["sent"]
post("simulate", {"siteId":"DET","scenario":"bearing","intensity":85})
time.sleep(7)
s_after = site(get("bootstrap"))
stream_after = get("stream")
sent_after = stream_after["sent"]
r5 = (s_after["scenario"] == "bearing" and
      s_after["status"] == "warning" and
      s_after["robots"][0].get("vibration", 0) > 3.0)
results.append(("KAFKA: bearing roundtrip updates state", r5,
    f"scenario={s_after['scenario']} status={s_after['status']} vibration={s_after['robots'][0].get('vibration')} msgs_sent={sent_after-sent_before}"))

# TEST 6: suppress_broadcast active in kafka+connected mode
r6 = stream_after.get("sourceMode") == "kafka" and stream_after.get("status") == "connected"
results.append(("suppress_broadcast active (kafka+connected)", r6,
    f"sourceMode={stream_after.get('sourceMode')} cloudStatus={stream_after.get('status')}"))

# TEST 7: Switch back to UI SIM, scenario persists
post("stream-mode", {"source":"sim"})
time.sleep(2)
s_sim = site(get("bootstrap"))
r7 = s_sim["scenario"] == "bearing"
results.append(("UI SIM: scenario persists after toggle back", r7,
    f"scenario={s_sim['scenario']} status={s_sim['status']}"))

# TEST 8: Final reset and verify clean state
post("simulate", {"siteId":"DET","scenario":"baseline","intensity":50})
time.sleep(3)
s_clean = site(get("bootstrap"))
r8 = s_clean["scenario"] == "baseline" and s_clean["status"] == "healthy"
results.append(("Final reset to healthy baseline", r8,
    f"scenario={s_clean['scenario']} status={s_clean['status']}"))

# PRINT RESULTS
print()
print("="*65)
print("  FACTORY PULSE -- END-TO-END TEST RESULTS")
print("="*65)
passed = 0
for name, ok, detail in results:
    icon = "PASS" if ok else "FAIL"
    print(f"  [{icon}] {name}")
    print(f"         {detail}")
    if ok:
        passed += 1
print("="*65)
print(f"  {passed}/{len(results)} tests passed")
print("="*65)
