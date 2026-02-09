"""
Quick test for synthesis_mcp_server.py
"""
import sys
from pathlib import Path

# Test imports
print("[TEST] Testing imports...")
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    print("[TEST] [OK] MCP SDK imported successfully")
except ImportError as e:
    print(f"[TEST] [ERROR] MCP SDK import failed: {e}")
    sys.exit(1)

# Test RAG import
print("[TEST] Testing RAG imports...")
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))

try:
    from rag_engine_lite import SynthesisRAG
    print("[TEST] [OK] RAG engine imported successfully")
except ImportError as e:
    print(f"[TEST] [WARNING] RAG engine import failed: {e}")
    print("[TEST] Server can run without RAG, but won't have RAG features")

# Test server instantiation
print("[TEST] Testing server instantiation...")
try:
    from synthesis_mcp_server import SynthesisMCPServer
    server = SynthesisMCPServer()
    print("[TEST] [OK] Server instantiated successfully")
except Exception as e:
    print(f"[TEST] [ERROR] Server instantiation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("[TEST] All tests passed!")
print("[TEST] Server is ready to run")
print("="*60)
print("\nTo run the server:")
print("  python synthesis_mcp_server.py")
print("\nOr register with MCPForUnity and connect via Claude Code/Cursor/etc.")
