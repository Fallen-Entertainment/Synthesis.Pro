# Synthesis.Pro MCP Server - Registration Guide

## Quick Test (Verify Server Works)

Test the server directly to ensure it's working:

```bash
cd "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\mcp"
../../runtime/python/python.exe synthesis_mcp_server.py
```

The server should start and show:
```
[Synthesis MCP] Starting Synthesis.Pro MCP Server...
[Synthesis MCP] Providing: RAG search, error patterns, Unity state, GameObject operations
[Synthesis MCP] [OK] RAG engine initialized
```

Press Ctrl+C to stop when done testing.

---

## Register with Claude Code

### Method 1: Using Claude CLI (Recommended)

If you have the `claude` CLI installed:

```bash
claude mcp add synthesis-pro \
  --command "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\runtime\python\python.exe" \
  --args "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\mcp\synthesis_mcp_server.py"
```

### Method 2: Manual Configuration

Add to your MCP client configuration file:

**Claude Code** (`~/.claude/mcp_servers.json`):
```json
{
  "synthesis-pro": {
    "command": "d:\\Unity Projects\\Synthesis.Pro\\Assets\\Synthesis.Pro\\Server\\runtime\\python\\python.exe",
    "args": [
      "d:\\Unity Projects\\Synthesis.Pro\\Assets\\Synthesis.Pro\\Server\\mcp\\synthesis_mcp_server.py"
    ],
    "env": {}
  }
}
```

**VS Code/Cursor** (`settings.json`):
```json
{
  "mcp.servers": {
    "synthesis-pro": {
      "command": "d:\\Unity Projects\\Synthesis.Pro\\Assets\\Synthesis.Pro\\Server\\runtime\\python\\python.exe",
      "args": [
        "d:\\Unity Projects\\Synthesis.Pro\\Assets\\Synthesis.Pro\\Server\\mcp\\synthesis_mcp_server.py"
      ]
    }
  }
}
```

---

## Available Tools

Once registered, you'll have access to these tools:

### RAG & Knowledge (Fully Functional)
- **search_rag**: Query knowledge base with hybrid BM25S + vector search
- **get_error_patterns**: Analyze historical error patterns
- **get_console_context**: Get recent Unity console errors with full context

### Unity Project Info (Fully Functional)
- **get_unity_project_info**: Get Unity version, installed packages
- **list_scenes**: List all scene files in the project

### Unity Editor Operations (Pending MCPForUnity Integration)
- **get_unity_state**: Get play mode, active scene, selection
- **get_scene_hierarchy**: Get GameObject tree for a scene
- **get_gameobject**: Get detailed GameObject information
- **create_gameobject**: Create new GameObjects
- **modify_gameobject**: Modify GameObject properties
- **execute_csharp**: Execute C# code in Unity Editor

---

## Testing Individual Tools

Use the test script to verify specific tools:

```bash
cd "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\mcp"
../../runtime/python/python.exe test_mcp_tools.py
```

This will test all implemented tools and show their outputs.

---

## Troubleshooting

### Server won't start
- Verify Python runtime exists at expected path
- Check that MCP SDK is installed: `pip list | grep mcp`
- Look for errors in the console output

### RAG tools return "RAG engine not available"
- Verify databases exist in `../database/`
- Check that RAG dependencies are installed (bm25s, sentence-transformers)
- Look for RAG initialization errors in console

### Can't connect from IDE
- Verify the server path in your MCP client config
- Check that the Python runtime path is absolute (not relative)
- Restart your IDE after configuration changes

---

## Next Steps

After registration:
1. Restart your IDE/MCP client
2. Check that "synthesis-pro" appears in available MCP servers
3. Try a simple query: "search_rag for error patterns"
4. Verify the RAG system returns results

---

**The server is ready to use!**

Working features: RAG search, error analysis, project introspection
Pending features: Unity Editor operations (require MCPForUnity bridge)
