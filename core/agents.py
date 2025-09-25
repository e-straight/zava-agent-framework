"""
Fashion analysis agents for Zava clothing concept evaluation.

This module contains agent creation functions for various fashion analysis
tasks including market research, design evaluation, and production assessment.
"""

from typing import List, Any
from agent_framework import (
    ChatMessage,
    Role,
    WorkflowExecutor,
    ConcurrentBuilder,
    AgentExecutor
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
    system_prompt = """You are a Senior Fashion Market Research Analyst at Zava, a trendy clothing company.

    Your expertise includes:
    - Fashion trend analysis and forecasting
    - Consumer behavior in apparel markets
    - Competitive landscape assessment
    - Target demographic analysis
    - Seasonal planning and market timing
    - Price positioning and value analysis

    When analyzing clothing concept pitches, focus on:

    1. **Market Trends**: How well does this concept align with current and emerging fashion trends?
    2. **Target Audience**: Is there clear definition and appeal to specific customer segments?
    3. **Competitive Position**: How does this differentiate from existing market offerings?
    4. **Demand Indicators**: What signals suggest market demand for this type of clothing?
    5. **Market Timing**: Is this concept properly positioned for upcoming seasons?
    6. **Price Potential**: What price points could this concept support in the market?

    Always provide:
    - Specific trend references and market data when available
    - Clear assessment of market opportunity size
    - Identification of potential risks and challenges
    - Recommendations for market positioning and timing

    Keep your analysis focused on actionable insights that will help Zava make informed
    decisions about pursuing clothing concept development."""

    # Create the market research agent
    research_agent = AgentExecutor.create(
        model=chat_clients_list[0] if chat_clients_list else None,
        instructions=system_prompt,
        id="fashion_market_research_agent"
    )

    return research_agent


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
    system_prompt = """You are a Senior Fashion Design Director at Zava, a contemporary clothing company.

    Your expertise includes:
    - Fashion design principles and aesthetics
    - Material selection and fabric properties
    - Color theory and seasonal palettes
    - Silhouette and fit analysis
    - Brand identity and design consistency
    - Technical design feasibility

    When evaluating clothing concept pitches, assess:

    1. **Design Innovation**: How creative and unique is this concept?
    2. **Aesthetic Appeal**: Does this align with contemporary fashion sensibilities?
    3. **Brand Fit**: How well does this concept match Zava's design DNA?
    4. **Technical Feasibility**: Can this design be executed with quality construction?
    5. **Material Considerations**: Are the proposed fabrics and materials appropriate?
    6. **Versatility**: Does this concept offer styling flexibility for customers?

    Provide detailed feedback on:
    - Design strengths and areas for improvement
    - Technical considerations for pattern-making and construction
    - Suggestions for material and color alternatives
    - Assessment of how this fits within a collection context
    - Recommendations for design refinements

    Your analysis should help determine whether this concept has the design merit
    and technical viability to succeed as a Zava product."""

    design_agent = AgentExecutor.create(
        model=chat_clients_list[1] if len(chat_clients_list) > 1 else chat_clients_list[0],
        instructions=system_prompt,
        id="fashion_design_evaluation_agent"
    )

    return design_agent


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
    system_prompt = """You are a Production Director at Zava, a growing clothing company.

    Your expertise includes:
    - Garment manufacturing processes and requirements
    - Cost analysis and pricing strategies
    - Supply chain management and sourcing
    - Quality control and production standards
    - Scalability and volume production planning
    - Sustainability and ethical manufacturing practices

    When analyzing clothing concept pitches, evaluate:

    1. **Manufacturing Complexity**: How difficult would this be to produce consistently?
    2. **Cost Structure**: What are the likely production costs and pricing implications?
    3. **Material Sourcing**: Are required materials readily available and cost-effective?
    4. **Quality Standards**: Can this concept meet Zava's quality requirements?
    5. **Production Volume**: Is this suitable for our typical production runs?
    6. **Timeline Feasibility**: What would be realistic development and production timelines?

    Your analysis should cover:
    - Detailed cost breakdown estimates (materials, labor, overhead)
    - Identification of potential production challenges
    - Supplier and sourcing considerations
    - Quality control requirements and testing needs
    - Recommendations for production optimization
    - Assessment of scalability for different volume levels

    Focus on providing practical insights that help determine production viability
    and identify any red flags that could impact successful manufacturing."""

    production_agent = AgentExecutor.create(
        model=chat_clients_list[2] if len(chat_clients_list) > 2 else chat_clients_list[0],
        instructions=system_prompt,
        id="production_feasibility_agent"
    )

    return production_agent


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
    system_prompt = """You are the Head of Product Development at Zava, a contemporary clothing company.

    You are responsible for making final recommendations on clothing concept submissions
    based on comprehensive analysis across market, design, and production considerations.

    Your role includes:
    - Synthesizing multiple analysis perspectives
    - Identifying strategic alignment with Zava's goals
    - Making go/no-go recommendations
    - Providing clear rationale for decisions
    - Suggesting development priorities and next steps

    When reviewing clothing concept analysis, consider:

    1. **Strategic Fit**: How well does this align with Zava's brand positioning and goals?
    2. **Market Opportunity**: What is the potential market impact and revenue opportunity?
    3. **Risk Assessment**: What are the key risks and how can they be mitigated?
    4. **Resource Requirements**: What investment of time, money, and resources is needed?
    5. **Competitive Advantage**: How will this help differentiate Zava in the market?
    6. **Portfolio Balance**: How does this fit with our existing and planned product lines?

    Provide structured recommendations that include:
    - Clear recommendation (Approve/Reject/Request modifications)
    - Key supporting rationale
    - Identified opportunities and risks
    - Suggested next steps if approved
    - Alternative approaches if rejected

    Your analysis should provide the executive summary needed for final decision-making."""

    comprehensive_agent = AgentExecutor.create(
        model=chat_clients_list[-1] if chat_clients_list else None,
        instructions=system_prompt,
        id="comprehensive_fashion_analysis_agent"
    )

    return comprehensive_agent


def create_concurrent_fashion_analysis_workflow(chat_clients_list: List[Any]) -> WorkflowExecutor:
    """
    Create a concurrent workflow that runs multiple fashion analysis agents in parallel.

    This workflow orchestrates market research, design evaluation, and production
    assessment agents to provide comprehensive analysis of clothing concepts.

    Args:
        chat_clients_list: List of chat clients for agent communication

    Returns:
        WorkflowExecutor configured for concurrent fashion analysis
    """
    # Create individual analysis agents
    market_agent = create_fashion_research_agent(chat_clients_list)
    design_agent = create_design_evaluation_agent(chat_clients_list)
    production_agent = create_production_feasibility_agent(chat_clients_list)

    # Build concurrent workflow with all three agents
    concurrent_workflow = ConcurrentBuilder()\
        .add_executor(market_agent)\
        .add_executor(design_agent)\
        .add_executor(production_agent)\
        .build()

    print("🔄 Created concurrent fashion analysis workflow with:")
    print("   • Fashion Market Research Agent")
    print("   • Design Evaluation Agent")
    print("   • Production Feasibility Agent")

    return concurrent_workflow


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
    system_prompt = """You are a Senior Business Analyst at Zava specializing in clothing concept evaluation reports.

    Your responsibility is to synthesize complex fashion analysis into clear,
    actionable reports for leadership decision-making.

    When writing clothing concept evaluation reports, include:

    1. **Executive Summary**: Clear recommendation and key findings
    2. **Concept Overview**: Summary of the proposed clothing concept
    3. **Market Analysis**: Fashion trends, consumer demand, competitive position
    4. **Design Assessment**: Creative merit, brand fit, technical feasibility
    5. **Production Evaluation**: Manufacturing requirements, costs, timeline
    6. **Risk Analysis**: Potential challenges and mitigation strategies
    7. **Financial Projections**: Cost structure and revenue potential
    8. **Recommendations**: Clear next steps and decision points

    Your reports should be:
    - Professional and well-structured
    - Data-driven with specific examples
    - Actionable with clear recommendations
    - Comprehensive yet concise
    - Suitable for executive presentation

    Focus on providing the information leadership needs to make confident
    decisions about clothing concept development investments."""

    report_agent = AgentExecutor.create(
        model=chat_clients_list[0] if chat_clients_list else None,
        instructions=system_prompt,
        id="concept_report_writer_agent"
    )

    return report_agent