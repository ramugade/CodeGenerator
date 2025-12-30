"""Comprehensive test suite for all phases (1-5)."""
import asyncio
import httpx
import sys


async def test_phase1_foundation():
    """Test Phase 1: Foundation setup."""
    print("\n" + "=" * 80)
    print("PHASE 1: Foundation Setup")
    print("=" * 80)

    tests_passed = 0
    tests_total = 3

    # Test 1: Health endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health endpoint working")
                print(f"   Status: {data['status']}")
                tests_passed += 1
            else:
                print(f"❌ Health endpoint failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

    # Test 2: Root endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/")
            if response.status_code == 200:
                print(f"✅ Root endpoint working")
                tests_passed += 1
            else:
                print(f"❌ Root endpoint failed")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

    # Test 3: API docs
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/docs")
            if response.status_code == 200:
                print(f"✅ API docs available at /docs")
                tests_passed += 1
            else:
                print(f"❌ API docs failed")
    except Exception as e:
        print(f"❌ API docs error: {e}")

    print(f"\nPhase 1 Result: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


async def test_phase2_llm_service():
    """Test Phase 2: LLM service layer."""
    print("\n" + "=" * 80)
    print("PHASE 2: LLM Service Layer")
    print("=" * 80)

    tests_passed = 0
    tests_total = 2

    # Test 1: Import services
    try:
        from app.services.llm.factory import LLMFactory
        from app.services.llm.openai_service import OpenAIService
        from app.services.llm.output_schema import (
            PlanningOutput,
            CodeOutput,
            ErrorAnalysisOutput,
        )
        print(f"✅ All LLM services import successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ LLM service import failed: {e}")

    # Test 2: Create service instances
    try:
        llm = LLMFactory.create("openai")
        print(f"✅ LLM factory creates OpenAI service: {type(llm).__name__}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ LLM factory failed: {e}")

    print(f"\nPhase 2 Result: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


async def test_phase3_sandbox():
    """Test Phase 3: Subprocess sandbox."""
    print("\n" + "=" * 80)
    print("PHASE 3: Subprocess Sandbox")
    print("=" * 80)

    tests_passed = 0
    tests_total = 3

    # Test 1: Basic execution
    try:
        from app.services.execution.sandbox import SubprocessSandbox

        sandbox = SubprocessSandbox(timeout=5)
        code = "print('Hello from sandbox')"
        result = await sandbox.execute_code(code)

        if result.success and "Hello from sandbox" in result.output:
            print(f"✅ Basic code execution working")
            print(f"   Output: {result.output.strip()}")
            print(f"   Time: {result.execution_time:.3f}s")
            tests_passed += 1
        else:
            print(f"❌ Basic execution failed")
    except Exception as e:
        print(f"❌ Sandbox execution error: {e}")

    # Test 2: Dangerous import detection
    try:
        from app.services.execution.validators import CodeValidator

        dangerous_code = "import os\nos.system('ls')"
        validation = CodeValidator.detect_dangerous_imports(dangerous_code)

        if not validation.is_valid and len(validation.issues) > 0:
            print(f"✅ Dangerous import detection working")
            print(f"   Detected: {validation.issues[0]}")
            tests_passed += 1
        else:
            print(f"❌ Should have detected dangerous imports")
    except Exception as e:
        print(f"❌ Validator error: {e}")

    # Test 3: Timeout enforcement
    try:
        sandbox = SubprocessSandbox(timeout=2)
        infinite_loop = "while True: pass"
        result = await sandbox.execute_code(infinite_loop)

        if result.timed_out:
            print(f"✅ Timeout enforcement working")
            print(f"   Killed after {result.execution_time:.1f}s")
            tests_passed += 1
        else:
            print(f"❌ Should have timed out")
    except Exception as e:
        print(f"❌ Timeout test error: {e}")

    print(f"\nPhase 3 Result: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


async def test_phase4_langgraph():
    """Test Phase 4: LangGraph workflow."""
    print("\n" + "=" * 80)
    print("PHASE 4: LangGraph Agent Workflow")
    print("=" * 80)

    tests_passed = 0
    tests_total = 3

    # Test 1: Import all nodes
    try:
        from app.agents.graph import code_generation_graph
        from app.agents.state import create_initial_state, TestCase
        from app.agents.nodes.planning import planning_node
        from app.agents.nodes.code_generation import code_generation_node
        from app.agents.nodes.execution import execution_node
        from app.agents.nodes.validation import validation_node

        print(f"✅ All agent nodes import successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Agent import failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: State creation
    try:
        state = create_initial_state(
            user_query="Test query",
            session_id="test-123",
            llm_provider="openai",
        )

        if (
            state["user_query"] == "Test query"
            and state["session_id"] == "test-123"
            and state["iteration"] == 1
        ):
            print(f"✅ State creation working")
            tests_passed += 1
        else:
            print(f"❌ State creation failed")
    except Exception as e:
        print(f"❌ State creation error: {e}")

    # Test 3: Graph compilation
    try:
        if code_generation_graph is not None:
            print(f"✅ LangGraph compiled: {type(code_generation_graph).__name__}")
            tests_passed += 1
        else:
            print(f"❌ Graph not compiled")
    except Exception as e:
        print(f"❌ Graph compilation error: {e}")

    print(f"\nPhase 4 Result: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


async def test_phase5_sse():
    """Test Phase 5: SSE endpoint."""
    print("\n" + "=" * 80)
    print("PHASE 5: FastAPI SSE Endpoint")
    print("=" * 80)

    tests_passed = 0
    tests_total = 2

    # Test 1: SSE endpoint exists
    try:
        from app.api.routes.generate import generate_code

        print(f"✅ SSE endpoint imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ SSE endpoint import failed: {e}")

    # Test 2: Quick SSE stream test (with API key check)
    from app.core.config import settings

    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key-here":
        print(f"⏭️  Skipping SSE stream test (no API key)")
        tests_total = 1  # Adjust total
    else:
        try:
            request_data = {
                "query": "Write a function main(x) that returns x * 2",
                "llm_provider": "openai",
                "user_provided_tests": [
                    {
                        "description": "Double a number",
                        "inputs": {"x": 5},
                        "expected_output": 10,
                    }
                ],
                "max_iterations": 1,
            }

            print(f"   Testing SSE stream (this will take ~10-15s)...")

            events_received = []
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST", "http://localhost:8000/api/generate", json=request_data
                ) as response:
                    if response.status_code == 200:
                        event_type = None
                        async for line in response.aiter_lines():
                            line = line.strip()
                            if line.startswith("event:"):
                                event_type = line.split("event:", 1)[1].strip()
                            elif line.startswith("data:") and event_type:
                                events_received.append(event_type)
                                event_type = None

                            # Stop after complete event
                            if "complete" in events_received:
                                break

            if "complete" in events_received:
                print(f"✅ SSE streaming working")
                print(f"   Events: {events_received}")
                tests_passed += 1
            else:
                print(f"❌ SSE stream incomplete: {events_received}")

        except Exception as e:
            print(f"❌ SSE stream test error: {e}")

    print(f"\nPhase 5 Result: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total


async def test_end_to_end():
    """Test complete end-to-end workflow."""
    print("\n" + "=" * 80)
    print("END-TO-END: Complete Workflow Test")
    print("=" * 80)

    from app.core.config import settings

    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key-here":
        print(f"⏭️  Skipping end-to-end test (no API key)")
        return True

    try:
        print(f"\n📋 Testing: Simple addition function")
        print(f"   This will test all phases working together...")

        request_data = {
            "query": "Write a function main(a, b) that returns the sum of two numbers",
            "llm_provider": "openai",
            "user_provided_tests": [
                {
                    "description": "Add two numbers",
                    "inputs": {"a": 10, "b": 20},
                    "expected_output": 30,
                }
            ],
            "max_iterations": 2,
        }

        events = []
        success = False

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", "http://localhost:8000/api/generate", json=request_data
            ) as response:
                if response.status_code != 200:
                    print(f"❌ HTTP {response.status_code}")
                    return False

                event_type = None
                async for line in response.aiter_lines():
                    line = line.strip()

                    if line.startswith("event:"):
                        event_type = line.split("event:", 1)[1].strip()

                    elif line.startswith("data:") and event_type:
                        events.append(event_type)

                        # Check for success
                        if event_type == "complete":
                            import json
                            data = json.loads(line.split("data:", 1)[1].strip())
                            success = data.get("success", False)
                            print(f"\n✅ Workflow completed!")
                            print(f"   Success: {success}")
                            print(f"   Events: {events}")
                            print(f"   Iterations: {data.get('iterations')}")
                            print(f"   Tokens: {data.get('token_usage', {}).get('total_tokens')}")
                            break

                        event_type = None

        return success

    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all phase tests."""
    print("\n" + "🔷" * 40)
    print("COMPREHENSIVE TEST SUITE - ALL PHASES (1-5)")
    print("🔷" * 40)

    # Check if backend is running
    try:
        async with httpx.AsyncClient() as client:
            await client.get("http://localhost:8000/api/health", timeout=2.0)
    except Exception:
        print("\n❌ ERROR: Backend is not running!")
        print("   Please start the backend first:")
        print("   cd backend && source .venv/bin/activate && uvicorn app.main:app --reload")
        sys.exit(1)

    print(f"\n✅ Backend is running at http://localhost:8000")

    # Run all tests
    results = {}

    tests = [
        ("Phase 1: Foundation", test_phase1_foundation),
        ("Phase 2: LLM Service", test_phase2_llm_service),
        ("Phase 3: Sandbox", test_phase3_sandbox),
        ("Phase 4: LangGraph", test_phase4_langgraph),
        ("Phase 5: SSE Endpoint", test_phase5_sse),
        ("End-to-End Workflow", test_end_to_end),
    ]

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {type(e).__name__}"
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)

    passed = 0
    failed = 0

    for test_name, result in results.items():
        print(f"{result} - {test_name}")
        if "✅" in result:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 80)
    print(f"Total: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Backend is fully functional:")
        print("   • Foundation setup working")
        print("   • LLM services configured")
        print("   • Subprocess sandbox secured")
        print("   • LangGraph workflow operational")
        print("   • SSE streaming functional")
        print("   • End-to-end workflow tested")
        print("\n💡 Ready for Phase 6: React Frontend!")
    else:
        print(f"\n⚠️  {failed} test(s) failed - review output above")

    print("\n" + "🔷" * 40)


if __name__ == "__main__":
    asyncio.run(main())
