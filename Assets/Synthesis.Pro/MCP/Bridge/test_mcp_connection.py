"""
Quick test script for MCP connection
"""

import asyncio
import sys
from pathlib import Path

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp_bridge import MCPBridge


async def test_connection():
    """Test MCP server connection"""
    print("=" * 60)
    print("Testing Synthesis.MCP Connection")
    print("=" * 60)
    print()

    bridge = MCPBridge()

    try:
        # Start the bridge
        await bridge.start()

        # Wait a moment for server startup
        await asyncio.sleep(2)

        # Test simple C# execution
        test_code = """
Debug.Log("Hello from Synthesis.MCP!");
Debug.Log("C# execution is working!");
"""

        print("\n[TEST] Attempting C# execution...")
        result = await bridge.execute_csharp(test_code, context={'test': True})

        print(f"\n[TEST] Result: {result}")

        if result.get('success'):
            print("\n✅ MCP connection successful!")
        else:
            print(f"\n❌ Execution failed: {result.get('error')}")

        # Keep server running for manual testing
        print("\n[TEST] MCP server is running")
        print("[TEST] Press Ctrl+C to stop")
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        print("\n[TEST] Stopping...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bridge.stop()
        print("\n[TEST] Test complete")


if __name__ == "__main__":
    asyncio.run(test_connection())
