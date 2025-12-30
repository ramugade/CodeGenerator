"""LangGraph workflow for code generation agent.

This file defines the complete agent workflow:
1. Planning → 2. Optional Test Inference → 3. Code Generation →
4. Execution → 5. Validation → (if failed) 6. Error Fixing → back to 3

Workflow stops when:
- All tests pass (success)
- Max iterations reached
- Critical error occurs
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState, StepType
from app.agents.nodes.planning import planning_node
from app.agents.nodes.optional_test_inference import optional_test_inference_node
from app.agents.nodes.code_generation import code_generation_node
from app.agents.nodes.execution import execution_node
from app.agents.nodes.validation import validation_node
from app.agents.nodes.error_fixing import error_fixing_node


def should_continue_after_validation(
    state: AgentState,
) -> Literal["error_fixing", "complete"]:
    """Routing function after validation.

    Routes to:
    - "complete" if all tests passed or workflow is marked complete
    - "error_fixing" if tests failed and we should retry

    Args:
        state: Current agent state

    Returns:
        Next node name
    """
    # Check if workflow is already marked complete
    if state.get("is_complete", False):
        return "complete"

    # Check if all tests passed
    if state.get("passed_tests", 0) == len(state.get("test_cases", [])):
        return "complete"

    # Check if we've hit max iterations
    if state.get("iteration", 1) >= state.get("max_iterations", 5):
        return "complete"

    # Tests failed - retry with error fixing
    return "error_fixing"


def should_skip_test_inference(
    state: AgentState,
) -> Literal["optional_test_inference", "code_generation"]:
    """Routing function after planning.

    Routes to:
    - "code_generation" if user provided tests (Directive 17)
    - "optional_test_inference" if tests need to be inferred

    Args:
        state: Current agent state

    Returns:
        Next node name
    """
    # Check if user provided tests (Directive 17)
    if state.get("test_inference_skipped", False):
        return "code_generation"

    return "optional_test_inference"


def create_code_generation_graph() -> StateGraph:
    """Create the LangGraph workflow for code generation.

    Workflow:
    START → planning → [optional_test_inference] → code_generation →
    execution → validation → [error_fixing → code_generation] → END

    Returns:
        Compiled StateGraph
    """
    # Create graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planning", planning_node)
    workflow.add_node("optional_test_inference", optional_test_inference_node)
    workflow.add_node("code_generation", code_generation_node)
    workflow.add_node("execution", execution_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("error_fixing", error_fixing_node)

    # Set entry point
    workflow.set_entry_point("planning")

    # Add edges
    # 1. Planning → Optional Test Inference or Code Generation (conditional)
    workflow.add_conditional_edges(
        "planning",
        should_skip_test_inference,
        {
            "optional_test_inference": "optional_test_inference",
            "code_generation": "code_generation",
        },
    )

    # 2. Optional Test Inference → Code Generation
    workflow.add_edge("optional_test_inference", "code_generation")

    # 3. Code Generation → Execution
    workflow.add_edge("code_generation", "execution")

    # 4. Execution → Validation
    workflow.add_edge("execution", "validation")

    # 5. Validation → Error Fixing or END (conditional)
    workflow.add_conditional_edges(
        "validation",
        should_continue_after_validation,
        {
            "error_fixing": "error_fixing",
            "complete": END,
        },
    )

    # 6. Error Fixing → Code Generation (retry loop)
    workflow.add_edge("error_fixing", "code_generation")

    # Compile graph
    app = workflow.compile()

    return app


# Create the compiled graph (singleton)
code_generation_graph = create_code_generation_graph()
