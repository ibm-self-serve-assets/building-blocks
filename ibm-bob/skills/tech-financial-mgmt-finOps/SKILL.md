---
name: build-finops-turbonomic-demo
description: Use when building, scaffolding, or replicating the IBM Cloudability + IBM Turbonomic Continuous FinOps React demo application with IBM Carbon g100 dark theme, complete API integrations, and multi-cloud optimization workflows.
---

# Build IBM Cloudability + IBM Turbonomic Continuous FinOps Demo App

This comprehensive guide provides end-to-end technical blueprints, exact architectural patterns, IBM Carbon Design System (g100 Dark Theme) specifications, data schemas, API contracts, and component implementation guides required to scaffold and build the **Continuous FinOps & Automated Cloud Cost Optimization** React application.

---

## 1. Project Overview & Architecture

### High-Level Value Proposition
- **IBM Cloudability:** Financial Intelligence (Cost allocation, ML forecasting, anomaly detection, TrueCost sharing, unit economics, executive showback).
- **IBM Turbonomic:** Resource Intelligence & Action (Performance-aware VM rightsizing, Kubernetes pod scaling, database sizing, off-hours workload parking, automated cloud actions).
- **Combined Impact:** Closed-Loop FinOps (`INFORM → OPTIMIZE → OPERATE → MEASURE`) delivering reduced spend while guaranteeing application SLOs.

### Technology Stack & Dependencies
- **Core Framework:** React 18+ / 19 with TypeScript (`"strict": true`)
- **Build Engine:** Vite
- **Styling:** Tailwind CSS with IBM Carbon g100 Dark Theme configuration
- **Icons:** `lucide-react`
- **Charting Engine:** `recharts` (ResponsiveContainer, ComposedChart, Area, Line, Bar, Pie)
- **JSON Handling:** Native JSON parsing with live schema validation

### File & Directory Structure
```
src/
├── types/
│   └── index.ts                 # Full TypeScript interfaces (Config, Applications, Actions, Forecasts, Anomalies, TrueCost, APIs)
├── data/
│   └── defaultConfig.ts         # Multi-cloud default scenario dataset ($2M/mo spend, Retail/Banking/Analytics apps)
├── services/
│   └── apiDocs.ts               # IBM Cloudability v3 & Turbonomic v3 REST API explorer endpoints, payloads, and mock engines
├── components/
│   ├── MetricHighlights.tsx              # Executive KPI banner (Monthly spend before/after, annualized savings, target status)
│   ├── CloudabilityAnalytics.tsx         # Financial Intelligence (Inform phase: App budgets, variance, cost breakdowns)
│   ├── CloudabilityCapabilitiesHub.tsx   # Advanced FinOps: ML Forecasts, Spending Anomalies, TrueCost Allocation, Unit Economics
│   ├── TurbonomicOptimizationEngine.tsx  # Resource Intelligence & Action Execution (Optimize & Operate: VM, K8s, Storage, Parking)
│   ├── ClosedLoopFinOpsWorkflow.tsx      # Step-by-step Interactive Closed-Loop Walkthrough (Inform -> Optimize -> Operate -> Measure)
│   ├── ApiInteractionHub.tsx             # Interactive REST API Inspector with live cURL, Node.js (Axios), and Python generators
│   ├── BusinessValueHub.tsx              # 4 Executive Value Pillars & Product Capability Comparison Matrix
│   └── EnvironmentConfigModal.tsx        # JSON input file editor, live validator, JSON export/download, and environment binding
├── App.tsx                      # Top-level Carbon shell, tabs state router, global action execution reducer, KPI recalculations
├── index.css                    # Tailwind CSS base and Carbon g100 dark background styles
└── main.tsx                     # React root DOM mount
```

---

## 2. IBM Carbon Design System (g100 Dark Theme) Specifications

All UI components MUST adhere to the IBM Carbon Design System g100 palette and layout conventions:

### Exact Carbon Color Tokens
| Carbon Token | Hex Code | Purpose / UI Placement |
| :--- | :--- | :--- |
| `background` (g100) | `#161616` | Root document background, main application canvas |
| `layer-01` (Surface) | `#262626` | Card background, metric tiles, modal containers |
| `layer-02` (Sub-surface) | `#393939` | Borders, table header backgrounds, dividers, inner well containers |
| `interactive-01` (Blue 60) | `#0f62fe` | Primary action buttons, active tab indicators, active links |
| `interactive-hover` (Blue 70) | `#0353e9` | Hover state for interactive blue buttons |
| `text-primary` | `#f4f4f4` | High-contrast headers, primary values, active tab text |
| `text-secondary` | `#c6c6c6` | Body text, table rows, descriptions |
| `text-muted` (Helper) | `#8d8d8d` | Form labels, helper captions, timestamps, inactive badges |
| `support-success` | `#42be65` / `#24a148` | Executed actions, cost savings, healthy SLO scores |
| `support-danger` | `#fa4d56` / `#da1e28` | Budget overruns, critical anomalies, performance risk alerts |
| `support-warning` | `#f1c21b` / `#f5a623` | High-priority warnings, unallocated costs, pending review |
| `support-purple` | `#8a3ffc` / `#a56eff` | Turbonomic actions, ML predictions, automation indicators |

### Carbon UI Layout & Typography Rules
1. **Sharp Geometry:** IBM Carbon uses square or 1px corners (`rounded-none` or `rounded-sm`). Do not use pill-shaped containers for cards or panels.
2. **Tabbed Top Navigation:** Tabs sit on a `#161616` shell with a 2px active bottom border (`border-b-2 border-[#0f62fe]`) and `#262626` active tab background.
3. **Monospace Values:** Always render currencies (`$370,000`), percentages (`+19.4%`), instance types (`m5.2xlarge`), and JSON in `font-mono`.
4. **Data Density:** High-density tables with `#393939` borders, uppercase tracking headers (`text-[11px] font-semibold tracking-wider text-[#8d8d8d] uppercase`), and subtle hover highlights (`hover:bg-[#2a2a2a]`).

---

## 3. TypeScript Interfaces & Data Contracts (`src/types/index.ts`)

```typescript
export interface EnvironmentConfig {
  name: string;
  description: string;
  monthlyBudgetTotal: number;
  cloudability: {
    endpoint: string;
    apiKey: string;
    viewId: string;
    vendorAccounts: {
      aws: string[];
      azure: string[];
      gcp: string[];
    };
  };
  turbonomic: {
    serverUrl: string;
    apiPath: string;
    authType: 'basic' | 'oauth2' | 'token';
    username: string;
    token?: string;
    targetScopes: string[];
  };
  applications: ApplicationData[];
  actions: TurbonomicAction[];
  finopsKpis: FinOpsKPIs;
  forecasts?: CloudabilityForecast[];
  anomalies?: SpendingAnomaly[];
  trueCostData?: TrueCostDimension[];
}

export interface CostBreakdown {
  compute: number;
  kubernetes: number;
  database: number;
  storage: number;
  networkOther: number;
  total: number;
}

export interface ApplicationData {
  id: string;
  name: string;
  businessUnit: string;
  environment: 'Production' | 'Staging' | 'Development';
  cloudProviders: ('AWS' | 'Azure' | 'GCP')[];
  monthlyBudget: number;
  currentCost: CostBreakdown;
  optimizedCost: CostBreakdown;
  unitEconomicsMetric: string;
  unitCostBefore: number;
  unitCostAfter: number;
  monthlyUnits: number;
  healthScore: number;
  turbonomicTargetId: string;
}

export interface TurbonomicAction {
  id: string;
  applicationId: string;
  targetEntityName: string;
  entityType: 'VirtualMachine' | 'ContainerPod' | 'DatabaseServer' | 'Volume' | 'CloudPolicy';
  cloudProvider: 'AWS' | 'Azure' | 'GCP';
  actionType: 'RIGHTSIZE' | 'RESIZE_CPU_MEM' | 'PARK_OFFHOURS' | 'PURGE_UNUSED' | 'SCALE_TIER';
  riskCategory: 'PERFORMANCE_ASSURANCE' | 'COST_EFFICIENCY' | 'SAVINGS_PLAN';
  currentSpecification: string;
  recommendedSpecification: string;
  monthlyCostSavings: number;
  reason: string;
  performanceMetrics: {
    cpuAvgUtilization: number;
    cpuPeakUtilization: number;
    memAvgUtilization: number;
    memPeakUtilization: number;
    iopsOrLatencyRisk?: string;
  };
  status: 'RECOMMENDED' | 'QUEUED' | 'EXECUTING' | 'EXECUTED' | 'ROLLED_BACK';
  executedAt?: string;
  policyAutomationEnabled: boolean;
}

export interface FinOpsKPIs {
  totalMonthlySpendBefore: number;
  totalMonthlySpendAfter: number;
  potentialMonthlySavings: number;
  realizedAnnualSavings: number;
  budgetVariancePercent: number;
  unallocatedCostPercent: number;
  wasteScoreReductionPercent: number;
  coverageCommitmentPercent: number;
}

export interface CloudabilityForecast {
  month: string;
  baselineHistorical: number | null;
  unconstrainedForecast: number;
  optimizedForecast: number;
  budgetTarget: number;
  confidenceLower: number;
  confidenceUpper: number;
}

export interface SpendingAnomaly {
  id: string;
  service: string;
  cloudProvider: 'AWS' | 'Azure' | 'GCP';
  applicationName: string;
  businessUnit: string;
  detectedDate: string;
  expectedCost: number;
  actualCost: number;
  spikeAmount: number;
  spikePercent: number;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  rootCause: string;
  turbonomicRemediation: string;
  status: 'ACTIVE_INVESTIGATING' | 'REMEDIATED' | 'ACCEPTED_EXPECTED';
}

export interface TrueCostDimension {
  id: string;
  dimensionCategory: string;
  rawSpend: number;
  amortizedDiscounts: number;
  sharedClusterReallocated: number;
  trueCost: number;
  attributedBU: string;
  tagComplianceScore: number;
}
```

---

## 4. Default Enterprise Scenario Dataset (`src/data/defaultConfig.ts`)

The default configuration models an enterprise with **$2,000,000/month** cloud spend across AWS, Azure, and GCP:

1. **Retail E-Commerce Platform ($370,000/mo spend vs. $310,000 budget | +19.4% overrun):**
   - Compute: $180,000 | Kubernetes: $80,000 | Database: $60,000 | Storage: $30,000 | Other: $20,000.
   - Turbonomic Actions:
     - 25 Oversized EC2 VMs (`m5.2xlarge` -> `m5.xlarge`) -> Save $28,500/mo.
     - Kubernetes Cart Pods CPU/Mem limit scale-down -> Save $22,000/mo.
     - Staging cluster off-hours workload parking -> Save $14,500/mo.
     - Database right-sizing & orphaned disk purge -> Save $15,000/mo.
   - Total Potential Savings: **$80,000/mo ($960,000/yr)** -> Optimized spend: **$290,000/mo**.

2. **Core Banking & Payments ($1,000,000/mo spend vs. $850,000 budget | +17.6% overrun):**
   - High security, hybrid Azure/AWS transaction engines.
   - Turbonomic Actions:
     - Azure VM Rightsizing (`D16s_v4` -> `D8s_v4`) -> Save $95,000/mo.
     - Pod memory limit rightsizing -> Save $65,000/mo.
     - Workload parking for QA payment gateways -> Save $45,000/mo.
     - Orphaned 8TB Ultra SSD disks purge -> Save $35,000/mo.
   - Total Potential Savings: **$240,000/mo ($2.88M/yr)** -> Optimized spend: **$760,000/mo**.

3. **Enterprise Data & AI Analytics ($630,000/mo spend vs. $590,000 budget | +6.8% overrun):**
   - AWS & GCP BigQuery / EMR pipelines.
   - Turbonomic Actions:
     - GCP BigQuery slot reservation alignment & VM rightsizing -> Save $75,000/mo.
     - AWS EMR spot/on-demand elasticity rebalancing -> Save $45,000/mo.
     - Off-hours staging pipeline parking -> Save $20,000/mo.
   - Total Potential Savings: **$140,000/mo ($1.68M/yr)** -> Optimized spend: **$490,000/mo**.

4. **Aggregate Portfolio Metrics:**
   - Total Spend Before: **$2,000,000/mo**
   - Total Spend After: **$1,540,000/mo**
   - Total Monthly Savings: **$460,000/mo**
   - Total Annualized Savings: **$5,520,000/yr**

---

## 5. Detailed Component & Tab Implementations

### Tab 1: Executive Overview (`MetricHighlights.tsx`)
- 4 Primary KPI metric tiles:
  1. *Total Monthly Spend (Before)*: `$2,000,000` (Red alert badge if over budget).
  2. *Optimized Monthly Spend (Live)*: Dynamically decrements as actions execute.
  3. *Realized Annualized Savings*: Dynamic calculation `(Total Executed Savings * 12)`.
  4. *Connected Cloud Targets*: Status pills for AWS, Azure, GCP, and Kubernetes.
- Interactive multi-cloud spend distribution chart and closed-loop process flow summary.

### Tab 2: Financial Intelligence (`CloudabilityAnalytics.tsx`)
- **INFORM Capability**:
  - Application spend cards showing current spend vs. budget and variance percentage.
  - Granular cost breakdown bar and donut visualizers (Compute, K8s, Database, Storage, Other).
  - Multi-cloud allocation breakdown (AWS vs. Azure vs. GCP).
  - Direct deep-link to trigger resource optimization for any over-budget application.

### Tab 3: Advanced FinOps Capabilities (`CloudabilityCapabilitiesHub.tsx`)
- 4 Sub-Tabs:
  1. **ML Spend Forecasting:** Recharts ComposedChart comparing 6-month unconstrained run-rate trajectory ($2.75M in Sep) vs. Turbonomic-optimized trajectory ($1.51M) with 95% confidence bands.
  2. **Spending Anomaly Detection:** Real-time spike alerts with root-cause diagnostics (e.g. DynamoDB batch indexing query, Azure unattached 8TB SSDs, BigQuery cross-region join).
  3. **TrueCost Allocation:** Multi-tenant K8s pod cost allocation, amortized commitment discounts (RIs/Savings Plans), and tag compliance scores.
  4. **Unit Economics:** Tracks unit business costs before vs. after optimization (*Cost per Checkout Order: $0.37 -> $0.29*, *Cost per Transaction: $0.050 -> $0.040*).

### Tab 4: Resource Optimization Engine (`TurbonomicOptimizationEngine.tsx`)
- **OPTIMIZE & OPERATE Capabilities**:
  - Filterable action grid (Filter by Application: All, Retail, Banking, Analytics; Filter by Type: VM Rightsizing, K8s Limits, Parking, Storage).
  - Action card details: Current spec vs. Recommended spec, CPU/Mem peak & average utilization, monthly savings, and risk category.
  - **Single Action Execution:** Interactive button with instant status progression (`RECOMMENDED` -> `EXECUTED`).
  - **Batch Execution:** `"Execute All Actions for [Application]"` button.
  - Performance Guardrail banner explaining non-disruptive sizing based on CPU, Memory, I/O, network, and latency constraints.

### Tab 5: Closed-Loop FinOps Workflow (`ClosedLoopFinOpsWorkflow.tsx`)
- Interactive step-by-step walkthrough of the 4 lifecycle stages:
  1. **INFORM (Cloudability):** Detects $370K Retail spend (+19.4% overrun).
  2. **OPTIMIZE (Turbonomic):** Discovers 25 oversized VMs and overprovisioned K8s pods.
  3. **OPERATE (Turbonomic):** Automates rightsizing and parking actions live.
  4. **MEASURE (Cloudability):** Verifies $80K/mo realized savings and updates executive showback reports.

### Tab 6: REST API Protocol Explorer (`ApiInteractionHub.tsx`)
- Live REST API client modeling official IBM endpoints:
  - **Cloudability v3 Endpoints:**
    - `GET /reporting/views`
    - `GET /reporting/reports/spend-by-dimension`
    - `GET /forecasting/models/ml-regressor`
    - `GET /anomalies/detections`
    - `GET /containers/truecost/allocations`
    - `GET /business-metrics/unit-economics/applications`
  - **Turbonomic v3 Endpoints:**
    - `GET /api/v3/actions?scope={scope}&risk_type=PERFORMANCE_ASSURANCE`
    - `POST /api/v3/actions/{actionId}` with payload `{"actionState": "EXECUTE"}`
- Features: Live endpoint URL & header viewer, JSON request/response payload viewers, cURL / Node.js (Axios) / Python (Requests) code generators with copy-to-clipboard, and live simulation execution.

### Tab 7: Executive Business Value Hub (`BusinessValueHub.tsx`)
- Detailed breakdown of the **4 Executive Pillars**:
  1. *Lower Cloud Spend*
  2. *Improve Cloud Cost Accountability*
  3. *Automated Cost Optimization*
  4. *Protect Application Performance*
- Comprehensive side-by-side Capability Matrix (Cloud spend visibility, Rightsizing, Kubernetes scaling, Parking, Performance assurance, Showback).

### Tab 8: Input File / Environment Configuration (`EnvironmentConfigModal.tsx`)
- Interactive JSON configuration editor.
- Features:
  - Live JSON syntax validation with line-level error messaging.
  - One-click **"Export / Download JSON"** file creation (`custom-enterprise-environment.json`).
  - **"Apply Configuration"** button to dynamically reload the entire application state.
  - **"Reset to Default Scenario"** button.

---

## 6. Global State Management & Dynamic Savings Reducer (`src/App.tsx`)

Implement state handling that updates realized spend and savings upon executing Turbonomic actions:

```typescript
// Execute single action
const handleExecuteAction = (actionId: string) => {
  setConfig((prev) => {
    const updatedActions: TurbonomicAction[] = prev.actions.map((act) => {
      if (act.id === actionId) {
        return {
          ...act,
          status: 'EXECUTED',
          executedAt: new Date().toISOString()
        };
      }
      return act;
    });

    const totalExecutedSavings = updatedActions
      .filter((a) => a.status === 'EXECUTED')
      .reduce((sum, a) => sum + a.monthlyCostSavings, 0);

    const newSpend = prev.finopsKpis.totalMonthlySpendBefore - totalExecutedSavings;

    return {
      ...prev,
      actions: updatedActions,
      finopsKpis: {
        ...prev.finopsKpis,
        totalMonthlySpendAfter: newSpend,
        potentialMonthlySavings: totalExecutedSavings
      }
    };
  });
};

// Batch execute actions for an application
const handleExecuteAllForApp = (appId: string) => {
  setConfig((prev) => {
    const updatedActions: TurbonomicAction[] = prev.actions.map((act) => {
      if (!appId || act.applicationId === appId) {
        return {
          ...act,
          status: 'EXECUTED',
          executedAt: new Date().toISOString()
        };
      }
      return act;
    });

    const totalExecutedSavings = updatedActions
      .filter((a) => a.status === 'EXECUTED')
      .reduce((sum, a) => sum + a.monthlyCostSavings, 0);

    const newSpend = prev.finopsKpis.totalMonthlySpendBefore - totalExecutedSavings;

    return {
      ...prev,
      actions: updatedActions,
      finopsKpis: {
        ...prev.finopsKpis,
        totalMonthlySpendAfter: newSpend,
        potentialMonthlySavings: totalExecutedSavings
      }
    };
  });
};
```

---

## 7. Verification & Build Validation Checklist

Before delivering or sharing the project:
1. **TypeScript Typecheck:** Run `npm run build` or `npx tsc -b`. Confirm `0` type errors.
2. **Build Verification:** Ensure Vite builds the production bundle in `dist/`.
3. **Action Execution State:** Verify clicking **Execute** updates the action badge to `EXECUTED`, decrements the live monthly spend, and increments realized annualized savings.
4. **Input File Validation:** Test pasting invalid JSON into the Config Tab; ensure the error banner catches syntax errors gracefully.
5. **API Explorer:** Ensure switching between Cloudability and Turbonomic updates cURL/Node/Python snippets and simulated execution outputs.
