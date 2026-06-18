# Planning Analytics Mode for Budget and Forecasting

A specialized Bob mode for IBM Planning Analytics that provides TM1 modeling expertise, workflow orchestration, and best practices for financial planning and analysis.

## Features

- Natural language to TM1 query translation
- TM1 modeling expertise (cubes, dimensions, rules, processes)
- Planning Analytics Workspace guidance
- REST API and OData integration patterns
- Financial analysis workflows (variance, trend, outlier detection)
- Executive reporting templates
- Best practices and troubleshooting workflows
- Response formatting for business users

## Mode Structure

The Planning Analytics mode includes:

1. **Mode Configuration** ([`custom_modes.yaml`](custom_modes.yaml))
2. **Mode Rules** ([`rules-planning-analytics/`](rules-planning-analytics/))
   - [`1_overview.xml`](rules-planning-analytics/1_overview.xml) - Mode purpose and capabilities
   - [`2_mcp_tools_reference.xml`](rules-planning-analytics/2_mcp_tools_reference.xml) - MCP tools documentation
   - [`3_workflows.xml`](rules-planning-analytics/3_workflows.xml) - Common workflow patterns
   - [`4_best_practices.xml`](rules-planning-analytics/4_best_practices.xml) - TM1 best practices
   - [`5_response_patterns.xml`](rules-planning-analytics/5_response_patterns.xml) - Business-friendly formatting
   - [`6_troubleshooting.xml`](rules-planning-analytics/6_troubleshooting.xml) - Common issues and solutions

## What This Mode Provides

### 1. TM1 Modeling Expertise
- **Cube Design**: Dimensional modeling, measure selection, aggregation rules
- **Dimension Management**: Hierarchies, attributes, consolidations, aliases
- **Rules & Calculations**: TM1 rules syntax, feeders, performance optimization
- **TurboIntegrator Processes**: Data loading, transformations, automation

### 2. Planning Analytics Workflows
- **Budget vs Actual Analysis**: Variance calculation, material variance identification
- **Forecast Analysis**: Forecast accuracy tracking, scenario comparison
- **Year-over-Year Analysis**: Growth trends, CAGR calculations
- **Trend Analysis**: Time series, moving averages, seasonal patterns
- **Outlier Detection**: Statistical analysis, anomaly identification
- **Key Driver Analysis**: Impact analysis, contribution breakdowns

### 3. API Integration Patterns
- **REST API**: Authentication, endpoint usage, response handling
- **OData**: Query construction, filtering, pagination
- **MDX Queries**: Multi-dimensional expressions, set operations
- **Server-Side Operations**: Process execution, cube management

### 4. Business-Focused Communication
- **Executive Summaries**: Key findings, actionable insights
- **Variance Explanations**: Root cause analysis, impact assessment
- **Professional Formatting**: Tables, charts, reports
- **Business Terminology**: Revenue, expenses, margins (not technical jargon)

## Installation

### Step 1: Extract the Mode Package
```bash
cd optimize/budget-and-forecasting/bob-modes/base-modes
unzip planning-analytics-mode.zip -d ~/.bob/modes/planning-analytics
```

### Step 2: Verify Installation
Check that the mode files are in place:
```bash
ls -la ~/.bob/modes/planning-analytics
```

You should see:
- `custom_modes.yaml` - Mode configuration
- `rules-planning-analytics/` - Mode rules directory

### Step 3: Restart Bob
Restart Bob to load the new mode configuration.

### Step 4: Activate the Mode
1. Open Bob
2. Look for "Planning Analytics" in the mode selector
3. Switch to Planning Analytics mode
4. The mode is now active with specialized capabilities

## Mode Configuration

The mode is configured in [`custom_modes.yaml`](custom_modes.yaml) with:

- **Mode Name**: Planning Analytics
- **Mode Slug**: planning-analytics
- **Description**: Specialized mode for IBM Planning Analytics and TM1
- **Capabilities**: TM1 modeling, financial analysis, MDX queries
- **File Restrictions**: Can edit `.md`, `.xml`, `.json`, `.yaml`, `.py`, `.js` files
- **Rules Directory**: `rules-planning-analytics/`

## Usage Examples

Once activated, you can ask Bob questions like:

### TM1 Modeling
- *"Create a Financial Performance cube with Time, Account, Department dimensions"*
- *"Design a dimension hierarchy for organizational structure"*
- *"Write a TM1 rule to calculate budget variance"*
- *"Create a TurboIntegrator process to load CSV data"*

### Financial Analysis
- *"Show Q1 2025 budget vs actual variance by department"*
- *"What's driving the revenue variance in North America?"*
- *"Identify outliers in March expense data"*
- *"Calculate year-over-year growth for all regions"*

### Query Construction
- *"Generate MDX to get Q1 revenue by region"*
- *"Create an OData query for budget data"*
- *"Build a REST API call to fetch pending actions"*
- *"Construct a search query for applications"*

### Troubleshooting
- *"Why is my TM1 rule not feeding?"*
- *"How do I optimize slow cube queries?"*
- *"What's the best way to handle large data loads?"*
- *"Why am I getting authentication errors?"*

## Mode Rules Overview

### 1. Overview ([`1_overview.xml`](rules-planning-analytics/1_overview.xml))
Defines the mode's purpose, capabilities, and scope:
- Mode identity and specialization
- Core competencies
- When to use this mode
- Integration with MCP tools

### 2. MCP Tools Reference ([`2_mcp_tools_reference.xml`](rules-planning-analytics/2_mcp_tools_reference.xml))
Comprehensive documentation of available MCP tools:
- Discovery tools (servers, cubes, dimensions, members)
- Query tools (natural language, MDX, data explorer)
- Analysis tools (impact, outlier, reporting)
- Management tools (cubes, views, processes)
- Tool usage patterns and examples

### 3. Workflows ([`3_workflows.xml`](rules-planning-analytics/3_workflows.xml))
Common workflow patterns for financial analysis:
- Budget vs Actual variance analysis workflow
- Year-over-Year comparison workflow
- Forecast accuracy assessment workflow
- Outlier investigation workflow
- Executive report generation workflow
- Cube discovery and exploration workflow

### 4. Best Practices ([`4_best_practices.xml`](rules-planning-analytics/4_best_practices.xml))
TM1 and Planning Analytics best practices:
- Cube design principles
- Dimension modeling guidelines
- Rule writing best practices
- Process optimization techniques
- Query performance optimization
- Security and access control
- Data quality management

### 5. Response Patterns ([`5_response_patterns.xml`](rules-planning-analytics/5_response_patterns.xml))
Business-friendly response formatting:
- Executive summary format
- Variance report format
- Trend analysis format
- Outlier report format
- Key findings presentation
- Actionable recommendations
- Professional table formatting

### 6. Troubleshooting ([`6_troubleshooting.xml`](rules-planning-analytics/6_troubleshooting.xml))
Common issues and solutions:
- Authentication failures
- Cube not found errors
- Member not found errors
- Query timeout issues
- No data returned scenarios
- Rule feeding problems
- Process execution failures
- Performance issues

## MCP Tools Integration

The mode leverages these MCP tools for Planning Analytics:

### Discovery Tools
- `get_available_tm1_servers` - List available servers
- `get_tm1_cubes` - List cubes with metadata
- `list_cubes_with_ai_analysis_metadata` - Check pre-analyzed cubes
- `get_cube_dimensions` - Get cube dimensions
- `get_cube_sample_members` - See sample members
- `lookup_potential_members` - Search for members

### Query Tools
- `get_data_from_data_explorer` - Natural language queries
- `execute_mdx_and_get_view` - Direct MDX queries
- `get_MDX_for_recommended_view` - Generate MDX

### Analysis Tools
- `perform_impact_analysis` - Identify key drivers
- `perform_outlier_detection` - Find anomalies
- `generate_exploration_analysis_report` - Create PDF reports

### Management Tools
- `create_tm1_cube` / `delete_tm1_cube` - Cube management
- `save_mdx_view` / `get_saved_view` / `list_cube_views` - View management
- `create_tm1_process` / `update_tm1_process` / `delete_tm1_process` - Process CRUD
- `execute_tm1_processes_asynchronously` - Execute processes

## Workflow Examples

### Budget vs Actual Variance Analysis
1. **Discover**: Use `get_tm1_cubes` to find Financial Performance cube
2. **Explore**: Use `get_cube_dimensions` to understand structure
3. **Query**: Use `get_data_from_data_explorer` for budget vs actual data
4. **Analyze**: Calculate variances, identify material differences
5. **Report**: Generate executive summary with key findings

### Year-over-Year Growth Analysis
1. **Discover**: Identify cube with historical data
2. **Query**: Fetch current year and prior year actuals
3. **Calculate**: Compute YoY growth rates and trends
4. **Visualize**: Present trends with growth percentages
5. **Insights**: Identify growth drivers and patterns

### Outlier Detection Workflow
1. **Query**: Fetch data for analysis period
2. **Analyze**: Use `perform_outlier_detection` tool
3. **Investigate**: Examine flagged anomalies
4. **Explain**: Generate root cause analysis
5. **Report**: Present findings with recommendations

## Best Practices

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

## Troubleshooting

### Mode doesn't appear after installation
1. Verify extraction path is correct (`~/.bob/modes/`)
2. Check file permissions on extracted files
3. Restart Bob to refresh mode list
4. Review Bob logs for error messages

### Mode is active but doesn't understand Planning Analytics queries
1. Be specific in requests (mention cube names, dimensions)
2. Reference specific features (variance analysis, trend analysis)
3. Provide context about what you're analyzing
4. Ask Bob to explain mode capabilities if unsure

### MCP tools not working
1. Verify MCP configuration in `~/.bob/mcp.json`
2. Check Planning Analytics credentials
3. Ensure network access to Planning Analytics instance
4. Review MCP server logs for errors

### Queries returning no data
1. Verify cube and member names are correct
2. Check time period selection
3. Use discovery tools to explore available data
4. Review dimension selections and filters

## Performance Notes

- Mode rules are loaded once at startup
- MCP tool calls are made on-demand
- Response formatting is optimized for readability
- Workflow patterns guide efficient tool usage

## Security Notes

- Mode has no special security privileges
- Respects TM1 security model and permissions
- Credentials managed through MCP configuration
- No data stored locally by the mode

## Related Resources

- [IBM Planning Analytics Documentation](https://www.ibm.com/docs/en/planning-analytics)
- [TM1 REST API Reference](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=api-tm1-rest)
- [Planning Analytics Workspace Guide](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=planning-analytics-workspace)
- [MDX Reference](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=reference-mdx)
- [Parent Directory README](../../README.md) - Complete building block documentation
- [Bob Skills README](../../bob-skills/README.md) - Planning Analytics skill documentation

## Version Information

- **Mode Version**: 1.0.0
- **Compatible with**: IBM Planning Analytics v11.x and later, TM1 v10.x and later
- **Last Updated**: 2026-06-17
- **Status**: Production Ready ✅

## Support

For issues or questions about this mode:
1. Check the troubleshooting section above
2. Review mode rules in `rules-planning-analytics/`
3. Review the [parent directory README](../../README.md) for examples
4. Ask Bob directly - the mode includes comprehensive knowledge
5. Refer to IBM Planning Analytics documentation

---

**Note**: This mode requires IBM Planning Analytics or TM1 access and valid API credentials configured in MCP settings.

Made with ❤️ for IBM Planning Analytics users