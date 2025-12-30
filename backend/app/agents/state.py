"""LangGraph agent state definition for code generation workflow.

This state is passed through all nodes in the agent graph, tracking:
- User input and configuration
- Workflow control (current step, iterations)
- Planning phase outputs
- Test cases (user-provided or LLM-inferred)
- Code generation history
- Execution and validation results
- Token usage tracking (Directive 09)
"""
from typing import TypedDict, Literal, Optional
from enum import Enum
from pydantic import BaseModel, Field


class StepType(str, Enum):
    """Workflow step types."""

    PLANNING = "planning"
    OPTIONAL_TEST_INFERENCE = "optional_test_inference"  # Directive 17
    CODE_GENERATION = "code_generation"
    EXECUTION = "execution"
    VALIDATION = "validation"
    ERROR_FIXING = "error_fixing"
    COMPLETE = "complete"


class TestCase(BaseModel):
    """Test case model."""

    description: str = Field(description="Test case description")
    inputs: dict = Field(description="Input parameters as dict")
    expected_output: str | int | float | list | dict | None = Field(
        description="Expected output value"
    )


class CodeVersion(BaseModel):
    """Versioned code attempt."""

    version: int = Field(description="Code version number (1-indexed)")
    code: str = Field(description="Python code")
    iteration: int = Field(description="Iteration when this code was generated")


class ExecutionResult(BaseModel):
    """Result of code execution."""

    version: int = Field(description="Code version that was executed")
    success: bool = Field(description="Whether execution succeeded")
    output: str = Field(default="", description="Stdout output")
    error: str = Field(default="", description="Stderr or error message")
    execution_time: float = Field(description="Execution time in seconds")
    timed_out: bool = Field(default=False, description="Whether execution timed out")


class ValidationResult(BaseModel):
    """Validation result for a single test case."""

    test_case: TestCase
    passed: bool
    actual_output: Optional[str] = None
    error: Optional[str] = None


class AgentState(TypedDict):
    """State passed through LangGraph workflow.

    This is the core state object that flows through all nodes.
    Each node reads and updates relevant fields.
    """

    # ===== INPUT CONFIGURATION =====
    user_query: str  # User's problem description
    session_id: str  # Unique session identifier
    llm_provider: Literal["openai", "anthropic"]  # Which LLM to use

    # ===== OPTIONAL USER-PROVIDED TEST CASES (Directive 17) =====
    user_provided_tests: Optional[
        list[TestCase]
    ]  # If user provides tests, skip inference

    # ===== WORKFLOW CONTROL =====
    current_step: StepType  # Current workflow step
    iteration: int  # Current iteration (1-indexed)
    max_iterations: int  # Maximum iterations allowed (default: 5)

    # ===== PLANNING PHASE =====
    problem_understanding: Optional[str]  # LLM's understanding of the problem
    approach: Optional[str]  # Planned approach to solve the problem

    # ===== TEST CASES =====
    test_cases: list[
        TestCase
    ]  # Either user-provided or LLM-inferred (Directive 17)
    test_inference_skipped: bool  # True if user provided tests (Directive 17)

    # ===== CODE GENERATION =====
    code_history: list[CodeVersion]  # All code versions generated
    current_code: Optional[str]  # Most recent code version

    # ===== EXECUTION RESULTS =====
    execution_results: list[ExecutionResult]  # All execution attempts

    # ===== VALIDATION RESULTS =====
    validation_results: list[ValidationResult]  # Validation results per test case
    passed_tests: int  # Number of passed tests
    failed_tests: int  # Number of failed tests

    # ===== ERROR CONTEXT FOR FIXING =====
    last_error_analysis: Optional[str]  # LLM's analysis of the last error
    error_history: list[str]  # History of error analyses

    # ===== TOKEN USAGE TRACKING (Directive 09) =====
    token_usage: dict[
        str, dict
    ]  # Per-step token usage: {"planning": {prompt: 50, completion: 100, ...}}
    total_tokens: int  # Total tokens used across all steps
    estimated_cost_usd: float  # Estimated cost based on token usage

    # ===== COMPLETION =====
    is_complete: bool  # Whether workflow is finished
    final_output: Optional[str]  # Final successful output
    completion_reason: Optional[
        str
    ]  # Why it completed (success, max_iterations, error)


def create_initial_state(
    user_query: str,
    session_id: str,
    llm_provider: Literal["openai", "anthropic"] = "openai",
    user_provided_tests: Optional[list[TestCase]] = None,
    max_iterations: int = 5,
) -> AgentState:
    """Create initial agent state.

    Args:
        user_query: User's problem description
        session_id: Unique session identifier
        llm_provider: LLM provider to use
        user_provided_tests: Optional user-provided test cases (Directive 17)
        max_iterations: Maximum iterations allowed

    Returns:
        Initialized AgentState
    """
    return AgentState(
        # Input configuration
        user_query=user_query,
        session_id=session_id,
        llm_provider=llm_provider,
        user_provided_tests=user_provided_tests,
        # Workflow control
        current_step=StepType.PLANNING,
        iteration=1,
        max_iterations=max_iterations,
        # Planning phase
        problem_understanding=None,
        approach=None,
        # Test cases
        test_cases=user_provided_tests or [],
        test_inference_skipped=user_provided_tests is not None,  # Directive 17
        # Code generation
        code_history=[],
        current_code=None,
        # Execution results
        execution_results=[],
        # Validation results
        validation_results=[],
        passed_tests=0,
        failed_tests=0,
        # Error context
        last_error_analysis=None,
        error_history=[],
        # Token usage (Directive 09)
        token_usage={},
        total_tokens=0,
        estimated_cost_usd=0.0,
        # Completion
        is_complete=False,
        final_output=None,
        completion_reason=None,
    )
