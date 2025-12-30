"""Validation node - validates code against test cases.

This node:
1. Runs code with each test case input
2. Compares actual output to expected output
3. Counts passed/failed tests
4. Determines if workflow should continue or retry
"""
from app.agents.state import AgentState, StepType, ValidationResult
from app.services.execution.sandbox import SubprocessSandbox
import json


async def validation_node(state: AgentState) -> AgentState:
    """Validation node - validate code against test cases.

    Args:
        state: Current agent state

    Returns:
        Updated state with validation results
    """
    print(f"\n{'='*60}")
    print(f"VALIDATION NODE - Iteration {state['iteration']}")
    print(f"{'='*60}")

    if not state["current_code"]:
        print("\n❌ No code to validate!")
        state["is_complete"] = True
        state["completion_reason"] = "No code to validate"
        return state

    if not state["test_cases"]:
        print("\n❌ No test cases to validate against!")
        state["is_complete"] = True
        state["completion_reason"] = "No test cases available"
        return state

    # Check if execution was successful
    if not state["execution_results"]:
        print("\n❌ No execution results available!")
        return state

    last_execution = state["execution_results"][-1]
    if not last_execution.success:
        print("\n❌ Code execution failed - cannot validate")
        print(f"   Error: {last_execution.error[:200]}")
        state["current_step"] = StepType.VALIDATION
        state["passed_tests"] = 0
        state["failed_tests"] = len(state["test_cases"])
        return state

    # Run validation tests
    sandbox = SubprocessSandbox()
    validation_results = []
    passed = 0
    failed = 0

    print(f"\n🧪 Running {len(state['test_cases'])} test cases...")

    for i, test_case in enumerate(state["test_cases"], 1):
        print(f"\n   Test {i}: {test_case.description}")
        print(f"      Inputs: {test_case.inputs}")
        print(f"      Expected: {test_case.expected_output}")

        # Build test code that calls main() with test inputs
        test_code = f"""{state['current_code']}

# Test case execution
import json
try:
    # Call main() with test inputs
    inputs = {json.dumps(test_case.inputs)}
    result = main(**inputs)

    # Print result as JSON for parsing
    print(json.dumps({{"success": True, "result": result}}))
except Exception as e:
    # Print error as JSON
    print(json.dumps({{"success": False, "error": f"{{type(e).__name__}}: {{str(e)}}"}}))\n"""

        # Execute test
        try:
            exec_result = await sandbox.execute_code(test_code)

            if exec_result.success and exec_result.output:
                # Parse output
                try:
                    output_data = json.loads(exec_result.output.strip())

                    if output_data.get("success"):
                        actual_output = output_data.get("result")

                        # Compare actual vs expected
                        if actual_output == test_case.expected_output:
                            print(f"      ✅ PASSED")
                            print(f"      Actual: {actual_output}")
                            validation_results.append(
                                ValidationResult(
                                    test_case=test_case,
                                    passed=True,
                                    actual_output=str(actual_output),
                                    error=None,
                                )
                            )
                            passed += 1
                        else:
                            print(f"      ❌ FAILED")
                            print(f"      Actual: {actual_output}")
                            validation_results.append(
                                ValidationResult(
                                    test_case=test_case,
                                    passed=False,
                                    actual_output=str(actual_output),
                                    error=f"Expected {test_case.expected_output}, got {actual_output}",
                                )
                            )
                            failed += 1
                    else:
                        error = output_data.get("error", "Unknown error")
                        print(f"      ❌ FAILED - {error}")
                        validation_results.append(
                            ValidationResult(
                                test_case=test_case,
                                passed=False,
                                actual_output=None,
                                error=error,
                            )
                        )
                        failed += 1

                except json.JSONDecodeError:
                    print(f"      ❌ FAILED - Could not parse output")
                    print(f"      Raw output: {exec_result.output[:100]}")
                    validation_results.append(
                        ValidationResult(
                            test_case=test_case,
                            passed=False,
                            actual_output=exec_result.output[:100],
                            error="Could not parse test output",
                        )
                    )
                    failed += 1
            else:
                print(f"      ❌ FAILED - Execution error")
                print(f"      Error: {exec_result.error[:100]}")
                validation_results.append(
                    ValidationResult(
                        test_case=test_case,
                        passed=False,
                        actual_output=None,
                        error=exec_result.error[:200],
                    )
                )
                failed += 1

        except Exception as e:
            print(f"      ❌ FAILED - {type(e).__name__}: {str(e)}")
            validation_results.append(
                ValidationResult(
                    test_case=test_case,
                    passed=False,
                    actual_output=None,
                    error=f"{type(e).__name__}: {str(e)}",
                )
            )
            failed += 1

    # Update state
    state["validation_results"] = validation_results
    state["passed_tests"] = passed
    state["failed_tests"] = failed
    state["current_step"] = StepType.VALIDATION

    # Print summary
    print(f"\n{'='*60}")
    print(f"VALIDATION SUMMARY:")
    print(f"   Passed: {passed}/{len(state['test_cases'])}")
    print(f"   Failed: {failed}/{len(state['test_cases'])}")
    print(f"{'='*60}")

    # Check if all tests passed
    if passed == len(state["test_cases"]):
        print(f"\n🎉 ALL TESTS PASSED! Code is complete.")
        state["is_complete"] = True
        state["final_output"] = last_execution.output
        state["completion_reason"] = "success"

    return state
