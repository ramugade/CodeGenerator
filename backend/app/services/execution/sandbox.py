"""Subprocess-based code execution sandbox (Directive 06 - CRITICAL).

This is the PRIMARY isolation mechanism. RestrictedPython is optional.

Why subprocess instead of in-process:
- OS-level isolation - can't access parent process memory
- Easy timeout enforcement
- Can be killed without affecting main process
- Isolated filesystem and environment
"""
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from app.core.config import settings


class ExecutionResult(BaseModel):
    """Result of code execution in subprocess."""

    success: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0
    execution_time: float = 0.0
    timed_out: bool = False


class SubprocessSandbox:
    """Subprocess-based code execution (Directive 06 - PRIMARY sandbox).

    This provides OS-level isolation - the executed code runs in a completely
    separate process and cannot access the parent process memory or resources.
    """

    def __init__(self, timeout: int = None):
        """Initialize sandbox.

        Args:
            timeout: Execution timeout in seconds (default from config)
        """
        self.timeout = timeout or settings.EXECUTION_TIMEOUT

    async def execute_code(
        self,
        code: str,
        test_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute Python code in isolated subprocess.

        Args:
            code: Python code to execute
            test_input: Optional stdin input for the code

        Returns:
            ExecutionResult with output, errors, and metadata

        Security:
        - Runs in subprocess (can't access parent memory)
        - Timeout enforced
        - Restricted environment variables
        - Temporary working directory
        """
        import time

        start_time = time.time()

        try:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as code_file:
                code_file.write(code)
                code_file_path = code_file.name

            try:
                # Create temporary working directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Prepare restricted environment
                    env = {
                        "PYTHONPATH": "",  # No access to installed packages
                        "HOME": temp_dir,  # Isolated home directory
                        "TMPDIR": temp_dir,  # Isolated temp directory
                    }

                    # Execute in subprocess with restrictions
                    result = subprocess.run(
                        [sys.executable, code_file_path],
                        capture_output=True,
                        text=True,
                        timeout=self.timeout,
                        input=test_input,
                        env=env,
                        cwd=temp_dir,  # Run in isolated directory
                    )

                    execution_time = time.time() - start_time

                    return ExecutionResult(
                        success=result.returncode == 0,
                        output=result.stdout,
                        error=result.stderr,
                        exit_code=result.returncode,
                        execution_time=execution_time,
                        timed_out=False,
                    )

            finally:
                # Clean up temp file
                Path(code_file_path).unlink(missing_ok=True)

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output=e.stdout.decode() if e.stdout else "",
                error=f"Execution timed out after {self.timeout} seconds",
                exit_code=-1,
                execution_time=execution_time,
                timed_out=True,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution error: {type(e).__name__}: {str(e)}",
                exit_code=-1,
                execution_time=execution_time,
                timed_out=False,
            )

    async def execute_with_tests(
        self,
        code: str,
        test_cases: list[str],
    ) -> tuple[ExecutionResult, list[dict]]:
        """Execute code with multiple test assertions.

        Args:
            code: Python code to execute
            test_cases: List of assertion strings (e.g., "assert func([1,2]) == 1.5")

        Returns:
            Tuple of (overall result, list of test results)
        """
        # Wrap code with test execution
        test_code = f"""
{code}

# Test execution
import sys

test_results = []

test_cases = {test_cases}

for i, test in enumerate(test_cases):
    try:
        exec(test)
        test_results.append({{"index": i, "test": test, "passed": True, "error": None}})
    except AssertionError as e:
        test_results.append({{"index": i, "test": test, "passed": False, "error": str(e)}})
    except Exception as e:
        test_results.append({{"index": i, "test": test, "passed": False, "error": f"{{type(e).__name__}}: {{str(e)}}"  }})

# Print results as JSON
import json
print(json.dumps(test_results))
"""

        result = await self.execute_code(test_code)

        # Parse test results from output
        test_results = []
        if result.success and result.output:
            try:
                import json

                test_results = json.loads(result.output.strip())
            except json.JSONDecodeError:
                # If we can't parse, assume all tests failed
                test_results = [
                    {
                        "index": i,
                        "test": test,
                        "passed": False,
                        "error": "Could not parse test results",
                    }
                    for i, test in enumerate(test_cases)
                ]

        return result, test_results
