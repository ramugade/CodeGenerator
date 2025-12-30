"""Output parser with validation and rejection logic (Directive 03).

CRITICAL: NO regex cleanup, NO markdown stripping.
LLMs must comply with schema or we reject the response.
"""
import json
from typing import TypeVar, Type
from pydantic import BaseModel, ValidationError
from app.services.llm.output_schema import (
    CodeOutput,
    TestInferenceOutput,
    ErrorAnalysisOutput,
)

T = TypeVar("T", bound=BaseModel)


class InvalidOutputError(Exception):
    """Raised when LLM returns malformed output that doesn't match schema."""

    pass


class OutputParser:
    """Parser that enforces structured output from LLMs (Directive 03).

    Philosophy: REJECT malformed responses, don't try to fix them.
    If the LLM can't follow the schema, it should retry.
    """

    @staticmethod
    def parse_structured_output(raw_output: str, schema: Type[T]) -> T:
        """Parse and validate LLM output against Pydantic schema.

        Args:
            raw_output: Raw string from LLM (should be JSON)
            schema: Pydantic model to validate against

        Returns:
            Validated Pydantic model instance

        Raises:
            InvalidOutputError: If output doesn't match schema
                (Directive 03 - NO cleanup, just reject)
        """
        try:
            # Try to parse as JSON
            data = json.loads(raw_output)
        except json.JSONDecodeError as e:
            raise InvalidOutputError(
                f"LLM returned invalid JSON. Must return valid JSON matching schema. "
                f"Error: {str(e)}\n"
                f"Raw output: {raw_output[:200]}..."
            )

        try:
            # Validate against Pydantic schema
            return schema(**data)
        except ValidationError as e:
            raise InvalidOutputError(
                f"LLM output doesn't match required schema {schema.__name__}. "
                f"Validation errors: {e.errors()}\n"
                f"Received data: {data}"
            )

    @staticmethod
    def validate_code_output(code_output: CodeOutput) -> None:
        """Additional validation for code output (Directive 03).

        Checks:
        - Code is not wrapped in markdown code fences
        - Code is actual Python (has basic syntax)
        - Filename ends with .py

        Raises:
            InvalidOutputError: If validation fails
        """
        # Check filename
        if not code_output.filename.endswith(".py"):
            raise InvalidOutputError(
                f"Filename must end with .py, got: {code_output.filename}"
            )

        # Check for markdown code fences (should NOT be present)
        code = code_output.code.strip()
        if code.startswith("```") or "```python" in code:
            raise InvalidOutputError(
                "Code contains markdown formatting (```). "
                "Must return RAW Python code only. "
                "This indicates the LLM didn't follow the schema correctly."
            )

        # Check code is not empty
        if not code or len(code.strip()) < 10:
            raise InvalidOutputError(
                f"Code is too short or empty: {len(code)} characters"
            )

        # Basic Python syntax check - must have at least one line that's not whitespace
        lines = [line for line in code.split("\n") if line.strip()]
        if len(lines) == 0:
            raise InvalidOutputError("Code contains no actual Python statements")

    @staticmethod
    def parse_code_output(raw_output: str) -> CodeOutput:
        """Parse and validate code generation output.

        This is the main method used for code generation nodes.

        Returns:
            Validated CodeOutput

        Raises:
            InvalidOutputError: If output is malformed (Directive 03)
        """
        output = OutputParser.parse_structured_output(raw_output, CodeOutput)
        OutputParser.validate_code_output(output)
        return output

    @staticmethod
    def parse_test_inference_output(raw_output: str) -> TestInferenceOutput:
        """Parse test inference output (Directive D - OPTIONAL)."""
        return OutputParser.parse_structured_output(raw_output, TestInferenceOutput)

    @staticmethod
    def parse_error_analysis_output(raw_output: str) -> ErrorAnalysisOutput:
        """Parse error analysis output for fixing iterations."""
        return OutputParser.parse_structured_output(raw_output, ErrorAnalysisOutput)
