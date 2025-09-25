"""
Fashion analysis agents for Zava clothing concept evaluation.

This module contains agent creation functions for various fashion analysis
tasks including market research, design evaluation, and production assessment.
"""

from typing import List, Any
import asyncio
from agent_framework import (
    ChatMessage,
    Role,
    WorkflowExecutor,
    ConcurrentBuilder,
    AgentExecutor,
    AgentExecutorResponse,
    WorkflowContext,
    executor
)


def create_fashion_research_agent(chat_clients_list: List[Any]) -> AgentExecutor:
    """
    Create an agent specialized in fashion market research and trend analysis.

    This agent analyzes clothing concepts from a market research perspective,
    focusing on fashion trends, consumer demand, and competitive positioning
    for Zava's target market.

    Args:
        chat_clients_list: List of chat clients for agent communication

    Returns:
        AgentExecutor configured for fashion market research
    """
    # Define the fashion research agent's expertise and role
    system_prompt = """You are a Senior Fashion Market Research Analyst at Zava.

    STRICT REQUIREMENTS:
    - Maximum 100 words total
    - Use bullet points
    - Be direct and specific
    - No fluff or filler text

    Provide:
    • **Trend Fit**: 1-2 sentences max
    • **Target Market**: 1 sentence
    • **Competition**: 1 sentence
    • **Demand**: 1 sentence
    • **Price**: 1 sentence

    STOP writing after 100 words."""

    # Create the market research agent using chat client
    if not chat_clients_list or len(chat_clients_list) == 0:
        raise ValueError("No chat clients available for agent creation. Please configure Foundry endpoint.")

    chat_client = chat_clients_list[0]
    research_agent = chat_client.create_agent(
        instructions=system_prompt,
        name="Fashion Market Research Agent",
        model_name="gpt-4o"  # or use a default model
    )
    # Wrap in AgentExecutor for workflow compatibility
    return AgentExecutor(research_agent, id="fashion_market_research_agent")


def create_design_evaluation_agent(chat_clients_list: List[Any]) -> AgentExecutor:
    """
    Create an agent specialized in fashion design and aesthetic evaluation.

    This agent evaluates clothing concepts from a design perspective,
    focusing on creativity, aesthetic appeal, and technical feasibility
    for Zava's brand identity.

    Args:
        chat_clients_list: List of chat clients for agent communication

    Returns:
        AgentExecutor configured for design evaluation
    """
    system_prompt = """You are a Senior Fashion Design Director at Zava.

    STRICT REQUIREMENTS:
    - Maximum 80 words total
    - Use bullet points only
    - No lengthy explanations

    Provide:
    • **Innovation**: 1 sentence max
    • **Brand Fit**: 1 sentence max
    • **Technical**: 1 sentence max
    • **Materials**: 1 sentence max
    • **Versatility**: 1 sentence max

    STOP writing after 80 words."""

    # Create the design evaluation agent using chat client
    if not chat_clients_list or len(chat_clients_list) == 0:
        raise ValueError("No chat clients available for agent creation. Please configure Foundry endpoint.")

    chat_client = chat_clients_list[1] if len(chat_clients_list) > 1 else chat_clients_list[0]
    design_agent = chat_client.create_agent(
        instructions=system_prompt,
        name="Fashion Design Evaluation Agent",
        model_name="gpt-4o"
    )
    return AgentExecutor(design_agent, id="fashion_design_evaluation_agent")


def create_production_feasibility_agent(chat_clients_list: List[Any]) -> AgentExecutor:
    """
    Create an agent specialized in production and manufacturing assessment.

    This agent evaluates clothing concepts from a production perspective,
    focusing on manufacturing feasibility, cost analysis, and supply chain
    considerations for Zava's operations.

    Args:
        chat_clients_list: List of chat clients for agent communication

    Returns:
        AgentExecutor configured for production assessment
    """
    system_prompt = """You are a Production Director at Zava.

    STRICT REQUIREMENTS:
    - Maximum 70 words total
    - Use bullet points only
    - Numbers and costs required

    Provide:
    • **Manufacturing**: Complexity level (1 sentence)
    • **Cost**: Specific $ range per unit (1 sentence)
    • **Sourcing**: Availability (1 sentence)
    • **Quality**: Main concern (1 sentence)
    • **Timeline**: Months needed (1 sentence)

    STOP writing after 70 words."""

    # Create the production feasibility agent using chat client
    if not chat_clients_list or len(chat_clients_list) == 0:
        raise ValueError("No chat clients available for agent creation. Please configure Foundry endpoint.")

    chat_client = chat_clients_list[2] if len(chat_clients_list) > 2 else chat_clients_list[0]
    production_agent = chat_client.create_agent(
        instructions=system_prompt,
        name="Production Feasibility Agent",
        model_name="gpt-4o"
    )
    return AgentExecutor(production_agent, id="production_feasibility_agent")


def create_comprehensive_analysis_agent(chat_clients_list: List[Any]) -> AgentExecutor:
    """
    Create an agent that provides comprehensive clothing concept analysis.

    This agent synthesizes insights from multiple perspectives to provide
    an overall evaluation and recommendation for Zava's decision-making.

    Args:
        chat_clients_list: List of chat clients for agent communication

    Returns:
        AgentExecutor configured for comprehensive analysis
    """
    system_prompt = """You are the Head of Product Development at Zava.

    STRICT REQUIREMENTS:
    - Maximum 100 words total
    - Start with decision word
    - Use bullet format only

    Provide:
    • **DECISION**: APPROVE/REJECT/MODIFY (1 word + reason)
    • **Strategy**: Brand fit (1 sentence)
    • **Opportunity**: Revenue potential (1 sentence)
    • **Risks**: Top 2 concerns (bullets)
    • **Actions**: Top 2 next steps (bullets)

    STOP writing after 100 words."""

    # Create the comprehensive analysis agent using chat client
    if not chat_clients_list or len(chat_clients_list) == 0:
        raise ValueError("No chat clients available for agent creation. Please configure Foundry endpoint.")

    chat_client = chat_clients_list[-1]  # Use the last client in the list
    comprehensive_agent = chat_client.create_agent(
        instructions=system_prompt,
        name="Comprehensive Fashion Analysis Agent",
        model_name="gpt-4o"
    )
    return AgentExecutor(comprehensive_agent, id="comprehensive_fashion_analysis_agent")


async def create_concurrent_fashion_analysis_workflow(chat_clients_list: List[Any]):
    """
    Create a concurrent workflow that runs multiple fashion analysis agents in parallel.

    Uses ConcurrentBuilder to create a proper concurrent subworkflow that aggregates
    results from market research, design evaluation, and production assessment agents.

    Args:
        chat_clients_list: List of chat clients for agent communication

    Returns:
        Concurrent workflow built with ConcurrentBuilder
    """
    print("Creating concurrent fashion analysis workflow...")

    # Create individual analysis agents with staggered initialization to avoid rate limits
    market_agent = create_fashion_research_agent(chat_clients_list)
    await asyncio.sleep(0.5)

    design_agent = create_design_evaluation_agent(chat_clients_list)
    await asyncio.sleep(0.5)

    production_agent = create_production_feasibility_agent(chat_clients_list)

    # Build concurrent workflow that returns aggregated analysis
    workflow = ConcurrentBuilder().participants([market_agent, design_agent, production_agent]).build()

    print("Created concurrent fashion analysis workflow with participants:")
    print("   • Fashion Market Research Agent")
    print("   • Fashion Design Evaluation Agent")
    print("   • Production Feasibility Agent")

    return workflow




def create_concept_report_writer_agent(chat_clients_list: List[Any]) -> AgentExecutor:
    """
    Create an agent specialized in writing comprehensive clothing concept reports.

    This agent synthesizes analysis results and creates detailed reports
    for presentation to Zava's leadership and design teams.

    Args:
        chat_clients_list: List of chat clients for agent communication

    Returns:
        AgentExecutor configured for report writing
    """
    system_prompt = """You are a Senior Business Analyst at Zava.

    STRICT REQUIREMENTS:
    - Maximum 150 words total
    - Start with APPROVE or REJECT
    - Use bullet format

    Provide:
    • **DECISION**: APPROVE/REJECT + why (1 sentence)
    • **Market**: Key trend (1 sentence)
    • **Design**: Innovation level (1 sentence)
    • **Production**: Cost estimate (1 sentence)
    • **Risks**: Top 2 risks (bullet points)
    • **Next Steps**: If approved, top 2 actions (bullet points)

    STOP writing after 150 words."""

    # Create the report writer agent using chat client
    if not chat_clients_list or len(chat_clients_list) == 0:
        raise ValueError("No chat clients available for agent creation. Please configure Foundry endpoint.")

    chat_client = chat_clients_list[0]
    report_agent = chat_client.create_agent(
        instructions=system_prompt,
        name="Concept Report Writer Agent",
        model_name="gpt-4o"
    )
    return AgentExecutor(report_agent, id="concept_report_writer_agent")