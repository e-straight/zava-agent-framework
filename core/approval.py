"""
Human approval workflow components for Zava clothing concept evaluation.

This module handles the human-in-the-loop approval process where Zava team members
review and make final decisions on clothing concept submissions.
"""

from typing import Any
from dataclasses import dataclass

from agent_framework import (
    Executor,
    WorkflowContext,
    RequestInfoMessage,
    RequestInfoExecutor
)


@dataclass
class ClothingConceptApprovalRequest(RequestInfoMessage):
    """
    Data structure for requesting human approval of clothing concepts.

    This class extends RequestInfoMessage to provide structured approval
    requests for Zava's clothing concept evaluation workflow.
    """

    question: str
    context: str

    def __str__(self) -> str:
        """Return a formatted string representation of the approval request."""
        return f"""
ZAVA CLOTHING CONCEPT APPROVAL REQUEST

{self.question}

CONCEPT ANALYSIS CONTEXT:
{self.context}

Please review the above analysis and decide whether to approve this clothing
concept for development or reject it for reconsideration.

Response Options:
- Type 'yes' to APPROVE the concept for development
- Type 'no' to REJECT the concept

Your decision will determine the next steps in our evaluation process.
        """.strip()


class ZavaApprovalDecision:
    """
    Data structure to represent approval decisions for clothing concepts.

    This class encapsulates the decision outcome and associated metadata
    for tracking approval workflow results.
    """

    def __init__(self, decision: str, feedback: str = "", timestamp: str = ""):
        self.decision = decision.lower().strip()
        self.feedback = feedback.strip()
        self.timestamp = timestamp
        self.is_approved = self.decision in ['yes', 'y', 'approve', 'approved']
        self.is_rejected = self.decision in ['no', 'n', 'reject', 'rejected', 'deny', 'denied']

    def __str__(self) -> str:
        """Return a formatted string representation of the decision."""
        status = "APPROVED" if self.is_approved else "REJECTED"
        return f"Decision: {status}" + (f" - {self.feedback}" if self.feedback else "")


class ZavaConceptApprovalManager(Executor):
    """
    Manages the human approval workflow for clothing concept evaluation.

    This executor handles the routing of approval requests and processes
    the human decisions to determine next steps in the workflow.
    """

    def __init__(self, id: str = "zava_approval_manager"):
        super().__init__(id=id)
        self.pending_requests = {}
        self.approval_history = []

    async def execute(self, input_data: Any, ctx: WorkflowContext[str]) -> Any:
        """
        Process approval workflow logic for clothing concept decisions.

        Args:
            input_data: Analysis results requiring human approval
            ctx: Workflow context for managing approval flow

        Returns:
            Routing decision based on human approval response
        """
        try:
            # Check if we have a human response to process
            if hasattr(input_data, 'response') and input_data.response:
                return await self._process_approval_response(input_data.response, ctx)

            # Otherwise, create a new approval request
            return await self._create_approval_request(input_data, ctx)

        except Exception as e:
            print(f"Approval Manager Error: {str(e)}")
            # Default to rejection on error
            return ZavaApprovalDecision("no", f"Error in approval process: {str(e)}")

    async def _create_approval_request(self, analysis_results: Any, ctx: WorkflowContext[str]) -> ClothingConceptApprovalRequest:
        """
        Create a structured approval request based on analysis results.

        Args:
            analysis_results: Comprehensive analysis from fashion agents
            ctx: Workflow context

        Returns:
            Structured approval request for human review
        """
        # Extract key information from analysis results
        analysis_text = str(analysis_results) if analysis_results else "No analysis provided"

        # Create comprehensive context for the approval decision
        approval_context = f"""
COMPREHENSIVE CLOTHING CONCEPT ANALYSIS SUMMARY

The fashion analysis agents have completed their evaluation of this clothing concept
submission. Below is the consolidated analysis covering market potential, design merit,
and production feasibility:

{analysis_text[:2000]}{'...' if len(analysis_text) > 2000 else ''}

KEY DECISION FACTORS:
• Market alignment with current fashion trends
• Design innovation and brand fit with Zava
• Production feasibility and cost considerations
• Competitive differentiation potential
• Strategic alignment with company goals

This decision will determine whether Zava proceeds with concept development
or provides constructive feedback for future submissions.
        """.strip()

        # Create the approval request
        approval_question = (
            "Based on the comprehensive fashion analysis above, should Zava approve "
            "this clothing concept for development?"
        )

        approval_request = ClothingConceptApprovalRequest(
            question=approval_question,
            context=approval_context
        )

        print("🤔 Created approval request for Zava design team review")
        return approval_request

    async def _process_approval_response(self, human_response: str, ctx: WorkflowContext[str]) -> ZavaApprovalDecision:
        """
        Process the human approval response and create a decision object.

        Args:
            human_response: The human decision (yes/no with optional feedback)
            ctx: Workflow context

        Returns:
            Structured approval decision object
        """
        from datetime import datetime

        # Parse the human response
        response_parts = human_response.split('\n', 1)
        decision = response_parts[0].strip()
        feedback = response_parts[1].strip() if len(response_parts) > 1 else ""

        # Create decision object
        approval_decision = ZavaApprovalDecision(
            decision=decision,
            feedback=feedback,
            timestamp=datetime.now().isoformat()
        )

        # Log the decision
        if approval_decision.is_approved:
            print(f"CONCEPT APPROVED by Zava design team")
            if feedback:
                print(f"   Feedback: {feedback}")
        elif approval_decision.is_rejected:
            print(f"CONCEPT REJECTED by Zava design team")
            if feedback:
                print(f"   Feedback: {feedback}")
        else:
            print(f"WARNING: UNCLEAR DECISION: {decision}")
            # Default to rejection for unclear responses
            approval_decision = ZavaApprovalDecision(
                decision="no",
                feedback=f"Unclear response '{decision}' interpreted as rejection",
                timestamp=approval_decision.timestamp
            )

        # Store in approval history
        self.approval_history.append(approval_decision)

        return approval_decision


def concept_approval_condition(decision: Any) -> bool:
    """
    Condition function to check if a clothing concept was approved.

    Args:
        decision: ZavaApprovalDecision or similar decision object

    Returns:
        True if the concept was approved, False otherwise
    """
    if isinstance(decision, ZavaApprovalDecision):
        return decision.is_approved

    # Handle string responses directly
    if isinstance(decision, str):
        return decision.lower().strip() in ['yes', 'y', 'approve', 'approved']

    # Handle other types by checking for approval attributes
    if hasattr(decision, 'is_approved'):
        return decision.is_approved

    if hasattr(decision, 'decision'):
        return str(decision.decision).lower().strip() in ['yes', 'y', 'approve', 'approved']

    # Default to False for unknown types
    return False


def concept_rejection_condition(decision: Any) -> bool:
    """
    Condition function to check if a clothing concept was rejected.

    Args:
        decision: ZavaApprovalDecision or similar decision object

    Returns:
        True if the concept was rejected, False otherwise
    """
    if isinstance(decision, ZavaApprovalDecision):
        return decision.is_rejected

    # Handle string responses directly
    if isinstance(decision, str):
        return decision.lower().strip() in ['no', 'n', 'reject', 'rejected', 'deny', 'denied']

    # Handle other types by checking for rejection attributes
    if hasattr(decision, 'is_rejected'):
        return decision.is_rejected

    if hasattr(decision, 'decision'):
        return str(decision.decision).lower().strip() in ['no', 'n', 'reject', 'rejected', 'deny', 'denied']

    # Default to True (reject) for unknown types as a safety measure
    return True


def create_zava_human_approver() -> RequestInfoExecutor:
    """
    Create a human approver executor for Zava clothing concept decisions.

    Returns:
        RequestInfoExecutor configured for human approval workflow
    """
    return RequestInfoExecutor(id="zava_human_approver")


# Convenience aliases for backward compatibility and clarity
yes_condition = concept_approval_condition
no_condition = concept_rejection_condition
ApprovalRequest = ClothingConceptApprovalRequest
RoutingDecision = ZavaApprovalDecision
ApprovalManager = ZavaConceptApprovalManager