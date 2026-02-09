# Synthesis.Pro Architecture (Final)

**Date:** 2026-02-07
**Status:** ✅ Production Ready

---

## Overview

Synthesis.Pro uses a **hybrid architecture** with two complementary systems:

1. **MCP Server** - The spine/nervous system for all operations
2. **WebSocket Server** - Silent background monitor for real-time error capture

Both systems work together, each serving their purpose.

---

## System 1: MCP Server (Primary)

**Purpose:** Main interface for AI-human interaction with Unity

**Location:** `Assets/Synthesis.Pro/Server/mcp/synthesis_mcp_server.py`

**Start Command:**
```bash
cd "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\mcp"
../../runtime/python/python.exe synthesis_mcp_server.py
```

**Tools (11 total):**

### RAG & Knowledge (Always Available)
1. `search_rag` - Hybrid BM25S + vector search
2. `get_error_patterns` - Historical error analysis
3. `get_console_context` - Recent Unity console errors

### Unity Project (Always Available)
4. `get_unity_project_info` - Unity version, packages
5. `list_scenes` - All scene files in project

### Unity Editor (Requires Unity + MCPForUnity Running)
6. `get_unity_state` - Play mode, active scene, selection
7. `get_scene_hierarchy` - GameObject tree with components
8. `get_gameobject` - Transform, components, hierarchy
9. `create_gameobject` - Creates actual GameObjects
10. `modify_gameobject` - Modifies transforms & properties
11. `execute_csharp` - Executes C# code in Editor

**Protocol:** JSON-RPC over stdio (MCP standard)

**Integration:** Works with Claude Code, Cursor, VS Code

---

## System 2: WebSocket Server (Background)

**Purpose:** Real-time error monitoring and automatic RAG capture

**Location:** `Assets/Synthesis.Pro/Server/core/websocket_server.py`

**Start Command:**
```bash
cd "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\core"
../runtime/python/python.exe websocket_server.py
```

**What It Does:**
- Receives console logs from Unity (via ConsoleWatcher)
- Processes with ConsoleMonitor (deep context capture)
- Performs intelligent pattern matching
- Stores to RAG private database
- Provides RAG onboarding (session previews, context detection)

**Protocol:** WebSocket (localhost:8765)

**Flow:**
```
Unity ConsoleWatcher → WebSocket → ConsoleMonitor → RAG Database
                                         ↓
                                  Pattern Matching
                                  Context Analysis
```

---

## How They Work Together

```
┌─────────────────────────────────────────────────────────────┐
│                     AI CLIENT                                │
│              (Claude Code / Cursor / VSCode)                 │
└───────────────────────────┬─────────────────────────────────┘
                            │ MCP Protocol
┌───────────────────────────▼─────────────────────────────────┐
│                   MCP SERVER (Primary)                       │
│                   synthesis_mcp_server.py                    │
│                                                              │
│  • RAG queries (instant)                                    │
│  • Unity operations (via bridge)                            │
│  • Project introspection                                    │
└───────┬──────────────────────────────────────┬──────────────┘
        │                                      │
        │ Direct Access                        │ HTTP Client
        ↓                                      ↓
┌──────────────────┐                  ┌──────────────────┐
│   RAG ENGINE     │                  │  UNITY BRIDGE    │
│  (BM25S + Vec)   │                  │   (aiohttp)      │
│                  │                  └────────┬─────────┘
│ Databases:       │                           │ HTTP
│ • synthesis_     │                           ↓
│   knowledge.db   │                  ┌──────────────────┐
│ • synthesis_     │                  │  MCPFORUNITY     │
│   private.db ◄───┼──────────────────┤  (localhost:6400)│
└──────────────────┘                  └────────┬─────────┘
        ▲                                      │
        │                                      ↓
        │                              ┌──────────────────┐
        │                              │  UNITY EDITOR    │
        │                              │                  │
        │                              │ • GameObjects    │
┌───────┴─────────┐                   │ • Scenes         │
│  WEBSOCKET      │                   │ • Components     │
│  SERVER         │                   └────────┬─────────┘
│  (Background)   │                            │
│                 │                            │ Observes
│ • Error capture │◄───────────────────────────┤
│ • Pattern match │                   ┌────────┴─────────┐
│ • RAG storage   │                   │ CONSOLEWATCHER   │
└─────────────────┘                   │ (Deep Context)   │
                                      └──────────────────┘
```

---

## Starting the Complete System

**1. Start WebSocket Server (Background Monitor)**
```bash
cd "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\core"
../runtime/python/python.exe websocket_server.py
```
*(Let this run in background - it just monitors silently)*

**2. Start Unity Editor**
- Open project in Unity
- ConsoleWatcher automatically connects to WebSocket
- Errors are captured automatically

**3. Start MCPForUnity Bridge (Optional - for Unity tools)**
- Window > MCP for Unity
- Click "Start Bridge"
- Enables MCP Unity Editor tools

**4. Start MCP Server (Main Interface)**
```bash
cd "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\mcp"
../../runtime/python/python.exe synthesis_mcp_server.py
```

**5. Connect from Claude Code/Cursor**
- MCP server registers automatically
- Use tools via AI interface

---

## What Works Without Unity Running

✅ RAG search (`search_rag`)
✅ Error patterns (`get_error_patterns`)
✅ Console history (`get_console_context`)
✅ Project info (`get_unity_project_info`)
✅ Scene listing (`list_scenes`)

## What Needs Unity Running

⚠️ Unity Editor state (`get_unity_state`)
⚠️ Scene hierarchy (`get_scene_hierarchy`)
⚠️ GameObject operations (get/create/modify)
⚠️ C# execution (`execute_csharp`)

## What Needs WebSocket Running

⚠️ Automatic error capture to RAG
⚠️ Real-time pattern matching
⚠️ Session preview on startup
⚠️ Context detection

---

## Key Files

**MCP System:**
- `Assets/Synthesis.Pro/Server/mcp/synthesis_mcp_server.py` - Main MCP server
- `Assets/Synthesis.Pro/Server/mcp/unity_bridge.py` - Unity HTTP client
- `Assets/Synthesis.Pro/Server/mcp/test_unity_bridge.py` - Connection test

**WebSocket System:**
- `Assets/Synthesis.Pro/Server/core/websocket_server.py` - WebSocket server
- `Assets/Synthesis.Pro/Server/context_systems/console_monitor.py` - Error processor
- `Assets/Synthesis.Pro/Server/rag_integration/rag_onboarding.py` - RAG integration

**RAG Engine:**
- `Assets/Synthesis.Pro/RAG/core/rag_engine_lite.py` - BM25S + embeddings
- `Assets/Synthesis.Pro/Server/database/synthesis_knowledge.db` - Public KB
- `Assets/Synthesis.Pro/Server/database/synthesis_private.db` - Private memory

**Unity Integration:**
- `Assets/Synthesis.Pro/Runtime/ConsoleWatcher.cs` - Deep error capture
- `Assets/Synthesis.Pro/MCPForUnity/` - Unity Editor bridge (3rd party)

---

## Performance

**MCP Server:**
- Startup: ~2 seconds (RAG initialization)
- Tool calls: 100-500ms typical
- Memory: ~250MB (with RAG loaded)

**WebSocket Server:**
- Startup: ~2 seconds (RAG initialization)
- Real-time monitoring: <10ms latency
- Memory: ~250MB (with RAG loaded)

**Total Footprint:** ~500MB when both running

---

## Design Philosophy

**MCP = The Spine**
- Central nervous system for all operations
- Request/response model
- Standard protocol integration
- Primary interface for AI

**WebSocket = The Sensor**
- Silent background observer
- Real-time monitoring
- Automatic capture
- Feeds data to spine (RAG)

**RAG = The Memory**
- Long-term knowledge storage
- Pattern recognition
- Historical context
- Shared by both systems

---

## Why Hybrid?

**Why Not MCP-Only?**
- MCP is request/response, not ideal for continuous monitoring
- Would lose real-time error capture
- Would need to poll for console logs (inefficient)

**Why Not WebSocket-Only?**
- WebSocket is custom protocol, not standard
- Harder to integrate with AI tools
- MCP is the industry standard for AI tool integration

**Why Both?**
- Each system does what it's best at
- MCP = operations and queries (AI interface)
- WebSocket = monitoring and capture (background)
- They complement, not compete
- RAG is shared memory between them

---

## Future Considerations

**When WebSocket Can Be Deprecated:**
- If ConsoleWatcher writes directly to RAG database
- If MCP adds streaming/subscription support
- If Unity tools can monitor console natively

**For Now:**
- Hybrid architecture is production-ready
- Both systems stable and tested
- Provides best of both worlds

---

**Built with partnership. Ready for production.** ✨
