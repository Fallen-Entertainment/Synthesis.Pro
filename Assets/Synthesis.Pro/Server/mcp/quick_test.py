"""
Quick functional test of MCP server tools
"""
import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))

async def test_tools():
    """Test MCP server tools"""
    print("="*60)
    print("SYNTHESIS MCP SERVER - FUNCTIONAL TEST")
    print("="*60)
    print()

    # Import server
    try:
        from synthesis_mcp_server import SynthesisMCPServer
        print("[TEST] [OK] Server module imported")
    except Exception as e:
        print(f"[TEST] [ERROR] Import failed: {e}")
        return

    # Create server instance
    try:
        server = SynthesisMCPServer()
        print("[TEST] [OK] Server instantiated")
    except Exception as e:
        print(f"[TEST] [ERROR] Instantiation failed: {e}")
        return

    # Initialize RAG
    print()
    print("Testing RAG initialization...")
    try:
        await server.initialize_rag()
        if server.rag:
            print("[TEST] [OK] RAG initialized")
        else:
            print("[TEST] [WARNING] RAG not available")
    except Exception as e:
        print(f"[TEST] [ERROR] RAG init failed: {e}")

    # Test Unity project info
    print()
    print("Testing get_unity_project_info...")
    try:
        result = await server.handle_unity_project_info({})
        print("[TEST] [OK] Unity project info retrieved")
        print(result[0].text[:200] + "...")
    except Exception as e:
        print(f"[TEST] [ERROR] Project info failed: {e}")

    # Test list scenes
    print()
    print("Testing list_scenes...")
    try:
        result = await server.handle_list_scenes({})
        print("[TEST] [OK] Scenes listed")
        print(result[0].text[:200] + "...")
    except Exception as e:
        print(f"[TEST] [ERROR] List scenes failed: {e}")

    # Test RAG search (if available)
    if server.rag:
        print()
        print("Testing search_rag...")
        try:
            result = await server.handle_search_rag({
                "query": "Unity",
                "scope": "both",
                "top_k": 3
            })
            print("[TEST] [OK] RAG search executed")
            print(result[0].text[:200] + "...")
        except Exception as e:
            print(f"[TEST] [ERROR] RAG search failed: {e}")

    print()
    print("="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_tools())
