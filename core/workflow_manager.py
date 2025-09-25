"""
Zava Clothing Concept Analysis Workflow Manager.

This module orchestrates the complete workflow for analyzing clothing concept
pitches submitted to Zava, from initial parsing through final approval decisions.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, List, Callable
from dotenv import load_dotenv

from agent_framework import (
    ChatMessage,
    Executor,
    Role,
    WorkflowBuilder,
    WorkflowCompletedEvent,
    WorkflowContext,
    WorkflowExecutor,
    RequestInfoEvent,
    RequestResponse
)

# Import our modular components
from core.executors import (
    process_clothing_concept_pitch,
    log_fashion_analysis_outputs,
    adapt_concept_for_analysis,
    save_approved_concept_report,
    draft_concept_rejection_email,
    handle_approved_concept,
    handle_rejected_concept
)
from core.agents import (
    create_fashion_research_agent,
    create_design_evaluation_agent,
    create_production_feasibility_agent,
    create_concurrent_fashion_analysis_workflow,
    create_concept_report_writer_agent
)
from core.approval import (
    ZavaConceptApprovalManager,
    create_zava_human_approver,
    concept_approval_condition,
    concept_rejection_condition
)


class ZavaConceptWorkflowManager:
    """
    Manages the complete clothing concept analysis workflow for Zava.

    This class orchestrates the end-to-end process of evaluating new clothing
    concepts, from initial pitch deck parsing through final approval decisions.
    """

    def __init__(self,
                 progress_callback: Optional[Callable] = None,
                 output_callback: Optional[Callable] = None,
                 approval_callback: Optional[Callable] = None,
                 error_callback: Optional[Callable] = None):
        """
        Initialize the Zava concept workflow manager.

        Args:
            progress_callback: Called with (step_name, progress_percent, step_data)
            output_callback: Called with (source, content, output_type)
            approval_callback: Called with (question, context) for human decisions
            error_callback: Called with (error_message) for error handling
        """
        # Store UI callback functions
        self.progress_callback = progress_callback
        self.output_callback = output_callback
        self.approval_callback = approval_callback
        self.error_callback = error_callback

        # Workflow components
        self.workflow = None
        self.chat_clients = []
        self.approval_response = None
        self.approval_event = None

        # Progress tracking for UI updates
        self.completed_steps = set()
        self.workflow_steps = {
            # Maps executor IDs to (display_name, progress_percent, completed_prerequisites)
            "clothing_concept_parser": (
                "Parse Clothing Concept", 15,
                []
            ),
            "fashion_research_prep": (
                "Prepare Fashion Analysis", 30,
                ["Parse Clothing Concept"]
            ),
            "concurrent_fashion_analysis": (
                "Comprehensive Fashion Analysis", 60,
                ["Parse Clothing Concept", "Prepare Fashion Analysis"]
            ),
            "concept_input_adapter": (
                "Fashion Analysis", 65,
                ["Parse Clothing Concept", "Prepare Fashion Analysis"]
            ),
            "concurrent_fashion_analysis_logger": (
                "Generate Analysis Report", 80,
                ["Parse Clothing Concept", "Prepare Fashion Analysis", "Market Analysis", "Design Evaluation"]
            ),
            "concept_report_writer_agent": (
                "Human Review", 90,
                ["Parse Clothing Concept", "Prepare Fashion Analysis", "Market Analysis",
                 "Design Evaluation", "Generate Analysis Report"]
            )
        }

        # Load environment variables for AI service configuration
        load_dotenv()

    async def build_concept_evaluation_workflow(self) -> bool:
        """
        Build the complete clothing concept evaluation workflow.

        Returns:
            True if workflow built successfully, False otherwise
        """
        try:
            await self._update_progress("Building Zava concept workflow...", 5)

            # Initialize AI clients for the agents
            await self._update_progress("Initializing AI agents...", 10)
            await self._initialize_chat_clients()

            # Create fashion analysis agents
            await self._update_progress("Creating fashion analysis agents...", 15)
            fashion_research_agent = create_fashion_research_agent(self.chat_clients)
            concept_report_writer = create_concept_report_writer_agent(self.chat_clients)

            # Create concurrent fashion analysis workflow
            await self._update_progress("Setting up concurrent analysis...", 20)
            concurrent_fashion_workflow = create_concurrent_fashion_analysis_workflow(self.chat_clients)

            # Wrap concurrent workflow in WorkflowExecutor
            concurrent_analysis_executor = WorkflowExecutor(
                concurrent_fashion_workflow,
                id="concurrent_fashion_analysis"
            )

            # Create approval management components
            await self._update_progress("Setting up approval workflow...", 25)
            approval_manager = ZavaConceptApprovalManager(id="zava_approval_manager")
            human_approver = create_zava_human_approver()

            # Build the complete workflow graph
            await self._update_progress("Assembling workflow components...", 30)
            self.workflow = WorkflowBuilder()\
                .set_start_executor(process_clothing_concept_pitch)\
                .add_edge(process_clothing_concept_pitch, fashion_research_agent)\
                .add_edge(fashion_research_agent, adapt_concept_for_analysis)\
                .add_edge(adapt_concept_for_analysis, concurrent_analysis_executor)\
                .add_edge(concurrent_analysis_executor, log_fashion_analysis_outputs)\
                .add_edge(log_fashion_analysis_outputs, concept_report_writer)\
                .add_edge(concept_report_writer, approval_manager)\
                .add_edge(approval_manager, human_approver)\
                .add_edge(human_approver, approval_manager)\
                .add_edge(approval_manager, save_approved_concept_report, condition=concept_approval_condition)\
                .add_edge(approval_manager, draft_concept_rejection_email, condition=concept_rejection_condition)\
                .add_edge(save_approved_concept_report, handle_approved_concept)\
                .add_edge(draft_concept_rejection_email, handle_rejected_concept)\
                .build()

            await self._update_progress("Zava concept workflow ready", 35)
            await self._add_output("System", "Workflow built successfully with fashion analysis agents", "success")

            return True

        except Exception as e:
            import traceback
            error_detail = f"Failed to build Zava concept workflow: {str(e)}\n{traceback.format_exc()}"
            print(f"🚨 WORKFLOW BUILD ERROR: {error_detail}")
            await self._handle_error(error_detail)
            return False

    async def analyze_clothing_concept(self, concept_file_path: str) -> str:
        """
        Run the complete analysis workflow for a clothing concept submission.

        Args:
            concept_file_path: Path to the PowerPoint file containing the concept pitch

        Returns:
            Final workflow result ("APPROVED" or "REJECTED")
        """
        try:
            # Build workflow if not already built
            if not self.workflow:
                success = await self.build_concept_evaluation_workflow()
                if not success:
                    raise Exception("Failed to build clothing concept evaluation workflow")

            # Configure telemetry if available
            try:
                await self._configure_telemetry()
                await self._add_output("System", "Telemetry configured for workflow tracking", "info")
            except Exception as e:
                await self._add_output("System", f"Telemetry unavailable: {str(e)}", "warning")

            # Initialize workflow progress
            await self._update_progress("Parse Clothing Concept", 15, {
                "current_step": "Parse Clothing Concept",
                "completed_steps": []
            })

            # Execute the workflow with human-in-the-loop approval
            pending_requests = None
            workflow_completed = None

            while not workflow_completed:
                # Run workflow iteration
                if pending_requests:
                    stream = self.workflow.send_responses_streaming(pending_requests)
                else:
                    stream = self.workflow.run_stream(concept_file_path)

                # Process all events from this iteration
                events = [event async for event in stream]
                pending_requests = None

                # Handle each event
                human_requests = []
                for event in events:
                    # Track progress based on event information
                    await self._track_workflow_progress(event)

                    if isinstance(event, WorkflowCompletedEvent):
                        workflow_completed = event
                        await self._update_progress("Save Results", 100, {
                            "current_step": "Save Results",
                            "completed_steps": [
                                "Parse Clothing Concept",
                                "Prepare Fashion Analysis",
                                "Market Analysis",
                                "Design Evaluation",
                                "Production Assessment",
                                "Generate Analysis Report",
                                "Human Review"
                            ]
                        })
                        await self._add_output("Workflow", f"Concept analysis completed: {event.data}", "success")

                    elif isinstance(event, RequestInfoEvent):
                        # Human approval required
                        await self._update_progress("Human Review", 90, {
                            "current_step": "Human Review",
                            "completed_steps": [
                                "Parse Clothing Concept",
                                "Prepare Fashion Analysis",
                                "Market Analysis",
                                "Design Evaluation",
                                "Production Assessment",
                                "Generate Analysis Report"
                            ]
                        })
                        await self._add_output("System", "Requesting Zava team approval", "info")
                        human_requests.append((event.request_id, event.data.question, event.data.context))

                # Process human approval requests
                if human_requests and not workflow_completed:
                    for request_id, question, context in human_requests:
                        # Request approval through UI callback
                        if self.approval_callback:
                            await self.approval_callback(question, context)

                        # Wait for human decision
                        approval_response = await self._wait_for_approval_decision()

                        # Set up response for next workflow iteration
                        if pending_requests is None:
                            pending_requests = {}
                        pending_requests[request_id] = approval_response

                        await self._add_output("Human", f"Decision: {approval_response}", "decision")

            return workflow_completed.data if workflow_completed else "UNKNOWN"

        except Exception as e:
            error_msg = f"Clothing concept analysis failed: {str(e)}"
            await self._handle_error(error_msg)
            raise

        finally:
            # Clean up resources
            await self._cleanup_resources()

    async def send_approval_decision(self, decision: str, feedback: str = "") -> None:
        """
        Send human approval decision to the workflow.

        Args:
            decision: "yes" to approve, "no" to reject
            feedback: Optional additional feedback
        """
        full_response = decision
        if feedback.strip():
            full_response += f"\n{feedback.strip()}"

        self.approval_response = full_response
        if self.approval_event:
            self.approval_event.set()

    async def _initialize_chat_clients(self) -> None:
        """Initialize AI chat clients for the fashion analysis agents."""
        try:
            # This would typically initialize the actual chat clients
            # For now, we'll use placeholder logic
            from agent_framework.foundry import FoundryChatClient
            from azure.identity.aio import AzureCliCredential

            # Create Azure CLI credential for authentication
            credential = AzureCliCredential()

            # Initialize Foundry chat client (or other preferred client)
            foundry_client = FoundryChatClient(
                endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT", ""),
                credential=credential
            )

            # Add to clients list (you might want multiple clients for different agents)
            self.chat_clients = [foundry_client] * 3  # Reuse client for simplicity

            await self._add_output("System", "AI chat clients initialized successfully", "info")

        except Exception as e:
            await self._add_output("System", f"Chat client initialization warning: {str(e)}", "warning")
            # Continue with empty clients list - agents will handle gracefully

    async def _configure_telemetry(self) -> None:
        """Configure OpenTelemetry tracing for workflow monitoring."""
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

            # Set up basic telemetry
            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)

            # Add console exporter for development
            span_processor = BatchSpanProcessor(ConsoleSpanExporter())
            trace.get_tracer_provider().add_span_processor(span_processor)

        except ImportError:
            # Telemetry dependencies not available
            raise RuntimeError("OpenTelemetry not configured")

    async def _track_workflow_progress(self, event) -> None:
        """Track workflow progress based on workflow events."""
        # Extract executor ID from event
        executor_id = None

        if hasattr(event, 'metadata') and event.metadata:
            executor_id = event.metadata.get('executor_id')
        elif hasattr(event, 'executor_id'):
            executor_id = event.executor_id
        elif hasattr(event, 'source') and hasattr(event.source, 'id'):
            executor_id = event.source.id

        # Update progress if this is a tracked step
        if executor_id and executor_id in self.workflow_steps and executor_id not in self.completed_steps:
            step_name, progress, completed_list = self.workflow_steps[executor_id]
            self.completed_steps.add(executor_id)

            await self._update_progress(step_name, progress, {
                "current_step": step_name,
                "completed_steps": completed_list
            })

    async def _wait_for_approval_decision(self, timeout: int = 300) -> str:
        """Wait for human approval decision from UI."""
        self.approval_event = asyncio.Event()
        self.approval_response = None

        try:
            await asyncio.wait_for(self.approval_event.wait(), timeout=timeout)
            return self.approval_response or "no"
        except asyncio.TimeoutError:
            await self._add_output("System", "Approval timeout - defaulting to reject", "warning")
            return "no"

    async def _update_progress(self, step: str, progress: int, step_data: Dict = None) -> None:
        """Update workflow progress through UI callback."""
        if self.progress_callback:
            if asyncio.iscoroutinefunction(self.progress_callback):
                await self.progress_callback(step, progress, step_data or {})
            else:
                self.progress_callback(step, progress, step_data or {})

    async def _add_output(self, source: str, content: str, output_type: str = "text") -> None:
        """Add workflow output through UI callback."""
        if self.output_callback:
            if asyncio.iscoroutinefunction(self.output_callback):
                await self.output_callback(source, content, output_type)
            else:
                self.output_callback(source, content, output_type)

    async def _handle_error(self, error: str) -> None:
        """Handle workflow errors through UI callback."""
        if self.error_callback:
            if asyncio.iscoroutinefunction(self.error_callback):
                await self.error_callback(error)
            else:
                self.error_callback(error)

    async def _cleanup_resources(self) -> None:
        """Clean up workflow resources."""
        try:
            # Close chat clients to prevent resource leaks
            for client in self.chat_clients:
                try:
                    if hasattr(client, 'close'):
                        await client.close()
                except Exception as e:
                    await self._add_output("System", f"Client cleanup warning: {str(e)}", "warning")
        except Exception:
            pass  # Ignore cleanup errors