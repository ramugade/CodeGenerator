"""Quick structural test for Phase 4 - verify imports and graph structure."""
import asyncio


def test_imports():
    """Test that all modules can be imported."""
    print("\n" + "=" * 60)
    print("TEST: Import all Phase 4 modules")
    print("=" * 60)

    try:
        from app.agents.state import (
            AgentState,
            StepType,
            TestCase,
            CodeVersion,
            ExecutionResult,
            ValidationResult,
            create_initial_state,
        )

        print("✅ state.py imports successful")

        from app.agents.nodes.planning import planning_node

        print("✅ planning.py imports successful")

        from app.agents.nodes.optional_test_inference import (
            optional_test_inference_node,
        )

        print("✅ optional_test_inference.py imports successful")

        from app.agents.nodes.code_generation import code_generation_node

        print("✅ code_generation.py imports successful")

        from app.agents.nodes.execution import execution_node

        print("✅ execution.py imports successful")

        from app.agents.nodes.validation import validation_node

        print("✅ validation.py imports successful")

        from app.agents.nodes.error_fixing import error_fixing_node

        print("✅ error_fixing.py imports successful")

        from app.agents.graph import (
            code_generation_graph,
            create_code_generation_graph,
        )

        print("✅ graph.py imports successful")

        return True

    except Exception as e:
        print(f"❌ Import failed: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_graph_structure():
    """Test LangGraph structure."""
    print("\n" + "=" * 60)
    print("TEST: Verify LangGraph structure")
    print("=" * 60)

    try:
        from app.agents.graph import code_generation_graph

        # Verify graph exists
        print(f"✅ Graph compiled: {type(code_generation_graph)}")

        # Verify graph has nodes
        if hasattr(code_generation_graph, "nodes"):
            print(f"✅ Graph has nodes attribute")
        else:
            print(f"⚠️  Graph structure may differ (no nodes attribute)")

        return True

    except Exception as e:
        print(f"❌ Graph structure test failed: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_state_creation():
    """Test state initialization."""
    print("\n" + "=" * 60)
    print("TEST: State creation and structure")
    print("=" * 60)

    try:
        from app.agents.state import create_initial_state, TestCase

        # Test 1: Without user-provided tests
        state1 = create_initial_state(
            user_query="Test query",
            session_id="test-123",
            llm_provider="openai",
            user_provided_tests=None,
        )

        assert state1["user_query"] == "Test query"
        assert state1["session_id"] == "test-123"
        assert state1["llm_provider"] == "openai"
        assert state1["test_inference_skipped"] == False
        assert state1["iteration"] == 1
        assert state1["max_iterations"] == 5
        print("✅ State creation without tests works")

        # Test 2: With user-provided tests (Directive 17)
        user_tests = [
            TestCase(
                description="Test 1",
                inputs={"x": 10},
                expected_output=20,
            )
        ]

        state2 = create_initial_state(
            user_query="Test query",
            session_id="test-456",
            llm_provider="anthropic",
            user_provided_tests=user_tests,
        )

        assert state2["test_inference_skipped"] == True
        assert len(state2["test_cases"]) == 1
        print("✅ State creation with user tests works (Directive 17)")

        return True

    except Exception as e:
        print(f"❌ State creation test failed: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_schemas():
    """Test output schemas."""
    print("\n" + "=" * 60)
    print("TEST: Output schemas")
    print("=" * 60)

    try:
        from app.services.llm.output_schema import (
            PlanningOutput,
            CodeOutput,
            ErrorAnalysisOutput,
        )

        # Test PlanningOutput
        planning = PlanningOutput(
            problem_understanding="Test understanding",
            approach="Test approach",
        )
        print(f"✅ PlanningOutput schema works")

        # Test CodeOutput
        code = CodeOutput(
            filename="test.py",
            code="def main():\n    pass",
            explanation="Test code",
        )
        print(f"✅ CodeOutput schema works")

        # Test ErrorAnalysisOutput
        error = ErrorAnalysisOutput(
            root_cause="Test error",
            failed_test_details=["Detail 1"],
            suggested_fix="Fix it",
        )
        print(f"✅ ErrorAnalysisOutput schema works")

        return True

    except Exception as e:
        print(f"❌ Schema test failed: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all structural tests."""
    print("\n" + "🔷" * 30)
    print("PHASE 4 - STRUCTURAL TESTS (No API calls)")
    print("🔷" * 30)

    tests = [
        ("Module imports", test_imports),
        ("Graph structure", test_graph_structure),
        ("State creation", test_state_creation),
        ("Output schemas", test_schemas),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {type(e).__name__}"
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results.items():
        print(f"{result} - {test_name}")

    all_passed = all("✅" in r for r in results.values())

    if all_passed:
        print("\n🎉 All structural tests passed!")
        print("\n📝 Phase 4 Implementation Complete:")
        print("   ✅ All modules import correctly")
        print("   ✅ LangGraph workflow compiled")
        print("   ✅ State management working")
        print("   ✅ Output schemas validated")
        print("\n💡 Ready for Phase 5 (FastAPI SSE Endpoint)")
    else:
        print("\n❌ Some tests failed - check output above")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
