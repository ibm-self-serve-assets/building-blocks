# LINE-01 Machine Exception Response — Standard Operating Procedure

**SOP number:** MFG-SOP-LINE01-007  
**Revision:** 2.1  
**Effective date:** 2025-01-15  
**Approved by:** Plant Manager — Austin-01  
**Applies to:** All production staff and maintenance technicians on LINE-01

---

## 1. Purpose

This procedure defines the required response when a machine condition event on LINE-01 is correlated with production loss or quality deterioration. Its purpose is to:

- Protect product quality by preventing non-conforming parts from reaching assembly.
- Reduce mean time to resolution (MTTR) by following a consistent diagnostic sequence.
- Ensure all resolution findings are captured as enterprise knowledge events so future incidents can be resolved faster.

Current MTTR target for LINE-01 machine exceptions: **≤ 2 hours** from first alert to confirmed root cause.

---

## 2. Scope and applicability

This SOP applies when **two or more** of the following are true simultaneously:

1. Machine vibration exceeds the warning threshold for the asset class (see CNC-03 OEM Inspection Guide for CNC-03/04/07 thresholds).
2. Cycle time has increased by more than 10 % from the current shift baseline.
3. Defect rate (dimensional or surface) has risen above 3 % on parts produced after the anomaly onset.
4. Projected shift output has fallen more than 5 % below the 1,000-unit shift target.

A single-signal anomaly (vibration only, with normal quality and cycle time) is handled under Tier 1 monitoring. This SOP governs Tier 2 (multi-signal correlated) and Tier 3 (production stop) responses.

---

## 3. Immediate response — first 10 minutes

### 3.1 Operator actions

1. **Mark the deviation point.** Record the part serial number at which the anomaly was first confirmed. All parts produced after this serial number are "suspect" until cleared by quality inspection.
2. **Do not continue the job** until machine condition is assessed by maintenance, unless instructed otherwise by the shift supervisor.
3. **Raise a work order** in MES immediately. Assign to the on-call maintenance technician. Include: current vibration reading, current cycle time, defect rate, and the part serial number at deviation onset.
4. **Notify shift supervisor** and quality technician within 5 minutes of anomaly confirmation.

### 3.2 Shift supervisor actions

1. Confirm the exception has been raised in MES and a work order number assigned.
2. Assess production impact: how many units are at risk? Can any other machine on LINE-01 or LINE-02 absorb partial capacity?
3. Authorise quality hold on suspect parts (from deviation serial number forward) if defect rate ≥ 5 %.
4. Update the shift handover log with the exception details and current status.

---

## 4. Diagnostic response — 10 to 60 minutes

Follow the diagnostic sequence from the relevant asset-specific inspection guide:

- **CNC-03, CNC-04, CNC-07:** See *CNC-03 Spindle and Tooling Inspection Guide* (MFG-DOC-CNC-002).
- **Assembly fixtures:** See *LINE-01 Fixture Inspection Guide* (MFG-DOC-FIX-005).

**Critical rule:** Do not replace high-cost components (bearings, spindles, servo drives) before completing the tool-holder and alignment checks. The majority of vibration-plus-quality exceptions on this line in the past 24 months were resolved by tool-holder replacement, not bearing replacement.

Diagnostic decision gate: after completing tool-holder and alignment checks, if vibration has not returned to the normal operating band, escalate to Level 2 maintenance (spindle specialist) and request a full bearing spectrum analysis.

---

## 5. Resolution and knowledge capture — mandatory

Upon confirming root cause and completing corrective action, the technician **must** complete all of the following before closing the work order:

1. **Record in MES work order:**
   - Confirmed root cause (select from standard list + free text).
   - Corrective action taken (part replaced, procedure performed, specification applied).
   - Before/after measurements: vibration (mm/s), cycle time (s), defect rate (%) if applicable.
   - Parts returned to production: serial range re-instated after quality clearance.
   - Time to repair and technician ID.

2. **Publish a knowledge event** to the enterprise knowledge stream (`rag.knowledge.raw`). This is not optional — it is the mechanism by which the next technician facing the same failure mode gets the benefit of this resolution without a manual knowledge base search. The FactoryPulse Streamhouse indexes this event within seconds.

   Required fields in the knowledge event:
   - Title: `[WO number] [Asset] [Root cause summary]`
   - Asset ID: machine identifier
   - Text: full diagnostic narrative including measurements, actions, and lessons learned
   - Source: `maintenance-work-order`
   - Metadata: work order number, technician ID, shift number

3. **Clear quality hold** on suspect parts only after dimensional inspection confirms acceptability.

---

## 6. Escalation path

| Condition | Escalation target | Response time |
|---|---|---|
| Root cause not confirmed within 60 min | Level 2 Maintenance Specialist | 30 min on-site |
| Second same-asset exception within 7 days | Reliability Engineering review | Next business day |
| Production target < 800 units projected | Plant Manager notification | Immediate |
| Safety concern at any point | Safety Officer + machine lockout | Immediate |

---

## 7. Post-incident review

For any exception that caused more than 2 hours of downtime or more than 50 suspect parts, a brief post-incident review (PIR) is required within 5 business days. Output: updated inspection guide or SOP revision if the root cause was not covered by existing procedures.

The PIR finding must also be published as a knowledge event so the RAG system reflects the updated guidance.

---

## 8. Key performance indicators

| Metric | Target |
|---|---|
| Mean time to respond (first work order update) | ≤ 10 min |
| Mean time to root cause confirmed | ≤ 60 min |
| Mean time to repair (machine back in production) | ≤ 2 hrs |
| Knowledge event published within 30 min of WO closure | 100 % compliance |
| Repeat same-root-cause exceptions within 30 days | 0 |
