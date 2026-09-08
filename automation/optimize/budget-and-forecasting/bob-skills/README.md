# Budget and Forecasting Skills

This directory contains Bob skills for Budget and Forecasting using IBM Planning Analytics.

## 🎯 Overview

The `planning-analytics-skill.zip` skill empowers Bob to help you explore IBM Planning Analytics and TM1 data through natural language queries, enabling business-focused insights, variance analysis, and executive-ready reporting for budget and forecasting workflows.

## 📦 Available Skill

### planning-analytics-skill

A comprehensive skill for working with IBM Planning Analytics, providing capabilities for:

#### 1. 🗣️ **Natural Language Queries**
Transform business questions into Planning Analytics insights:
- Plain English queries (no MDX knowledge required)
- Automatic cube and dimension discovery
- Member lookup and validation
- Query translation (Natural Language → MDX)
- Pre-analyzed cube support for faster results

#### 2. 📊 **Variance Analysis**
Comprehensive financial variance analysis capabilities:
- Budget vs Actual comparisons with automatic variance calculation
- Forecast vs Actual accuracy tracking
- Period-over-Period analysis (Month-over-Month, Quarter-over-Quarter)
- Year-over-Year growth analysis
- Material variance identification (>10% or >$100K)
- Hierarchical rollups (department → region → total)

#### 3. 🔍 **Outlier Detection**
Identify anomalous patterns requiring attention:
- Statistical outlier detection
- Pattern anomaly identification
- Threshold-based alerts
- Root cause suggestions
- Variance volatility tracking

#### 4. 📈 **Key Driver Analysis**
Understand what's driving your results:
- Impact analysis for material variances
- Contribution analysis by dimension
- Waterfall breakdowns
- Driver ranking and prioritization
- Cross-functional impact assessment

#### 5. 📄 **Executive Reporting**
Professional, business-ready report generation:
- Executive summaries with key findings
- Variance reports with explanations
- Trend analysis visualizations
- Key metrics highlights
- Actionable recommendations
- PDF report generation

#### 6. 🤖 **AI-Powered Insights**
Automated analysis and recommendations:
- AI-generated variance explanations
- Automated root cause analysis
- Predictive variance modeling
- Forecast accuracy improvement suggestions
- Business context generation

## 🚀 Installation and Setup

### Step 1: Download the Skill
Download the `planning-analytics-skill.zip` file from this directory.

### Step 2: Extract the Skill to Bob Workspace
Extract the contents to your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the skill
unzip /path/to/planning-analytics-skill.zip
```

After extraction, you should see a `planning-analytics` folder in your `.bob/skills` directory.

### Step 3: Configure MCP Servers
Copy the MCP configuration from the assets directory:

```bash
cp optimize/budget-and-forecasting/assets/mcp.json ~/.bob/mcp.json
```

**Update credentials** in mcp.json:
- Replace `Authorization` header with your Planning Analytics API key
- Update server URLs if using different instances
- Configure timeout values based on your data volume

To encode credentials:
```bash
echo -n "APIKey:your-api-key" | base64
```

### Step 4: Verify Installation
Check that the skill is properly installed:

```bash
ls -la .bob/skills/planning-analytics
```

You should see the skill files including SKILL.md, README.md, USAGE-GUIDE.md, and examples.

### Step 5: Activate the Skill
To use the skill:
1. Open Bob and select Advanced mode (or any mode with MCP support)
2. Enable the **Skills** button in that mode
3. The `planning-analytics` skill will be available for use within that mode

## 💡 Usage Examples

Once activated, you can ask Bob to help with tasks like:

### Budget vs Actual Analysis
- *"Show Q1 2025 compensation budget vs actual by department"*
- *"What's the variance in marketing expenses for March?"*
- *"Compare budget to actual revenue by region"*
- *"Identify all material variances for January 2024"*

### Forecast Analysis
- *"Show forecast vs actual sales for Q4"*
- *"What's the forecast accuracy by product line?"*
- *"Compare forecast to actual by region"*
- *"How accurate was the Q2 forecast?"*

### Year-over-Year Analysis
- *"Compare Q1 2024 revenue to Q1 2023 by region"*
- *"Show year-over-year growth trends for North America Sales"*
- *"What is the 3-year CAGR for enterprise software revenue?"*
- *"Which region had the strongest YoY growth?"*

### Trend Analysis
- *"Show sales trends over the last 12 months"*
- *"What are the quarterly revenue patterns?"*
- *"Display monthly expense trends for 2024"*
- *"Calculate the 3-month rolling average for R&D expenses"*

### Outlier Detection
- *"Find unusual expense patterns in March"*
- *"Identify anomalies in sales data"*
- *"Show outliers in compensation by department"*
- *"Which departments have the most variance volatility?"*

### Key Driver Analysis
- *"What's driving revenue variance in the East region?"*
- *"Identify top contributors to expense growth"*
- *"Show key drivers of profit change"*
- *"How did the sales miss impact other departments?"*

### Executive Reporting
- *"Generate executive summary for Q1 results"*
- *"Create variance report for the board"*
- *"Produce monthly financial dashboard"*
- *"Generate PDF report with variance analysis"*

## 🎓 What Bob Can Help You Build

With this skill, Bob can assist you in creating:

1. **Financial Dashboards**: Interactive Planning Analytics dashboards with variance analysis and trend visualization
2. **Variance Reports**: Automated variance investigation reports with AI-generated explanations
3. **Forecast Models**: Predictive models for forecast accuracy improvement
4. **Custom Queries**: Tailored MDX queries for specific business requirements
5. **TM1 Processes**: TurboIntegrator processes for data loading and automation
6. **Executive Summaries**: Business-ready reports with key findings and recommendations

## 📋 Prerequisites

To work with this skill effectively, you should have:

- IBM Planning Analytics or TM1 instance (v11.x or higher recommended)
- Valid Planning Analytics credentials with API access
- Network connectivity to your Planning Analytics instance
- Bob AI assistant with MCP support enabled
- Basic understanding of financial planning concepts (Bob will guide you through the technical details)

## 🔧 Key Technologies

This skill helps you work with:

- **IBM Planning Analytics**: Enterprise planning and analytics platform
- **TM1**: Multi-dimensional OLAP database engine
- **MDX**: Multi-dimensional expressions query language
- **Planning Analytics REST API**: RESTful API for data access
- **OData**: Open Data Protocol for standardized queries
- **Model Context Protocol (MCP)**: Tool integration framework
- **Planning Analytics Workspace**: Modern web-based interface

## 🔍 MCP Tools Reference

The skill leverages these MCP tools:

### Discovery Tools
- `get_available_tm1_servers` - List available Planning Analytics servers
- `get_tm1_cubes` - List cubes with metadata
- `list_cubes_with_ai_analysis_metadata` - Check pre-analyzed cubes
- `get_cube_dimensions` - Get cube dimensions and hierarchies
- `get_cube_sample_members` - See sample dimension members
- `lookup_potential_members` - Search for members by name

### Query Tools
- `get_data_from_data_explorer` - Natural language queries (pre-analyzed cubes)
- `execute_mdx_and_get_view` - Direct MDX queries (any cube)
- `get_MDX_for_recommended_view` - Generate MDX from natural language

### Analysis Tools
- `perform_impact_analysis` - Identify key drivers and impacts
- `perform_outlier_detection` - Find anomalies and patterns
- `generate_exploration_analysis_report` - Create comprehensive PDF reports

### Management Tools
- `create_tm1_cube` / `delete_tm1_cube` - Cube management
- `save_mdx_view` / `get_saved_view` / `list_cube_views` - View management
- `create_tm1_process` / `update_tm1_process` / `delete_tm1_process` - Process CRUD
- `execute_tm1_processes_asynchronously` - Execute TurboIntegrator processes

## 🐛 Troubleshooting

### Skill doesn't appear after installation
1. Verify the extraction path is correct (`.bob/skills/`)
2. Check file permissions on the extracted files
3. Restart Bob to refresh the skills list
4. Ensure you've enabled the Skills button in your current mode
5. Review Bob logs for any error messages

### Skill is active but Bob doesn't understand Planning Analytics requests
1. Be specific in your requests (mention "Planning Analytics" or specific cube names)
2. Reference specific features (e.g., "budget vs actual", "variance analysis")
3. Provide context about what you're trying to analyze
4. Ask Bob to explain the skill's capabilities if unsure

### "Cube not found" error
1. Use `get_tm1_cubes` to list available cubes
2. Verify server connection in mcp.json
3. Check cube name spelling and case sensitivity
4. Ensure you have access permissions to the cube

### "Cube not pre-analyzed" message
1. Check status with `list_cubes_with_ai_analysis_metadata`
2. Switch to `execute_mdx_and_get_view` with MDX query
3. Use `get_cube_sample_members` to construct MDX manually

### "Member not found" error
1. Use `lookup_potential_members` to search for members
2. Use `get_cube_sample_members` to see available members
3. Check member name spelling and hierarchy path

### Query timeout issues
1. Increase timeout in mcp.json (default: 300 seconds)
2. Add filters to reduce data volume
3. Use aggregated members instead of leaf members
4. Consider breaking large queries into smaller chunks

### Authentication failed
1. Verify API key is correct and active
2. Check network access to Planning Analytics
3. Regenerate API key if expired
4. Verify Authorization header format in mcp.json

### No data returned
1. Verify members exist and have data
2. Check time period selection
3. Use `get_cube_sample_members` to find populated members
4. Review dimension selections and filters

## 📚 Related Resources

- [IBM Planning Analytics Documentation](https://www.ibm.com/docs/en/planning-analytics)
- [TM1 REST API Reference](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=api-tm1-rest)
- [Planning Analytics Workspace Guide](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=planning-analytics-workspace)
- [MDX Reference](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=reference-mdx)
- [Parent Directory README](../README.md) - Complete building block documentation
- [Sample Dataset](../assets/FPA_Variance_Analysis/README.md) - Hands-on learning dataset

## 🎯 Skill Capabilities Summary

| Capability | Description |
|------------|-------------|
| **Natural Language Queries** | Ask questions in plain English, no MDX required |
| **Variance Analysis** | Budget vs Actual, Forecast vs Actual, Period-over-Period |
| **Outlier Detection** | Statistical analysis to identify anomalies |
| **Key Driver Analysis** | Understand what's driving variances and trends |
| **Executive Reporting** | Professional reports with AI-generated insights |
| **Trend Analysis** | Time series analysis with growth rates and patterns |
| **Forecast Accuracy** | Track and improve forecast accuracy over time |
| **Cross-Functional Impact** | Analyze how variances cascade across departments |
| **Cube Discovery** | Automatic discovery of cubes, dimensions, and members |
| **MDX Generation** | Automatic MDX query generation from natural language |

## 📊 Performance

Typical response times:

- **Initial Discovery**: ~2-5 seconds (server + cube listing)
- **Simple Query**: ~1-3 seconds (pre-analyzed cubes)
- **Complex Query**: ~5-15 seconds (MDX with calculations)
- **Variance Analysis**: ~3-10 seconds (depends on data volume)
- **Outlier Detection**: ~10-30 seconds (statistical analysis)
- **PDF Report**: ~15-45 seconds (includes analysis + formatting)

## 💬 Support

For issues or questions about this skill:
1. Check the troubleshooting section above
2. Review the [parent directory README](../README.md) for detailed examples
3. Review the skill's USAGE-GUIDE.md for comprehensive usage instructions
4. Ask Bob directly - the skill includes comprehensive knowledge
5. Refer to IBM Planning Analytics documentation for API-specific questions

## 📝 Version Information

- **Skill Version**: 1.0.0
- **Compatible with**: IBM Planning Analytics v11.x and later, TM1 v10.x and later
- **Last Updated**: 2026-06-17
- **Status**: Production Ready ✅

---

**Note**: This skill requires IBM Planning Analytics or TM1 access and valid API credentials. Ensure you have proper access and credentials before starting.

Made with ❤️ for IBM Planning Analytics users