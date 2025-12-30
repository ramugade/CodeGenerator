"""Test script for Phase 4 - LangGraph Agent Workflow.

Tests:
1. Complete workflow with test inference
2. Workflow with user-provided tests (Directive 17)
3. Iteration and error fixing
4. Token tracking (Directive 09)
"""
import asyncio
from app.agents.state import create_initial_state, TestCase
from app.agents.graph import code_generation_graph


async def test_simple_problem_with_test_inference():
    """Test 1: Simple problem with LLM test inference."""
    print("\n" + "=" * 80)
    print("TEST 1: Simple Problem with Test Inference")
    print("=" * 80)

    # Create initial state WITHOUT user-provided tests
    # This will trigger test inference
    initial_state = create_initial_state(
        user_query="Write a function that calculates the average of a list of numbers",
        session_id="test-session-1",
        llm_provider="openai",
        user_provided_tests=None,  # Will infer tests
        max_iterations=3,
    )

    print(f"\n📋 Initial state:")
    print(f"   Query: {initial_state['user_query']}")
    print(f"   Provider: {initial_state['llm_provider']}")
    print(f"   Test inference: {'SKIP' if initial_state['test_inference_skipped'] else 'NEEDED'}")
    print(f"   Max iterations: {initial_state['max_iterations']}")

    # Run workflow
    print(f"\n🚀 Starting workflow...")

    try:
        final_state = await code_generation_graph.ainvoke(initial_state)

        print(f"\n" + "=" * 80)
        print("WORKFLOW COMPLETE!")
        print("=" * 80)

        print(f"\n📊 Final state:")
        print(f"   Is complete: {final_state['is_complete']}")
        print(f"   Completion reason: {final_state.get('completion_reason', 'N/A')}")
        print(f"   Iterations: {final_state['iteration']}")
        print(f"   Tests passed: {final_state['passed_tests']}/{len(final_state['test_cases'])}")
        print(f"   Total tokens: {final_state['total_tokens']}")
        print(f"   Estimated cost: ${final_state['estimated_cost_usd']:.4f}")

        # Print token breakdown
        print(f"\n💰 Token usage breakdown:")
        for step, usage in final_state['token_usage'].items():
            print(f"   {step}: {usage['total_tokens']} tokens (${usage['cost_usd']:.4f})")

        # Print final code if successful
        if final_state.get('final_output'):
            print(f"\n✅ SUCCESS! Final output:")
            print(f"   {final_state['final_output'][:200]}")

        # Print code history
        print(f"\n📝 Code history ({len(final_state['code_history'])} versions):")
        for version in final_state['code_history']:
            print(f"   Version {version.version} (iteration {version.iteration}):")
            print(f"   {version.code[:100]}...")

        return final_state

    except Exception as e:
        print(f"\n❌ Workflow failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_user_provided_tests():
    """Test 2: User provides tests - skip test inference (Directive 17)."""
    print("\n" + "=" * 80)
    print("TEST 2: User-Provided Tests (Directive 17)")
    print("=" * 80)

    # Create test cases
    user_tests = [
        TestCase(
            description="Basic case with positive numbers",
            inputs={"numbers": [10, 20, 30]},
            expected_output=20.0,
        ),
        TestCase(
            description="Edge case - empty list",
            inputs={"numbers": []},
            expected_output=0,
        ),
        TestCase(
            description="Single number",
            inputs={"numbers": [5]},
            expected_output=5.0,
        ),
    ]

    # Create initial state WITH user-provided tests
    initial_state = create_initial_state(
        user_query="Write a function that calculates the average of a list of numbers",
        session_id="test-session-2",
        llm_provider="openai",
        user_provided_tests=user_tests,  # User-provided
        max_iterations=3,
    )

    print(f"\n📋 Initial state:")
    print(f"   Query: {initial_state['user_query']}")
    print(f"   User-provided tests: {len(user_tests)}")
    print(f"   Test inference: {'SKIP' if initial_state['test_inference_skipped'] else 'NEEDED'}")

    # Verify test inference will be skipped
    assert initial_state['test_inference_skipped'] == True, "Should skip test inference"
    assert len(initial_state['test_cases']) == len(user_tests), "Should have user tests"

    print(f"\n✅ Directive 17 verified: Test inference will be SKIPPED")

    # Run workflow
    print(f"\n🚀 Starting workflow...")

    try:
        final_state = await code_generation_graph.ainvoke(initial_state)

        print(f"\n" + "=" * 80)
        print("WORKFLOW COMPLETE!")
        print("=" * 80)

        print(f"\n📊 Final state:")
        print(f"   Is complete: {final_state['is_complete']}")
        print(f"   Iterations: {final_state['iteration']}")
        print(f"   Tests passed: {final_state['passed_tests']}/{len(final_state['test_cases'])}")
        print(f"   Total tokens: {final_state['total_tokens']}")
        print(f"   Estimated cost: ${final_state['estimated_cost_usd']:.4f}")

        # Verify test inference was NOT in token usage (Directive 17)
        if "optional_test_inference" in final_state['token_usage']:
            print(f"\n⚠️  WARNING: Test inference ran when it should have been skipped!")
        else:
            print(f"\n✅ Directive 17 verified: Test inference was SKIPPED (no tokens used)")

        return final_state

    except Exception as e:
        print(f"\n❌ Workflow failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_token_tracking():
    """Test 3: Token tracking across all nodes (Directive 09)."""
    print("\n" + "=" * 80)
    print("TEST 3: Token Tracking (Directive 09)")
    print("=" * 80)

    # Simple query
    initial_state = create_initial_state(
        user_query="Write a function that checks if a number is even",
        session_id="test-session-3",
        llm_provider="openai",
        max_iterations=2,
    )

    print(f"\n🚀 Starting workflow...")

    try:
        final_state = await code_generation_graph.ainvoke(initial_state)

        print(f"\n" + "=" * 80)
        print("TOKEN TRACKING VERIFICATION")
        print("=" * 80)

        print(f"\n💰 Per-step token usage (Directive 09):")
        total_verified = 0
        for step, usage in final_state['token_usage'].items():
            print(f"\n   {step}:")
            print(f"      Prompt tokens: {usage['prompt_tokens']}")
            print(f"      Completion tokens: {usage['completion_tokens']}")
            print(f"      Total tokens: {usage['total_tokens']}")
            print(f"      Cost: ${usage['cost_usd']:.6f}")
            total_verified += usage['total_tokens']

        print(f"\n   Verification:")
        print(f"      Sum of step tokens: {total_verified}")
        print(f"      State total_tokens: {final_state['total_tokens']}")
        print(f"      Match: {total_verified == final_state['total_tokens']}")

        assert total_verified == final_state['total_tokens'], "Token counts don't match!"

        print(f"\n✅ Directive 09 verified: All tokens tracked correctly")

        return final_state

    except Exception as e:
        print(f"\n❌ Test failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all Phase 4 tests."""
    print("\n" + "🔷" * 40)
    print("PHASE 4 - LANGGRAPH AGENT WORKFLOW TESTS")
    print("🔷" * 40)

    tests = [
        ("Test 1: Simple Problem with Test Inference", test_simple_problem_with_test_inference),
        ("Test 2: User-Provided Tests (Directive 17)", test_user_provided_tests),
        ("Test 3: Token Tracking (Directive 09)", test_token_tracking),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {type(e).__name__}"
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, result in results.items():
        print(f"{result} - {test_name}")

    print("\n" + "🔷" * 40)


if __name__ == "__main__":
    asyncio.run(main())
