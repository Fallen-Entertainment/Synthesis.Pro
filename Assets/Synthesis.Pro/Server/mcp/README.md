# Synthesis.Pro MCP Server

**MIT Licensed** - Asset Store Compatible

## What This Is

An MCP (Model Context Protocol) server that exposes Synthesis.Pro's AI partnership features:

- **RAG Search**: Query knowledge base for context and patterns
- **Error Patterns**: Historical error analysis and fix suggestions
- **Console Context**: Deep Unity error state from ConsoleWatcher
- **C# Execution**: Execute code in Unity Editor (via MCPForUnity)

## Architecture

```
Claude Code / Cursor / VSCode
        ↓
   MCPForUnity (manages servers)
        ↓
   Synthesis.Pro MCP Server (this!)
        ↓
   RAG + ConsoleWatcher + Unity
```

## Installation

```bash
# Install MCP SDK
cd Assets/Synthesis.Pro/Server/mcp
../../runtime/python/python.exe -m pip install -r requirements.txt
```

## Configuration

MCPForUnity will auto-discover and manage this server.

**Manual config** (for Claude Code, Cursor, etc.):

```json
{
  "mcpServers": {
    "synthesis-pro": {
      "command": "python",
      "args": ["path/to/synthesis_mcp_server.py"]
    }
  }
}
```

## Tools Provided

### search_rag
Search Synthesis.Pro knowledge base for context, patterns, and historical fixes.

**Parameters:**
- `query` (string, required): Search query
- `scope` (string): "public", "private", or "both" (default: "both")
- `top_k` (integer): Number of results (default: 5)

### get_error_patterns
Get error patterns and historical fixes.

**Parameters:**
- `error_signature` (string, required): Error signature to search for

### get_console_context
Get recent Unity console errors captured by ConsoleWatcher.

**Parameters:**
- `error_type` (string): Filter by error type (optional)
- `limit` (integer): Number of errors to retrieve (default: 5)

### execute_csharp
Execute C# code in Unity Editor (integration with MCPForUnity pending).

**Parameters:**
- `code` (string, required): C# code to execute
- `context` (object): Optional RAG/ConsoleWatcher context

## Development

**Test the server:**
```bash
cd Assets/Synthesis.Pro/Server/mcp
../../runtime/python/python.exe synthesis_mcp_server.py
```

**Add new tools:**
1. Add tool definition to `list_tools()`
2. Implement handler in `call_tool()`
3. Add implementation method

## Integration with MCPForUnity

This server is designed to be managed by MCPForUnity:
1. MCPForUnity handles server lifecycle
2. MCPForUnity manages IDE connections
3. MCPForUnity provides Unity bridge for C# execution

Our server focuses on:
- RAG context and knowledge
- Error pattern matching
- ConsoleWatcher integration
- Learning from outcomes

## License

MIT License - fully compatible with Unity Asset Store.

See main project LICENSE for full terms.

## Architecture Philosophy

Following Synthesis.Pro's core principles:

- **Enable, don't force**: Tools available when helpful, not mandatory
- **AI comfort first**: Clear structured responses, rich context
- **Partnership model**: Both human and AI can act
- **Zero friction**: Seamless integration with existing workflows

---

**Part of the Synthesis.Pro ecosystem**
Building AI partnership for Unity development.
