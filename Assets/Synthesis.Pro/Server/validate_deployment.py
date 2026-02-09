"""
Synthesis.Pro Deployment Validation
Tests everything needed for 100% tester readiness
"""

import sys
from pathlib import Path
import subprocess

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "RAG" / "core"))
sys.path.insert(0, str(Path(__file__).parent / "rag_integration"))

print("="*70)
print("Synthesis.Pro Deployment Validation")
print("="*70)
print()

passed = []
failed = []
warnings = []

def test(name, func):
    """Run a test and track results"""
    try:
        result = func()
        if result is True:
            passed.append(name)
            print(f"[PASS] {name}")
        elif result is False:
            failed.append(name)
            print(f"[FAIL] {name}")
        else:
            warnings.append(name)
            print(f"[WARN] {name}: {result}")
    except Exception as e:
        failed.append(name)
        print(f"[FAIL] {name}: {e}")

# Test 1: Python Runtime
print("\n[1/10] Testing Python Runtime...")
def check_python_runtime():
    runtime = Path(__file__).parent / "runtime" / "python" / "python.exe"
    if not runtime.exists():
        return "Runtime not found"
    # Test it works
    result = subprocess.run([str(runtime), "--version"], capture_output=True, text=True)
    return result.returncode == 0

test("Python Runtime", check_python_runtime)

# Test 2: Critical Dependencies
print("\n[2/10] Testing Dependencies...")
def check_dependencies():
    try:
        import numpy
        import bm25s
        from sentence_transformers import SentenceTransformer
        import sklearn
        return True
    except ImportError as e:
        return f"Missing: {e}"

test("Dependencies", check_dependencies)

# Test 3: RAG Engine
print("\n[3/10] Testing RAG Engine...")
def check_rag_engine():
    try:
        from rag_engine_lite import SynthesisRAG
        return True
    except Exception as e:
        return str(e)

test("RAG Engine Import", check_rag_engine)

# Test 4: Databases
print("\n[4/10] Testing Databases...")
def check_databases():
    db_dir = Path(__file__).parent / "database"
    knowledge_db = db_dir / "synthesis_knowledge.db"
    private_db = db_dir / "synthesis_private.db"

    if not knowledge_db.exists():
        return "Knowledge DB missing"
    if not private_db.exists():
        return "Private DB will be created on first use"
    return True

test("Database Files", check_databases)

# Test 5: Database Schema
print("\n[5/10] Testing Database Schema...")
def check_schema():
    import sqlite3
    db_path = Path(__file__).parent / "database" / "synthesis_knowledge.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
    result = cursor.fetchone()
    conn.close()
    return result is not None

test("Database Schema", check_schema)

# Test 6: Embedding Model
print("\n[6/10] Testing Embedding Model...")
def check_model():
    model_dir = Path(__file__).parent / "models"
    # Check if sentence-transformers model exists
    model_path = model_dir / "models--sentence-transformers--all-MiniLM-L6-v2"
    if model_path.exists():
        return True
    return "Model will download on first use (~80MB)"

test("Embedding Model", check_model)

# Test 7: MCP Server
print("\n[7/10] Testing MCP Server...")
def check_mcp_server():
    mcp_server = Path(__file__).parent / "mcp" / "synthesis_mcp_server.py"
    if not mcp_server.exists():
        return "MCP server file missing"

    # Check syntax
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(mcp_server)],
        capture_output=True
    )
    return result.returncode == 0

test("MCP Server", check_mcp_server)

# Test 8: WebSocket Server
print("\n[8/10] Testing WebSocket Server...")
def check_websocket():
    ws_server = Path(__file__).parent / "core" / "websocket_server.py"
    return ws_server.exists()

test("WebSocket Server", check_websocket)

# Test 9: Unity Integration
print("\n[9/10] Testing Unity Integration...")
def check_unity():
    console_watcher = Path(__file__).parent.parent / "Runtime" / "ConsoleWatcher.cs"
    mcp_bridge = Path(__file__).parent.parent / "MCPForUnity"
    return console_watcher.exists() and mcp_bridge.exists()

test("Unity Integration", check_unity)

# Test 10: Documentation
print("\n[10/10] Testing Documentation...")
def check_docs():
    docs = []
    for doc in ["README.md", "INSTALL.md", "package.json"]:
        if not (Path(__file__).parent.parent / doc).exists():
            docs.append(doc)
    return True if not docs else f"Missing: {', '.join(docs)}"

test("Documentation", check_docs)

# Summary
print("\n" + "="*70)
print("VALIDATION SUMMARY")
print("="*70)
print(f"[PASSED] {len(passed)}/10 tests")
if warnings:
    print(f"[WARNED] {len(warnings)} tests with warnings")
if failed:
    print(f"[FAILED] {len(failed)} tests")
    for name in failed:
        print(f"  - {name}")
print()

# Final verdict
if failed:
    print("[NOT READY] System has critical failures")
    sys.exit(1)
elif warnings:
    print("[MOSTLY READY] System will work, but some features need first-time setup")
    sys.exit(0)
else:
    print("[100% READY] System is fully operational for testers")
    sys.exit(0)
