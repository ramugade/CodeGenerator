"""Test Phase 5 - FastAPI SSE Endpoint."""
import asyncio
import httpx
from app.agents.state import TestCase


async def test_sse_streaming():
    """Test SSE streaming endpoint with real workflow."""
    print("\n" + "=" * 80)
    print("PHASE 5 TEST: SSE Streaming Endpoint")
    print("=" * 80)

    # Prepare request
    request_data = {
        "query": "Write a function named main(x, y) that multiplies two numbers",
        "llm_provider": "openai",
        "user_provided_tests": [
            {
                "description": "Multiply two positive numbers",
                "inputs": {"x": 4, "y": 5},
                "expected_output": 20,
            }
        ],
        "max_iterations": 2,
    }

    print(f"\n📋 Request:")
    print(f"   Query: {request_data['query']}")
    print(f"   Provider: {request_data['llm_provider']}")
    print(f"   User-provided tests: {len(request_data['user_provided_tests'])}")

    print(f"\n🔄 Streaming events from POST /api/generate...")

    events_received = []

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "http://localhost:8000/api/generate",
                json=request_data,
            ) as response:
                if response.status_code != 200:
                    print(f"\n❌ HTTP {response.status_code}")
                    print(await response.aread())
                    return False

                print(f"\n✅ Connection established (HTTP {response.status_code})")
                print(f"\n{'='*80}")
                print("STREAMING EVENTS:")
                print(f"{'='*80}\n")

                event_type = None
                async for line in response.aiter_lines():
                    line = line.strip()

                    if line.startswith("event:"):
                        event_type = line.split("event:", 1)[1].strip()

                    elif line.startswith("data:"):
                        if event_type:
                            data = line.split("data:", 1)[1].strip()
                            events_received.append((event_type, data))

                            # Print event
                            print(f"📡 Event: {event_type}")

                            # Parse and show key info
                            import json
                            try:
                                event_data = json.loads(data)

                                if event_type == "planning":
                                    print(f"   Understanding: {event_data.get('understanding', '')[:80]}...")
                                    print(f"   Approach: {event_data.get('approach', '')[:80]}...")

                                elif event_type == "test_inference_skipped":
                                    print(f"   {event_data.get('message')}")
                                    print(f"   Test count: {event_data.get('test_count')}")

                                elif event_type == "code_generated":
                                    version = event_data.get('version')
                                    iteration = event_data.get('iteration')
                                    code_preview = event_data.get('code', '')[:100]
                                    print(f"   Version: {version} (iteration {iteration})")
                                    print(f"   Code: {code_preview}...")

                                elif event_type == "execution":
                                    success = event_data.get('success')
                                    exec_time = event_data.get('execution_time')
                                    print(f"   Success: {success}")
                                    print(f"   Time: {exec_time:.3f}s")
                                    if event_data.get('output'):
                                        print(f"   Output: {event_data.get('output')[:50]}")

                                elif event_type == "validation":
                                    passed = event_data.get('passed')
                                    total = event_data.get('total')
                                    print(f"   Tests: {passed}/{total} passed")

                                elif event_type == "complete":
                                    success = event_data.get('success')
                                    iterations = event_data.get('iterations')
                                    tokens = event_data.get('token_usage', {}).get('total_tokens', 0)
                                    cost = event_data.get('token_usage', {}).get('estimated_cost_usd', 0)
                                    print(f"   Success: {success}")
                                    print(f"   Iterations: {iterations}")
                                    print(f"   Tokens: {tokens}")
                                    print(f"   Cost: ${cost:.4f}")

                                elif event_type == "error":
                                    print(f"   ❌ Error: {event_data.get('error')}")

                            except json.JSONDecodeError:
                                print(f"   Data (raw): {data[:100]}...")

                            print()  # Blank line between events
                            event_type = None

        print(f"{'='*80}")
        print(f"STREAM COMPLETE")
        print(f"{'='*80}\n")

        # Verify events
        print(f"📊 Events received: {len(events_received)}")
        event_types = [et for et, _ in events_received]
        print(f"   Event types: {event_types}")

        # Check for required events
        required_events = ["planning", "code_generated", "execution", "validation", "complete"]
        missing = [e for e in required_events if e not in event_types]

        if missing:
            print(f"\n⚠️  Missing expected events: {missing}")
        else:
            print(f"\n✅ All required events received!")

        # Check for completion
        if "complete" in event_types:
            print(f"✅ Workflow completed successfully!")
            return True
        else:
            print(f"❌ Workflow did not complete")
            return False

    except Exception as e:
        print(f"\n❌ Test failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_health_endpoint():
    """Test health endpoint."""
    print("\n" + "=" * 80)
    print("TEST: Health Endpoint")
    print("=" * 80)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/health")

            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Health check successful")
                print(f"   Status: {data.get('status')}")
                print(f"   App: {data.get('app')}")
                print(f"   Version: {data.get('version')}")
                return True
            else:
                print(f"\n❌ HTTP {response.status_code}")
                return False

    except Exception as e:
        print(f"\n❌ Health check failed: {type(e).__name__}: {str(e)}")
        return False


async def main():
    """Run Phase 5 tests."""
    print("\n" + "🔷" * 40)
    print("PHASE 5 - FASTAPI SSE ENDPOINT TESTS")
    print("🔷" * 40)

    print(f"\n⚠️  Make sure the backend is running:")
    print(f"   cd backend && source .venv/bin/activate && uvicorn app.main:app --reload")
    print(f"\n   Press Ctrl+C to cancel, or wait 5 seconds to continue...")

    await asyncio.sleep(5)

    # Run tests
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("SSE Streaming", test_sse_streaming),
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

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, result in results.items():
        print(f"{result} - {test_name}")

    print("\n" + "🔷" * 40)


if __name__ == "__main__":
    asyncio.run(main())
