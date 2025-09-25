"""
Zava Clothing Concept Analysis Workflow Manager.

This module orchestrates the complete workflow for analyzing clothing concept
pitches submitted to Zava, from initial parsing through final approval decisions.
"""

import asyncio
import json
import os
import re
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
    convert_report_to_approval_request,
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

        # Force fresh workflow builds to avoid caching issues
        self._force_rebuild = True

        # Progress tracking for UI updates
        self.completed_steps = set()
        self.workflow_steps = {
            # Maps executor IDs to (display_name, progress_percent, completed_prerequisites)
            "clothing_concept_parser": (
                "Parse Clothing Concept", 15,
                []
            ),
            "concept_input_adapter": (
                "Prepare Fashion Analysis", 25,
                ["Parse Clothing Concept"]
            ),
            "concurrent_fashion_analysis": (
                "Concurrent Fashion Analysis", 50,
                ["Parse Clothing Concept", "Prepare Fashion Analysis"]
            ),
            "concurrent_fashion_analysis_logger": (
                "Generate Analysis Report", 60,
                ["Parse Clothing Concept", "Prepare Fashion Analysis", "Concurrent Fashion Analysis"]
            ),
            "concept_report_writer_agent": (
                "Create Executive Report", 80,
                ["Parse Clothing Concept", "Prepare Fashion Analysis", "Concurrent Fashion Analysis", "Generate Analysis Report"]
            ),
            "convert_report_to_approval_request": (
                "Prepare Approval Request", 85,
                ["Parse Clothing Concept", "Prepare Fashion Analysis", "Concurrent Fashion Analysis", "Generate Analysis Report", "Create Executive Report"]
            ),
            "zava_human_approver": (
                "Human Review", 90,
                ["Parse Clothing Concept", "Prepare Fashion Analysis", "Concurrent Fashion Analysis", "Generate Analysis Report", "Create Executive Report", "Prepare Approval Request"]
            )
        }

        # Load environment variables for AI service configuration
        load_dotenv()

    async def _execute_workflow_with_retry(self, workflow_stream, max_retries: int = 3) -> List[Any]:
        """Execute workflow with retry logic for rate limiting."""
        for attempt in range(max_retries):
            try:
                events = [event async for event in workflow_stream]
                return events

            except Exception as e:
                # Check if this is a rate limit error
                error_str = str(e)
                if "rate limit" in error_str.lower():
                    # Extract wait time from error message
                    wait_match = re.search(r'try again in (\d+) seconds', error_str.lower())
                    wait_seconds = int(wait_match.group(1)) if wait_match else 30

                    if attempt < max_retries - 1:  # Not the last attempt
                        await self._add_output("System", f"Rate limit hit. Waiting {wait_seconds} seconds before retry {attempt + 1}/{max_retries}...", "warning")
                        await asyncio.sleep(wait_seconds + 2)  # Add 2 second buffer

                        # Create fresh workflow stream for retry
                        if hasattr(self, '_last_stream_params'):
                            if self._last_stream_params.get('pending_requests'):
                                workflow_stream = self.workflow.send_responses_streaming(self._last_stream_params['pending_requests'])
                            else:
                                workflow_stream = self.workflow.run_stream(self._last_stream_params['concept_file_path'])
                        continue
                    else:
                        await self._add_output("System", f"Rate limit exceeded after {max_retries} attempts", "error")
                        raise
                else:
                    # Non-rate-limit error, re-raise immediately
                    raise

        return []

    async def build_concept_evaluation_workflow(self) -> bool:
        """
        Build the complete clothing concept evaluation workflow.

        Returns:
            True if workflow built successfully, False otherwise
        """
        try:
            await self._update_progress("Building Zava concept workflow...", 5)

            # Clean up any existing resources first
            await self._cleanup_resources()

            # Initialize AI clients for the agents
            await self._update_progress("Initializing AI agents...", 10)
            await self._initialize_chat_clients()

            # Create fashion analysis agents
            await self._update_progress("Creating fashion analysis agents...", 15)
            concept_report_writer = create_concept_report_writer_agent(self.chat_clients)

            # Create concurrent fashion analysis workflow
            await self._update_progress("Creating concurrent fashion analysis workflow...", 20)
            concurrent_analysis_workflow = await create_concurrent_fashion_analysis_workflow(self.chat_clients)

            # Wrap concurrent workflow in WorkflowExecutor (REQUIRED pattern)
            await self._update_progress("Setting up concurrent subworkflow executor...", 22)
            print("Creating WorkflowExecutor for concurrent fashion analysis...")
            concurrent_analysis_subworkflow = WorkflowExecutor(concurrent_analysis_workflow, id="concurrent_fashion_analysis")

            # Create approval management components
            await self._update_progress("Setting up approval workflow...", 25)
            human_approver = create_zava_human_approver()
            approval_manager = ZavaConceptApprovalManager()

            # Build the complete workflow graph
            await self._update_progress("Assembling workflow components...", 30)
            self.workflow = WorkflowBuilder()\
                .set_start_executor(process_clothing_concept_pitch)\
                .add_edge(process_clothing_concept_pitch, adapt_concept_for_analysis)\
                .add_edge(adapt_concept_for_analysis, concurrent_analysis_subworkflow)\
                .add_edge(concurrent_analysis_subworkflow, log_fashion_analysis_outputs)\
                .add_edge(log_fashion_analysis_outputs, concept_report_writer)\
                .add_edge(concept_report_writer, convert_report_to_approval_request)\
                .add_edge(convert_report_to_approval_request, approval_manager)\
                .add_edge(approval_manager, human_approver)\
                .add_edge(human_approver, approval_manager)\
                .add_edge(approval_manager, save_approved_concept_report, condition=concept_approval_condition)\
                .add_edge(approval_manager, draft_concept_rejection_email, condition=concept_rejection_condition)\
                .add_edge(save_approved_concept_report, handle_approved_concept)\
                .add_edge(draft_concept_rejection_email, handle_rejected_concept)\
                .build()

            await self._update_progress("Zava concept workflow ready", 35)
            await self._add_output("System", "Workflow built successfully with fashion analysis agents", "success")

            # Generate workflow visualization
            await self._generate_workflow_visualization()

            return True

        except Exception as e:
            import traceback
            error_detail = f"Failed to build Zava concept workflow: {str(e)}\n{traceback.format_exc()}"
            print(f"WORKFLOW BUILD ERROR: {error_detail}")
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
            # Always rebuild workflow to ensure fresh agents with updated instructions
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

            # Initialize shared state for RequestInfoExecutor
            print("=" * 80)
            print("WORKFLOW: INITIALIZING SHARED STATE FOR HUMAN APPROVAL")
            print("=" * 80)

            try:
                if self.workflow:
                    print(f"WORKFLOW: Workflow object available: {type(self.workflow)}")

                    # Try to access and initialize the workflow's shared state using proper SharedState API
                    if hasattr(self.workflow, '_shared_state') and self.workflow._shared_state is not None:
                        print(f"WORKFLOW: Found _shared_state: {type(self.workflow._shared_state)}")
                        await self.workflow._shared_state.set('_af_pending_request_info', {})
                        await self._add_output("System", "Initialized workflow shared state for human approval", "info")
                        print("WORKFLOW: Successfully initialized _shared_state")
                    elif hasattr(self.workflow, 'shared_state') and self.workflow.shared_state is not None:
                        print(f"WORKFLOW: Found shared_state: {type(self.workflow.shared_state)}")
                        await self.workflow.shared_state.set('_af_pending_request_info', {})
                        await self._add_output("System", "Initialized workflow shared state (alt) for human approval", "info")
                        print("WORKFLOW: Successfully initialized shared_state")
                    else:
                        print("WORKFLOW: No shared state found on workflow object")
                        await self._add_output("System", "Workflow shared state not accessible - approval may have issues", "warning")
                else:
                    print("WORKFLOW: No workflow object available")
            except Exception as e:
                print(f"WORKFLOW: Shared state initialization failed: {str(e)}")
                await self._add_output("System", f"Warning: Could not initialize shared state for approval: {str(e)}", "warning")

            print("=" * 80)

            # Execute the workflow with human-in-the-loop approval
            pending_requests = None
            workflow_completed = None

            while not workflow_completed:
                # Run workflow iteration
                if pending_requests:
                    stream = self.workflow.send_responses_streaming(pending_requests)
                    self._last_stream_params = {'pending_requests': pending_requests}
                else:
                    stream = self.workflow.run_stream(concept_file_path)
                    self._last_stream_params = {'concept_file_path': concept_file_path}

                # Process all events from this iteration with retry logic
                events = await self._execute_workflow_with_retry(stream)
                pending_requests = None

                # Handle each event
                human_requests = []
                print(f"WORKFLOW: Processing {len(events)} events from workflow iteration")

                for i, event in enumerate(events):
                    print("=" * 60)
                    print(f"WORKFLOW: Processing event {i+1}/{len(events)}")
                    print(f"WORKFLOW: Event type: {type(event).__name__}")

                    if hasattr(event, 'source'):
                        print(f"WORKFLOW: Event source: {event.source}")
                    if hasattr(event, 'data'):
                        print(f"WORKFLOW: Event data type: {type(event.data)}")

                    # Track progress based on event information
                    await self._track_workflow_progress(event)

                    if isinstance(event, WorkflowCompletedEvent):
                        workflow_completed = event
                        await self._update_progress("Save Results", 100, {
                            "current_step": "Save Results",
                            "completed_steps": [
                                "Parse Clothing Concept",
                                "Prepare Fashion Analysis",
                                "Concurrent Fashion Analysis",
                                "Generate Analysis Report",
                                "Create Executive Report",
                                "Prepare Approval Request",
                                "Human Review"
                            ]
                        })
                        await self._add_output("Workflow", f"Concept analysis completed: {event.data}", "success")

                    elif isinstance(event, RequestInfoEvent):
                        # Human approval required
                        print("=" * 60)
                        print("WORKFLOW: HUMAN APPROVAL REQUEST DETECTED!")
                        print("=" * 60)
                        print(f"WORKFLOW: Request ID: {event.request_id}")
                        print(f"WORKFLOW: Question: {event.data.question[:100]}..." if len(event.data.question) > 100 else f"WORKFLOW: Question: {event.data.question}")
                        print(f"WORKFLOW: Context length: {len(event.data.context)} characters")

                        await self._update_progress("Human Review", 90, {
                            "current_step": "Human Review",
                            "completed_steps": [
                                "Parse Clothing Concept",
                                "Prepare Fashion Analysis",
                                "Concurrent Fashion Analysis",
                                "Generate Analysis Report",
                                "Create Executive Report",
                                "Prepare Approval Request"
                            ]
                        })
                        await self._add_output("System", "Requesting Zava team approval", "info")
                        human_requests.append((event.request_id, event.data.question, event.data.context))
                        print("WORKFLOW: Human request added to processing queue")
                        print("=" * 60)

                # Process human approval requests
                if human_requests and not workflow_completed:
                    print(f"WORKFLOW: Processing {len(human_requests)} human approval requests")

                    for i, (request_id, question, context) in enumerate(human_requests):
                        print("=" * 80)
                        print(f"WORKFLOW: PROCESSING HUMAN APPROVAL REQUEST {i+1}/{len(human_requests)}")
                        print("=" * 80)
                        print(f"WORKFLOW: Request ID: {request_id}")

                        # Request approval through UI callback
                        if self.approval_callback:
                            print("WORKFLOW: Calling approval callback to show UI prompt")
                            await self.approval_callback(question, context)
                            print("WORKFLOW: Approval callback completed")
                        else:
                            print("WARNING: No approval callback configured!")

                        # Wait for human decision
                        print("WORKFLOW: Waiting for human approval decision...")
                        approval_response = await self._wait_for_approval_decision()
                        print(f"WORKFLOW: Received human decision: {approval_response}")

                        # Set up response for next workflow iteration
                        if pending_requests is None:
                            pending_requests = {}

                        # The approval_response is just a string ("yes" or "no")
                        # Send it directly - RequestInfoExecutor will handle the wrapping
                        pending_requests[request_id] = approval_response

                        print(f"WORKFLOW: Created RequestResponse for next iteration")
                        print("=" * 80)

                        await self._add_output("Human", f"Decision: {approval_response}", "decision")
                elif human_requests and workflow_completed:
                    print("WORKFLOW: Human requests found but workflow already completed - this may be unexpected")
                elif not human_requests and not workflow_completed:
                    print("WORKFLOW: No human requests in this iteration, workflow continuing...")

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
        # Check for required environment variable
        project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT") or os.getenv("PROJECT_ENDPOINT")
        if not project_endpoint:
            raise ValueError(
                "FOUNDRY_PROJECT_ENDPOINT or PROJECT_ENDPOINT environment variable is required. "
                "Please set it in your .env file. "
                "Example: FOUNDRY_PROJECT_ENDPOINT=https://your-project.eastus2.inference.ml.azure.com"
            )

        try:
            from agent_framework.foundry import FoundryChatClient
            from azure.identity.aio import AzureCliCredential

            await self._add_output("System", f"Initializing fresh Foundry clients with endpoint: {project_endpoint}", "info")

            # Create Azure CLI credential for authentication
            credential = AzureCliCredential()

            # Initialize multiple Foundry chat clients to avoid caching
            client1 = FoundryChatClient(project_endpoint=project_endpoint, async_credential=credential)
            client2 = FoundryChatClient(project_endpoint=project_endpoint, async_credential=credential)
            client3 = FoundryChatClient(project_endpoint=project_endpoint, async_credential=credential)

            # Use separate clients for each agent to ensure fresh instructions
            self.chat_clients = [client1, client2, client3]

            await self._add_output("System", "Fresh AI chat clients initialized successfully", "info")

        except Exception as e:
            error_msg = (
                f"Failed to initialize Foundry chat client: {str(e)}\n"
                f"Please ensure:\n"
                f"1. FOUNDRY_PROJECT_ENDPOINT or PROJECT_ENDPOINT is correctly set in .env\n"
                f"2. You are authenticated with Azure CLI (run: az login)\n"
                f"3. Your Azure account has access to the AI project"
            )
            await self._add_output("System", error_msg, "error")
            raise RuntimeError(error_msg)

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

    async def _generate_workflow_visualization(self) -> None:
        """Generate workflow visualization files (Mermaid and SVG)."""
        if not self.workflow:
            await self._add_output("System", "No workflow available for visualization", "warning")
            return

        try:
            # Import WorkflowViz
            from agent_framework._workflow._viz import WorkflowViz

            await self._add_output("System", "Generating workflow visualization...", "info")
            viz = WorkflowViz(self.workflow)

            # Generate and save Mermaid diagram
            mermaid_content = viz.to_mermaid()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mermaid_filename = f"zava_workflow_diagram_{timestamp}.mmd"

            with open(mermaid_filename, 'w') as f:
                f.write(mermaid_content)

            await self._add_output("System", f"Mermaid diagram saved: {mermaid_filename}", "success")

            # Try to export SVG visualization
            try:
                # Set Graphviz path if not in system PATH (Windows)
                graphviz_path = "C:/Program Files/Graphviz/bin"
                if os.path.exists(graphviz_path):
                    os.environ["PATH"] = graphviz_path + ";" + os.environ.get("PATH", "")
                    await self._add_output("System", f"Added Graphviz to PATH: {graphviz_path}", "info")

                # Export the DiGraph visualization as SVG
                svg_filename = f"zava_workflow_visualization_{timestamp}.svg"
                svg_file = viz.export(format="svg", filename=svg_filename)
                await self._add_output("System", f"SVG visualization saved: {svg_filename}", "success")

            except ImportError:
                await self._add_output("System", "Tip: Install 'viz' extra for SVG export: pip install agent-framework[viz]", "warning")
            except Exception as e:
                await self._add_output("System", f"SVG export failed: {str(e)}. You may need to install Graphviz: https://graphviz.org/download/", "warning")

        except ImportError:
            await self._add_output("System", "WorkflowViz not available - visualization skipped", "warning")
        except Exception as e:
            await self._add_output("System", f"Visualization generation failed: {str(e)}", "error")

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