import math
import os
import time
from datetime import datetime, timezone

from plants import PLANTS, ROBOT_TYPES


def clamp(n, a, b):
    return max(a, min(b, n))


def r(x, d=1):
    return round(float(x), d)


def now():
    return datetime.now(timezone.utc).isoformat()


class FactorySimulation:
    def __init__(self, random=None):
        import random as _random
        self.random = random if random is not None else _random.random
        self.tick = 0
        self.paused = False
        self.sites = {}
        for i, p in enumerate(PLANTS):
            self.sites[p["id"]] = {
                # scenario starts at baseline with zero intensity; OEE seeded from
                # the plant's own realistic baseline rather than a shared constant.
                "scenario": "baseline", "intensity": 0, "paused": False, "stopped": False,
                "seed": i, "output": 0, "oee": r(p["oee_base"]), "history": [],
                "robots": [
                    {"id": f"{p['id']}-R{str(j + 1).zfill(2)}", "name": ROBOT_TYPES[j],
                     "status": "running", "health": 99 - j, "rpm": 1800, "vibration": 1.2,
                     "temperature": 36, "energyKw": 12, "quality": 99.1}
                    for j in range(6)
                ],
            }
        self.events = []
        self.alerts = []
        self.actions = []
        self.listeners = set()
        self.last_batch = []
        self.suppress_broadcast = False  # set True in Kafka mode so step() doesn't push snapshot directly

    def subscribe(self, fn):
        self.listeners.add(fn)
        return lambda: self.listeners.discard(fn)

    def emit(self, event, payload):
        for fn in list(self.listeners):
            fn(event, payload)

    def inject(self, site_id, scenario, intensity=75):
        s = self.sites.get(site_id)
        if not s:
            raise ValueError("Unknown factory")
        if scenario not in ("baseline", "bearing", "thermal", "quality", "surge"):
            raise ValueError("Invalid scenario")
        s["scenario"] = scenario
        s["intensity"] = clamp(float(intensity) if intensity is not None else 75, 1, 100)
        s["paused"] = False
        # Clearing a fault via baseline also clears any protective stop.
        if scenario == "baseline":
            s["stopped"] = False
        self.emit("scenario", {"siteId": site_id, "scenario": scenario, "intensity": s["intensity"]})
        return {"siteId": site_id, "scenario": scenario, "intensity": s["intensity"]}

    def act(self, site_id, action, robot_id=None):
        s = self.sites.get(site_id)
        if not s:
            raise ValueError("Unknown factory")
        if action not in ("pause", "resume", "maintenance", "acknowledge"):
            raise ValueError("Invalid action")
        if action == "pause":
            s["paused"] = True
        if action == "resume":
            s["paused"] = False
            s["stopped"] = False
            s["scenario"] = "baseline"
        if action == "maintenance":
            s["scenario"] = "baseline"
            s["paused"] = False
            s["stopped"] = False
            for robot in s["robots"]:
                robot["health"] = 99
        if action == "acknowledge":
            for a in self.alerts:
                if a["siteId"] == site_id:
                    a["acknowledged"] = True
        result = {"id": f"ACT-{int(time.time() * 1000)}", "timestamp": now(), "siteId": site_id, "action": action, "robotId": robot_id, "mode": "simulation"}
        self.actions.insert(0, result)
        self.actions = self.actions[:50]
        self.emit("action", result)
        return result

    def step(self):
        if self.paused:
            return []
        self.tick += 1
        batch = []
        generated = []
        for p in PLANTS:
            s = self.sites[p["id"]]
            severity = 0 if s["scenario"] == "baseline" else s["intensity"] / 100
            mod = {"baseline": 0, "bearing": 1, "thermal": 2, "quality": 3, "surge": 4}[s["scenario"]]
            sin = math.sin(self.tick / 4 + s["seed"])

            # A protective fault stop freezes the line: treat as fully stopped for
            # sensor purposes until maintenance clears it.
            line_down = s["paused"] or s["stopped"]

            temp_base = 35 + max(0, (severity * 51 if mod == 2 else severity * 8)) + sin * 1.6
            vibration_base = 1.1 + (severity * 7.3 if mod == 1 else severity * 0.9) + abs(sin) * 0.32
            quality_base = 99.3 - (severity * 24 if mod == 3 else severity * 1.8) + sin * 0.35

            # OEE target is anchored to the plant's own realistic baseline, not a
            # shared constant, so sites maintain distinct identities at steady state.
            target_oee = clamp(
                p["oee_base"]
                - (severity * 17 if mod == 1 else 0)
                - (severity * 23 if mod == 2 else 0)
                - (severity * 21 if mod == 3 else 0)
                + (severity * 2  if mod == 4 else 0),
                45, 99,
            )
            # Fault trip collapses OEE toward zero; operator pause holds it (planned stop).
            if s["stopped"]:
                target_oee = 0
            s["oee"] = r(s["oee"] * 0.67 + target_oee * 0.33)

            # Throughput uses a per-plant unit rate that reflects the product type,
            # and is zeroed on both operator pause AND fault trip.
            base_rate = p["rate"] * p["lines"]
            throughput = 0 if line_down else round(
                base_rate * ((1 + severity * 0.25) if mod == 4 else 1) * (s["oee"] / 100)
            )
            s["output"] += throughput
            s["history"].append({"t": self.tick, "output": throughput, "oee": s["oee"], "temp": r(temp_base), "vibration": r(vibration_base, 2), "quality": r(quality_base)})
            if len(s["history"]) > 55:
                s["history"].pop(0)

            any_robot_tripped = False
            for j in range(len(s["robots"])):
                robot = s["robots"][j]
                noise = (self.random() - 0.5) * 0.6
                temp = r(temp_base + noise * 3 + j * 0.55)
                vibration = r(vibration_base + noise * 0.5 + j * 0.06, 2)

                # RPM drops to zero on operator pause OR fault trip (not just pause).
                rpm = 0 if line_down else round(1800 + (severity * 420 if mod == 4 else 0) - severity * 95 + math.sin(self.tick / 2 + j) * 25)

                health = clamp(round(99 - (severity * 43 if mod == 1 else 0) - (severity * 30 if mod == 2 else 0) - (severity * 19 if mod == 3 else 0) + noise * 2 - j * 0.5), 15, 100)

                # Energy falls to standby on operator pause OR fault trip (not just pause).
                energy_kw = r(1.5 if line_down else 12 + (severity * 4.5 if mod == 4 else 0) + (severity * 3 if mod == 2 else 0) + j * 0.6, 1)

                quality = r(clamp(quality_base + noise, 55, 100), 1)
                flag = (not line_down) and (temp > 72 or vibration > 5.2 or quality < 86)

                if line_down:
                    # Operator-paused → "stopped"; fault-tripped → keep existing
                    # robot status so the tripped robot remains visible as "warning".
                    if s["paused"]:
                        robot["status"] = "stopped"
                    # s["stopped"] case: leave robot["status"] as-is (warning / running)
                else:
                    robot["status"] = "warning" if flag else "running"

                robot.update(temperature=temp, vibration=vibration, rpm=rpm, health=health, energyKw=energy_kw, quality=quality)

                # Trip detection: if a robot just entered "warning" on a fault scenario,
                # check whether severity is high enough to trigger a protective line stop.
                if flag and not s["stopped"] and mod in (1, 2) and severity >= 0.6:
                    s["stopped"] = True
                    any_robot_tripped = True

                if j == (self.tick + s["seed"]) % 6 or j == (self.tick + s["seed"] + 3) % 6:
                    batch.append({
                        "topic": "factory-iot-telemetry",
                        "key": {"id": robot["id"]},
                        "value": {
                            "eventId": f"{p['id']}-{self.tick}-{j}", "timestamp": now(), "siteId": p["id"], "siteName": p["name"],
                            "assetId": robot["id"], "assetType": robot["name"], "lineId": f"LINE-{j % 3 + 1}",
                            "scenario": s["scenario"], "temperature": temp, "vibration": vibration, "rpm": rpm, "energyKw": energy_kw,
                            "qualityScore": quality, "health": health, "status": robot["status"],
                            "batchId": f"BATCH-{int(self.tick / 12) + 1001}",
                        },
                    })
            if self.tick % 3 == 0:
                for robot in s["robots"][:3]:
                    batch.append({
                        "topic": "factory-asset-state",
                        "key": {"id": robot["id"]},
                        "value": {"assetId": robot["id"], "siteId": p["id"], "timestamp": now(), "status": robot["status"],
                                  "health": robot["health"], "temperature": robot["temperature"], "vibration": robot["vibration"],
                                  "qualityScore": robot["quality"], "scenario": s["scenario"]},
                    })
            if (not line_down) and s["scenario"] != "baseline" and self.tick % 5 == 0 and severity >= 0.35:
                kind = {"bearing": "BEARING_RISK", "thermal": "OVERHEAT", "quality": "QUALITY_DRIFT", "surge": "CAPACITY_PRESSURE"}[s["scenario"]]
                alert = {
                    "id": f"AL-{p['id']}-{self.tick}", "timestamp": now(), "siteId": p["id"], "siteName": p["name"],
                    "assetId": s["robots"][0]["id"], "type": kind,
                    "severity": "critical" if s["intensity"] >= 70 else "warning",
                    "message": {
                        "bearing": "Abnormal spindle vibration detected",
                        "thermal": "Temperature exceeds safe operating envelope",
                        "quality": "First-pass yield is trending below target",
                        "surge": "Line utilization above planned capacity",
                    }[s["scenario"]],
                    "acknowledged": False,
                }
                self.alerts.insert(0, alert)
                self.alerts = self.alerts[:45]
                generated.append(alert)
                batch.append({
                    "topic": "factory-maintenance-events",
                    "key": {"id": alert["id"]},
                    "value": {"eventId": alert["id"], "timestamp": alert["timestamp"], "siteId": alert["siteId"],
                              "assetId": alert["assetId"], "eventType": alert["type"], "severity": alert["severity"],
                              "message": alert["message"], "acknowledged": False},
                })
        self.last_batch = batch
        self.events = [e["value"] for e in batch if e["topic"] == "factory-iot-telemetry"] + self.events
        self.events = self.events[:90]
        snapshot = self.snapshot()
        if not self.suppress_broadcast:
            self.emit("snapshot", snapshot)
        for a in generated:
            self.emit("alert", a)
        return batch

    def snapshot(self):
        sites = []
        total_lines = sum(p["lines"] for p in PLANTS)
        for p in PLANTS:
            s = self.sites[p["id"]]
            alerts = [a for a in self.alerts if a["siteId"] == p["id"] and not a["acknowledged"]]
            sites.append({
                **p, "scenario": s["scenario"], "intensity": s["intensity"],
                "paused": s["paused"], "stopped": s["stopped"], "oee": s["oee"],
                "throughput": s["history"][-1]["output"] if s["history"] else 0, "output": s["output"],
                "alerts": len(alerts),
                # A fault-tripped line is "warning" (not idle); idle is only operator pause.
                "status": "idle" if s["paused"] else ("warning" if (s["stopped"] or any(r["status"] == "warning" for r in s["robots"])) else "healthy"),
                "robots": [dict(r) for r in s["robots"]], "history": list(s["history"]),
            })
        # Network OEE weighted by number of lines so larger plants count more.
        weighted_oee = r(sum(sv["oee"] * p["lines"] for sv, p in zip(sites, PLANTS)) / total_lines)
        return {
            "tick": self.tick, "timestamp": now(), "paused": self.paused, "sites": sites,
            "alerts": self.alerts[:25], "actions": self.actions[:20],
            "recentEvents": self.events[:32],
            "summary": {
                "plants": len(sites),
                "assets": sum(len(s2["robots"]) for s2 in sites),
                "throughput": sum(s2["throughput"] for s2 in sites),
                "oee": weighted_oee,
                "activeAlerts": sum(1 for a in self.alerts if not a["acknowledged"]),
                # eventsPerSecond derived from the actual telemetry messages in the last batch.
                "eventsPerSecond": r(len(self.last_batch) / (max(250, float(os.environ.get("SIM_INTERVAL_MS", "1700"))) / 1000)),
            },
        }
