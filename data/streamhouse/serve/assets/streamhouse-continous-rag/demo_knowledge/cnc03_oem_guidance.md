# CNC-03 Spindle and Tooling Inspection Guide

**Asset class:** CNC Machining Centre — 5-axis vertical spindle  
**Applies to:** CNC-03, CNC-04, CNC-07 (LINE-01, LINE-02)  
**Document owner:** Maintenance Engineering  
**Revision:** 4.2 | Last updated by: J. Hartley, Senior Maintenance Engineer

---

## 1. Vibration thresholds and action levels

| Vibration (mm/s RMS) | Classification | Required action |
|---|---|---|
| 0.0 – 2.5 | Normal operating band | Continue production |
| 2.6 – 3.5 | Monitor | Increase monitoring frequency to every 30 min |
| 3.6 – 4.5 | Warning | Schedule inspection at next safe stop within 4 hours |
| 4.6 – 5.5 | High — production risk | Stop machine at next part completion; do not start new job |
| > 5.5 | Critical — quality and safety risk | Immediate safe stop; do not continue until root cause confirmed |

Vibration alone is not sufficient to determine root cause. Always correlate with cycle time trend and dimensional inspection results before deciding which component to replace.

---

## 2. Inspection sequence — vibration onset

When vibration rises above the warning threshold (3.6 mm/s), follow this sequence. Do not skip steps or reorder them — premature bearing replacement on a tool-holder imbalance case has been observed twice on this line in the past 18 months.

### Step 1 — Tool and tool-holder inspection (15–20 min)

1. Power down spindle and apply LOTO procedure LOTO-CNC-03-001 before touching any tooling.
2. Remove the active tool assembly (tool + holder + retention knob).
3. Inspect tool holder bore for chips, burrs, or visible wear on the taper contact surface. Acceptance criterion: no visible score marks; taper contact area ≥ 85 % blued contact.
4. Check tool holder balance class. LINE-01 specification: G2.5 at 25,000 RPM for all holders used above 12,000 RPM spindle speed. Holders outside this specification must be removed from service.
5. Measure tool runout at 50 mm gauge length using a dial indicator. Acceptance limit: ≤ 0.003 mm TIR. Readings > 0.005 mm TIR indicate holder damage or contamination.
6. If tool holder fails any criterion above: replace with a balanced spare (see Tooling Store, rack T-07), recalibrate, and test-run at reduced feed before resuming production.

### Step 2 — Spindle bearing condition check (10–15 min)

1. With spindle cold, spin spindle by hand. It should rotate freely with no roughness or intermittent drag.
2. Attach accelerometer to spindle housing at bearing location (front and rear). Record baseline spectrum.
3. Compare spectrum to last known-good baseline stored in MES asset history for CNC-03.
4. Key indicators of bearing degradation: elevated broadband noise floor above 2 kHz; ball-pass frequency harmonics; sudden change in 1× or 2× runout magnitude.
5. Check lubrication port. Oil-air mist lubricator should show flow indicator green. Blocked lubricator can cause rapid bearing degradation — this was the root cause in WO-10552 bearing failure.

### Step 3 — Alignment and thermal check (20 min)

1. Check spindle-to-table perpendicularity using a precision test bar (500 mm) and indicator. Acceptance: ≤ 0.010 mm over 300 mm.
2. Inspect spindle nose for contamination (coolant, chips). Clean with lint-free cloth and inspect for corrosion.
3. Record spindle temperature at bearing housing. If temperature > 65 °C at idle, suspect lubrication or overload condition.

### Step 4 — Test part and dimensional validation

1. Run a controlled test part using the most recent approved NC programme.
2. Inspect critical dimensions: bore diameter ±0.010 mm, surface finish Ra ≤ 1.6 µm, positional tolerance ≤ 0.015 mm.
3. If dimensional results are within tolerance and vibration has returned to normal operating band after tool-holder replacement, the machine is cleared for production.
4. Document findings in MES under asset CNC-03, work order number, and technician ID.

---

## 3. Common root cause patterns on this asset

| Observed symptom | Most likely cause | Secondary check |
|---|---|---|
| Vibration ↑ with dimensional drift, cycle time stable | Tool-holder imbalance or damage | Check holder balance, runout |
| Vibration ↑ with cycle time ↑, quality normal | Spindle bearing or drive issue | Bearing spectrum, servo load |
| Vibration ↑ after tooling change | Wrong holder spec or contamination | Balance class, taper contact |
| Vibration ↑ gradually over weeks | Bearing wear — lubrication check | Lube flow indicator, oil sample |
| Vibration spike during cut, normal at idle | Interrupted cut or chip impaction | Tool condition, chip evacuation |

---

## 4. Spare parts — CNC-03

| Part | Part number | Location | Lead time |
|---|---|---|---|
| Spindle bearing (front) | SKF-7018-BECBP | Stores bin B-14 | Same day |
| Spindle bearing (rear) | SKF-7015-BECBP | Stores bin B-14 | Same day |
| Balanced tool holder BT-40 | SANDVIK-390.140-4032 | Tooling rack T-07 | Same day |
| Retention knob (standard) | BILZ-RK-BT40-M16 | Tooling rack T-07 | Same day |
| Spindle oil-air lubricator filter | BIJUR-F-50 | Maintenance store M-03 | 2 days |

---

## 5. Maintenance history notes

- **WO-10552 (3 months ago):** Spindle bearing replaced after vibration rose to 4.8 mm/s. Root cause confirmed as bearing wear accelerated by blocked lubricator filter (part BIJUR-F-50). Filter replaced simultaneously. Lesson: always check lubricator when replacing bearing.
- **WO-10871 (CNC-07, 6 weeks ago):** Tool-holder imbalance — vibration and dimensional drift together. Tool holder replaced; machine returned to spec without bearing replacement.
- **Recommendation:** When vibration rises together with dimensional drift, always inspect tool holder before opening the spindle. This sequence has saved an average of 3.5 hours of unplanned downtime per incident on this line.
