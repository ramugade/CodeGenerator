"""Simple Phase 4 test - just planning node with API call."""
import asyncio
import sys
from app.agents.state import create_initial_state
from app.agents.nodes.planning import planning_node


async def test_planning_only():
    """Test just the planning node with a real API call."""
    print("\n" + "=" * 80)
    print("PHASE 4 TEST: Planning Node with OpenAI API")
    print("=" * 80)

    # Create initial state
    initial_state = create_initial_state(
        user_query="Write a function that adds two numbers",
        session_id="test-simple",
        llm_provider="openai",
        max_iterations=1,
    )

    print(f"\n📋 Testing planning node...")
    print(f"   Query: {initial_state['user_query']}")
    print(f"   Provider: {initial_state['llm_provider']}")

    try:
        # Run planning node
        result_state = await planning_node(initial_state)

        # Check results
        if result_state.get("problem_understanding") and result_state.get("approach"):
            print(f"\n✅ Planning node SUCCESS!")
            print(f"\n   Problem Understanding:")
            print(f"   {result_state['problem_understanding'][:150]}...")
            print(f"\n   Approach:")
            print(f"   {result_state['approach'][:150]}...")

            # Check token tracking
            if "planning" in result_state['token_usage']:
                tokens = result_state['token_usage']['planning']
                print(f"\n   Token usage:")
                print(f"      Prompt: {tokens['prompt_tokens']}")
                print(f"      Completion: {tokens['completion_tokens']}")
                print(f"      Total: {tokens['total_tokens']}")
                print(f"      Cost: ${tokens['cost_usd']:.4f}")

            return True
        else:
            print(f"\n❌ Planning node FAILED - missing output")
            if result_state.get("completion_reason"):
                print(f"   Reason: {result_state['completion_reason']}")
            return False

    except Exception as e:
        print(f"\n❌ Planning node ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_workflow_simple():
    """Test full workflow with a very simple problem."""
    print("\n" + "=" * 80)
    print("PHASE 4 TEST: Full Workflow (Simple Problem)")
    print("=" * 80)

    from app.agents.graph import code_generation_graph

    # Create initial state with user-provided test (to skip test inference)
    from app.agents.state import TestCase

    user_tests = [
        TestCase(
            description="Add two positive numbers",
            inputs={"a": 5, "b": 3},
            expected_output=8,
        ),
    ]

    initial_state = create_initial_state(
        user_query="Write a function named main(a, b) that adds two numbers and returns the result",
        session_id="test-full",
        llm_provider="openai",
        user_provided_tests=user_tests,  # Skip test inference
        max_iterations=2,  # Only 2 iterations
    )

    print(f"\n📋 Starting full workflow...")
    print(f"   Query: {initial_state['user_query']}")
    print(f"   User-provided tests: {len(user_tests)}")
    print(f"   Max iterations: 2")

    try:
        # Run workflow
        final_state = await asyncio.wait_for(
            code_generation_graph.ainvoke(initial_state),
            timeout=90.0  # 90 second timeout
        )

        print(f"\n" + "=" * 80)
        print("WORKFLOW COMPLETE")
        print("=" * 80)

        # Print results
        print(f"\n📊 Final Results:")
        print(f"   Complete: {final_state['is_complete']}")
        print(f"   Reason: {final_state.get('completion_reason', 'N/A')}")
        print(f"   Iterations: {final_state['iteration']}")
        print(f"   Tests passed: {final_state['passed_tests']}/{len(final_state['test_cases'])}")

        # Token summary
        print(f"\n💰 Token Usage:")
        print(f"   Total tokens: {final_state['total_tokens']}")
        print(f"   Estimated cost: ${final_state['estimated_cost_usd']:.4f}")

        # Show which nodes ran
        print(f"\n🔄 Nodes executed:")
        for step in final_state['token_usage'].keys():
            tokens = final_state['token_usage'][step]
            print(f"   - {step}: {tokens['total_tokens']} tokens")

        # Final code
        if final_state.get('current_code'):
            print(f"\n📝 Final Code:")
            print("   " + "-" * 60)
            code_lines = final_state['current_code'].split('\n')
            for line in code_lines[:15]:
                print(f"   {line}")
            if len(code_lines) > 15:
                remaining = len(code_lines) - 15
                print(f"   ... ({remaining} more lines)")
            print("   " + "-" * 60)

        # Success/failure
        success = final_state['passed_tests'] == len(final_state['test_cases'])
        if success:
            print(f"\n🎉 SUCCESS! All tests passed!")
            return True
        else:
            print(f"\n⚠️  Completed but not all tests passed")
            return False

    except asyncio.TimeoutError:
        print(f"\n⏰ Workflow timed out after 90 seconds")
        return False
    except Exception as e:
        print(f"\n❌ Workflow ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run Phase 4 tests."""
    print("\n" + "🔷" * 40)
    print("PHASE 4 - LANGGRAPH WORKFLOW TESTS")
    print("Testing with real OpenAI API calls")
    print("🔷" * 40)

    # Check for API key
    from app.core.config import settings
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key-here":
        print("\n❌ ERROR: OPENAI_API_KEY not set in .env file")
        print("   Please add your OpenAI API key to backend/.env")
        sys.exit(1)

    print(f"\n✅ OpenAI API key found")

    # Run tests
    tests = [
        ("Planning Node Only", test_planning_only),
        ("Full Workflow (Simple)", test_full_workflow_simple),
    ]

    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*80}")
        print(f"Running: {test_name}")
        print(f"{'='*80}")

        try:
            result = await test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {type(e).__name__}"
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, result in results.items():
        print(f"{result} - {test_name}")

    print("\n" + "🔷" * 40)


if __name__ == "__main__":
    asyncio.run(main())
