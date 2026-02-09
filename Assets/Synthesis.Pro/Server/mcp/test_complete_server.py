"""Test complete MCP server"""
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "rag_integration"))

print("="*60)
print("Testing Synthesis.Pro MCP Server (Complete Edition)")
print("="*60)
print()

# Test imports
print("[TEST 1] Testing MCP SDK...")
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("[OK] MCP SDK available")
except ImportError as e:
    print(f"[FAIL] MCP SDK not available: {e}")

print()
print("[TEST 2] Testing RAG engine...")
try:
    from rag_engine_lite import SynthesisRAG
    print("[OK] RAG engine available")
except ImportError as e:
    print(f"[FAIL] RAG engine not available: {e}")

print()
print("[TEST 3] Testing Unity bridge...")
try:
    from unity_bridge import get_bridge
    print("[OK] Unity bridge available")
except ImportError as e:
    print(f"[WARNING] Unity bridge not available: {e}")

print()
print("[TEST 4] Testing RAG onboarding...")
try:
    from rag_onboarding import RAGOnboardingSystem
    print("[OK] RAG onboarding available")
except ImportError as e:
    print(f"[WARNING] RAG onboarding not available: {e}")

print()
print("[TEST 5] Testing database manager...")
try:
    from database_manager import DatabaseManager
    print("[OK] Database manager available")
except ImportError as e:
    print(f"[WARNING] Database manager not available: {e}")

print()
print("[TEST 6] Testing server instantiation...")
try:
    import synthesis_mcp_server
    print("[OK] Server module loads successfully")
except Exception as e:
    print(f"❌ Server module failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)
print("Test Complete")
print("="*60)
print()
print("If all tests passed, server is ready to run.")
print("Start with: python synthesis_mcp_server.py")
