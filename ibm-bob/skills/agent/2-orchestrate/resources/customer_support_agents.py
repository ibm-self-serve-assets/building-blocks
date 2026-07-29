#!/usr/bin/env python3
"""
Customer Support Multi-Agent System
Supervisor-worker pattern with specialized agents
"""

from ibm_watsonx_orchestrate.agent_builder import Agent
from ibm_watsonx_orchestrate import orchestrate


def create_billing_agent():
    """Create billing specialist agent"""
    return Agent(
        name="billing_specialist",
        description="""
        Specialist in billing, payments, invoices, and account charges.
        Can process payments, generate invoices, handle refunds, and
        explain billing statements. Cannot help with technical issues
        or general product questions.
        """,
        tools=["process_payment", "generate_invoice", "issue_refund"],
        instructions="""
        Be professional and empathetic when discussing billing issues.
        Always verify customer identity before processing payments.
        Explain charges clearly and provide itemized breakdowns.
        """
    )


def create_technical_agent():
    """Create technical support specialist agent"""
    return Agent(
        name="technical_specialist",
        description="""
        Technical support specialist for product issues, bugs, and
        troubleshooting. Can diagnose problems, create support tickets,
        and provide technical solutions. Cannot handle billing or
        general inquiries.
        """,
        tools=["diagnose_issue", "create_ticket", "check_system_status"],
        instructions="""
        Gather detailed information about technical issues.
        Provide step-by-step troubleshooting guidance.
        Create tickets for issues requiring engineering team.
        """
    )


def create_general_agent():
    """Create general inquiries agent"""
    return Agent(
        name="general_specialist",
        description="""
        Handles general product questions, account information,
        and basic inquiries. Can provide product information,
        explain features, and guide users. Cannot handle billing
        or technical issues.
        """,
        tools=["get_product_info", "get_account_info"],
        instructions="""
        Be friendly and helpful.
        Provide clear, concise answers.
        Direct complex issues to appropriate specialists.
        """
    )


def create_supervisor_agent(billing_agent, technical_agent, general_agent):
    """Create supervisor agent that routes to specialists"""
    return Agent(
        name="customer_service_supervisor",
        description="""
        Customer service supervisor that routes inquiries to
        appropriate specialists based on the nature of the request.
        """,
        collaborators=[billing_agent, technical_agent, general_agent],
        instructions="""
        Analyze the customer's inquiry to determine the appropriate specialist.
        Route billing questions to billing_specialist.
        Route technical issues to technical_specialist.
        Route general questions to general_specialist.
        If unsure, ask clarifying questions before routing.
        """
    )


def deploy_customer_support_system():
    """Deploy complete customer support multi-agent system"""
    print("Creating specialist agents...")
    billing_agent = create_billing_agent()
    technical_agent = create_technical_agent()
    general_agent = create_general_agent()
    
    print("Creating supervisor agent...")
    supervisor = create_supervisor_agent(
        billing_agent,
        technical_agent,
        general_agent
    )
    
    print("Importing agents to watsonx Orchestrate...")
    orchestrate.agents.import_agent(supervisor)
    
    print("Customer support system deployed successfully!")
    print(f"Supervisor: {supervisor.name}")
    print(f"Collaborators: {len(supervisor.collaborators)}")


if __name__ == "__main__":
    deploy_customer_support_system()

# Made with Bob
