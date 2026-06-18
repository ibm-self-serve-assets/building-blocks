# IBM Planning Analytics Budget and Forecasting

---

## 🔗 Navigation

**Optimize Building Blocks:**
- [← Back to Optimize](../README.md)
- [← Automated Resource Management](../automated-resource-mgmt/README.md)
- [Automated Resilience →](../automated-resilience-and-compliance/README.md)

**Other Categories:**
- [Build & Deploy](../../build-and-deploy/README.md)
- [Secure](../../secure/non-human-identity/README.md)

---

# IBM Planning Analytics Budget and Forecasting

A comprehensive Bob skill and mode package for exploring IBM Planning Analytics and TM1 data through natural language queries, enabling business-focused insights, variance analysis, and executive-ready reporting for budget and forecasting workflows.

## 🎯 Overview

This building block transforms Planning Analytics into an accessible business intelligence platform for financial planning and analysis, enabling users to:

- 🗣️ **Natural Language Queries** - Ask questions in plain English, not MDX
- 📊 **Variance Analysis** - Budget vs Actual, Forecast vs Actual, Period-over-Period
- 🔍 **Outlier Detection** - Identify anomalous patterns requiring attention
- 📈 **Key Driver Analysis** - Understand what's driving your results
- 📄 **Executive Reports** - Professional, business-ready formatting
- 🤖 **AI-Powered Insights** - Automated analysis and recommendations

## ✅ What's Included

This building block provides:

### 📦 Bob Skills
- **planning-analytics-skill.zip** - Complete Planning Analytics skill with:
  - Natural language to TM1 query translation
  - Financial analysis capabilities (variance, trend, outlier detection)
  - Executive reporting templates
  - Pre-analyzed cube support
  - Comprehensive usage guide and examples

### 🎨 Bob Modes
- **planning-analytics-mode.zip** - Specialized mode configuration with:
  - TM1 modeling expertise (cubes, dimensions, rules, processes)
  - Planning Analytics Workspace guidance
  - REST API and OData integration patterns
  - Best practices and troubleshooting workflows
  - Response formatting for business users

### 🔌 Assets
- **mcp.json** - Model Context Protocol configuration for:
  - IBM Planning Analytics MCP servers (production and TechZone)
  - Pre-configured tool permissions
  - Authentication headers
  - Timeout and connection settings

### 📊 Sample Dataset
- **FPA_Variance_Analysis/** - Complete sample dataset for hands-on learning:
  - 5 dimension files (Time, Account, Department, Scenario, Version)
  - 1 fact file with 163 financial records spanning 3.5 years
  - Budget vs Actual variance data with AI-generated explanations
  - Year-over-Year comparison data (FY2023-2026)
  - Ready-to-import CSV files for Planning Analytics
  - Comprehensive README with 20+ example queries and answers

## 📋 Prerequisites

- IBM Planning Analytics or TM1 instance (v11.x or higher recommended)
- Valid Planning Analytics credentials with API access
- Network access to Planning Analytics REST API
- Bob AI assistant with MCP support
- Planning Analytics Workspace (optional, for enhanced features)

## 🚀 Quick Start

### 1. Install Bob Skills

Extract the skill package:

```bash
cd optimize/budget-and-forecasting/bob-skills
unzip planning-analytics-skill.zip -d ~/.bob/skills/planning-analytics
```

Or manually copy to your Bob skills directory.

### 2. Install Bob Modes

Extract the mode package:

```bash
cd optimize/budget-and-forecasting/bob-modes/base-modes
unzip planning-analytics-mode.zip -d ~/.bob/modes/planning-analytics
```

The mode includes:
- Custom mode configuration (custom_modes.yaml)
- Mode rules and workflows (rules-planning-analytics/)

### 3. Configure MCP Servers

Copy the MCP configuration:

```bash
cp optimize/budget-and-forecasting/assets/mcp.json ~/.bob/mcp.json
```

**Update credentials** in mcp.json:
- Replace `Authorization` header with your Planning Analytics API key
- Update server URLs if using different instances
- Configure timeout values based on your data volume

### 4. Activate and Use

**In Advanced Mode:**
```
"Use planning-analytics skill to show Q1 2025 compensation budget vs actual by department"
```

**In Planning Analytics Mode:**
```
"Show Q1 2025 compensation budget vs actual by department"
```

The skill activates automatically for Planning Analytics queries.

## 📁 Project Structure

```
optimize/budget-and-forecasting/
├── README.md                                    # This file
├── assets/
│   ├── mcp.json                                # MCP server configuration
│   └── FPA_Variance_Analysis/                 # Sample dataset
│       ├── README.md                           # Dataset documentation
│       ├── dim_time.csv                        # 42 months (FY2023-2026)
│       ├── dim_account.csv                     # 17 accounts (Revenue, COGS, OpEx)
│       ├── dim_department.csv                  # 12 departments
│       ├── dim_scenario.csv                    # 7 scenarios (Budget, Actual, Forecast, PY)
│       ├── dim_version.csv                     # 5 versions
│       └── fact_financial_data.csv             # 163 financial records
├── bob-modes/
│   └── base-modes/
│       └── planning-analytics-mode.zip         # Mode + rules package
│           ├── custom_modes.yaml               # Mode configuration
│           └── rules-planning-analytics/       # Mode rules
│               ├── 1_overview.xml
│               ├── 2_mcp_tools_reference.xml
│               ├── 3_workflows.xml
│               ├── 4_best_practices.xml
│               ├── 5_response_patterns.xml
│               └── 6_troubleshooting.xml
└── bob-skills/
    └── planning-analytics-skill.zip            # Complete skill package
        ├── SKILL.md                            # Skill specification
        ├── README.md                           # Skill overview
        ├── USAGE-GUIDE.md                      # Detailed usage guide
        └── examples/                           # Query examples
```

## 🎨 Features by Use Case

### 1. 📊 Budget vs Actual Analysis

**Example Queries:**
```
"Show Q1 2025 compensation budget vs actual by department"
"What's the variance in marketing expenses for March?"
"Compare budget to actual revenue by region"
```

**Capabilities:**
- Automatic variance calculation ($ and %)
- Material variance identification (>10% or >$100K)
- Hierarchical rollups (department → region → total)
- Key findings and insights
- Data quality notes

### 2. 📈 Forecast Analysis

**Example Queries:**
```
"Show forecast vs actual sales for Q4"
"What's the forecast accuracy by product line?"
"Compare forecast to actual by region"
```

**Capabilities:**
- Forecast accuracy metrics
- Trend identification
- Seasonal pattern detection
- Forecast bias analysis

### 3. 🔍 Outlier Detection

**Example Queries:**
```
"Find unusual expense patterns in March"
"Identify anomalies in sales data"
"Show outliers in compensation by department"
```

**Capabilities:**
- Statistical outlier detection
- Pattern anomaly identification
- Threshold-based alerts
- Root cause suggestions

### 4. 📉 Trend Analysis

**Example Queries:**
```
"Show sales trends over the last 12 months"
"What are the quarterly revenue patterns?"
"Display monthly expense trends for 2024"
```

**Capabilities:**
- Time series visualization
- Growth rate calculation
- Moving averages
- Seasonal decomposition

### 5. 🎯 Key Driver Analysis

**Example Queries:**
```
"What's driving revenue variance in the East region?"
"Identify top contributors to expense growth"
"Show key drivers of profit change"
```

**Capabilities:**
- Impact analysis
- Contribution analysis
- Waterfall breakdowns
- Driver ranking

### 6. 📄 Executive Reporting

**Example Queries:**
```
"Generate executive summary for Q1 results"
"Create variance report for the board"
"Produce monthly financial dashboard"
```

**Capabilities:**
- Professional formatting
- Executive summaries
- Key metrics highlights
- Actionable recommendations
- PDF report generation

## 🔧 Configuration

### MCP Server Configuration

The `mcp.json` file configures three MCP servers:

1. **ibm-pa-tools** (Production)
   - URL: IBM Planning Analytics SaaS
   - Purpose: Production data queries
   - Tools: Data explorer, cube discovery, member lookup

2. **ibm-pa-tools-tz-server** (TechZone - Analysis)
   - URL: TechZone demo environment
   - Purpose: Process management and execution
   - Tools: TI process CRUD, execution, monitoring

3. **ibm-pa-tools-tz-cube** (TechZone - Cube)
   - URL: TechZone demo environment
   - Purpose: Cube operations and analysis
   - Tools: Data queries, cube management, impact analysis

### Authentication

Update the `Authorization` header in mcp.json:

```json
"Authorization": "Basic <your-base64-encoded-credentials>"
```

To encode credentials:
```bash
echo -n "APIKey:your-api-key" | base64
```

### Timeout Configuration

Adjust timeout values based on your data volume:

```json
"timeout": 300  // 5 minutes for large queries
```

## 🏗️ Architecture

### Components

1. **Planning Analytics Skill**
   - Natural language understanding
   - Query translation (NL → MDX)
   - Financial analysis algorithms
   - Report formatting
   - Business context generation

2. **Planning Analytics Mode**
   - TM1 modeling expertise
   - Workflow orchestration
   - Best practices enforcement
   - Error handling and recovery
   - Response formatting

3. **MCP Integration**
   - Server connection management
   - Tool invocation
   - Response normalization
   - Error handling
   - Session management

### Data Flow

```
User Query → Skill Activation → Intent Understanding
    ↓
Cube Discovery → Member Lookup → Query Construction
    ↓
MCP Tool Invocation → TM1 API → Data Retrieval
    ↓
Analysis (Variance/Trend/Outlier) → Insight Generation
    ↓
Report Formatting → Executive Summary → User Response
```

## 🔍 MCP Tools Reference

### Discovery Tools
- `get_available_tm1_servers` - List available servers
- `get_tm1_cubes` - List cubes with metadata
- `list_cubes_with_ai_analysis_metadata` - Check pre-analyzed cubes
- `get_cube_dimensions` - Get cube dimensions
- `get_cube_sample_members` - See sample members
- `lookup_potential_members` - Search for members by name

### Query Tools
- `get_data_from_data_explorer` - Natural language queries (pre-analyzed cubes)
- `execute_mdx_and_get_view` - Direct MDX queries (any cube)
- `get_MDX_for_recommended_view` - Generate MDX from natural language

### Analysis Tools
- `perform_impact_analysis` - Identify key drivers
- `perform_outlier_detection` - Find anomalies
- `generate_exploration_analysis_report` - Create PDF reports

### Management Tools
- `create_tm1_cube` / `delete_tm1_cube` - Cube management
- `save_mdx_view` / `get_saved_view` / `list_cube_views` - View management
- `create_tm1_process` / `update_tm1_process` / `delete_tm1_process` - Process CRUD
- `execute_tm1_processes_asynchronously` - Execute processes

## 🐛 Troubleshooting

### Issue: "Cube not found"

**Cause**: Cube name mismatch or server not connected

**Solution**:
1. Use `get_tm1_cubes` to list available cubes
2. Verify server connection in mcp.json
3. Check cube name spelling and case sensitivity

### Issue: "Cube not pre-analyzed"

**Cause**: Cube lacks AI-generated metadata

**Solution**:
1. Check status with `list_cubes_with_ai_analysis_metadata`
2. Switch to `execute_mdx_and_get_view` with MDX query
3. Use `get_cube_sample_members` to construct MDX

### Issue: "Member not found"

**Cause**: Member name mismatch or doesn't exist

**Solution**:
1. Use `lookup_potential_members` to search for members
2. Use `get_cube_sample_members` to see available members
3. Check member name spelling and hierarchy

### Issue: "Query timeout"

**Cause**: Large data volume or slow network

**Solution**:
1. Increase timeout in mcp.json (default: 300 seconds)
2. Add filters to reduce data volume
3. Use aggregated members instead of leaf members

### Issue: "Authentication failed"

**Causes**:
- Invalid API key
- Expired credentials
- Network connectivity

**Solutions**:
1. Verify API key is correct and active
2. Check network access to Planning Analytics
3. Regenerate API key if expired
4. Verify Authorization header format in mcp.json

### Issue: "No data returned"

**Cause**: Empty cells or incorrect member selection

**Solution**:
1. Verify members exist and have data
2. Check time period selection
3. Use `get_cube_sample_members` to find populated members
4. Review dimension selections

## 📊 Performance

- **Initial Discovery**: ~2-5 seconds (server + cube listing)
- **Simple Query**: ~1-3 seconds (pre-analyzed cubes)
- **Complex Query**: ~5-15 seconds (MDX with calculations)
- **Variance Analysis**: ~3-10 seconds (depends on data volume)
- **Outlier Detection**: ~10-30 seconds (statistical analysis)
- **PDF Report**: ~15-45 seconds (includes analysis + formatting)

## 📊 Using the Sample Dataset

### Overview

The included **FPA_Variance_Analysis** dataset provides a complete, ready-to-use example for learning Planning Analytics budget and forecasting workflows with Bob.

**Dataset Contents:**
- **163 financial records** spanning 3.5 years (FY2023-2026)
- **5 dimensions**: Time (42 months), Account (17), Department (12), Scenario (7), Version (5)
- **Real-world variance scenarios** with AI-generated explanations
- **Year-over-Year data** for trend analysis
- **Material variances** flagged for investigation

### Quick Start with Sample Data

#### Step 1: Import to Planning Analytics

**Option A: Using Bob (Recommended)**
```
"Use planning-analytics skill to create a Financial Performance cube from the CSV files in assets/FPA_Variance_Analysis"
```

Bob will:
1. Create dimensions from dim_*.csv files
2. Build the Financial Performance cube
3. Load fact data from fact_financial_data.csv
4. Verify data integrity

**Option B: Manual Import via TurboIntegrator**
1. Create dimensions: Time, Account, Department, Scenario, Version
2. Create cube: Financial_Performance
3. Run TI process to load fact_financial_data.csv

#### Step 2: Try Example Queries

Once data is loaded, try these queries with Bob:

**Budget vs Actual Analysis:**
```
"Show Q1 2024 budget vs actual variance by department"
"What were the material variances in January 2024?"
"Why did North America Sales miss budget in January 2024?"
```

**Year-over-Year Analysis:**
```
"Compare Q1 2024 revenue to Q1 2023 by region"
"Show year-over-year growth trends for North America Sales"
"Which region had the strongest YoY growth in Q1 2024?"
```

**Trend Analysis:**
```
"Show month-over-month revenue trends for Q1 2024"
"What is the 3-month rolling average for R&D expenses?"
"Identify seasonal patterns in sales data"
```

**Outlier Detection:**
```
"Find unusual expense patterns in March 2024"
"Identify anomalies in APAC sales performance"
"Show departments with high variance volatility"
```

### Sample Dataset Features

#### 1. Rich Variance Explanations

Every material variance includes:
- **Root cause** (e.g., "Two deals slipped to February")
- **Supporting details** (e.g., "Acme Corp $120K, TechStart $80K")
- **Variance type** (Timing, Structural, Operational)
- **Impact assessment** (Revenue, downstream effects)
- **Resolution status** (e.g., "Both deals closed in February")

**Example from dataset:**
```
NA Sales Jan 2024: -$175K (-35%)
Explanation: "Two major deals slipped to February: Acme Corp $120K 
(procurement delayed) and TechStart $80K (budget freeze). 
Timing-related variance."
```

#### 2. Multi-Year Comparisons

Track performance across 3.5 years:
- **FY2023**: Baseline year
- **FY2024**: Growth with timing challenges
- **FY2025**: Strong recovery and expansion
- **FY2026**: Normalization at higher baseline

**Example YoY Trend (NA Sales January):**
- 2023: $450K (baseline)
- 2024: $325K (-28% - timing issue)
- 2025: $625K (+92% - recovery)
- 2026: $595K (-5% - normalization)

#### 3. Cross-Functional Impact Analysis

See how variances cascade across departments:

**Primary Variance:**
- NA Sales Revenue: -$175K

**Downstream Impacts:**
- Sales Commissions: -$17.5K (favorable)
- Professional Services: -$15K (delayed implementations)
- Marketing: +$7K (pipeline investment)

#### 4. Forecast Accuracy Tracking

Multiple forecast scenarios:
- **FC-Q1**: Quarter 1 forecast
- **FC-Q2**: Quarter 2 forecast
- **FC-Q3**: Quarter 3 forecast
- **FC-Q4**: Quarter 4 forecast

Compare forecasts to actuals to measure accuracy.

### Example Workflows with Sample Data

#### Workflow 1: Monthly Variance Review

```
1. "Show all material variances for January 2024"
   → Bob identifies 4 variances >$100K or >20%

2. "Explain the NA Sales revenue variance"
   → Bob provides root cause analysis with details

3. "What was the downstream impact on other departments?"
   → Bob shows cascade effects (commissions, services, marketing)

4. "Did the variance resolve in February?"
   → Bob compares Feb performance and confirms recovery
```

#### Workflow 2: Year-over-Year Growth Analysis

```
1. "Compare Q1 2024 to Q1 2023 by region"
   → Bob shows YoY growth for all regions

2. "Which region had the strongest growth?"
   → Bob identifies EMEA with +12% YoY

3. "Show the 3-year trend for North America"
   → Bob displays Jan 2023-2026 with CAGR calculation

4. "What's driving the growth in EMEA?"
   → Bob analyzes variance explanations for insights
```

#### Workflow 3: Forecast Accuracy Assessment

```
1. "How accurate was the Q1 2024 forecast?"
   → Bob compares FC-Q1 to ACT for Q1 2024

2. "Which departments had the largest forecast errors?"
   → Bob ranks departments by forecast variance

3. "What patterns exist in forecast errors?"
   → Bob identifies timing-related vs structural issues

4. "Generate a forecast accuracy report"
   → Bob creates executive summary with recommendations
```

### Dataset Statistics

**Coverage:**
- **Time Periods**: 42 months (Jan 2023 - Jun 2026)
- **Departments**: 12 (Sales: 4, Engineering: 2, Services: 2, Corporate: 4)
- **Accounts**: 17 (Revenue: 4, COGS: 2, OpEx: 11)
- **Scenarios**: 7 (ACT, BUD, 4 Forecasts, PY-ACT)
- **Records**: 163 with rich metadata

**Variance Distribution:**
- **Material Variances**: 28 records (>$100K or >20%)
- **Timing-Related**: 60% of variances
- **Structural**: 30% of variances
- **Operational**: 10% of variances

**Data Quality:**
- **Completeness**: 100% (no missing values)
- **Explanations**: 100% for material variances
- **Data Sources**: Tracked for all records
- **Audit Trail**: Full lineage available

### Learning Path

**Beginner (Week 1):**
1. Import sample data to Planning Analytics
2. Run basic queries (budget vs actual)
3. Explore variance explanations
4. Try simple trend analysis

**Intermediate (Week 2):**
1. Perform year-over-year comparisons
2. Calculate rolling averages
3. Identify outliers and patterns
4. Generate variance reports

**Advanced (Week 3):**
1. Cross-functional impact analysis
2. Forecast accuracy assessment
3. Predictive variance modeling
4. Custom TM1 rules and calculations

**Expert (Week 4):**
1. Automated variance investigation workflows
2. Integration with external data sources
3. Custom AI-powered analysis
4. Executive dashboard creation

### Additional Resources

For detailed information about the sample dataset:
- See [`assets/FPA_Variance_Analysis/README.md`](assets/FPA_Variance_Analysis/README.md)
- 20+ example queries with answers
- Complex TM1 rules and calculations
- Variance investigation workflows
- Forecast accuracy tracking methods

## 🔒 Security

- **Credentials**: Stored in MCP configuration only
- **API Keys**: Base64 encoded in Authorization header
- **SSL**: HTTPS for production servers
- **Session Management**: Token-based authentication
- **Data Access**: Respects TM1 security model
- **No Data Storage**: All data in memory only

## 🧪 Testing

### Manual Testing Checklist

- [ ] Skill activates for Planning Analytics queries
- [ ] Server discovery works (`get_available_tm1_servers`)
- [ ] Cube listing works (`get_tm1_cubes`)
- [ ] Natural language query works (pre-analyzed cube)
- [ ] MDX query works (any cube)
- [ ] Variance analysis produces correct results
- [ ] Outlier detection identifies anomalies
- [ ] Report formatting is professional
- [ ] Error messages are clear and actionable
- [ ] MCP tools respond within timeout

### Example Test Queries

```
# Basic Query
"Show Q1 2025 compensation data"

# Variance Analysis
"Compare Q1 budget vs actual by department"

# Trend Analysis
"Show monthly sales trends for 2024"

# Outlier Detection
"Find unusual expense patterns in March"

# Key Driver Analysis
"What's driving revenue variance in East region?"
```

## 📝 Best Practices

### Query Construction
- Use specific time periods (Q1 2025, March 2024)
- Specify dimensions clearly (by department, by region)
- Request specific measures (budget, actual, forecast)
- Use business terminology, not technical names

### Data Analysis
- Always request variance analysis for budget/actual comparisons
- Use outlier detection for large datasets
- Request key driver analysis for material variances
- Generate executive summaries for board presentations

### Performance Optimization
- Use pre-analyzed cubes when available
- Filter data at query time, not post-processing
- Use aggregated members for high-level views
- Request only needed dimensions and measures

### Error Handling
- Check cube availability before querying
- Verify member existence before filtering
- Handle empty results gracefully
- Provide clear error messages to users

## 📚 Additional Resources

- [IBM Planning Analytics Documentation](https://www.ibm.com/docs/en/planning-analytics)
- [TM1 REST API Reference](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=api-tm1-rest)
- [Planning Analytics Workspace Guide](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=planning-analytics-workspace)
- [MDX Reference](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=reference-mdx)

## 📄 License

This building block is provided as-is for use with IBM Planning Analytics.

## 🙏 Acknowledgments

- Built for IBM Planning Analytics and TM1
- Powered by Model Context Protocol (MCP)
- Integrated with Bob AI assistant
- Designed for financial planning and analysis professionals

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review skill USAGE-GUIDE.md for detailed examples
3. Verify MCP server configuration
4. Check Planning Analytics API access
5. Review mode rules for workflow guidance

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-17  
**Status**: Production Ready ✅

Made with ❤️ for IBM Planning Analytics users