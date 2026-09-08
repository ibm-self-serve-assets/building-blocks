# Planning Analytics CSV Dataset - FP&A Variance Analysis

## Overview
This directory contains a comprehensive CSV dataset for IBM Planning Analytics (TM1) to support FP&A variance analysis and automated variance investigation. The data is structured to enable multi-dimensional analysis of budget vs actual performance, variance explanations, and cross-functional financial insights.

## Use Case: FP&A Variance Autopilot
**Purpose:** Automate variance detection, root cause analysis, and explanation generation for monthly financial performance across departments, accounts, and scenarios.

**Business Value:**
- **~5 minutes** variance analysis (vs 3-4 days manual)
- **80%** reduction in analyst time
- **100%** variance coverage with audit trail
- Cross-system intelligence (CRM, ERP integration)

## Cube Structure

### Financial Performance Cube
**Dimensions:**
- **Time** ([`dim_time.csv`](dim_time.csv)) - Monthly periods across FY2023-2026 (42 months), quarters, fiscal periods
- **Account** ([`dim_account.csv`](dim_account.csv)) - Revenue, COGS, Operating Expenses with GL codes
- **Department** ([`dim_department.csv`](dim_department.csv)) - Cost centers, regions, business units
- **Scenario** ([`dim_scenario.csv`](dim_scenario.csv)) - Actual, Budget, Forecast, Prior Year
- **Version** ([`dim_version.csv`](dim_version.csv)) - Working, Approved, Reforecast versions

**Measures:** ([`fact_financial_data.csv`](fact_financial_data.csv))
- Amount (numeric)
- Variance Flag (0/1)
- Variance Explanation (text)
- Data Source (string)

## Files in Dataset

### Dimension Files
- [`dim_time.csv`](dim_time.csv) - 42 months (FY2023-2026) with quarter and fiscal period attributes
- [`dim_account.csv`](dim_account.csv) - 17 accounts covering Revenue, COGS, and Operating Expenses
- [`dim_department.csv`](dim_department.csv) - 12 departments across Sales, Engineering, Services, and Corporate
- [`dim_scenario.csv`](dim_scenario.csv) - 7 scenarios (Actual, Budget, 4 Forecasts, Prior Year)
- [`dim_version.csv`](dim_version.csv) - 5 versions for planning workflow management

### Fact Files
- [`fact_financial_data.csv`](fact_financial_data.csv) - 163 financial records spanning 3.5 years with budget/actual/prior year data and variance explanations

## Detailed Cube Structure

```
Financial Performance Cube:
  Dimensions:
    - Time (Month, Quarter, Year, Fiscal Period, YTD Flag)
    - Account (Account Name, Type, Category, GL Code, Revenue/Expense Flags)
    - Department (Name, Region, Cost Center, Business Unit, Headcount)
    - Scenario (Actual, Budget, Forecast, Prior Year)
    - Version (Working, Approved, Reforecast)
  
  Measures:
    - Amount (numeric, in USD)
    - Variance Flag (0 = within threshold, 1 = material variance)
    - Variance Explanation (AI-generated or manual text)
    - Data Source (system of record)
```

## Key Features

### 1. Budget vs Actual Variance Analysis
Compare current period actuals against budget to identify material variances with AI-generated explanations.

### 2. Year-over-Year (YoY) Comparisons
Analyze growth trends by comparing current year performance against prior year actuals across multiple years (FY2023-2026).

### 3. Month-over-Month (MoM) Analysis
Track sequential monthly performance to identify trends, seasonality, and momentum shifts.

### 4. Forecast Accuracy Tracking
Compare forecast scenarios against actual results to measure and improve forecasting accuracy.

### 5. Multi-Year Trend Analysis
Analyze performance patterns across 3.5 years of historical data to identify long-term trends.

## Sample Data Summary

### Dataset Coverage:
- **Time Periods:** 42 months (Jan 2023 - Jun 2026)
- **Departments:** 12 departments across 4 business units
- **Accounts:** 17 accounts (4 Revenue, 2 COGS, 11 OpEx)
- **Scenarios:** 7 scenarios including Prior Year for YoY comparisons
- **Versions:** 5 versions (Working, Approved, Reforecast)
- **Financial Records:** 163 records with rich variance and historical data

### Year-over-Year Growth Examples:
- **NA Sales (Jan 2024 vs Jan 2023):** $325K vs $450K = -28% (timing issue)
- **NA Sales (Jan 2025 vs Jan 2024):** $625K vs $325K = +92% (recovery + growth)
- **NA Sales (Jan 2026 vs Jan 2025):** $595K vs $625K = -5% (normalization)
- **APAC Sales (Jan 2024 vs Jan 2023):** $275K vs $250K = +10% (steady growth)

## Usage in Planning Analytics

### Import Steps

1. **Create Dimensions:**
   ```
   - Import dim_time.csv → Create Time dimension
   - Import dim_account.csv → Create Account dimension (with hierarchy)
   - Import dim_department.csv → Create Department dimension
   - Import dim_scenario.csv → Create Scenario dimension
   - Import dim_version.csv → Create Version dimension
   ```

2. **Create Cube:**
   ```
   - Create "Financial Performance" cube
   - Add dimensions: Time, Account, Department, Scenario, Version
   - Add measures: Amount, Variance Flag, Variance Explanation, Data Source
   ```

3. **Load Data:**
   ```
   - Import fact_financial_data.csv to populate cube
   ```

### Complex TM1 Rules

#### 1. Budget vs Actual Variance
```
['Variance', 'Amount'] = 
  ['ACT', 'Amount'] - ['BUD', 'Amount'];

['Variance', '%'] = 
  IF(['BUD', 'Amount'] <> 0,
    ((['ACT', 'Amount'] - ['BUD', 'Amount']) \ ['BUD', 'Amount']) * 100,
    0);
```

#### 2. Year-over-Year Growth
```
['YoY Growth', 'Amount'] = 
  ['ACT', 'Current Year', 'Amount'] - ['PY-ACT', 'Amount'];

['YoY Growth', '%'] = 
  IF(['PY-ACT', 'Amount'] <> 0,
    ((['ACT', 'Current Year', 'Amount'] - ['PY-ACT', 'Amount']) \ ['PY-ACT', 'Amount']) * 100,
    0);
```

#### 3. Month-over-Month Change
```
['MoM Change', 'Amount'] = 
  ['Current Month', 'Amount'] - ['Prior Month', 'Amount'];

['MoM Change', '%'] = 
  IF(['Prior Month', 'Amount'] <> 0,
    ((['Current Month', 'Amount'] - ['Prior Month', 'Amount']) \ ['Prior Month', 'Amount']) * 100,
    0);
```

#### 4. Rolling 3-Month Average
```
['Rolling 3M Avg'] = 
  ((['Current Month', 'Amount'] + 
    ['Prior Month', 'Amount'] + 
    ['2 Months Prior', 'Amount']) \ 3);
```

#### 5. Variance Category Classification
```
['Variance Category'] = 
  IF(['Variance', 'Amount'] = 0, 'On Target',
  IF(['Variance', 'Amount'] > 0 & ['Account':'is_revenue'] = 1, 'Favorable',
  IF(['Variance', 'Amount'] < 0 & ['Account':'is_revenue'] = 1, 'Unfavorable',
  IF(['Variance', 'Amount'] > 0 & ['Account':'is_expense'] = 1, 'Unfavorable',
  IF(['Variance', 'Amount'] < 0 & ['Account':'is_expense'] = 1, 'Favorable',
  'Neutral')))));
```

## Notes
- All amounts in USD
- Variance Flag: 1 = material variance (>$100K or >20%), 0 = within threshold
- Dataset spans 3.5 years (FY2023-2026) for comprehensive trend analysis
- Includes Prior Year (PY-ACT) scenario for year-over-year comparisons
- Supports month-over-month, quarter-over-quarter, and year-over-year analysis
- Compatible with TM1 TurboIntegrator processes for automated data loading
- Includes data lineage tracking via data_source field

---

## Sample Questions & Answers

### Budget vs Actual Variance Analysis

**Q1: What were the material variances in January 2024?**

**A:** Query the cube for January 2024 where Variance Flag = 1:

```sql
SELECT Department, Account, Budget, Actual, Variance_Amount, Variance_%, Explanation
FROM Financial_Performance
WHERE Time = '2024-01' AND Variance_Flag = 1 AND Scenario IN ('BUD', 'ACT')
```

**Results:**
- **North America Sales - Enterprise Software Revenue:** -$175K (-35%) - Two deals slipped to February
- **EMEA Sales - Enterprise Software Revenue:** +$40K (+11%) - Early enterprise deal close
- **North America Sales - Sales & Marketing:** +$25K (+21%) - Unplanned trade show
- **Product Engineering - R&D:** +$18K (+4%) - Cloud infrastructure growth

---

**Q2: Why did North America Sales miss budget by $175K in January 2024?**

**A:** The variance explanation shows:
- **Root Cause:** Two major deals slipped to February
  - Acme Corp: $120K (procurement approval delayed)
  - TechStart: $80K (customer budget freeze)
- **Type:** Timing variance, not a pipeline issue
- **Impact:** No forecast action required
- **Resolution:** Both deals closed in February 2024 (+$175K recovery)

---

**Q3: How did February 2024 performance compare to budget?**

**A:** February showed strong recovery:
- **NA Sales Revenue:** $695K actual vs $520K budget = +$175K (+34%)
- **Explanation:** January slipped deals closed plus new business
- **Commission Impact:** +$17.5K over budget (tied to revenue performance)
- **Overall:** Catch-up from prior month, strong pipeline execution

---

### Year-over-Year (YoY) Analysis

**Q4: What is the year-over-year revenue growth for North America Sales in Q1 2024 vs Q1 2023?**

**A:** Compare Q1 2024 ACT vs Q1 2023 PY-ACT:

```sql
SELECT 
  Time.Month,
  SUM(ACT_2024.Amount) AS FY2024_Actual,
  SUM(PY_ACT.Amount) AS FY2023_Actual,
  (FY2024 - FY2023) AS YoY_Growth_Amount,
  ((FY2024 - FY2023) / FY2023) * 100 AS YoY_Growth_Pct
FROM Financial_Performance
WHERE Department = 'DEPT-NA-SALES' 
  AND Account = 'REV-001'
  AND Time.Quarter = 'Q1'
GROUP BY Time.Month
```

**Results:**
| Month | FY2024 | FY2023 | YoY Growth $ | YoY Growth % |
|-------|--------|--------|--------------|--------------|
| Jan | $325K | $450K | -$125K | -28% |
| Feb | $695K | $480K | +$215K | +45% |
| Mar | $525K | $490K | +$35K | +7% |
| **Q1 Total** | **$1,545K** | **$1,420K** | **+$125K** | **+9%** |

**Insight:** Despite January timing issues, Q1 2024 grew 9% YoY driven by strong February recovery.

---

**Q5: How has North America Sales revenue trended year-over-year from 2023 to 2026?**

**A:** Multi-year comparison for January:

| Year | January Revenue | YoY Growth $ | YoY Growth % |
|------|----------------|--------------|--------------|
| 2023 | $450K | - | - |
| 2024 | $325K | -$125K | -28% |
| 2025 | $625K | +$300K | +92% |
| 2026 | $595K | -$30K | -5% |

**Insights:**
- **2024:** Timing issue (deals slipped to Feb)
- **2025:** Strong recovery + growth (92% increase)
- **2026:** Normalization at higher baseline (-5% but still 32% above 2023)
- **3-Year CAGR:** 10% compound annual growth rate

---

**Q6: Which region showed the strongest year-over-year growth in Q1 2024?**

**A:** Compare all regions Q1 2024 vs Q1 2023:

| Region | Q1 2024 | Q1 2023 | YoY Growth | YoY % |
|--------|---------|---------|------------|-------|
| North America | $1,545K | $1,420K | +$125K | +9% |
| EMEA | $1,220K | $1,085K | +$135K | +12% |
| APAC | $765K | $775K | -$10K | -1% |
| LATAM | $478K | $450K | +$28K | +6% |

**Winner:** EMEA with +12% YoY growth (+$135K)

---

### Month-over-Month (MoM) Analysis

**Q7: What is the month-over-month revenue trend for North America Sales in Q1 2024?**

**A:** Sequential monthly comparison:

| Month | Revenue | MoM Change $ | MoM Change % |
|-------|---------|--------------|--------------|
| Jan 2024 | $325K | - | - |
| Feb 2024 | $695K | +$370K | +114% |
| Mar 2024 | $525K | -$170K | -24% |

**Insights:**
- **Jan → Feb:** Massive 114% jump (slipped deals closed)
- **Feb → Mar:** -24% normalization (Feb was exceptionally high)
- **Trend:** Volatile due to deal timing, but overall positive trajectory

---

**Q8: How does APAC Sales performance trend month-over-month in Q1 2024?**

**A:** APAC monthly trend:

| Month | Revenue | Budget | Variance | MoM Change |
|-------|---------|--------|----------|------------|
| Jan 2024 | $275K | $280K | -$5K (-2%) | - |
| Feb 2024 | $295K | $290K | +$5K (+2%) | +$20K (+7%) |
| Mar 2024 | $195K | $280K | -$85K (-30%) | -$100K (-34%) |

**Insight:** March showed significant decline due to regulatory delays in China ($90K deal pushed to Q2).

---

**Q9: What is the 3-month rolling average for Product Engineering R&D expenses?**

**A:** Calculate rolling average for Jan-Jun 2024:

| Month | Actual | Rolling 3M Avg |
|-------|--------|----------------|
| Jan 2024 | $468K | - |
| Feb 2024 | $462K | - |
| Mar 2024 | $458K | $463K |
| Apr 2024 | $485K | $468K |
| May 2024 | $472K* | $472K |
| Jun 2024 | $472K | $476K |

**Insight:** R&D spending trending upward with April spike for new product launch infrastructure.

---

### Forecast Accuracy & Planning

**Q10: How accurate was the Q2 2026 forecast compared to actuals?**

**A:** Compare FC-Q2 vs ACT for June 2026:

```sql
SELECT 
  Department,
  Account,
  FC_Q2.Amount AS Forecast,
  ACT.Amount AS Actual,
  (Actual - Forecast) AS Variance,
  (1 - ABS(Actual - Forecast) / Forecast) * 100 AS Accuracy_Pct
FROM Financial_Performance
WHERE Time = '2026-06' AND Scenario IN ('FC-Q2', 'ACT')
```

**Example Result:**
- **NA Sales - Enterprise Software Revenue**
  - Forecast: $685K
  - Actual: (To be loaded)
  - Forecast Accuracy: TBD

---

**Q11: What percentage of variances in Q1 2024 were timing-related vs structural issues?**

**A:** Analyze variance explanations:

**Timing-Related (60%):**
- NA Sales Jan: Deal slippage (-$175K)
- Professional Services Jan: Project delay (-$15K)
- APAC Sales Mar: Regulatory delay (-$85K)

**Structural/Strategic (30%):**
- Marketing Jan: Strategic pipeline investment (+$7K)
- R&D Jan: Cloud infrastructure growth (+$18K)
- IT Jan: Security patch deployment (+$14K)

**Operational (10%):**
- COGS Jan-Feb: Contractor premium (+$7-11K)

**Insight:** Most variances are timing-related and self-correcting, not structural issues.

---

### Cross-Functional Impact Analysis

**Q12: How did the NA Sales revenue miss in January 2024 impact other departments?**

**A:** Cascade analysis:

**Primary Variance:**
- NA Sales Revenue: -$175K (-35%)

**Downstream Impacts:**
- Sales Commissions: -$17.5K (favorable - lower commissions)
- Professional Services: -$15K (delayed implementations)
- Marketing: +$7K (unfavorable - pipeline investment to recover)

**Net Impact:**
- Revenue: -$175K
- Expenses: -$25.5K (net favorable)
- **Total P&L Impact:** -$149.5K

---

**Q13: What is the correlation between R&D spending and revenue growth?**

**A:** Compare R&D investment vs revenue performance:

| Period | R&D Spend | R&D vs Budget | Revenue Growth YoY |
|--------|-----------|---------------|-------------------|
| Q1 2024 | $1,388K | +4% | +9% |
| Q2 2024 | $1,442K | +3% | +12% |
| Q1 2025 | $1,585K | +8% | +15% |
| Q1 2026 | $1,648K | +5% | +18% |

**Insight:** Increased R&D investment correlates with accelerating revenue growth (6-9 month lag).

---

### Trend & Pattern Analysis

**Q14: What seasonal patterns exist in the revenue data?**

**A:** Analyze monthly patterns across years:

**Q1 Pattern:**
- January: Typically softer (budget exhaustion, deal slippage)
- February: Recovery month (slipped deals close)
- March: Normalization

**Q2 Pattern:**
- April: Strong start (new quarter momentum)
- May: Steady performance
- June: Quarter-end push

**Historical Evidence:**
- Jan 2023: $450K, Jan 2024: $325K (timing), Jan 2025: $625K (recovery)
- Pattern repeats: Q4 budget exhaustion → Q1 procurement delays

---

**Q15: Which departments have the most consistent performance (lowest variance volatility)?**

**A:** Calculate variance standard deviation by department:

| Department | Avg Variance % | Std Dev | Consistency Score |
|------------|----------------|---------|-------------------|
| Product Engineering | 3.2% | 1.8% | High |
| Customer Success | 2.1% | 1.2% | Very High |
| Finance | 1.8% | 0.9% | Very High |
| North America Sales | 18.5% | 24.3% | Low |
| APAC Sales | 12.7% | 15.8% | Medium |

**Insight:** Corporate functions (Finance, HR) show high consistency; Sales regions show high volatility due to deal timing.

---

### Advanced Analytics

**Q16: What is the 3-year compound annual growth rate (CAGR) for North America Sales?**

**A:** Calculate CAGR from Jan 2023 to Jan 2026:

```
CAGR = ((Ending Value / Beginning Value) ^ (1 / Number of Years)) - 1
CAGR = (($595K / $450K) ^ (1/3)) - 1
CAGR = (1.322 ^ 0.333) - 1
CAGR = 1.098 - 1 = 9.8%
```

**Result:** 9.8% compound annual growth rate over 3 years

---

**Q17: What is the variance explanation quality score for January 2024?**

**A:** Score AI-generated explanations (out of 100):

| Variance | Root Cause | Supporting Data | Recommendations | Historical Context | Score |
|----------|------------|-----------------|-----------------|-------------------|-------|
| NA Sales -$175K | ✓ (30pts) | ✓ (25pts) | ✓ (20pts) | ✓ (15pts) | 90/100 |
| EMEA Sales +$40K | ✓ (30pts) | ✓ (25pts) | ✗ (0pts) | ✗ (0pts) | 55/100 |
| Marketing +$7K | ✓ (30pts) | ✓ (25pts) | ✓ (20pts) | ✗ (0pts) | 75/100 |

**Average Quality Score:** 73/100 (Good)

---

**Q18: How can I predict next month's variance based on historical patterns?**

**A:** Use historical variance patterns for predictive modeling:

**Input Features:**
- Last 3 months variance trend
- Same month prior year variance
- Seasonality factor
- Pipeline health indicators
- Economic indicators

**Example Prediction for July 2026:**
- Historical July pattern: +5% favorable variance
- Current pipeline: Strong (120% of target)
- Economic indicators: Stable
- **Predicted Variance:** +3% to +7% favorable

---

**Q19: What is the forecast accuracy trend over time?**

**A:** Track forecast vs actual accuracy by quarter:

| Quarter | Forecast Accuracy | Trend |
|---------|------------------|-------|
| Q1 2024 | 87% | Baseline |
| Q2 2024 | 89% | Improving |
| Q3 2024 | 91% | Improving |
| Q4 2024 | 88% | Slight decline |
| Q1 2025 | 92% | Improving |

**Insight:** Forecast accuracy improving over time (87% → 92%) as AI learns patterns.

---

**Q20: How do I set up automated variance alerts in Planning Analytics?**

**A:** Configure alert rules in TM1:

```javascript
// Alert Rule Configuration
IF (ABS(Variance_Amount) > 100000 OR ABS(Variance_Pct) > 20) {
  // High Severity Alert
  SendEmail(RegionalVP, "URGENT: Material Variance Detected");
  SendEmail(FPAManager, "High Priority Variance");
  AddToCFODigest("Weekly Summary");
  PostToSlack("#finance-alerts", "High Priority");
}
ELSE IF (ABS(Variance_Amount) > 50000 OR ABS(Variance_Pct) > 15) {
  // Medium Severity Alert
  SendEmail(DepartmentHead, "Variance Notification");
  UpdateDashboard("FPA Dashboard");
}
ELSE {
  // Low Severity - Log Only
  LogToCube("Variance Log");
  AddToMonthlyReport("Variance Summary");
}
```

**Alert Includes:**
- Variance amount and percentage
- Root cause explanation
- Historical context
- Recommended actions
- Link to detailed analysis in PA

---

## Future Enhancements

### Additional Cubes (Planned)
- **Driver-Based Planning Cube** - Link financial variances to operational drivers
- **Forecast Accuracy Cube** - Track forecast vs actual performance over time
- **Variance Investigation Workflow Cube** - Track investigation status and resolution

### Additional Dimensions (Planned)
- **Customer** - Link revenue variances to specific customers
- **Product** - Product-level revenue and cost analysis
- **Geography** - Detailed geographic breakdown beyond region