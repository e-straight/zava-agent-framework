"""
Workflow executors for Zava clothing concept analysis.

This module contains the core workflow executors that process clothing concept
pitches through various analysis stages.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from agent_framework import (
    WorkflowContext,
    executor,
    AgentExecutorResponse
)

from services.pitch_parser import extract_clothing_concept_data
from services.report_generator import ZavaFashionReportGenerator


@executor(id="clothing_concept_parser")
async def process_clothing_concept_pitch(file_path: str, ctx: WorkflowContext[str]) -> None:
    """
    Parse a clothing concept pitch deck and extract all design information.

    This executor processes PowerPoint presentations containing new clothing
    concepts, fashion ideas, or design proposals for Zava.

    Args:
        file_path: Path to the .pptx file containing the clothing concept pitch
        ctx: Workflow context for sending results to the next stage
    """
    print("STEP 1: Starting clothing concept pitch analysis...")

    try:
        # Extract all data from the clothing concept presentation
        concept_data_json = extract_clothing_concept_data(file_path)

        # Log successful parsing
        concept_data = json.loads(concept_data_json)
        if "error" not in concept_data:
            slides_count = concept_data.get('total_slides', 0)
            elements_count = concept_data.get('concept_summary', {}).get('total_concept_elements', 0)

            print(f"SUCCESS: Successfully parsed clothing concept with {slides_count} slides")
            print(f"INFO: Identified {elements_count} fashion-related elements")
        else:
            print(f"ERROR: Error parsing concept: {concept_data['error']}")

        # Send the extracted data to the next workflow step
        await ctx.send_message(concept_data_json)

    except Exception as e:
        error_msg = f"Failed to process clothing concept pitch: {str(e)}"
        print(f"STEP 1 ERROR: {error_msg}")

        # Send error information in a structured format
        error_data = {
            "error": error_msg,
            "error_type": "concept_parsing_error",
            "timestamp": datetime.now().isoformat()
        }
        await ctx.send_message(json.dumps(error_data))


@executor(id="concurrent_fashion_analysis_logger")
async def log_fashion_analysis_outputs(responses: list[AgentExecutorResponse], ctx: WorkflowContext[str]) -> None:
    """
    Process and log outputs from concurrent fashion analysis agents.

    This executor receives results from multiple fashion analysis agents
    (market research, design evaluation, production assessment) and
    consolidates them for report generation.

    Args:
        responses: List of responses from concurrent fashion analysis agents
        ctx: Workflow context for sending consolidated results
    """
    print("STEP 4: Processing fashion analysis results...")

    try:
        consolidated_analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_type": "comprehensive_fashion_evaluation",
            "components": {}
        }

        # Process each analysis component
        for i, response in enumerate(responses):
            component_name = f"fashion_analysis_component_{i + 1}"

            if hasattr(response, 'output') and response.output:
                # Extract key insights from each analysis component
                analysis_content = str(response.output).strip()

                # Categorize the analysis based on content keywords
                if any(keyword in analysis_content.lower() for keyword in
                      ["market", "trend", "consumer", "demand", "demographic"]):
                    component_name = "market_trend_analysis"
                elif any(keyword in analysis_content.lower() for keyword in
                        ["design", "aesthetic", "style", "color", "fabric", "material"]):
                    component_name = "design_evaluation"
                elif any(keyword in analysis_content.lower() for keyword in
                        ["production", "manufacturing", "cost", "supply", "logistics"]):
                    component_name = "production_feasibility"
                elif any(keyword in analysis_content.lower() for keyword in
                        ["sustainability", "ethical", "environmental", "eco"]):
                    component_name = "sustainability_assessment"

                consolidated_analysis["components"][component_name] = {
                    "content": analysis_content,
                    "length": len(analysis_content),
                    "agent_id": getattr(response, 'agent_id', f"agent_{i + 1}")
                }

                print(f"PROCESSED: {component_name}: {len(analysis_content)} characters")

        # Log summary of analysis components
        total_components = len(consolidated_analysis["components"])
        print(f"CONSOLIDATED: {total_components} fashion analysis components")

        for component_name, component_data in consolidated_analysis["components"].items():
            print(f"  - {component_name}: {component_data['length']} chars")

        # Send consolidated analysis to the report generation stage
        await ctx.send_message(json.dumps(consolidated_analysis, indent=2))

    except Exception as e:
        error_msg = f"Failed to process fashion analysis outputs: {str(e)}"
        print(f"STEP 4 ERROR: {error_msg}")

        # Send error information
        error_data = {
            "error": error_msg,
            "error_type": "analysis_consolidation_error",
            "timestamp": datetime.now().isoformat()
        }
        await ctx.send_message(json.dumps(error_data))


@executor(id="concept_input_adapter")
async def adapt_concept_for_analysis(concept_data_json: str, ctx: WorkflowContext[str]) -> None:
    """
    Adapt clothing concept data for concurrent fashion analysis agents.

    This executor takes the parsed concept data and formats it appropriately
    for the concurrent analysis workflow that evaluates market potential,
    design quality, and production feasibility.

    Args:
        concept_data_json: JSON string containing extracted concept data
        ctx: Workflow context for sending adapted data
    """
    print("STEP 3: Adapting concept data for fashion analysis...")

    try:
        concept_data = json.loads(concept_data_json)

        if "error" in concept_data:
            print(f"WARNING: Received error from previous step: {concept_data['error']}")
            # Pass through error data
            await ctx.send_message(concept_data_json)
            return

        # Create analysis-focused summary
        adapted_data = {
            "concept_summary": {
                "file_name": concept_data.get('concept_file_name', 'Unknown Concept'),
                "total_slides": concept_data.get('total_slides', 0),
                "concept_elements": concept_data.get('concept_summary', {}).get('total_concept_elements', 0),
                "analysis_timestamp": datetime.now().isoformat()
            },
            "design_content": [],
            "market_signals": [],
            "production_notes": []
        }

        # Extract and categorize content from slides
        if 'slides' in concept_data:
            for slide in concept_data['slides']:
                slide_text = " ".join(slide.get('text_content', []))
                concept_elements = slide.get('concept_elements', [])

                # Add all content for comprehensive analysis
                if slide_text.strip():
                    adapted_data["design_content"].append({
                        "slide_number": slide['slide_number'],
                        "content": slide_text,
                        "concept_elements": concept_elements
                    })

                # Identify market-related signals
                market_keywords = ["target", "audience", "market", "customer", "demographic",
                                 "price", "competitor", "trend", "season"]
                if any(keyword in slide_text.lower() for keyword in market_keywords):
                    adapted_data["market_signals"].append(slide_text)

                # Identify production-related information
                production_keywords = ["fabric", "material", "manufacturing", "cost", "supplier",
                                     "production", "quality", "sizes", "fit"]
                if any(keyword in slide_text.lower() for keyword in production_keywords):
                    adapted_data["production_notes"].append(slide_text)

        # Create comprehensive analysis prompt
        analysis_prompt = f"""
        ZAVA CLOTHING CONCEPT ANALYSIS REQUEST

        Concept File: {adapted_data['concept_summary']['file_name']}
        Total Slides: {adapted_data['concept_summary']['total_slides']}
        Fashion Elements: {adapted_data['concept_summary']['concept_elements']}

        Please analyze this clothing concept submission from the perspective of Zava,
        a fashion-forward clothing company evaluating new design concepts.

        CONCEPT CONTENT:
        {json.dumps(adapted_data['design_content'], indent=2)}

        Please provide comprehensive analysis covering:
        1. Market potential and fashion trend alignment
        2. Design innovation and aesthetic appeal
        3. Production feasibility and cost considerations
        4. Brand fit with Zava's positioning
        5. Competitive differentiation opportunities

        Focus on actionable insights that will help determine whether to approve
        this concept for development.
        """

        print(f"SUCCESS: Adapted concept data for analysis:")
        print(f"  - {len(adapted_data['design_content'])} slides with content")
        print(f"  - {len(adapted_data['market_signals'])} market signals identified")
        print(f"  - {len(adapted_data['production_notes'])} production notes found")

        # Send the analysis prompt to the concurrent analysis workflow
        await ctx.send_message(analysis_prompt)

    except Exception as e:
        error_msg = f"Failed to adapt concept data: {str(e)}"
        print(f"STEP 3 ERROR: {error_msg}")

        # Send error information
        error_data = {
            "error": error_msg,
            "error_type": "concept_adaptation_error",
            "timestamp": datetime.now().isoformat()
        }
        await ctx.send_message(json.dumps(error_data))


@executor(id="save_approved_concept_report")
async def save_approved_concept_report(approval_data: Any, ctx: WorkflowContext[str]) -> None:
    """
    Generate and save a comprehensive report for an approved clothing concept.

    Args:
        approval_data: Data from the approval process including analysis results
        ctx: Workflow context for sending final results
    """
    print("STEP 6A: Generating approved concept development report...")

    try:
        # Initialize the report generator
        report_generator = ZavaFashionReportGenerator()

        # Extract analysis components (these would come from the workflow context)
        # For now, we'll create placeholder content
        concept_data = {
            "concept_file_name": "Approved_Clothing_Concept.pptx",
            "total_slides": 8,
            "concept_summary": {"total_concept_elements": 12}
        }

        market_analysis = "Strong market potential identified with growing demand in target demographic."
        design_analysis = "Innovative design approach with excellent aesthetic appeal and brand alignment."
        production_analysis = "Feasible production requirements with reasonable cost projections."
        approval_feedback = str(approval_data) if approval_data else ""

        # Generate the comprehensive approval report
        report_content = report_generator.generate_approved_concept_report(
            concept_data=concept_data,
            market_analysis=market_analysis,
            design_analysis=design_analysis,
            production_analysis=production_analysis,
            approval_feedback=approval_feedback
        )

        # Save the report to file
        filename = report_generator.save_report_to_file(
            report_content=report_content,
            filename_prefix="zava_approved_concept",
            report_type="Concept Approval"
        )

        print(f"SUCCESS: Approved concept report generated: {filename}")

        # Send confirmation message
        await ctx.send_message("APPROVED")

    except Exception as e:
        error_msg = f"Failed to generate approved concept report: {str(e)}"
        print(f"STEP 6A ERROR: {error_msg}")
        await ctx.send_message(f"ERROR: {error_msg}")


@executor(id="draft_concept_rejection_email")
async def draft_concept_rejection_email(rejection_data: Any, ctx: WorkflowContext[str]) -> None:
    """
    Generate a professional rejection email for a clothing concept submission.

    Args:
        rejection_data: Data from the rejection decision including reasons
        ctx: Workflow context for sending final results
    """
    print("STEP 6B: Generating concept rejection notification...")

    try:
        # Initialize the report generator
        report_generator = ZavaFashionReportGenerator()

        # Extract rejection information
        concept_data = {
            "concept_file_name": "Submitted_Clothing_Concept.pptx",
            "total_slides": 6,
            "concept_summary": {"total_concept_elements": 8}
        }

        rejection_reasons = (
            "After careful evaluation, this concept does not align with our current "
            "strategic direction and seasonal planning requirements."
        )

        constructive_feedback = (
            "The design shows creativity, but we recommend focusing on more "
            "sustainable materials and clearer target market definition."
        )

        alternative_suggestions = (
            "Consider exploring eco-friendly fabric options and developing "
            "concepts that appeal to our core demographic of 25-40 year old professionals."
        )

        # Generate the rejection email
        email_content = report_generator.generate_rejected_concept_email(
            concept_data=concept_data,
            rejection_reasons=rejection_reasons,
            constructive_feedback=constructive_feedback,
            alternative_suggestions=alternative_suggestions
        )

        # Save the email to file
        filename = report_generator.save_report_to_file(
            report_content=email_content,
            filename_prefix="zava_concept_rejection",
            report_type="Concept Rejection"
        )

        print(f"SUCCESS: Rejection email generated: {filename}")

        # Send confirmation message
        await ctx.send_message("REJECTED")

    except Exception as e:
        error_msg = f"Failed to generate rejection email: {str(e)}"
        print(f"STEP 6B ERROR: {error_msg}")
        await ctx.send_message(f"ERROR: {error_msg}")


@executor(id="approved_concept_handler")
async def handle_approved_concept(result: str, ctx: WorkflowContext[str]) -> None:
    """Handle the final processing of an approved clothing concept."""
    print(f"SUCCESS: Clothing concept APPROVED for development: {result}")
    await ctx.send_message("APPROVED")


@executor(id="rejected_concept_handler")
async def handle_rejected_concept(result: str, ctx: WorkflowContext[str]) -> None:
    """Handle the final processing of a rejected clothing concept."""
    print(f"REJECTED: Clothing concept REJECTED: {result}")
    await ctx.send_message("REJECTED")