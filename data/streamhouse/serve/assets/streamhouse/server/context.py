# Rule-based, deterministic fallback. This is NOT an LLM or Confluent RTCE response.
import re


def demo_answer(question, site):
    robots = site["robots"]
    bad = [r for r in robots if r["status"] == "warning"]
    q = str(question or "").lower()
    focus = site["name"]
    if re.search(r"maintenance|failure|risk|bearing|critical", q):
        return {
            "title": "Maintenance risk assessment",
            "risk": "Elevated" if bad else "Low",
            "answer": (
                f"{focus} has {len(bad)} assets above normal thresholds. {bad[0]['id']} currently reads "
                f"{bad[0]['vibration']:.2f} mm/s vibration and {bad[0]['temperature']:.1f}°C. "
                "A condition-based inspection is recommended before the next shift."
            ) if bad else f"No currently simulated threshold breach at {focus}. Continue condition monitoring; no urgent work order is indicated.",
            "evidence": [f"Scenario: {site['scenario']}", f"Active assets: {sum(1 for x in robots if x['status'] == 'running')}/{len(robots)}", f"Plant OEE: {site['oee']}%"],
            "suggestion": "Inspect affected equipment and schedule maintenance if confirmed.",
        }
    if re.search(r"quality|reject|yield", q):
        avg = sum(r["quality"] for r in robots) / len(robots)
        return {
            "title": "Quality and yield analysis",
            "risk": "Elevated" if any(r["quality"] < 86 for r in robots) else "Low",
            "answer": (
                f"The current simulated average quality score for {focus} is {avg:.1f}%. "
                + ("A deliberate inspection drift is active; check vision calibration and the current batch." if site["scenario"] == "quality" else "No significant quality drift is active.")
            ),
            "evidence": [f"Shift throughput: {site['throughput']} units/min", f"Scenario: {site['scenario']}"],
            "suggestion": "Review inspection calibration and quarantine suspect lots if necessary.",
        }
    if re.search(r"energy|power|consumption", q):
        return {
            "title": "Energy and utilization",
            "risk": "Informational",
            "answer": f"Estimated current modeled asset load for {focus}: {sum(r['energyKw'] for r in robots):.1f} kW. Utilization increases during surge conditions.",
            "evidence": [f"Plant OEE: {site['oee']}%", f"Active production lines: {site['lines']}"],
            "suggestion": "Compare production intensity with energy usage in your analytics lakehouse.",
        }
    return {
        "title": "Live operations briefing",
        "risk": "Attention" if bad else "Normal",
        "answer": (
            f"{focus} is reporting {site['oee']}% OEE and {site['throughput']} units/min throughput. "
            + (f"{len(bad)} robot(s) need attention." if bad else "All modeled robots are operating within normal sensor thresholds.")
            + " This is a demo-derived summary, not a query to Confluent RTCE."
        ),
        "evidence": [f"Active scenario: {site['scenario']}", f"Last telemetry: {__import__('datetime').datetime.now().strftime('%H:%M:%S')}"],
        "suggestion": "Select a fault scenario and compare live operational context.",
    }
