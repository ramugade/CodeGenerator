"""Test script for subprocess sandbox and validators (Phase 3).

Tests:
1. Subprocess execution (Directive 06)
2. Anti-hardcoding detection (Directive 05)
3. Security (dangerous imports, timeouts)
4. Process cancellation (Directive 07)
"""
import asyncio
from app.services.execution.sandbox import SubprocessSandbox
from app.services.execution.validators import CodeValidator


async def test_basic_execution():
    """Test basic code execution in subprocess."""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Subprocess Execution (Directive 06)")
    print("=" * 60)

    sandbox = SubprocessSandbox(timeout=5)

    # Simple working code
    code = """
def add(a, b):
    return a + b

print(add(5, 3))
"""

    print("\n📝 Test code: Simple addition function")
    result = await sandbox.execute_code(code)

    if result.success:
        print(f"✅ Execution successful!")
        print(f"   Output: {result.output.strip()}")
        print(f"   Time: {result.execution_time:.3f}s")
    else:
        print(f"❌ Execution failed: {result.error}")

    assert result.success, "Basic execution should succeed"
    assert "8" in result.output, "Output should contain 8"


async def test_isolation():
    """Test that subprocess is isolated from parent process."""
    print("\n" + "=" * 60)
    print("TEST 2: Process Isolation (Directive 06)")
    print("=" * 60)

    sandbox = SubprocessSandbox()

    # Code that tries to access parent process (should fail)
    code = """
import os
# Try to access environment variables (should be restricted)
print(f"PATH: {os.environ.get('PATH', 'NOT FOUND')}")
print(f"USER: {os.environ.get('USER', 'NOT FOUND')}")
"""

    print("\n📝 Test: Attempting to access parent environment")
    result = await sandbox.execute_code(code)

    print(f"   Exit code: {result.exit_code}")
    print(f"   Output: {result.output[:100]}")

    # The environment should be restricted
    if "NOT FOUND" in result.output:
        print("✅ Environment is restricted (isolated)")
    else:
        print("⚠️  Environment may not be fully isolated")


async def test_timeout():
    """Test timeout enforcement."""
    print("\n" + "=" * 60)
    print("TEST 3: Timeout Enforcement (Directive 06)")
    print("=" * 60)

    sandbox = SubprocessSandbox(timeout=2)  # 2 second timeout

    # Infinite loop code
    code = """
while True:
    pass
"""

    print("\n📝 Test: Infinite loop (should timeout after 2s)")
    result = await sandbox.execute_code(code)

    if result.timed_out:
        print(f"✅ Correctly timed out after {result.execution_time:.1f}s")
    else:
        print(f"❌ Should have timed out")

    assert result.timed_out, "Infinite loop should timeout"
    assert not result.success, "Timed out execution should not be successful"


async def test_dangerous_imports():
    """Test detection of dangerous imports."""
    print("\n" + "=" * 60)
    print("TEST 4: Dangerous Import Detection (Security)")
    print("=" * 60)

    dangerous_code = """
import os
import subprocess

os.system('echo dangerous')
"""

    print("\n📝 Test: Code with dangerous imports (os, subprocess)")
    validation = CodeValidator.detect_dangerous_imports(dangerous_code)

    if not validation.is_valid:
        print(f"✅ Correctly detected dangerous imports:")
        for issue in validation.issues:
            print(f"   - {issue}")
    else:
        print("❌ Should have detected dangerous imports")

    assert not validation.is_valid, "Should detect dangerous imports"


async def test_anti_hardcoding():
    """Test anti-hardcoding detection (Directive 05)."""
    print("\n" + "=" * 60)
    print("TEST 5: Anti-Hardcoding Detection (Directive 05)")
    print("=" * 60)

    # Code with hardcoded lookup table
    hardcoded_code = """
def calculate(x):
    # Suspicious: large lookup table
    results = {
        1: 10, 2: 20, 3: 30, 4: 40, 5: 50,
        6: 60, 7: 70, 8: 80, 9: 90, 10: 100,
        11: 110, 12: 120, 13: 130, 14: 140, 15: 150,
        16: 160, 17: 170, 18: 180, 19: 190, 20: 200,
        21: 210, 22: 220, 23: 230, 24: 240, 25: 250,
    }
    return results.get(x, 0)
"""

    print("\n📝 Test 5a: Large dictionary literal (>20 entries)")
    validation = CodeValidator.detect_hardcoding(hardcoded_code)

    if validation.suspicious_patterns:
        print(f"✅ Detected suspicious patterns:")
        for pattern in validation.suspicious_patterns:
            print(f"   - {pattern}")
    else:
        print("❌ Should have detected large literal")

    assert len(validation.suspicious_patterns) > 0, "Should detect large dictionary"

    # Code with multiple string checks
    string_matching_code = """
def process(input_str):
    if input_str == "hello":
        return "world"
    elif input_str == "foo":
        return "bar"
    elif input_str == "test":
        return "result"
    elif input_str == "one":
        return "1"
    elif input_str == "two":
        return "2"
    elif input_str == "three":
        return "3"
    return "unknown"
"""

    print("\n📝 Test 5b: Multiple string equality checks")
    validation = CodeValidator.detect_hardcoding(string_matching_code)

    if validation.suspicious_patterns:
        print(f"✅ Detected suspicious string matching")
    else:
        print("⚠️  May not have detected string matching")


async def test_with_assertions():
    """Test code execution with test assertions."""
    print("\n" + "=" * 60)
    print("TEST 6: Execution with Test Assertions")
    print("=" * 60)

    sandbox = SubprocessSandbox()

    code = """
def average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
"""

    test_cases = [
        "assert average([10, 20, 30]) == 20.0",
        "assert average([]) == 0",
        "assert average([5, 5, 5, 5]) == 5.0",
    ]

    print(f"\n📝 Testing average function with {len(test_cases)} assertions")
    result, test_results = await sandbox.execute_with_tests(code, test_cases)

    passed = sum(1 for t in test_results if t.get("passed"))
    total = len(test_results)

    print(f"\n   Test Results: {passed}/{total} passed")
    for test_result in test_results:
        status = "✅" if test_result.get("passed") else "❌"
        print(f"   {status} {test_result['test']}")
        if not test_result.get("passed"):
            print(f"      Error: {test_result.get('error')}")

    assert passed == total, f"All tests should pass, got {passed}/{total}"


async def test_syntax_validation():
    """Test syntax validation."""
    print("\n" + "=" * 60)
    print("TEST 7: Syntax Validation")
    print("=" * 60)

    invalid_code = """
def broken(:
    print("missing closing paren"
"""

    print("\n📝 Test: Code with syntax errors")
    validation = CodeValidator.validate_syntax(invalid_code)

    if not validation.is_valid:
        print(f"✅ Correctly detected syntax errors:")
        for issue in validation.issues:
            print(f"   - {issue}")
    else:
        print("❌ Should have detected syntax error")

    assert not validation.is_valid, "Should detect syntax errors"


async def main():
    """Run all sandbox and validator tests."""
    print("\n" + "🔒" * 30)
    print("SUBPROCESS SANDBOX & VALIDATOR TESTS (Phase 3)")
    print("Testing Directive 05 (Anti-Hardcoding) & Directive 06 (Subprocess Sandbox)")
    print("🔒" * 30)

    tests = [
        test_basic_execution,
        test_isolation,
        test_timeout,
        test_dangerous_imports,
        test_anti_hardcoding,
        test_with_assertions,
        test_syntax_validation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {type(e).__name__}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
        print("\n💡 Phase 3 Complete - Ready for Phase 4 (LangGraph Agent)")
    else:
        print(f"\n❌ {failed} test(s) failed")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
