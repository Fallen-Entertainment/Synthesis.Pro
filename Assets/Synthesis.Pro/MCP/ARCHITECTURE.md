# Synthesis.Pro MCP Architecture

**Clean, Legal, Extensible**

## System Overview

```
┌─────────────────────────────────────────┐
│  IDE (Claude Code, Cursor, VSCode)      │
└────────────────┬────────────────────────┘
                 │ MCP Protocol
┌────────────────▼────────────────────────┐
│  MCPForUnity (MIT - Third Party)        │
│  - Server lifecycle management          │
│  - IDE integration & configuration      │
│  - Unity bridge (HTTP/StdIO)           │
│  - Port management                      │
└────────┬────────────────────────────────┘
         │ Manages Multiple MCP Servers
    ┌────▼────────────────────────┐
    │ Synthesis.Pro MCP Server    │
    │ (MIT - Our Implementation)  │
    │                             │
    │ Tools:                      │
    │  - search_rag()             │
    │  - get_error_patterns()     │
    │  - get_console_context()    │
    │  - execute_csharp()         │
    └────┬────────────────────────┘
         │ Integrates With
    ┌────▼─────────────────────────┐
    │ Synthesis.Pro Core Systems    │
    │                               │
    │ - RAG Engine (BM25S + vectors)│
    │ - ConsoleWatcher (Unity C#)   │
    │ - Error Pattern Matcher       │
    │ - Knowledge Databases         │
    └───────────────────────────────┘
```

## Component Responsibilities

### MCPForUnity (Third-Party, MIT)
**What it does:**
- Discovers and manages MCP servers
- Handles IDE client connections
- Provides Unity Editor bridge
- Manages ports and transport

**What we DON'T reimplement:**
- Server lifecycle
- IDE configurations
- Transport protocols
- Unity bridge communication

### Synthesis.Pro MCP Server (Ours, MIT)
**What it provides:**
- RAG search and knowledge access
- Error pattern analysis
- ConsoleWatcher integration
- Historical fix suggestions
- Learning from outcomes

**Future capabilities:**
- C# execution (via MCPForUnity bridge)
- Scene manipulation
- Asset workflows
- Automated testing

### Synthesis.Pro Core (Ours, MIT)
**Foundation systems:**
- RAG engine with dual databases
- ConsoleWatcher for deep Unity context
- Error pattern matcher
- Observation storage
- WebSocket server (existing)

## Data Flow

### Error Occurs in Unity
```
Unity Error
    ↓
ConsoleWatcher captures (full context)
    ↓
Stored in RAG (private database)
    ↓
Pattern matcher analyzes
    ↓
Available via MCP tools
    ↓
IDE client can query/fix
```

### AI Requests Fix
```
IDE (Claude Code)
    ↓
MCPForUnity routes request
    ↓
Synthesis.Pro MCP Server
    ↓
search_rag("similar error")
    ↓
Returns historical context + suggested fix
    ↓
execute_csharp(fix_code) via MCPForUnity
    ↓
Outcome stored in RAG for learning
```

## Extension Points

### Adding New Tools
```python
# In synthesis_mcp_server.py

@self.server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="your_new_tool",
            description="What it does",
            inputSchema={...}
        )
    ]

@self.server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "your_new_tool":
        return await self.handle_your_tool(arguments)
```

### Adding New Resources
Use MCPForUnity's resource system for read-only Unity state.
Use our MCP server tools for RAG/analysis operations.

## Port Management

**Managed by MCPForUnity:**
- MCP Server: 6500 (default)
- Unity Bridge: Auto-assigned
- No port conflicts - single management system

**Our WebSocket (existing):**
- Port 9766 (SynLink)
- Independent of MCP system
- Used for direct Unity communication

## Security Model

**Sandboxing:**
- MCPForUnity handles filesystem permissions
- Our server operates on its databases only
- No direct Unity Editor access (goes through MCPForUnity)

**Authentication:**
- Managed by MCPForUnity
- We inherit security model
- No separate auth needed

## Future Development

### Phase 1 (Current)
✅ MCP server structure
✅ RAG search tools
✅ Error pattern analysis
✅ Console context access
🔜 C# execution integration

### Phase 2 (Next)
- Scene manipulation tools
- Asset creation workflows
- Test runner integration
- Automated fix application

### Phase 3 (Future)
- Multi-project learning
- Community pattern sharing
- Advanced AI planning
- Proactive suggestions

## Why This Architecture

**Clean separation:**
- MCPForUnity: Framework (not our problem)
- Our MCP Server: Unique value (RAG, patterns, learning)
- Core Systems: Foundation (already working)

**Legal compliance:**
- All MIT licensed
- No NC restrictions
- Asset Store ready

**Extensibility:**
- Add tools without touching framework
- Integrate new AI capabilities easily
- Build on solid foundation

**No reinvention:**
- Use MCPForUnity's battle-tested transport
- Use their IDE integrations
- Focus on our unique value

---

**This is the architecture for the future.**

Built clean. Licensed right. Designed to grow.
