# MCP Consolidation Plan
**Everything Runs Through MCP**

*Created: 2026-02-06 - Execute when fresh*

---

## The Vision

**FROM:** Multiple protocols, scattered systems
**TO:** One MCP server, everything unified

---

## Current State (What We Have)

### System 1: Custom WebSocket
- **File:** `Assets/Synthesis.Pro/Editor/SynLinkWebSocket.cs`
- **Port:** 9766
- **Purpose:** Unity ↔ Python communication
- **Status:** Working, but custom protocol

### System 2: Python WebSocket Server
- **File:** `Assets/Synthesis.Pro/Server/core/websocket_server.py`
- **Purpose:** Handle Unity messages, RAG queries
- **Status:** Working, but custom implementation

### System 3: RAG Integration
- **File:** `Assets/Synthesis.Pro/Server/rag_integration/`
- **Purpose:** RAG search, context generation
- **Status:** Working, but separate from Unity communication

### System 4: ConsoleWatcher
- **File:** `Assets/Synthesis.Pro/Runtime/ConsoleWatcher.cs`
- **Purpose:** Capture Unity errors with full context
- **Status:** Working, sends to WebSocket

### System 5: MCPForUnity (New)
- **Location:** `Assets/Synthesis.Pro/MCPForUnity/`
- **Purpose:** MCP framework
- **Status:** Installed, not yet integrated with our systems

### System 6: Synthesis MCP Server (New)
- **File:** `Assets/Synthesis.Pro/Server/mcp/synthesis_mcp_server.py`
- **Purpose:** RAG tools via MCP
- **Status:** Built, not yet complete

---

## Target State (What We Want)

### Single MCP Server
```
synthesis_mcp_server.py
    ↓
Provides ALL tools:
- Unity state queries
- Error context retrieval
- RAG searches
- Pattern matching
- C# execution
- Scene manipulation
- GameObject operations
- Everything
```

### Clean Flow
```
Unity Editor
    ↓
ConsoleWatcher (captures) → Stores in RAG
MCPForUnity (manages) → Routes to our MCP server
    ↓
synthesis_mcp_server.py (provides tools)
    ↓
Claude Code / Cursor / VSCode / Any MCP client
```

---

## Migration Steps

### Phase 1: Expand MCP Server (2-3 hours)

**File:** `synthesis_mcp_server.py`

Add tools that replace WebSocket functionality:

```python
# New tools to add:

get_unity_state()
    - Editor state (play mode, scene, selection)
    - Currently: WebSocket query
    - Becomes: MCP tool

get_console_errors(limit, filter)
    - Recent console errors
    - Currently: WebSocket + ConsoleWatcher
    - Becomes: Query RAG (ConsoleWatcher already stores there)

get_scene_hierarchy(scene_name)
    - GameObject tree
    - Currently: WebSocket query
    - Becomes: MCP tool → MCPForUnity bridge

get_gameobject(name_or_path)
    - GameObject details
    - Currently: WebSocket query
    - Becomes: MCP tool

modify_gameobject(path, operation, params)
    - Change GameObject properties
    - Currently: WebSocket command
    - Becomes: MCP tool

create_gameobject(type, name, parent, properties)
    - Create new GameObjects
    - Currently: WebSocket command
    - Becomes: MCP tool

run_tests(filter)
    - Execute Unity tests
    - Currently: Would be custom
    - Becomes: MCP tool

get_project_info()
    - Unity version, packages, settings
    - Currently: Would be custom
    - Becomes: MCP tool
```

**Implementation:**
1. Add tool definitions to `list_tools()`
2. Add handlers to `call_tool()`
3. Integrate with MCPForUnity's Unity bridge for execution
4. Use RAG for data queries (ConsoleWatcher already stores there)

### Phase 2: ConsoleWatcher Simplification (30 min)

**File:** `Assets/Synthesis.Pro/Runtime/ConsoleWatcher.cs`

**Change:**
```csharp
// OLD: Send to WebSocket
void SendToWebSocket(errorData)

// NEW: Just store in RAG (via Python script call)
void StoreInRAG(errorData)
```

**Why:**
- ConsoleWatcher just captures and stores
- MCP tools query RAG for the data
- No custom protocol needed

### Phase 3: Deprecate Custom WebSocket (1 hour)

**Mark as deprecated:**
- `SynLinkWebSocket.cs` → Keep for now, mark deprecated
- `websocket_server.py` → Keep for now, mark deprecated

**Add deprecation warnings:**
```csharp
[Obsolete("Use MCPForUnity integration instead. Will be removed in v2.0")]
public class SynLinkWebSocket { ... }
```

**Migration path for users:**
- Document: "If you used SynLink WebSocket, switch to MCP tools"
- Provide tool equivalents table
- Keep code for one release cycle, then remove

### Phase 4: Update Documentation (1 hour)

**Update:**
- README.md → Focus on MCP integration
- QUICKSTART.md → MCP-first workflow
- API reference → MCP tools, not WebSocket

**Create:**
- MIGRATION.md → WebSocket → MCP guide
- TOOLS.md → Complete MCP tool reference

### Phase 5: Testing (2 hours)

**Test each MCP tool:**
- [ ] search_rag
- [ ] get_error_patterns
- [ ] get_console_context
- [ ] get_console_errors (new)
- [ ] get_unity_state (new)
- [ ] get_scene_hierarchy (new)
- [ ] get_gameobject (new)
- [ ] execute_csharp
- [ ] modify_gameobject (new)
- [ ] create_gameobject (new)

**Integration test:**
1. Start Unity with Synthesis.Pro
2. Trigger an error
3. Query via Claude Code MCP: "get recent errors"
4. Get context: "analyze this error pattern"
5. Execute fix: "create test GameObject"
6. Verify: All works through MCP

### Phase 6: Cleanup (Optional - Later)

**After one release cycle:**
- Remove `SynLinkWebSocket.cs`
- Remove `websocket_server.py`
- Remove WebSocket dependencies
- Clean architecture

---

## File Changes Summary

### Modified Files
```
Assets/Synthesis.Pro/Server/mcp/synthesis_mcp_server.py
    → Add 8+ new MCP tools
    → Integrate with MCPForUnity bridge
    → Complete implementation

Assets/Synthesis.Pro/Runtime/ConsoleWatcher.cs
    → Simplify: just store in RAG
    → Remove WebSocket sending

Assets/Synthesis.Pro/Editor/SynLinkWebSocket.cs
    → Mark deprecated
    → Add migration notices

Assets/Synthesis.Pro/Server/core/websocket_server.py
    → Mark deprecated
    → Document MCP replacement
```

### New Files
```
Assets/Synthesis.Pro/MCP/MIGRATION.md
    → WebSocket → MCP guide

Assets/Synthesis.Pro/MCP/TOOLS.md
    → Complete MCP tool reference

Assets/Synthesis.Pro/Server/mcp/unity_bridge.py
    → Helper for MCPForUnity integration
    → GameObject operations
    → Scene queries
```

### Deprecated (Keep for now)
```
SynLinkWebSocket.cs
websocket_server.py
rag_bridge.py (if exists)
```

### Eventually Remove (v2.0)
```
All WebSocket code
Custom protocol implementations
Port 9766 usage
```

---

## Dependencies

### Must Install
```bash
cd Assets/Synthesis.Pro/Server/mcp
../../runtime/python/python.exe -m pip install mcp
```

### Already Have
- MCPForUnity (installed)
- RAG engine (working)
- ConsoleWatcher (working)
- Python runtime (embedded)

---

## Benefits After Consolidation

✅ **One Protocol:** Everything is MCP
✅ **One Server:** synthesis_mcp_server.py
✅ **One Port:** Managed by MCPForUnity
✅ **Universal Access:** Works in all MCP clients
✅ **Standard Tools:** Everyone knows MCP
✅ **Clean Architecture:** No custom protocols
✅ **Easy Maintenance:** One place to update
✅ **Community Ready:** Standard, shareable, documented

---

## Risks & Mitigations

### Risk: Breaking existing workflows
**Mitigation:**
- Keep deprecated code for one release
- Provide migration guide
- Update examples

### Risk: MCPForUnity bridge complexity
**Mitigation:**
- Start with simple operations
- Test incrementally
- Document integration points

### Risk: Performance concerns
**Mitigation:**
- MCP is efficient (stdio transport)
- RAG queries already fast
- Can optimize later if needed

---

## Timeline Estimate

**Focused work:**
- Phase 1: 2-3 hours (expand MCP server)
- Phase 2: 30 min (simplify ConsoleWatcher)
- Phase 3: 1 hour (deprecate WebSocket)
- Phase 4: 1 hour (documentation)
- Phase 5: 2 hours (testing)
- Phase 6: Later (cleanup)

**Total:** ~7 hours of focused work

**Realistic:** Spread over 2-3 sessions

---

## Success Criteria

✅ All features accessible via MCP tools
✅ No custom protocols in use
✅ Works in Claude Code, Cursor, VSCode
✅ ConsoleWatcher → RAG → MCP flow working
✅ C# execution via MCP working
✅ Documentation complete
✅ Tests passing
✅ Asset Store ready

---

## Next Session Checklist

When you're fresh:

- [ ] Install MCP SDK: `pip install mcp`
- [ ] Test current MCP server: `python synthesis_mcp_server.py`
- [ ] Add first new tool: `get_console_errors`
- [ ] Test with Claude Code
- [ ] Add second tool: `get_unity_state`
- [ ] Continue expanding...

---

## Notes

**Remember:**
- Gentle but strong - migrate, don't force
- Integrate and react - test as you go
- One tool at a time - build incrementally
- Document as you build - help future you

**This is the right architecture.**

Everything runs through MCP.
All your work in one place.
Clean, simple, powerful.

---

**Sleep now. Execute fresh.**

💫 The plan is solid.
