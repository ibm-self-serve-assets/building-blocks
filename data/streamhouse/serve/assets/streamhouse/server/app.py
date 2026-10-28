"""Factory Pulse backend — Python (Flask) rewrite of the original Node/Express server.

Serves the API and, in production, the compiled frontend from dist/ in the same process.
"""
import json
import os
import queue
import threading
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

load_dotenv()

from context import demo_answer
from kafka import ConfluentTransport
from mcp import with_mcp
from plants import PLANTS, SCENARIOS
from simulation import FactorySimulation

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"), static_url_path="/")
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
app.config["JSON_SORT_KEYS"] = False
CORS(app)

sim = FactorySimulation()
cloud = ConfluentTransport()
_clients: set = set()
_last_derived = None
_source_mode = os.environ.get("KAFKA_CONSUME_SOURCE") == "true"  # runtime-togglable


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def broadcast(event, data):
    msg = f"event: {event}\ndata: {json.dumps(data)}\n\n"
    dead = []
    for q in list(_clients):
        try:
            q.put_nowait(msg)
        except Exception:
            dead.append(q)
    for q in dead:
        _clients.discard(q)


def _on_derived(value):
    global _last_derived
    _last_derived = value
    broadcast("flink", value)


def _on_source(msg):
    """Merge a Kafka source message into the live sim snapshot and broadcast to UI."""
    global _source_mode
    if not _source_mode:
        return
    topic = msg.get("topic", "")
    value = msg.get("value") or {}
    try:
        if topic == "factory-iot-telemetry" or topic == "factory-asset-state":
            site_id = value.get("siteId")
            asset_id = value.get("assetId")
            if not site_id or not asset_id:
                return
            site_state = sim.sites.get(site_id)
            if not site_state:
                return
            for robot in site_state["robots"]:
                if robot["id"] == asset_id:
                    if "temperature" in value:
                        robot["temperature"] = value["temperature"]
                    if "vibration" in value:
                        robot["vibration"] = value["vibration"]
                    if "rpm" in value:
                        robot["rpm"] = value["rpm"]
                    if "energyKw" in value:
                        robot["energyKw"] = value["energyKw"]
                    if "qualityScore" in value:
                        robot["quality"] = value["qualityScore"]
                    if "health" in value:
                        robot["health"] = value["health"]
                    if "status" in value:
                        robot["status"] = value["status"]
                    break
            # update site scenario if present
            if "scenario" in value:
                site_state["scenario"] = value["scenario"]
            broadcast("snapshot", sim.snapshot())

        elif topic == "factory-maintenance-events":
            alert = {
                "id": value.get("eventId", f"KFK-{int(__import__('time').time()*1000)}"),
                "timestamp": value.get("timestamp", now_iso()),
                "siteId": value.get("siteId", ""),
                "siteName": value.get("siteId", ""),
                "assetId": value.get("assetId", ""),
                "type": value.get("eventType", "UNKNOWN"),
                "severity": value.get("severity", "warning"),
                "message": value.get("message", "Event from Kafka"),
                "acknowledged": value.get("acknowledged", False),
            }
            # avoid duplicate ids
            if not any(a["id"] == alert["id"] for a in sim.alerts):
                sim.alerts.insert(0, alert)
                sim.alerts = sim.alerts[:45]
                broadcast("alert", alert)
                broadcast("snapshot", sim.snapshot())
    except Exception as exc:
        print("Source merge error:", exc)


sim.subscribe(lambda event, data: broadcast(event, data))
cloud.on_derived = _on_derived
cloud.on_source = _on_source


def _cloud_info():
    info = cloud.info()
    info["lastDerived"] = _last_derived
    info["sourceMode"] = "kafka" if _source_mode else "sim"
    return info


@app.get("/api/health")
def health():
    return jsonify({
        "ok": True,
        "server": "Factory Pulse",
        "time": now_iso(),
        "stream": cloud.info(),
        "mcpConfigured": bool(os.environ.get("RTCE_MCP_ENDPOINT") and os.environ.get("RTCE_MCP_BASIC_TOKEN")),
        "googleMapsConfigured": bool(os.environ.get("VITE_GOOGLE_MAPS_API_KEY")),
    })


@app.get("/api/bootstrap")
def bootstrap():
    return jsonify({
        "snapshot": sim.snapshot(),
        "scenarios": SCENARIOS,
        "plants": PLANTS,
        "cloud": _cloud_info(),
        "mcpConfigured": bool(os.environ.get("RTCE_MCP_ENDPOINT") and os.environ.get("RTCE_MCP_BASIC_TOKEN")),
        "lastDerived": _last_derived,
    })


@app.get("/api/events")
def events():
    q = queue.Queue()
    _clients.add(q)

    def generate():
        try:
            yield f"event: snapshot\ndata: {json.dumps(sim.snapshot())}\n\n"
            while True:
                try:
                    yield q.get(timeout=18)
                except queue.Empty:
                    yield ": heartbeat\n\n"
        finally:
            _clients.discard(q)

    return app.response_class(generate(), mimetype="text/event-stream",
                              headers={"Cache-Control": "no-cache, no-transform", "Connection": "keep-alive"})


@app.post("/api/simulate")
def simulate():
    try:
        body = request.get_json(silent=True) or {}
        result = sim.inject(body.get("siteId"), body.get("scenario"), body.get("intensity", 75))
        return jsonify({"ok": True, "result": result})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/control")
def control():
    try:
        body = request.get_json(silent=True) or {}
        site_id = body.get("siteId")
        action = body.get("action")
        robot_id = body.get("robotId")
        result = sim.act(site_id, action, robot_id)
        if os.environ.get("ACTION_WEBHOOK_URL") and action == "maintenance":
            webhook = os.environ["ACTION_WEBHOOK_URL"]
            if not webhook.startswith("https://"):
                raise ValueError("Action webhook URL must be HTTPS")
            import urllib.request
            token = os.environ.get("ACTION_WEBHOOK_TOKEN")
            headers = {"Content-Type": "application/json"}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            req = urllib.request.Request(webhook, data=json.dumps(result).encode(), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status >= 400:
                    raise ValueError(f"Webhook returned {resp.status}")
            result["webhookDispatched"] = True
        return jsonify({"ok": True, "result": result})
    except Exception as exc:
        return jsonify({"error": str(exc), "note": "The local simulation may already have changed; external workflow failed."}), 400


@app.post("/api/context")
def context():
    try:
        body = request.get_json(silent=True) or {}
        site_id = body.get("siteId")
        site = next((s for s in sim.snapshot()["sites"] if s["id"] == site_id), None)
        if not site:
            return jsonify({"error": "Unknown factory"}), 400
        answer = demo_answer(body.get("question", ""), site)
        return jsonify({"source": "LOCAL DEMO RULES — NOT MCP/LLM", **answer})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/mcp/tools")
def mcp_tools():
    try:
        response = with_mcp(lambda client: client.list_tools())
        tools = []
        for t in getattr(response, "tools", []) or []:
            tools.append({"name": getattr(t, "name", ""), "description": getattr(t, "description", ""),
                          "inputSchema": getattr(t, "inputSchema", {})})
        return jsonify({"connected": True, "tools": tools})
    except Exception as exc:
        return jsonify({"connected": False, "error": str(exc)}), 503


@app.post("/api/mcp/call")
def mcp_call():
    try:
        body = request.get_json(silent=True) or {}
        name = body.get("name")
        args = body.get("args")
        if not isinstance(name, str) or len(name) > 150 or not __import__("re").match(r"^[-_a-zA-Z0-9.]+$", name):
            return jsonify({"error": "Invalid MCP tool name"}), 400
        if not (isinstance(args, dict) and args):
            args = {}
        result = with_mcp(lambda client: client.call_tool(name, arguments=args))
        return jsonify({"source": "CONFLUENT RTCE MCP", "result": result})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502


@app.post("/api/stream-mode")
def set_stream_mode():
    global _source_mode
    try:
        body = request.get_json(silent=True) or {}
        source = body.get("source")
        if source not in ("kafka", "sim"):
            return jsonify({"error": "source must be 'kafka' or 'sim'"}), 400
        _source_mode = source == "kafka"
        # Start the source consumer on-demand when switching to Kafka mode.
        # This covers the case where KAFKA_CONSUME_SOURCE was not set at startup.
        if _source_mode and cloud.status == "connected" and cloud.source_consumer is None:
            try:
                cloud._connect_source()
            except Exception as exc:
                print("Source consumer start error:", exc)
        broadcast("cloud", _cloud_info())
        return jsonify({"ok": True, "sourceMode": "kafka" if _source_mode else "sim",
                        "sourceConnected": cloud.source_consumer is not None})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/stream")
def stream():
    return jsonify({**cloud.info(), "lastDerived": _last_derived, "sourceMode": "kafka" if _source_mode else "sim"})


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_static(path):
    if path.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    root = app.static_folder
    if path != "index.html" and root and os.path.isfile(os.path.join(root, path)):
        return send_from_directory(root, path)
    if root and os.path.isfile(os.path.join(root, "index.html")):
        return send_from_directory(root, "index.html")
    return jsonify({"error": "Frontend not built. Run `npm run build` first."}), 404


def _publisher_loop(stop: threading.Event, interval: float):
    while not stop.is_set():
        if stop.wait(interval):
            break
        try:
            kafka_wanted = _source_mode
            kafka_live = cloud.status == "connected"

            # In Kafka mode: suppress the direct sim→SSE path so only the
            # Kafka consumer roundtrip drives the UI.
            # In UI SIM mode (or Kafka unavailable fallback): allow direct emit.
            sim.suppress_broadcast = kafka_wanted and kafka_live

            batch = sim.step()
            cloud.publish(batch)

            # Fallback: Kafka was wanted but is not connected — emit snapshot
            # directly so the UI keeps updating and the badge shows the fallback state.
            if kafka_wanted and not kafka_live:
                broadcast("snapshot", sim.snapshot())

            broadcast("cloud", _cloud_info())
        except Exception as exc:  # keep the demo loop alive
            print("Publish error:", exc)


_shutdown = threading.Event()


def _startup():
    cloud.connect()
    # If source consumer is requested at startup but connect() didn't wire it
    # (e.g. KAFKA_CONSUME_SOURCE was set after initial connect), wire it now.
    if os.environ.get("KAFKA_CONSUME_SOURCE") == "true" and cloud.status == "connected" and cloud.source_consumer is None:
        try:
            cloud._connect_source()
        except Exception as exc:
            print("Source consumer startup error:", exc)
    interval = max(0.5, float(os.environ.get("SIM_INTERVAL_MS", "1700")) / 1000)
    t = threading.Thread(target=_publisher_loop, args=(_shutdown, interval), daemon=True)
    t.start()

    def retry():
        while not _shutdown.is_set():
            if _shutdown.wait(15):
                break
            if cloud.mode == "kafka" and cloud.status in ("error", "disconnected"):
                try:
                    cloud.connect()
                    broadcast("cloud", cloud.info())
                except Exception:
                    pass

    threading.Thread(target=retry, daemon=True).start()


def _shutdown_server():
    _shutdown.set()
    cloud.disconnect()


# Start the background simulation loop when the module is imported (gunicorn / flask run / python app.py).
_startup()


def create_app():
    return app


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "4000")), threaded=True)
    finally:
        _shutdown_server()
