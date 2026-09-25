// src/config/dashboardConfig.js
// ============================================================
// CANONICAL DASHBOARD CONFIGURATION
// This file is the single source of truth for the Application
// Observability dashboard layout, component order, and settings.
//
// Components read from this file — they do NOT independently
// determine their own layout or ordering.
//
// ⚠️  DO NOT change tab names, KPI order, chart order, chart types,
//      column definitions, or analysis section names.
//      Only environment-specific values may differ between deployments.
// ============================================================

export const DASHBOARD_CONFIG = {
  // ── Application Identity ─────────────────────────────────────
  // These are the ONLY values that differ between environments.
  appTitle: 'Application Observability using IBM Instana',
  appSubtitle: 'With IBM Bob and Instana',
  applicationId: process.env.REACT_APP_APPLICATION_ID || '',
  applicationName: process.env.REACT_APP_APPLICATION_NAME || 'Application',
  instanaUrl: process.env.REACT_APP_INSTANA_URL || '',

  // ── Timing ───────────────────────────────────────────────────
  // Default lookback window in minutes
  defaultTimeRange: parseInt(process.env.REACT_APP_DEFAULT_TIME_RANGE || '60', 10),
  // Auto-refresh interval in milliseconds
  refreshInterval: parseInt(process.env.REACT_APP_REFRESH_INTERVAL || '30000', 10),

  // ── Time Range Options (fixed) ────────────────────────────────
  // Expressed in ms to match REACT_APP_TIME_WINDOW_MS convention.
  timeRangeOptions: [
    { id: '900000',    label: 'Last 15 minutes', windowMs: 900000    },
    { id: '1800000',   label: 'Last 30 minutes', windowMs: 1800000   },
    { id: '3600000',   label: 'Last 1 hour',     windowMs: 3600000   },
    { id: '10800000',  label: 'Last 3 hours',    windowMs: 10800000  },
    { id: '21600000',  label: 'Last 6 hours',    windowMs: 21600000  },
    { id: '43200000',  label: 'Last 12 hours',   windowMs: 43200000  },
    { id: '86400000',  label: 'Last 24 hours',   windowMs: 86400000  },
  ],

  // ── Primary Tabs (FIXED — do not rename, reorder, or add) ────
  tabs: [
    { id: 'service-overview',        label: 'Service Overview' },
    { id: 'trace-details',           label: 'Trace Details' },
    { id: 'intelligent-analysis',    label: 'Intelligent Analysis & Insights' },
  ],

  // ── Service Overview KPI Cards (FIXED ORDER) ─────────────────
  // All 5 must be rendered in this exact order.
  // If a value is null/undefined, show '—' — do not remove the card.
  kpis: [
    {
      id:    'calls',
      label: 'Calls / Requests',
      unit:  '',
      field: 'totalCalls',          // maps to analysed metrics object
      format: 'number',
      thresholds: null,             // no colour threshold — always neutral
    },
    {
      id:    'mean-latency',
      label: 'Mean Latency',
      unit:  'ms',
      field: 'meanLatency',
      format: 'integer',
      thresholds: { healthy: 200, degraded: 500 }, // > 500ms = error
    },
    {
      id:    'p95-latency',
      label: 'P95 Latency',
      unit:  'ms',
      field: 'p95Latency',
      format: 'integer',
      thresholds: { healthy: 500, degraded: 1000 },
    },
    {
      id:    'error-rate',
      label: 'Error Rate',
      unit:  '%',
      field: 'errorRate',
      format: 'percent',
      thresholds: { healthy: 1, degraded: 5 }, // > 5% = error
    },
    {
      id:    'affected-services',
      label: 'Affected Services',
      unit:  '',
      field: 'affectedServices',
      format: 'integer',
      thresholds: null,
    },
  ],

  // ── Service Overview Charts (FIXED ORDER, FIXED TYPES) ────────
  // 3 rows × 2 columns (time-series charts removed — API returns
  // too few buckets for a meaningful line chart on sparse traffic).
  charts: [
    // Row 1
    {
      id:        'top-services-by-calls',
      title:     'Top Services by Calls',
      type:      'horizontal-bar',
      component: 'ServiceCallsChart',
      row: 1, col: 1,
      dataKey:   'serviceCallsData',
    },
    {
      id:        'top-services-by-latency',
      title:     'Top Services by Latency',
      type:      'horizontal-bar',
      component: 'ServiceLatencyChart',
      row: 1, col: 2,
      dataKey:   'serviceLatencyData',
    },
    // Row 2
    {
      id:        'top-endpoints-by-calls',
      title:     'Top Endpoints by Calls',
      type:      'horizontal-bar',
      component: 'EndpointCallsChart',
      row: 2, col: 1,
      dataKey:   'endpointCallsData',
    },
    {
      id:        'top-endpoints-by-latency',
      title:     'Top Endpoints by Latency',
      type:      'horizontal-bar',
      component: 'EndpointLatencyChart',
      row: 2, col: 2,
      dataKey:   'endpointLatencyData',
    },
    // Row 3
    {
      id:        'status-distribution',
      title:     'HTTP Status / Error Distribution',
      type:      'donut',
      component: 'StatusDistributionChart',
      row: 3, col: 1,
      dataKey:   'statusDistribution',
    },
  ],

  // ── Trace Details KPI Cards (FIXED ORDER) ────────────────────
  traceKpis: [
    { id: 'total-traces', label: 'Total Traces',  field: 'totalTraces',  format: 'integer' },
    { id: 'slow-traces',  label: 'Slow Traces',   field: 'slowTraces',   format: 'integer' },
    { id: 'error-traces', label: 'Error Traces',  field: 'errorTraces',  format: 'integer' },
    { id: 'mean-duration',label: 'Mean Duration', field: 'meanDuration', format: 'integer', unit: 'ms' },
  ],

  // ── Trace Table Columns (FIXED ORDER) ────────────────────────
  traceColumns: [
    { id: 'traceId',    header: 'Trace ID',    sortable: false, clickable: true  },
    { id: 'timestamp',  header: 'Timestamp',   sortable: true,  clickable: false },
    { id: 'service',    header: 'Service',     sortable: true,  clickable: false },
    { id: 'endpoint',   header: 'Endpoint',    sortable: true,  clickable: false },
    { id: 'duration',   header: 'Duration',    sortable: true,  clickable: false },
    { id: 'status',     header: 'Status',      sortable: true,  clickable: false },
    { id: 'error',      header: 'Error',       sortable: false, clickable: false },
  ],

  // ── Intelligent Analysis Sections (FIXED ORDER) ──────────────
  analysisSections: [
    {
      id:          'health-summary',
      title:       'Application Health Summary',
      description: 'Overall health assessment based on request volume, latency, error rate, and service performance.',
    },
    {
      id:          'performance-insights',
      title:       'Performance Insights',
      description: 'Slow services, slow endpoints, latency increases, and traffic spikes.',
    },
    {
      id:          'error-analysis',
      title:       'Error Analysis',
      description: 'Services and endpoints generating errors, HTTP error patterns, and error-rate trends.',
    },
    {
      id:          'bottleneck-analysis',
      title:       'Bottleneck Analysis',
      description: 'Potential bottlenecks identified from service latency, trace duration, slow spans, and dependencies.',
    },
    {
      id:          'recommended-actions',
      title:       'Recommended Actions',
      description: 'Actionable recommendations based on available telemetry.',
    },
  ],

  // ── Status Thresholds ─────────────────────────────────────────
  // Used by analysisService.js and KPICard status colour logic.
  thresholds: {
    errorRate:   { healthy: 1,    degraded: 5    }, // %
    meanLatency: { healthy: 200,  degraded: 500  }, // ms
    p95Latency:  { healthy: 500,  degraded: 1000 }, // ms
    p99Latency:  { healthy: 1000, degraded: 2000 }, // ms
    slowTrace:   500,                                 // ms — traces above this are "slow"
    trafficSpike: 2.0,                                // multiplier above baseline
  },

  // ── Analysis Thresholds ───────────────────────────────────────
  analysisThresholds: {
    slowServiceLatencyMs:    500,   // p95 > this triggers slow service alert
    slowEndpointLatencyMs:   1000,  // p99 > this triggers slow endpoint alert
    highErrorRatePct:        1,     // error rate > this triggers error alert
    longTraceDurationMs:     2000,  // trace duration > this is "long"
    slowSpanContributionPct: 50,    // span > this % of parent is a bottleneck
    topN:                    10,    // max items in ranking charts
  },
};
