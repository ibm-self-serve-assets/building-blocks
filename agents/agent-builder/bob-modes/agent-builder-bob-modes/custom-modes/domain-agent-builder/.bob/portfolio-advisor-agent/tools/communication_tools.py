"""
Communication Tools for Portfolio Advisor Agent

This module provides tools for generating personalized investment communications
for account holders in the financial portfolio management domain.

⚠️ IMPORTANT: Data is embedded directly in the tools since WXO tools
cannot access local CSV files when deployed. Tools do NOT call other tools
(e.g., get_account_holder_by_id). In WXO, tools run in isolation and must be
self-contained.
"""
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import Dict, Optional, Any
from datetime import datetime


# Embedded account holder data - WXO tools cannot access local files
ACCOUNT_HOLDER_DATA = [
    {
        "account_id": "ACC001",
        "name": "Sarah Johnson",
        "email": "sarah.johnson@email.com",
        "tier": "Diamond",
        "status": "active",
        "portfolio_value": 2500000.00,
        "asset_allocation": {"stocks": 60, "bonds": 25, "real_estate": 10, "cash": 5},
        "investment_goals": "Long-term growth and wealth preservation",
        "risk_tolerance": "Moderate",
        "ytd_return": 12.5
    },
    {
        "account_id": "ACC002",
        "name": "Michael Chen",
        "email": "michael.chen@email.com",
        "tier": "Gold",
        "status": "active",
        "portfolio_value": 850000.00,
        "asset_allocation": {"stocks": 70, "bonds": 20, "real_estate": 5, "cash": 5},
        "investment_goals": "Aggressive growth for retirement",
        "risk_tolerance": "High",
        "ytd_return": 15.2
    },
    {
        "account_id": "ACC003",
        "name": "Emily Rodriguez",
        "email": "emily.rodriguez@email.com",
        "tier": "Silver",
        "status": "active",
        "portfolio_value": 325000.00,
        "asset_allocation": {"stocks": 55, "bonds": 35, "real_estate": 5, "cash": 5},
        "investment_goals": "Balanced growth and income",
        "risk_tolerance": "Moderate",
        "ytd_return": 9.8
    },
    {
        "account_id": "ACC004",
        "name": "David Thompson",
        "email": "david.thompson@email.com",
        "tier": "Bronze",
        "status": "active",
        "portfolio_value": 75000.00,
        "asset_allocation": {"stocks": 50, "bonds": 40, "real_estate": 0, "cash": 10},
        "investment_goals": "Building wealth for first home",
        "risk_tolerance": "Low",
        "ytd_return": 7.5
    },
    {
        "account_id": "ACC005",
        "name": "Jennifer Martinez",
        "email": "jennifer.martinez@email.com",
        "tier": "Gold",
        "status": "active",
        "portfolio_value": 1200000.00,
        "asset_allocation": {"stocks": 65, "bonds": 25, "real_estate": 8, "cash": 2},
        "investment_goals": "Retirement planning and legacy building",
        "risk_tolerance": "Moderate-High",
        "ytd_return": 11.3
    },
    {
        "account_id": "ACC006",
        "name": "Robert Kim",
        "email": "robert.kim@email.com",
        "tier": "Silver",
        "status": "active",
        "portfolio_value": 280000.00,
        "asset_allocation": {"stocks": 60, "bonds": 30, "real_estate": 5, "cash": 5},
        "investment_goals": "College savings and retirement",
        "risk_tolerance": "Moderate",
        "ytd_return": 10.1
    },
    {
        "account_id": "ACC007",
        "name": "Lisa Anderson",
        "email": "lisa.anderson@email.com",
        "tier": "Diamond",
        "status": "active",
        "portfolio_value": 3800000.00,
        "asset_allocation": {"stocks": 55, "bonds": 30, "real_estate": 12, "cash": 3},
        "investment_goals": "Wealth preservation and philanthropic planning",
        "risk_tolerance": "Conservative",
        "ytd_return": 8.9
    },
    {
        "account_id": "ACC008",
        "name": "James Wilson",
        "email": "james.wilson@email.com",
        "tier": "Bronze",
        "status": "active",
        "portfolio_value": 45000.00,
        "asset_allocation": {"stocks": 45, "bonds": 45, "real_estate": 0, "cash": 10},
        "investment_goals": "Emergency fund and long-term savings",
        "risk_tolerance": "Low",
        "ytd_return": 6.2
    }
]


@tool
def generate_investment_communication(
    account_id: str,
    communication_type: str,
    custom_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate personalized investment communications for account holders.

    Args:
        account_id: The account holder's unique identifier
        communication_type: Type of communication ('portfolio_performance_report', 
                          'quarterly_statement', 'investment_recommendation', 
                          'rebalancing_alert', 'market_update')
        custom_content: Optional custom content to include

    Returns:
        Dictionary containing the generated communication with subject and body

    Example:
        >>> generate_investment_communication("ACC001", "portfolio_performance_report")
        {"subject": "...", "body": "...", "format": "html"}
    """
    # Look up from embedded data (do NOT call other tools! do NOT load from CSV!)
    account_holder = None
    for a in ACCOUNT_HOLDER_DATA:
        if a.get('account_id') == account_id:
            account_holder = a
            break
    
    if not account_holder:
        return {
            "error": f"Account holder {account_id} not found",
            "subject": "Error",
            "body": f"<p>Could not find account holder with ID {account_id}</p>",
            "format": "html"
        }
    
    # Get message template based on type
    template = _get_message_template(communication_type, account_holder.get('tier'))
    
    # Personalize content
    personalized = _personalize_content(
        template,
        account_holder,
        custom_content
    )
    
    return {
        "subject": personalized["subject"],
        "body": personalized["body"],
        "format": "html",
        "account_id": account_id,
        "communication_type": communication_type
    }


def _get_message_template(communication_type: str, tier: Optional[str] = None) -> Dict[str, str]:
    """
    Get the appropriate message template based on type and tier.
    
    Args:
        communication_type: The type of communication to generate
        tier: Optional tier for tier-specific templates
    
    Returns:
        Dictionary with subject and body templates
    """
    # Define tier-specific styling
    tier_colors = {
        "Bronze": "#CD7F32",  # Bronze
        "Silver": "#C0C0C0",  # Silver
        "Gold": "#FFD700",    # Gold
        "Diamond": "#B9F2FF", # Diamond blue
    }
    
    tier_color = tier_colors.get(tier, "#2C3E50")
    current_date = datetime.now().strftime("%B %d, %Y")
    
    templates = {
        "portfolio_performance_report": {
            "subject": "Your Portfolio Performance Report",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
                    <div style="background: {tier_color}; color: white; padding: 30px; text-align: center;">
                        <h1 style="margin: 0;">Portfolio Advisor Agent</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">Your Intelligent Investment Partner</p>
                    </div>
                    <div style="padding: 30px; background: #f9f9f9;">
                        <p>Dear {{{{name}}}},</p>
                        <p>As a valued <strong>{{{{tier}}}}</strong> account holder, here is your comprehensive portfolio performance report as of {current_date}.</p>
                        
                        <div style="background: white; padding: 20px; margin: 20px 0; border-left: 4px solid {tier_color};">
                            <h2 style="color: {tier_color}; margin-top: 0;">Portfolio Summary</h2>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Total Portfolio Value:</strong></td>
                                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">${{{{portfolio_value}}}}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Year-to-Date Return:</strong></td>
                                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right; color: #27ae60;"><strong>{{{{ytd_return}}}}%</strong></td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px;"><strong>Risk Tolerance:</strong></td>
                                    <td style="padding: 10px; text-align: right;">{{{{risk_tolerance}}}}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div style="background: white; padding: 20px; margin: 20px 0; border-left: 4px solid {tier_color};">
                            <h2 style="color: {tier_color}; margin-top: 0;">Asset Allocation</h2>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">Stocks</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{{{{stocks}}}}%</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">Bonds</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{{{{bonds}}}}%</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">Real Estate</td>
                                    <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{{{{real_estate}}}}%</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px;">Cash</td>
                                    <td style="padding: 8px; text-align: right;">{{{{cash}}}}%</td>
                                </tr>
                            </table>
                        </div>
                        
                        {{{{custom_content}}}}
                        
                        <p style="margin-top: 30px;"><strong>Investment Goals:</strong> {{{{investment_goals}}}}</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" style="background: {tier_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                View Detailed Analysis
                            </a>
                        </div>
                        
                        <p style="font-size: 14px; color: #666;">As a <strong>{{{{tier}}}}</strong> account holder, you have access to {{{{tier_benefits}}}}.</p>
                        
                        <p>Best regards,<br>Your Portfolio Advisor Team</p>
                    </div>
                    <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                        <p>This report is for informational purposes only and does not constitute investment advice. Past performance does not guarantee future results.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        },
        "quarterly_statement": {
            "subject": "Your Quarterly Investment Statement",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
                    <div style="background: {tier_color}; color: white; padding: 30px; text-align: center;">
                        <h1 style="margin: 0;">Quarterly Statement</h1>
                        <p style="margin: 10px 0 0 0;">Quarter Ending {current_date}</p>
                    </div>
                    <div style="padding: 30px; background: #f9f9f9;">
                        <p>Dear {{{{name}}}},</p>
                        <p>Please find your quarterly investment statement for your <strong>{{{{tier}}}}</strong> account.</p>
                        
                        <div style="background: white; padding: 20px; margin: 20px 0;">
                            <h2 style="color: {tier_color};">Account Summary</h2>
                            <p><strong>Account ID:</strong> {{{{account_id}}}}</p>
                            <p><strong>Statement Period:</strong> Q1 2026</p>
                            <p><strong>Portfolio Value:</strong> ${{{{portfolio_value}}}}</p>
                            <p><strong>Quarterly Return:</strong> <span style="color: #27ae60;">{{{{ytd_return}}}}%</span></p>
                        </div>
                        
                        {{{{custom_content}}}}
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" style="background: {tier_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Download Full Statement
                            </a>
                        </div>
                        
                        <p>Thank you for your continued trust in our services.</p>
                        <p>Best regards,<br>Portfolio Advisor Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
        },
        "investment_recommendation": {
            "subject": "Personalized Investment Recommendation",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
                    <div style="background: {tier_color}; color: white; padding: 30px; text-align: center;">
                        <h1 style="margin: 0;">Investment Opportunity</h1>
                        <p style="margin: 10px 0 0 0;">Tailored for Your Portfolio</p>
                    </div>
                    <div style="padding: 30px; background: #f9f9f9;">
                        <p>Dear {{{{name}}}},</p>
                        <p>Based on your investment goals of <em>{{{{investment_goals}}}}</em> and your <strong>{{{{risk_tolerance}}}}</strong> risk tolerance, we have identified opportunities that may align with your portfolio strategy.</p>
                        
                        <div style="background: white; padding: 20px; margin: 20px 0; border-left: 4px solid {tier_color};">
                            <h2 style="color: {tier_color}; margin-top: 0;">Recommendation Highlights</h2>
                            <p>Your current portfolio allocation shows strong performance with a {{{{ytd_return}}}}% year-to-date return. We recommend considering diversification opportunities in emerging sectors that match your risk profile.</p>
                            {{{{custom_content}}}}
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" style="background: {tier_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Schedule Consultation
                            </a>
                        </div>
                        
                        <p style="font-size: 14px; color: #666;">As a <strong>{{{{tier}}}}</strong> member, you receive {{{{tier_benefits}}}}.</p>
                        
                        <p>Best regards,<br>Your Investment Advisory Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
        },
        "rebalancing_alert": {
            "subject": "Portfolio Rebalancing Alert",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
                    <div style="background: #e74c3c; color: white; padding: 30px; text-align: center;">
                        <h1 style="margin: 0;">⚠️ Rebalancing Alert</h1>
                        <p style="margin: 10px 0 0 0;">Action Recommended</p>
                    </div>
                    <div style="padding: 30px; background: #f9f9f9;">
                        <p>Dear {{{{name}}}},</p>
                        <p>Our analysis indicates that your portfolio allocation has drifted from your target allocation. We recommend rebalancing to maintain your desired risk profile.</p>
                        
                        <div style="background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #e74c3c;">
                            <h2 style="color: #e74c3c; margin-top: 0;">Current vs. Target Allocation</h2>
                            <p><strong>Current Allocation:</strong></p>
                            <ul>
                                <li>Stocks: {{{{stocks}}}}%</li>
                                <li>Bonds: {{{{bonds}}}}%</li>
                                <li>Real Estate: {{{{real_estate}}}}%</li>
                                <li>Cash: {{{{cash}}}}%</li>
                            </ul>
                            {{{{custom_content}}}}
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" style="background: #e74c3c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Review Rebalancing Options
                            </a>
                        </div>
                        
                        <p>Best regards,<br>Portfolio Management Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
        },
        "market_update": {
            "subject": "Market Update: Impact on Your Portfolio",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
                    <div style="background: {tier_color}; color: white; padding: 30px; text-align: center;">
                        <h1 style="margin: 0;">Market Update</h1>
                        <p style="margin: 10px 0 0 0;">{current_date}</p>
                    </div>
                    <div style="padding: 30px; background: #f9f9f9;">
                        <p>Dear {{{{name}}}},</p>
                        <p>We wanted to provide you with insights on recent market developments and their potential impact on your portfolio.</p>
                        
                        <div style="background: white; padding: 20px; margin: 20px 0; border-left: 4px solid {tier_color};">
                            <h2 style="color: {tier_color}; margin-top: 0;">Your Portfolio Performance</h2>
                            <p>Your portfolio has delivered a <strong style="color: #27ae60;">{{{{ytd_return}}}}%</strong> return year-to-date, demonstrating resilience in the current market environment.</p>
                            {{{{custom_content}}}}
                        </div>
                        
                        <p><strong>Investment Strategy:</strong> {{{{investment_goals}}}}</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" style="background: {tier_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Read Full Market Analysis
                            </a>
                        </div>
                        
                        <p>Best regards,<br>Market Research Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
    }
    
    return templates.get(communication_type, templates["portfolio_performance_report"])


def _personalize_content(
    template: Dict[str, str],
    account_holder: Dict[str, Any],
    custom_content: Optional[str] = None
) -> Dict[str, str]:
    """
    Personalize the message template with account holder information.
    
    Args:
        template: The message template
        account_holder: The account holder data
        custom_content: Optional custom content
    
    Returns:
        Personalized message with subject and body
    """
    # Get tier benefits
    tier_benefits_map = {
        "Bronze": "quarterly reports and basic portfolio tracking",
        "Silver": "monthly statements, enhanced reporting, and priority support",
        "Gold": "advanced analytics, personalized recommendations, and dedicated advisor access",
        "Diamond": "comprehensive wealth management, real-time alerts, custom strategies, and white-glove service"
    }
    
    tier_benefits = tier_benefits_map.get(account_holder.get("tier", "Bronze"), "standard portfolio services")
    
    # Format portfolio value
    portfolio_value = f"{account_holder.get('portfolio_value', 0):,.2f}"
    
    # Get asset allocation
    allocation = account_holder.get("asset_allocation", {})
    
    # Replace placeholders
    body = template["body"]
    body = body.replace("{{{{name}}}}", account_holder.get("name", "Valued Account Holder"))
    body = body.replace("{{{{tier}}}}", account_holder.get("tier", "Bronze"))
    body = body.replace("{{{{account_id}}}}", account_holder.get("account_id", ""))
    body = body.replace("{{{{portfolio_value}}}}", portfolio_value)
    body = body.replace("{{{{ytd_return}}}}", str(account_holder.get("ytd_return", 0)))
    body = body.replace("{{{{risk_tolerance}}}}", account_holder.get("risk_tolerance", "Moderate"))
    body = body.replace("{{{{investment_goals}}}}", account_holder.get("investment_goals", "Long-term growth"))
    body = body.replace("{{{{tier_benefits}}}}", tier_benefits)
    body = body.replace("{{{{stocks}}}}", str(allocation.get("stocks", 0)))
    body = body.replace("{{{{bonds}}}}", str(allocation.get("bonds", 0)))
    body = body.replace("{{{{real_estate}}}}", str(allocation.get("real_estate", 0)))
    body = body.replace("{{{{cash}}}}", str(allocation.get("cash", 0)))
    
    # Add custom content if provided
    if custom_content:
        body = body.replace("{{{{custom_content}}}}", f"<div style='background: #fff3cd; padding: 15px; margin: 15px 0; border-left: 4px solid #ffc107;'><p><strong>Additional Note:</strong> {custom_content}</p></div>")
    else:
        body = body.replace("{{{{custom_content}}}}", "")
    
    return {
        "subject": template["subject"],
        "body": body
    }

# Made with Bob
