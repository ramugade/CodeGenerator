"""Structured output schemas for LLM responses (Directive 03).

CRITICAL: LLMs MUST return structured JSON, not freeform text or markdown.
This enforces clean output without requiring regex cleanup.
"""
from pydantic import BaseModel, Field
from typing import Optional


class PlanningOutput(BaseModel):
    """Structured output for planning step (Directive 03)."""

    problem_understanding: str = Field(
        description=(
            "Clear understanding of what the user wants to achieve. "
            "Include: input format, expected output, constraints, edge cases."
        )
    )
    approach: str = Field(
        description=(
            "High-level approach to solve the problem. "
            "Include: algorithm/method, key steps, complexity considerations."
        )
    )


class CodeOutput(BaseModel):
    """Structured output schema for code generation (Directive 03).

    LLMs must return JSON matching this exact schema.
    Backend will REJECT malformed responses - NO regex cleanup allowed.
    """

    filename: str = Field(
        description="Name of the Python file (e.g., 'solution.py')",
        examples=["solution.py", "calculator.py"],
    )

    code: str = Field(
        description=(
            "Complete Python code with a main() function. "
            "NO markdown formatting, NO code fences, just raw Python code."
        ),
    )

    explanation: str = Field(
        description="Brief explanation of how the code works and what it does",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "solution.py",
                "code": "def main(numbers):\n    return sum(numbers) / len(numbers) if numbers else 0\n\nif __name__ == '__main__':\n    print(main([10, 20, 30]))",
                "explanation": "Calculates the average of a list of numbers with edge case handling for empty lists.",
            }
        }


class TestCaseOutput(BaseModel):
    """Structured output for test case inference (Directive 04 - optional).

    Used only when user doesn't provide tests and optional inference is enabled.
    """

    description: str = Field(
        description="What this test case validates",
    )

    assertion: str = Field(
        description="Python assertion statement to validate the code",
        examples=["assert average([10, 20, 30]) == 20.0"],
    )


class TestInferenceOutput(BaseModel):
    """Structured output for multiple test cases (Directive D - OPTIONAL)."""

    test_cases: list[TestCaseOutput] = Field(
        description="List of inferred test cases",
        min_length=1,
    )

    reasoning: str = Field(
        description="Explanation of what aspects the tests cover",
    )


class ErrorAnalysisOutput(BaseModel):
    """Structured output for error analysis during fixing iteration."""

    root_cause: str = Field(
        description=(
            "Root cause of the error. What exactly went wrong? "
            "Be specific about syntax errors, logic errors, or failed test cases."
        )
    )
    failed_test_details: list[str] = Field(
        description=(
            "Details of each failed test case. "
            "For each: what was expected, what was produced, why it differs."
        ),
        default_factory=list,
    )
    suggested_fix: str = Field(
        description=(
            "Concrete suggestions for fixing the code. "
            "Include specific changes needed (algorithm, edge cases, logic)."
        )
    )
