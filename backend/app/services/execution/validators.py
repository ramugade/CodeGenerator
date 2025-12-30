"""Code validators including anti-hardcoding detection (Directive 05).

Prevents LLMs from hardcoding outputs for given test examples.
"""
import ast
import re
from typing import Optional
from pydantic import BaseModel


class ValidationResult(BaseModel):
    """Result of code validation."""

    is_valid: bool
    issues: list[str] = []
    warnings: list[str] = []
    suspicious_patterns: list[str] = []


class CodeValidator:
    """Validates generated code for security and quality (Directive 05)."""

    # Dangerous imports that should be blocked
    DANGEROUS_IMPORTS = {
        "os",
        "subprocess",
        "sys",
        "socket",
        "requests",
        "urllib",
        "http",
        "ftplib",
        "telnetlib",
        "eval",
        "exec",
        "compile",
        "__import__",
    }

    @staticmethod
    def validate_syntax(code: str) -> ValidationResult:
        """Validate Python syntax using AST parsing.

        Args:
            code: Python code to validate

        Returns:
            ValidationResult with syntax issues
        """
        issues = []
        warnings = []

        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            issues.append(f"Parse error: {type(e).__name__}: {str(e)}")

        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
        )

    @staticmethod
    def detect_dangerous_imports(code: str) -> ValidationResult:
        """Detect dangerous imports in code.

        Args:
            code: Python code to check

        Returns:
            ValidationResult with dangerous imports flagged
        """
        issues = []
        warnings = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in CodeValidator.DANGEROUS_IMPORTS:
                            issues.append(
                                f"Dangerous import detected: {alias.name}"
                            )

                elif isinstance(node, ast.ImportFrom):
                    if node.module in CodeValidator.DANGEROUS_IMPORTS:
                        issues.append(
                            f"Dangerous import detected: from {node.module}"
                        )

        except Exception as e:
            warnings.append(f"Could not check imports: {str(e)}")

        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
        )

    @staticmethod
    def detect_hardcoding(
        code: str,
        test_inputs: Optional[list[str]] = None,
    ) -> ValidationResult:
        """Detect suspicious hardcoding patterns (Directive 05).

        Checks:
        1. Large dictionary/list literals (>20 entries)
        2. Direct string matching on test inputs
        3. Suspicious constants that match all expected outputs

        Args:
            code: Python code to analyze
            test_inputs: Optional test inputs to check for hardcoding

        Returns:
            ValidationResult with hardcoding warnings
        """
        issues = []
        warnings = []
        suspicious_patterns = []

        try:
            tree = ast.parse(code)

            # Check 1: Large literal collections (likely hardcoded lookup tables)
            for node in ast.walk(tree):
                if isinstance(node, (ast.List, ast.Dict, ast.Set)):
                    if isinstance(node, ast.List) and len(node.elts) > 20:
                        suspicious_patterns.append(
                            f"Large list literal ({len(node.elts)} items) - possible hardcoding"
                        )
                    elif isinstance(node, ast.Dict) and len(node.keys) > 20:
                        suspicious_patterns.append(
                            f"Large dict literal ({len(node.keys)} entries) - possible hardcoding"
                        )

            # Check 2: Direct string matching in if statements
            if_string_pattern = re.compile(r'if\s+.*==\s*["\'].*["\']')
            matches = if_string_pattern.findall(code)
            if len(matches) > 5:
                suspicious_patterns.append(
                    f"Multiple string equality checks ({len(matches)}) - possible input hardcoding"
                )

            # Check 3: Return statements with only literals (no computation)
            return_literal_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.Return) and isinstance(
                    node.value, (ast.Constant, ast.Num, ast.Str)
                ):
                    return_literal_count += 1

            if return_literal_count > 3:
                suspicious_patterns.append(
                    f"Multiple return literal statements ({return_literal_count}) - possible output hardcoding"
                )

            # Check 4: If test inputs provided, check for exact string matches
            if test_inputs:
                for test_input in test_inputs[:5]:  # Check first 5 inputs
                    # Extract numbers/values from test input
                    test_values = re.findall(r'\d+', str(test_input))
                    for value in test_values:
                        # Check if value appears as string literal in code
                        if f'"{value}"' in code or f"'{value}'" in code:
                            suspicious_patterns.append(
                                f"Test value '{value}' found as string literal in code"
                            )
                            break

        except Exception as e:
            warnings.append(f"Could not analyze for hardcoding: {str(e)}")

        # If we found suspicious patterns, add a warning
        if suspicious_patterns:
            warnings.append(
                "ANTI-HARDCODING CHECK (Directive 05): Suspicious patterns detected. "
                "Code may be hardcoded for specific inputs."
            )

        return ValidationResult(
            is_valid=True,  # Don't reject, just warn
            issues=issues,
            warnings=warnings,
            suspicious_patterns=suspicious_patterns,
        )

    @staticmethod
    def validate_code(
        code: str,
        test_inputs: Optional[list[str]] = None,
    ) -> ValidationResult:
        """Run all validation checks on code.

        Args:
            code: Python code to validate
            test_inputs: Optional test inputs for hardcoding detection

        Returns:
            Combined ValidationResult
        """
        results = [
            CodeValidator.validate_syntax(code),
            CodeValidator.detect_dangerous_imports(code),
            CodeValidator.detect_hardcoding(code, test_inputs),
        ]

        # Combine all results
        all_issues = []
        all_warnings = []
        all_suspicious = []

        for result in results:
            all_issues.extend(result.issues)
            all_warnings.extend(result.warnings)
            all_suspicious.extend(result.suspicious_patterns)

        return ValidationResult(
            is_valid=len(all_issues) == 0,
            issues=all_issues,
            warnings=all_warnings,
            suspicious_patterns=all_suspicious,
        )
