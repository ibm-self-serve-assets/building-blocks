"""
Account Holder Management Tools for Portfolio Advisor Agent

This module provides tools for retrieving and managing account holder data
in the financial portfolio management domain.

⚠️ IMPORTANT: Data is embedded directly in the tools since WXO tools
cannot access local CSV files when deployed.
"""
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import Dict, List, Optional, Any


# Embedded account holder data - WXO tools cannot access local files
ACCOUNT_HOLDER_DATA = [
    {
        "account_id": "ACC001",
        "name": "Sarah Johnson",
        "email": "sarah.johnson@email.com",
        "phone": "555-0101",
        "tier": "Diamond",
        "status": "active",
        "portfolio_value": 2500000.00,
        "asset_allocation": {
            "stocks": 60,
            "bonds": 25,
            "real_estate": 10,
            "cash": 5
        },
        "investment_goals": "Long-term growth and wealth preservation",
        "risk_tolerance": "Moderate",
        "ytd_return": 12.5,
        "account_opened": "2020-03-15"
    },
    {
        "account_id": "ACC002",
        "name": "Michael Chen",
        "email": "michael.chen@email.com",
        "phone": "555-0102",
        "tier": "Gold",
        "status": "active",
        "portfolio_value": 850000.00,
        "asset_allocation": {
            "stocks": 70,
            "bonds": 20,
            "real_estate": 5,
            "cash": 5
        },
        "investment_goals": "Aggressive growth for retirement",
        "risk_tolerance": "High",
        "ytd_return": 15.2,
        "account_opened": "2019-07-22"
    },
    {
        "account_id": "ACC003",
        "name": "Emily Rodriguez",
        "email": "emily.rodriguez@email.com",
        "phone": "555-0103",
        "tier": "Silver",
        "status": "active",
        "portfolio_value": 325000.00,
        "asset_allocation": {
            "stocks": 55,
            "bonds": 35,
            "real_estate": 5,
            "cash": 5
        },
        "investment_goals": "Balanced growth and income",
        "risk_tolerance": "Moderate",
        "ytd_return": 9.8,
        "account_opened": "2021-01-10"
    },
    {
        "account_id": "ACC004",
        "name": "David Thompson",
        "email": "david.thompson@email.com",
        "phone": "555-0104",
        "tier": "Bronze",
        "status": "active",
        "portfolio_value": 75000.00,
        "asset_allocation": {
            "stocks": 50,
            "bonds": 40,
            "real_estate": 0,
            "cash": 10
        },
        "investment_goals": "Building wealth for first home",
        "risk_tolerance": "Low",
        "ytd_return": 7.5,
        "account_opened": "2022-05-18"
    },
    {
        "account_id": "ACC005",
        "name": "Jennifer Martinez",
        "email": "jennifer.martinez@email.com",
        "phone": "555-0105",
        "tier": "Gold",
        "status": "active",
        "portfolio_value": 1200000.00,
        "asset_allocation": {
            "stocks": 65,
            "bonds": 25,
            "real_estate": 8,
            "cash": 2
        },
        "investment_goals": "Retirement planning and legacy building",
        "risk_tolerance": "Moderate-High",
        "ytd_return": 11.3,
        "account_opened": "2018-11-05"
    },
    {
        "account_id": "ACC006",
        "name": "Robert Kim",
        "email": "robert.kim@email.com",
        "phone": "555-0106",
        "tier": "Silver",
        "status": "active",
        "portfolio_value": 280000.00,
        "asset_allocation": {
            "stocks": 60,
            "bonds": 30,
            "real_estate": 5,
            "cash": 5
        },
        "investment_goals": "College savings and retirement",
        "risk_tolerance": "Moderate",
        "ytd_return": 10.1,
        "account_opened": "2020-09-12"
    },
    {
        "account_id": "ACC007",
        "name": "Lisa Anderson",
        "email": "lisa.anderson@email.com",
        "phone": "555-0107",
        "tier": "Diamond",
        "status": "active",
        "portfolio_value": 3800000.00,
        "asset_allocation": {
            "stocks": 55,
            "bonds": 30,
            "real_estate": 12,
            "cash": 3
        },
        "investment_goals": "Wealth preservation and philanthropic planning",
        "risk_tolerance": "Conservative",
        "ytd_return": 8.9,
        "account_opened": "2017-02-28"
    },
    {
        "account_id": "ACC008",
        "name": "James Wilson",
        "email": "james.wilson@email.com",
        "phone": "555-0108",
        "tier": "Bronze",
        "status": "active",
        "portfolio_value": 45000.00,
        "asset_allocation": {
            "stocks": 45,
            "bonds": 45,
            "real_estate": 0,
            "cash": 10
        },
        "investment_goals": "Emergency fund and long-term savings",
        "risk_tolerance": "Low",
        "ytd_return": 6.2,
        "account_opened": "2023-03-20"
    }
]


@tool
def get_account_holder_data(
    account_id: Optional[str] = None,
    tier: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve account holder data with flexible filtering options.
    
    Args:
        account_id: Filter by specific account ID
        tier: Filter by tier level (Bronze, Silver, Gold, Diamond)
        status: Filter by account status (e.g., 'active', 'inactive')
        limit: Maximum number of results to return
    
    Returns:
        List of account holders matching the filter criteria
    
    Example:
        >>> get_account_holder_data(tier="Gold", limit=5)
        [{"account_id": "ACC002", "name": "Michael Chen", ...}, ...]
    """
    results = ACCOUNT_HOLDER_DATA.copy()
    
    # Apply filters
    if account_id:
        results = [a for a in results if a.get("account_id") == account_id]
    if tier:
        results = [a for a in results if a.get("tier") == tier]
    if status:
        results = [a for a in results if a.get("status") == status]
    
    # Apply limit
    if limit and limit > 0:
        results = results[:limit]
    
    return results


@tool
def get_account_holder_by_id(account_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single account holder by their unique account identifier.
    
    Args:
        account_id: The unique identifier for the account holder
    
    Returns:
        Account holder data if found, error message otherwise
    
    Example:
        >>> get_account_holder_by_id("ACC001")
        {"account_id": "ACC001", "name": "Sarah Johnson", ...}
    """
    for account in ACCOUNT_HOLDER_DATA:
        if account.get("account_id") == account_id:
            return account
    return {"error": f"Account holder {account_id} not found"}


@tool
def get_account_holders_by_tier(tier: str) -> List[Dict[str, Any]]:
    """
    Retrieve all account holders in a specific tier level.
    
    Args:
        tier: The tier name (Bronze, Silver, Gold, Diamond)
    
    Returns:
        List of account holders in the specified tier
    
    Example:
        >>> get_account_holders_by_tier("Gold")
        [{"account_id": "ACC002", "tier": "Gold", ...}, ...]
    """
    return [a for a in ACCOUNT_HOLDER_DATA if a.get("tier") == tier]


@tool
def calculate_portfolio_metrics(
    tier: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate aggregated portfolio metrics for account holders.
    
    Args:
        tier: Optional tier to filter by
    
    Returns:
        Dictionary containing calculated portfolio metrics
    
    Example:
        >>> calculate_portfolio_metrics(tier="Gold")
        {"total_accounts": 2, "total_aum": 2050000.00, ...}
    """
    accounts = ACCOUNT_HOLDER_DATA if not tier else get_account_holders_by_tier(tier)
    
    if not accounts:
        return {"error": "No accounts found for the specified criteria"}
    
    total_aum = sum(a.get("portfolio_value", 0) for a in accounts)
    avg_portfolio_value = total_aum / len(accounts) if accounts else 0
    avg_ytd_return = sum(a.get("ytd_return", 0) for a in accounts) / len(accounts) if accounts else 0
    
    # Calculate asset allocation averages
    asset_types = ["stocks", "bonds", "real_estate", "cash"]
    avg_allocation = {}
    for asset in asset_types:
        total = sum(a.get("asset_allocation", {}).get(asset, 0) for a in accounts)
        avg_allocation[asset] = round(total / len(accounts), 1) if accounts else 0
    
    return {
        "total_accounts": len(accounts),
        "total_aum": round(total_aum, 2),
        "average_portfolio_value": round(avg_portfolio_value, 2),
        "average_ytd_return": round(avg_ytd_return, 2),
        "average_asset_allocation": avg_allocation,
        "tier_distribution": {
            t: len([a for a in accounts if a.get("tier") == t])
            for t in set(a.get("tier") for a in accounts)
        },
        "risk_tolerance_distribution": {
            rt: len([a for a in accounts if a.get("risk_tolerance") == rt])
            for rt in set(a.get("risk_tolerance") for a in accounts)
        }
    }

# Made with Bob
