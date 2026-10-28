import urllib.request, json, time, threading

base = "http://localhost:4000"

def post(path, body):
    req = urllib.request.Request(base+"/api/"+path,
        data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=5).read())

# Reset to UI SIM / baseline
post("stream-mode", {"source":"sim"})
post("simulate", {"siteId":"DET","scenario":"baseline","intensity":50})
time.sleep(2)

received = []

def listen(secs=7):
    try:
        req = urllib.request.Request(base+"/api/events",
            headers={"Accept":"text/event-stream"})
        r = urllib.request.urlopen(req, timeout=secs+2)
        deadline = time.monotonic() + secs
        buf = ""
        while time.monotonic() < deadline:
            chunk = r.read(512).decode("utf-8", errors="ignore")
            if not chunk:
                break
            buf += chunk
            for line in buf.split("\n"):
                if line.startswith("data:"):
                    try:
                        d = json.loads(line[5:].strip())
                        det = next((s for s in d.get("sites",[]) if s["id"]=="DET"), None)
                        if det:
                            received.append({
                                "scenario": det["scenario"],
                                "status": det["status"],
                                "vibration": det["robots"][0].get("vibration")
                            })
                    except Exception:
                        pass
            buf = ""
    except Exception as e:
        print("SSE error:", e)

t = threading.Thread(target=listen, args=(7,))
t.start()
time.sleep(0.5)
post("simulate", {"siteId":"DET","scenario":"bearing","intensity":85})
print("Injected bearing scenario at t=0.5s")
t.join(10)

print("Received", len(received), "SSE snapshots:")
for i, s in enumerate(received):
    print("  [{}] scenario={} status={} vibration={}".format(i, s["scenario"], s["status"], s["vibration"]))

# Check if bearing arrived
bearing_found = any(s["scenario"] == "bearing" and s["status"] == "warning" for s in received)
print()
print("RESULT:", "PASS - bearing scenario arrived via SSE" if bearing_found else "FAIL - bearing never arrived in SSE stream")
