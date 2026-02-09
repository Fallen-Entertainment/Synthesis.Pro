"""
Test script for Synthesis.Pro MCP Server tools
Verifies each tool works correctly without needing MCP client
"""

import sys
import asyncio
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))

from mcp.types import TextContent

# Import server class
import importlib.util
spec = importlib.util.spec_from_file_location("synthesis_mcp_server", "synthesis_mcp_server.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SynthesisMCPServer = module.SynthesisMCPServer


async def test_tool(server, name, args):
    """Test a specific tool"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Arguments: {args}")
    print('='*60)

    try:
        # Get the handler method
        handler_name = f"handle_{name}" if not name.startswith("handle_") else name

        # Map tool names to handler methods
        tool_handlers = {
            "search_rag": server.handle_search_rag,
            "get_error_patterns": server.handle_error_patterns,
            "get_console_context": server.handle_console_context,
            "get_unity_project_info": server.handle_unity_project_info,
            "list_scenes": server.handle_list_scenes,
            "get_unity_state": server.handle_unity_state,
            "get_scene_hierarchy": server.handle_scene_hierarchy,
            "get_gameobject": server.handle_get_gameobject,
            "create_gameobject": server.handle_create_gameobject,
            "modify_gameobject": server.handle_modify_gameobject,
        }

        handler = tool_handlers.get(name)
        if not handler:
            print(f"[ERROR] No handler found for: {name}")
            return False

        # Call the handler
        result = await handler(args)

        # Print result
        if result:
            for item in result:
                if isinstance(item, TextContent):
                    print(item.text)
                else:
                    print(item)

        print(f"\n[OK] {name} completed successfully")
        return True

    except Exception as e:
        print(f"\n[ERROR] {name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("[TEST] Synthesis.Pro MCP Server - Tool Testing")
    print("="*60)

    # Create server instance
    print("[TEST] Creating server instance...")
    server = SynthesisMCPServer()

    # Initialize RAG
    print("[TEST] Initializing RAG engine...")
    await server.initialize_rag()

    results = {}

    # Test Unity Project Info tools (should work)
    print("\n\n" + "="*60)
    print("TESTING: Unity Project Introspection Tools")
    print("="*60)

    results["get_unity_project_info"] = await test_tool(
        server, "get_unity_project_info", {}
    )

    results["list_scenes"] = await test_tool(
        server, "list_scenes", {}
    )

    # Test RAG tools (should work if RAG is initialized)
    print("\n\n" + "="*60)
    print("TESTING: RAG Knowledge Tools")
    print("="*60)

    results["get_console_context"] = await test_tool(
        server, "get_console_context", {"limit": 3}
    )

    # Test Unity Editor tools (will show pending integration)
    print("\n\n" + "="*60)
    print("TESTING: Unity Editor Tools (Pending Integration)")
    print("="*60)

    results["get_unity_state"] = await test_tool(
        server, "get_unity_state", {}
    )

    results["get_scene_hierarchy"] = await test_tool(
        server, "get_scene_hierarchy", {"scene_name": "TestScene"}
    )

    results["get_gameobject"] = await test_tool(
        server, "get_gameobject", {"path": "Main Camera"}
    )

    results["create_gameobject"] = await test_tool(
        server, "create_gameobject", {
            "name": "TestCube",
            "type": "Cube",
            "position": {"x": 0, "y": 0, "z": 0}
        }
    )

    results["modify_gameobject"] = await test_tool(
        server, "modify_gameobject", {
            "path": "Main Camera",
            "operation": "set_position",
            "params": {"x": 1, "y": 2, "z": 3}
        }
    )

    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nResults: {passed}/{total} tests passed\n")

    for tool, success in results.items():
        status = "[OK]" if success else "[FAIL]"
        print(f"  {status} {tool}")

    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
