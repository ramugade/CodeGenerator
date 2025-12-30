"""Interactive test for Phase 3 - Subprocess Sandbox and Security.

This test demonstrates:
1. Safe code execution
2. Malicious code blocking
3. Timeout handling
4. Anti-hardcoding detection
5. Test assertion framework
"""
import asyncio
from app.services.execution.sandbox import SubprocessSandbox
from app.services.execution.validators import CodeValidator


async def demo_safe_execution():
    """Demonstrate safe code execution."""
    print("\n" + "🟢" * 30)
    print("DEMO 1: Safe Code Execution")
    print("🟢" * 30)

    sandbox = SubprocessSandbox(timeout=5)

    # Example: Calculate factorial
    code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Test it
for i in range(1, 6):
    print(f"factorial({i}) = {factorial(i)}")
"""

    print("\n📝 Code to execute:")
    print("-" * 60)
    print(code)
    print("-" * 60)

    print("\n⏳ Executing in subprocess...")
    result = await sandbox.execute_code(code)

    if result.success:
        print(f"\n✅ SUCCESS!")
        print(f"   Execution time: {result.execution_time:.3f}s")
        print(f"   Output:")
        print("   " + "\n   ".join(result.output.strip().split("\n")))
    else:
        print(f"\n❌ FAILED: {result.error}")


async def demo_malicious_code_blocking():
    """Demonstrate blocking of malicious code."""
    print("\n" + "🔴" * 30)
    print("DEMO 2: Malicious Code Detection & Blocking")
    print("🔴" * 30)

    malicious_codes = [
        ("File System Access", """
import os
# Try to list files
print(os.listdir('/'))
"""),
        ("Network Access", """
import socket
# Try to create socket
s = socket.socket()
print("Socket created")
"""),
        ("Subprocess Execution", """
import subprocess
# Try to run shell command
subprocess.run(['ls', '-la'])
"""),
    ]

    for name, code in malicious_codes:
        print(f"\n🚨 Test: {name}")
        print(f"   Code preview: {code.strip()[:50]}...")

        # Validate first
        validation = CodeValidator.detect_dangerous_imports(code)

        if not validation.is_valid:
            print(f"   ✅ BLOCKED by validator:")
            for issue in validation.issues:
                print(f"      - {issue}")
        else:
            print(f"   ⚠️  Passed validation (may still fail in subprocess)")


async def demo_timeout_protection():
    """Demonstrate timeout protection."""
    print("\n" + "⏰" * 30)
    print("DEMO 3: Timeout Protection")
    print("⏰" * 30)

    sandbox = SubprocessSandbox(timeout=3)

    infinite_loop = """
# Infinite loop - should be killed after 3 seconds
import time
start = time.time()
count = 0
while True:
    count += 1
    # This will never finish
"""

    print("\n📝 Code: Infinite loop")
    print("\n⏳ Executing with 3-second timeout...")

    result = await sandbox.execute_code(infinite_loop)

    if result.timed_out:
        print(f"\n✅ TIMEOUT PROTECTION WORKED!")
        print(f"   Process killed after {result.execution_time:.1f}s")
        print(f"   Error message: {result.error}")
    else:
        print(f"\n❌ Should have timed out!")


async def demo_anti_hardcoding():
    """Demonstrate anti-hardcoding detection."""
    print("\n" + "🔍" * 30)
    print("DEMO 4: Anti-Hardcoding Detection (Directive 05)")
    print("🔍" * 30)

    # Example 1: Hardcoded lookup table
    hardcoded_example = """
def calculate_score(name):
    # Suspicious: hardcoded results for specific inputs
    scores = {
        "alice": 95, "bob": 87, "charlie": 92, "david": 88, "eve": 90,
        "frank": 85, "grace": 93, "henry": 89, "iris": 91, "jack": 86,
        "kate": 94, "leo": 87, "mary": 90, "nancy": 88, "oliver": 92,
        "paul": 89, "quinn": 91, "rachel": 93, "sam": 86, "tina": 95,
        "uma": 88, "victor": 90, "wendy": 92, "xavier": 87, "yvonne": 94,
    }
    return scores.get(name, 0)
"""

    print("\n🔍 Analyzing hardcoded lookup table...")
    validation = CodeValidator.detect_hardcoding(hardcoded_example)

    if validation.suspicious_patterns:
        print(f"\n⚠️  SUSPICIOUS PATTERNS DETECTED:")
        for pattern in validation.suspicious_patterns:
            print(f"   - {pattern}")
        print(f"\n   This code may be hardcoded for specific test inputs!")
    else:
        print(f"\n✅ No suspicious patterns detected")

    # Example 2: Proper solution (should pass)
    proper_solution = """
def calculate_score(name):
    # Proper implementation: uses algorithm, not lookup
    return len(name) * 10 + ord(name[0].lower()) % 10
"""

    print("\n\n🔍 Analyzing proper algorithmic solution...")
    validation = CodeValidator.detect_hardcoding(proper_solution)

    if validation.suspicious_patterns:
        print(f"\n⚠️  Suspicious patterns: {len(validation.suspicious_patterns)}")
    else:
        print(f"\n✅ Clean code - no hardcoding detected")


async def demo_test_assertions():
    """Demonstrate test assertion framework."""
    print("\n" + "🧪" * 30)
    print("DEMO 5: Test Assertion Framework")
    print("🧪" * 30)

    sandbox = SubprocessSandbox()

    # Code to test
    code = """
def is_palindrome(s):
    # Remove spaces and convert to lowercase
    s = s.replace(" ", "").lower()
    return s == s[::-1]
"""

    test_cases = [
        "assert is_palindrome('racecar') == True",
        "assert is_palindrome('hello') == False",
        "assert is_palindrome('A man a plan a canal Panama') == True",
        "assert is_palindrome('') == True",
        "assert is_palindrome('Madam') == True",
    ]

    print(f"\n🧪 Testing palindrome function with {len(test_cases)} test cases...")
    print("\n   Test cases:")
    for i, test in enumerate(test_cases, 1):
        print(f"   {i}. {test}")

    print("\n⏳ Running tests...")
    result, test_results = await sandbox.execute_with_tests(code, test_cases)

    print(f"\n📊 Results:")
    passed = 0
    for test_result in test_results:
        if test_result.get("passed"):
            passed += 1
            print(f"   ✅ Test {test_result['index'] + 1}: PASSED")
        else:
            print(f"   ❌ Test {test_result['index'] + 1}: FAILED")
            print(f"      Error: {test_result.get('error')}")

    print(f"\n   Final Score: {passed}/{len(test_cases)} tests passed")

    if passed == len(test_cases):
        print(f"   🎉 All tests passed!")


async def demo_syntax_validation():
    """Demonstrate syntax validation."""
    print("\n" + "📝" * 30)
    print("DEMO 6: Syntax Validation")
    print("📝" * 30)

    examples = [
        ("Valid Code", """
def greet(name):
    return f"Hello, {name}!"
""", True),
        ("Missing Colon", """
def broken(x)
    return x * 2
""", False),
        ("Unclosed String", """
def test():
    print("Hello
""", False),
        ("Invalid Indentation", """
def foo():
return 42
""", False),
    ]

    for name, code, should_be_valid in examples:
        print(f"\n📝 Example: {name}")
        validation = CodeValidator.validate_syntax(code)

        if validation.is_valid:
            print(f"   ✅ Syntax is valid")
            if not should_be_valid:
                print(f"   ⚠️  Expected to be invalid!")
        else:
            print(f"   ❌ Syntax errors detected:")
            for issue in validation.issues:
                print(f"      - {issue}")
            if should_be_valid:
                print(f"   ⚠️  Expected to be valid!")


async def main():
    """Run all interactive demos."""
    print("\n" + "=" * 80)
    print(" " * 20 + "PHASE 3 INTERACTIVE DEMO")
    print(" " * 10 + "Subprocess Sandbox & Security Features")
    print("=" * 80)

    demos = [
        demo_safe_execution,
        demo_malicious_code_blocking,
        demo_timeout_protection,
        demo_anti_hardcoding,
        demo_test_assertions,
        demo_syntax_validation,
    ]

    for demo in demos:
        try:
            await demo()
            await asyncio.sleep(0.5)  # Pause between demos
        except Exception as e:
            print(f"\n❌ Demo failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print(" " * 25 + "DEMO COMPLETE!")
    print("=" * 80)
    print("\n✅ Phase 3 Features Demonstrated:")
    print("   1. ✅ Safe subprocess execution (Directive 06)")
    print("   2. ✅ Dangerous import detection")
    print("   3. ✅ Timeout protection")
    print("   4. ✅ Anti-hardcoding detection (Directive 05)")
    print("   5. ✅ Test assertion framework")
    print("   6. ✅ Syntax validation")
    print("\n💡 All security features working correctly!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
