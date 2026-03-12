# Portfolio Advisor Agent

AI-powered financial adviser agent that helps account holders manage investment portfolios and track asset performance in the financial services domain.

## Overview

The Portfolio Advisor Agent is a watsonx Orchestrate agent designed to help account holders with:
- Portfolio performance tracking and analysis
- Investment report generation
- Asset allocation monitoring
- Portfolio metrics calculation
- Personalized investment communications

## Quick Start

### Prerequisites
- Python 3.8+
- watsonx Orchestrate API key
- IBM watsonx Orchestrate CLI (uvx with ibm-watsonx-orchestrate package)

### Deployment

1. Ensure you have your WXO API key ready (you'll be asked for it during deployment)

2. Make deployment scripts executable:
```bash
chmod +x portfolio-advisor-agent/scripts/*.sh
```

3. Deploy the agent:
```bash
cd portfolio-advisor-agent
./scripts/deploy_all.sh
```

Note: During deployment, you will be prompted for your WXO API key to activate the environment.

## Project Structure

```
portfolio-advisor-agent/
├── agent_config.yaml                    # Agent configuration
├── tools/
│   ├── account_holder_tools.py         # Account holder management tools
│   └── communication_tools.py          # Investment communication generation
├── data/
│   └── account_holders.csv             # Account holder portfolio data
├── knowledge_bases/
│   └── finance_portfolio_kb.yaml       # Knowledge base configuration
├── scripts/
│   ├── deploy_all.sh                   # Complete deployment script
│   ├── import_tools.sh                 # Import tools script
│   ├── import_kb.sh                    # Import knowledge base script
│   └── deploy_agent.sh                 # Deploy agent script
└── README.md                            # This file
```

## Capabilities

### Account Holder Management
- **Retrieve account holder data**: Get portfolio information with flexible filtering by account ID, tier, or status
- **Get specific account holder**: Look up individual account holders by their unique account ID
- **Filter by tier**: Retrieve all account holders in a specific tier (Bronze, Silver, Gold, Diamond)
- **Calculate portfolio metrics**: Compute aggregated analytics including total AUM, average returns, and asset allocation

### Investment Communication Generation
- **Portfolio Performance Reports**: Comprehensive analysis with returns, allocation, and recommendations
- **Quarterly Statements**: Formal quarterly investment statements with detailed holdings
- **Investment Recommendations**: Personalized investment opportunities and portfolio optimization
- **Rebalancing Alerts**: Notifications when portfolio allocation drifts from targets
- **Market Updates**: Timely market insights and portfolio impact analysis

## Account Holder Tiers

- **Bronze**: Entry-level accounts with portfolio values up to $100K
  - Benefits: Basic portfolio tracking and quarterly reports
  
- **Silver**: Mid-tier accounts with portfolio values $100K-$500K
  - Benefits: Enhanced reporting, monthly statements, and priority support
  
- **Gold**: Premium accounts with portfolio values $500K-$2M
  - Benefits: Advanced analytics, personalized recommendations, and dedicated advisor access
  
- **Diamond**: Elite accounts with portfolio values over $2M
  - Benefits: Comprehensive wealth management, real-time alerts, custom strategies, and white-glove service

## Sample Queries

Try these queries with the agent:

### Retrieve Account Holder Data
- "Show me all account holders in Gold tier"
- "Get details for account holder ACC001"
- "List all active account holders"
- "Show me Diamond tier account holders"

### Generate Investment Communications
- "Generate a portfolio performance report for ACC001"
- "Create a quarterly statement for ACC002"
- "Generate investment recommendations for ACC005"
- "Send a rebalancing alert to ACC003"
- "Create a market update for ACC007"

### Calculate Portfolio Metrics
- "Calculate portfolio metrics for Gold tier account holders"
- "Show me overall portfolio statistics"
- "Calculate metrics for all account holders"
- "What's the average return for Silver tier?"

### Knowledge Base Queries
- "What investment goals does ACC001 have?"
- "Tell me about account holder risk tolerance levels"
- "What are the asset allocation strategies?"

## Customization

### Adding New Tools
1. Create a new Python file in `tools/`
2. Use the `@tool` decorator from `ibm_watsonx_orchestrate.agent_builder.tools`
3. Embed data directly in the tool (do not load from CSV files)
4. Import tools: `./scripts/import_tools.sh`
5. Redeploy agent: `./scripts/deploy_agent.sh`

### Modifying Account Holder Data
1. Edit `data/account_holders.csv` with new portfolio data
2. Update embedded data in `tools/account_holder_tools.py` and `tools/communication_tools.py`
3. Redeploy knowledge base: `./scripts/import_kb.sh`
4. Re-import tools: `./scripts/import_tools.sh`
5. Redeploy agent: `./scripts/deploy_agent.sh`

### Updating Agent Configuration
1. Edit `agent_config.yaml`
2. Redeploy: `uvx --from ibm-watsonx-orchestrate orchestrate agents import -f agent_config.yaml`
3. Deploy: `uvx --from ibm-watsonx-orchestrate orchestrate agents deploy -n portfolio_advisor_agent`

### Adding New Communication Types
1. Edit `tools/communication_tools.py`
2. Add new template in `_get_message_template()` function
3. Update agent_config.yaml to document the new communication type
4. Re-import tools and redeploy

## Data Model

### Account Holder Fields
- `account_id`: Unique account identifier (e.g., ACC001)
- `name`: Account holder name
- `email`: Contact email
- `phone`: Contact phone number
- `tier`: Account tier (Bronze, Silver, Gold, Diamond)
- `status`: Account status (active, inactive)
- `portfolio_value`: Total portfolio value in USD
- `asset_allocation`: Breakdown by asset type (stocks, bonds, real_estate, cash)
- `investment_goals`: Account holder's investment objectives
- `risk_tolerance`: Risk profile (Low, Moderate, Moderate-High, High, Conservative)
- `ytd_return`: Year-to-date return percentage
- `account_opened`: Account opening date

## Troubleshooting

### Common Issues

**Issue: API key not found during deployment**
- Solution: You will be prompted for your API key during deployment. Have it ready when running `./scripts/deploy_all.sh`

**Issue: Tool import fails**
- Solution: Check Python syntax and ensure `@tool` decorators are present on all tool functions

**Issue: Knowledge base import fails**
- Solution: Verify YAML syntax in `knowledge_bases/finance_portfolio_kb.yaml` and ensure data file paths are correct

**Issue: Agent deployment fails**
- Solution: Check `agent_config.yaml` syntax and ensure all referenced tools and knowledge bases exist

**Issue: "Account holder not found" errors**
- Solution: Verify that data is embedded directly in tools (not loaded from CSV files). WXO tools cannot access local files when deployed.

**Issue: Scripts not executable**
- Solution: Run `chmod +x scripts/*.sh` to make scripts executable

## Technical Notes

### Data Access Pattern
⚠️ **IMPORTANT**: WXO tools run in an isolated cloud environment and cannot access local CSV files. All tools embed data directly as Python dictionaries. The CSV files in the `data/` directory are used only for knowledge base vectorization, not for tool data access.

### Tool Isolation
Tools in WXO are self-contained and cannot call other tools or import functions from other tool files. Each tool must embed its own copy of any data it needs.

### Maximum Tools
Agents are limited to a maximum of 5 tools for optimal performance. This agent uses all 5 slots:
1. get_account_holder_data
2. get_account_holder_by_id
3. get_account_holders_by_tier
4. calculate_portfolio_metrics
5. generate_investment_communication

## Next Steps

1. **Replace sample data** with real account holder portfolio data
2. **Customize communication templates** with your firm's branding
3. **Add domain-specific tools** as needed (within the 5-tool limit)
4. **Integrate with external systems** or APIs for live portfolio data
5. **Set up monitoring and logging** for production use
6. **Gather user feedback** and iterate on capabilities

## Support

For issues or questions:
- Review the troubleshooting section above
- Check the [watsonx Orchestrate documentation](https://developer.watson-orchestrate.ibm.com/)
- Verify all deployment steps were completed successfully

## License

[Your License Information]