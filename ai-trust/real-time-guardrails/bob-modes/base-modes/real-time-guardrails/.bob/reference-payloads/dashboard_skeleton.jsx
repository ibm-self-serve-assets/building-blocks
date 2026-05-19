// Production-flavored guardrail dashboard.
//
// Data source: GET /api/audit/recent — backend endpoint that reads the
// AuditLogger JSONL file (see backend_guardrails_proxy.py).
//
// Structurally similar to the smart-supplier-selection-demo's dashboard.jsx,
// but data source is the server-side audit log, NOT localStorage.
//
// What it renders:
//   - Top: summary stacked bar (Pass / Flag / Block counts)
//   - Middle: per-metric MUI LinearProgress bars (avg score + counts)
//   - Bottom: expandable transaction history table
//
// Polls every 30 s. For sub-second latency: replace polling with WebSockets
// or server-sent events from the backend (out of scope for this reference).
//
// Pair with backend_guardrails_proxy.py for the /api/audit/recent endpoint.

import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  Box,
  Chip,
  Collapse,
  IconButton,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";

const AUDIT_ENDPOINT = "/api/audit/recent?limit=500";
const POLL_INTERVAL_MS = 30_000;

// =====================================================================
// Aggregation helpers — pure functions, no React state
// =====================================================================

/** Average score per metric across all records. Returns Map<metricName, avg>. */
function avgScorePerMetric(records) {
  const sums = new Map();
  const counts = new Map();
  for (const rec of records) {
    for (const [name, m] of Object.entries(rec.metrics || {})) {
      if (m.score == null) continue;
      sums.set(name, (sums.get(name) || 0) + m.score);
      counts.set(name, (counts.get(name) || 0) + 1);
    }
  }
  const avg = new Map();
  for (const [name, total] of sums) {
    avg.set(name, total / counts.get(name));
  }
  return avg;
}

/** Action counts per metric. Returns Map<metricName, {Pass, Flag, Block}>. */
function actionCountsPerMetric(records) {
  const out = new Map();
  for (const rec of records) {
    for (const [name, m] of Object.entries(rec.metrics || {})) {
      if (!out.has(name)) out.set(name, { Pass: 0, Flag: 0, Block: 0 });
      const bucket = out.get(name);
      if (bucket[m.action] != null) bucket[m.action] += 1;
    }
  }
  return out;
}

/** Overall counts across all records (one row per record). */
function overallActionCounts(records) {
  const out = { Pass: 0, Flag: 0, Block: 0 };
  for (const rec of records) {
    if (out[rec.overall_action] != null) out[rec.overall_action] += 1;
  }
  return out;
}

// =====================================================================
// Top-level dashboard
// =====================================================================

export default function GuardrailDashboard() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      const resp = await fetch(AUDIT_ENDPOINT, { credentials: "include" });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setRecords(Array.isArray(data.records) ? data.records : []);
      setError(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, POLL_INTERVAL_MS);
    return () => clearInterval(t);
  }, [load]);

  const overall = useMemo(() => overallActionCounts(records), [records]);
  const avg = useMemo(() => avgScorePerMetric(records), [records]);
  const counts = useMemo(() => actionCountsPerMetric(records), [records]);
  const metricNames = useMemo(
    () => Array.from(new Set([...avg.keys(), ...counts.keys()])).sort(),
    [avg, counts]
  );

  if (loading && records.length === 0) return <Typography>Loading…</Typography>;
  if (error) return <Typography color="error">Error loading audit log: {error}</Typography>;

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: "auto" }}>
      <Typography variant="h4" sx={{ mb: 2 }}>
        🛡️ Guardrail Dashboard
      </Typography>

      <SummaryBar counts={overall} total={records.length} />

      <Typography variant="h6" sx={{ mt: 4, mb: 1 }}>
        Per-metric scores
      </Typography>
      <Paper sx={{ p: 2 }}>
        {metricNames.map((name) => (
          <MetricRow
            key={name}
            name={name}
            avgScore={avg.get(name)}
            actionCounts={counts.get(name)}
          />
        ))}
      </Paper>

      <Typography variant="h6" sx={{ mt: 4, mb: 1 }}>
        Recent decisions (last {records.length})
      </Typography>
      <HistoryTable records={records} />
    </Box>
  );
}

// =====================================================================
// Summary stacked bar — Pass / Flag / Block counts
// =====================================================================

function SummaryBar({ counts, total }) {
  if (total === 0) {
    return <Typography variant="body2">No decisions recorded yet.</Typography>;
  }
  const pct = (n) => (total === 0 ? 0 : (n / total) * 100);
  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: "flex", height: 32, borderRadius: 1, overflow: "hidden" }}>
        <Slice color="#4caf50" pct={pct(counts.Pass)} label={`Pass ${counts.Pass}`} />
        <Slice color="#ff9800" pct={pct(counts.Flag)} label={`Flag ${counts.Flag}`} />
        <Slice color="#f44336" pct={pct(counts.Block)} label={`Block ${counts.Block}`} />
      </Box>
      <Typography variant="caption" sx={{ mt: 1, display: "block" }}>
        {total} total decisions
      </Typography>
    </Paper>
  );
}

function Slice({ color, pct, label }) {
  if (pct === 0) return null;
  return (
    <Box
      sx={{
        bgcolor: color,
        width: `${pct}%`,
        color: "white",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 12,
      }}
    >
      {pct > 8 ? label : null}
    </Box>
  );
}

// =====================================================================
// MetricRow — average score bar + per-action counts
// =====================================================================

function MetricRow({ name, avgScore, actionCounts }) {
  const score = avgScore ?? 0;
  const counts = actionCounts || { Pass: 0, Flag: 0, Block: 0 };
  const total = counts.Pass + counts.Flag + counts.Block;
  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
        <Typography variant="body2">{name}</Typography>
        <Typography variant="caption">
          avg={score.toFixed(3)} · {counts.Block} block · {counts.Flag} flag · {counts.Pass} pass · {total} total
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={Math.max(0, Math.min(100, score * 100))}
        sx={{ height: 8, borderRadius: 1 }}
      />
    </Box>
  );
}

// =====================================================================
// HistoryTable — expandable one-row-per-decision view
// =====================================================================

function HistoryTable({ records }) {
  return (
    <TableContainer component={Paper}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell />
            <TableCell>Time</TableCell>
            <TableCell>Request ID</TableCell>
            <TableCell>Overall Action</TableCell>
            <TableCell>Blocked metrics</TableCell>
            <TableCell>Flagged metrics</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {records
            .slice()
            .reverse() // newest first
            .map((rec, i) => (
              <HistoryRow key={`${rec.request_id}-${i}`} record={rec} />
            ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

function HistoryRow({ record }) {
  const [open, setOpen] = useState(false);
  const color = {
    Pass: "success",
    Flag: "warning",
    Block: "error",
  }[record.overall_action] || "default";

  return (
    <>
      <TableRow hover>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>{new Date(record.timestamp).toLocaleString()}</TableCell>
        <TableCell sx={{ fontFamily: "monospace", fontSize: 12 }}>
          {(record.request_id || "").slice(0, 8)}
        </TableCell>
        <TableCell>
          <Chip label={record.overall_action} color={color} size="small" />
        </TableCell>
        <TableCell>{(record.blocked_metrics || []).join(", ") || "—"}</TableCell>
        <TableCell>{(record.flagged_metrics || []).join(", ") || "—"}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell colSpan={6} sx={{ p: 0, borderBottom: open ? undefined : 0 }}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ p: 2, bgcolor: "grey.50" }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Per-metric breakdown
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Metric</TableCell>
                    <TableCell>Score</TableCell>
                    <TableCell>Action</TableCell>
                    <TableCell>Threshold</TableCell>
                    <TableCell>Flag threshold</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(record.metrics || {}).map(([name, m]) => (
                    <TableRow key={name}>
                      <TableCell>{name}</TableCell>
                      <TableCell>{m.score == null ? "—" : m.score.toFixed(3)}</TableCell>
                      <TableCell>{m.action}</TableCell>
                      <TableCell>{m.threshold}</TableCell>
                      <TableCell>{m.flag_threshold ?? "—"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
}
