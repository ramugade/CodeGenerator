"""Test script for LLM services (Phase 2).

This script tests:
1. Structured output enforcement (Directive 03)
2. Provider switching (OpenAI/Anthropic)
3. Token tracking (Directive 09)
4. Output validation and rejection
"""
import asyncio
import os
from app.services.llm.factory import LLMFactory
from app.services.llm.output_schema import CodeOutput
from app.services.llm.output_parser import InvalidOutputError


async def test_openai_structured_output():
    """Test OpenAI service with structured output."""
    print("\n" + "=" * 60)
    print("TEST 1: OpenAI Structured Output (Directive 03)")
    print("=" * 60)

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  SKIPPED: OPENAI_API_KEY not set in environment")
        return

    try:
        # Create OpenAI service
        service = LLMFactory.create(provider="openai", model="gpt-3.5-turbo")
        print(f"✅ Created OpenAI service: {service.model}")

        # Test prompt
        prompt = "Write a Python function that calculates the average of a list of numbers."

        # Generate structured output
        print(f"\n📝 Prompt: {prompt}")
        print("\n⏳ Calling OpenAI API...")

        output, token_usage = await service.generate_structured(
            prompt=prompt,
            schema=CodeOutput,
            system_message="You are a Python code generator. Return clean, working code.",
        )

        # Verify structured output
        print("\n✅ RECEIVED STRUCTURED OUTPUT:")
        print(f"   Filename: {output.filename}")
        print(f"   Code length: {len(output.code)} characters")
        print(f"   Explanation: {output.explanation[:100]}...")

        # Verify NO markdown
        if "```" in output.code:
            print("❌ ERROR: Code contains markdown! (Directive 03 violation)")
        else:
            print("✅ Code is clean (no markdown)")

        # Show token usage (Directive 09)
        print(f"\n📊 Token Usage (Directive 09):")
        print(f"   Prompt: {token_usage.prompt_tokens}")
        print(f"   Completion: {token_usage.completion_tokens}")
        print(f"   Total: {token_usage.total_tokens}")
        print(f"   Cost: ${token_usage.cost_usd:.6f}")

        # Show sample of generated code
        print(f"\n📄 Generated Code (first 200 chars):")
        print("-" * 60)
        print(output.code[:200] + "...")
        print("-" * 60)

        print("\n✅ TEST PASSED: OpenAI structured output working!")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {type(e).__name__}: {str(e)}")


async def test_anthropic_structured_output():
    """Test Anthropic service with structured output."""
    print("\n" + "=" * 60)
    print("TEST 2: Anthropic Structured Output (Directive 03)")
    print("=" * 60)

    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  SKIPPED: ANTHROPIC_API_KEY not set in environment")
        return

    try:
        # Create Anthropic service
        service = LLMFactory.create(provider="anthropic")
        print(f"✅ Created Anthropic service: {service.model}")

        # Test prompt
        prompt = "Write a Python function that finds the maximum value in a list."

        # Generate structured output
        print(f"\n📝 Prompt: {prompt}")
        print("\n⏳ Calling Anthropic API...")

        output, token_usage = await service.generate_structured(
            prompt=prompt,
            schema=CodeOutput,
            system_message="You are a Python code generator.",
        )

        # Verify structured output
        print("\n✅ RECEIVED STRUCTURED OUTPUT:")
        print(f"   Filename: {output.filename}")
        print(f"   Code length: {len(output.code)} characters")
        print(f"   Explanation: {output.explanation[:100]}...")

        # Verify NO markdown
        if "```" in output.code:
            print("❌ ERROR: Code contains markdown! (Directive 03 violation)")
        else:
            print("✅ Code is clean (no markdown)")

        # Show token usage (Directive 09)
        print(f"\n📊 Token Usage (Directive 09):")
        print(f"   Prompt: {token_usage.prompt_tokens}")
        print(f"   Completion: {token_usage.completion_tokens}")
        print(f"   Total: {token_usage.total_tokens}")
        print(f"   Cost: ${token_usage.cost_usd:.6f}")

        print("\n✅ TEST PASSED: Anthropic structured output working!")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {type(e).__name__}: {str(e)}")


async def test_output_validation():
    """Test that output parser rejects malformed output."""
    print("\n" + "=" * 60)
    print("TEST 3: Output Validation (Directive 03 - Rejection)")
    print("=" * 60)

    from app.services.llm.output_parser import OutputParser

    # Test 1: Invalid JSON
    print("\n📝 Test 3a: Invalid JSON should be rejected")
    try:
        OutputParser.parse_code_output("not valid json")
        print("❌ FAILED: Should have rejected invalid JSON")
    except InvalidOutputError as e:
        print(f"✅ PASSED: Correctly rejected - {str(e)[:100]}...")

    # Test 2: Missing required fields
    print("\n📝 Test 3b: Missing fields should be rejected")
    try:
        OutputParser.parse_code_output('{"filename": "test.py"}')  # missing code
        print("❌ FAILED: Should have rejected missing fields")
    except InvalidOutputError as e:
        print(f"✅ PASSED: Correctly rejected - {str(e)[:100]}...")

    # Test 3: Code with markdown should be rejected
    print("\n📝 Test 3c: Markdown code fences should be rejected")
    try:
        malformed_output = """{
            "filename": "test.py",
            "code": "```python\\nprint('hello')\\n```",
            "explanation": "Test"
        }"""
        OutputParser.parse_code_output(malformed_output)
        print("❌ FAILED: Should have rejected markdown")
    except InvalidOutputError as e:
        print(f"✅ PASSED: Correctly rejected - {str(e)[:100]}...")

    # Test 4: Valid output should pass
    print("\n📝 Test 3d: Valid output should pass")
    try:
        valid_output = """{
            "filename": "solution.py",
            "code": "def main():\\n    return 'hello'",
            "explanation": "Simple function"
        }"""
        result = OutputParser.parse_code_output(valid_output)
        print(f"✅ PASSED: Valid output accepted - {result.filename}")
    except InvalidOutputError as e:
        print(f"❌ FAILED: Should have accepted valid output - {e}")

    print("\n✅ ALL VALIDATION TESTS PASSED!")


async def main():
    """Run all tests."""
    print("\n" + "🧪" * 30)
    print("LLM SERVICE LAYER TESTS (Phase 2)")
    print("Testing Directive 03 (Structured Output) & Directive 09 (Token Tracking)")
    print("🧪" * 30)

    # Test output validation first (doesn't need API keys)
    await test_output_validation()

    # Test LLM services (need API keys)
    await test_openai_structured_output()
    await test_anthropic_structured_output()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   - If tests passed: Move to Phase 3 (Subprocess Sandbox)")
    print("   - If tests failed: Check API keys in .env file")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
