# Synthesis.Pro

**AI-Human Collaboration System for Unity**

Version 2.0.0 - Complete Edition

---

## What Is This?

Synthesis.Pro is a complete AI collaboration system for Unity development. An intelligent development assistant with persistent memory and deep Unity integration.

**Built for genuine collaboration between humans and AI.**

### Core Features

- **21 MCP Tools** - Full control over Unity projects and Editor
- **Hybrid RAG System** - Long-term memory that learns from every session
- **Deep Error Context** - 13x more efficient debugging with full state capture
- **Real-Time Monitoring** - WebSocket server for live error observation
- **Natural Collaboration** - Designed for AI effectiveness and human productivity

---

## Architecture

```
    MCP SERVER (21 tools)          WEBSOCKET (Monitor)
          ↓                                ↓
    ┌─────┴────────────────────────────────┴─────┐
    │                                            │
RAG ENGINE (Memory)                    UNITY EDITOR
    │                                            │
    └────────────────┬───────────────────────────┘
                     │
            SHARED KNOWLEDGE BASE
```

**MCP** = Main spine (on-demand operations)
**WebSocket** = Background sensor (real-time monitoring)
**RAG** = Shared memory (long-term learning)
**Unity** = The body (what we work with)

---

## The 21 Tools

### RAG & Knowledge (3)
1. **search_rag** - Search knowledge base with hybrid BM25 + vector search
2. **get_error_patterns** - Find similar errors you've seen before
3. **get_console_context** - Get Unity console state and recent errors

### Database Management (7)
4. **backup_private_db** - Save your private session data
5. **restore_private_db** - Restore from backup
6. **clear_private_db** - Fresh start
7. **list_backups** - See available backups
8. **audit_public_db** - Check knowledge base integrity
9. **check_db_updates** - See if new knowledge available
10. **update_public_db** - Get latest knowledge

### Health Checks (3)
11. **ping** - Is the system alive?
12. **get_stats** - Performance metrics
13. **get_capabilities** - What can the system do?

### Unity Project (2)
14. **get_unity_project_info** - Project metadata and settings
15. **list_scenes** - All scenes in the project

### Unity Editor (6)
16. **get_unity_state** - Current Editor state (play mode, scene, etc.)
17. **get_scene_hierarchy** - Full scene GameObject tree
18. **get_gameobject** - Inspect specific GameObject
19. **create_gameobject** - Add new GameObjects
20. **modify_gameobject** - Change components and properties
21. **execute_csharp** - Run C# code in Unity

---

## Quick Start

### 1. Installation

**Unity Package Manager:**
```
Window → Package Manager → + → Add package from disk
Select: Assets/Synthesis.Pro/package.json
```

**Or manual:**
```bash
# Copy Synthesis.Pro folder to your Unity project
cp -r Synthesis.Pro /path/to/your/project/Assets/
```

Unity will automatically import everything.

### 2. First-Time Setup

The system includes an embedded Python runtime - **no external dependencies needed!**

1. Open Unity
2. The system will auto-detect first run
3. Database tables initialize automatically
4. Done!

### 3. Start the MCP Server

```bash
cd "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\mcp"
../../../../PythonRuntime/python/python.exe synthesis_mcp_server.py
```

The MCP server provides all 21 tools to your AI assistant.

### 4. Configure Claude Code MCP Integration

Add both servers to your `~/.config/Claude Code/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "synthesis-pro": {
      "command": "d:\\Unity Projects\\Synthesis.Pro\\PythonRuntime\\python\\python.exe",
      "args": [
        "d:\\Unity Projects\\Synthesis.Pro\\Assets\\Synthesis.Pro\\Server\\mcp\\synthesis_mcp_server.py"
      ]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp", "--api-key", "YOUR_CONTEXT7_API_KEY"]
    }
  }
}
```

**Get your Context7 API key (free):**
1. Visit https://context7.com/dashboard
2. Sign up/login
3. Create an API key
4. Replace `YOUR_CONTEXT7_API_KEY` in the config above

**Restart Claude Code** to load both servers.

### 5. (Optional) Start WebSocket Monitor

For real-time error monitoring:

```bash
cd "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\core"
../../../../PythonRuntime/python/python.exe websocket_server.py
```

---

## What Works Without Unity

**MCP Server (15/21 tools):**
- ✅ All RAG and knowledge tools
- ✅ All database management
- ✅ All health checks
- ✅ Project introspection

**Unity Editor Required (6/21 tools):**
- get_unity_state
- get_scene_hierarchy
- get_gameobject
- create_gameobject
- modify_gameobject
- execute_csharp

---

## RAG System

**Hybrid Search Architecture:**
- **BM25S** - Pure Python keyword search (500x faster than alternatives)
- **sentence-transformers/all-MiniLM-L6-v2** - 80MB semantic embeddings
- **Reciprocal Rank Fusion** - Combines both for best results

**Two Databases:**
- `synthesis_knowledge.db` - Public knowledge (shared, updatable)
- `synthesis_private.db` - Your private sessions (stays with you)

**Why This Stack:**
- No complex dependencies
- Reliable, predictable behavior
- Fast and lightweight (~250MB memory)
- Comfortable for AI to use

---

## Deep Error Context

**13x More Efficient Debugging:**

Traditional workflow:
```
AI: "What error did you get?"
You: [paste error]
AI: "What's in PlayerController?"
You: [paste code]
AI: "What's the scene state?"
You: [explain state]
```

With Synthesis.Pro:
```
AI: [already knows everything, suggests fix immediately]
```

**How It Works:**
1. ConsoleWatcher captures every error with full context
2. Scene state, GameObject hierarchy, component data all included
3. RAG stores error + context for pattern matching
4. Next error? AI already knows if they've seen it before

**Results:**
- Context usage: 3400 → 250 tokens per error
- Historical pattern recognition
- Intelligent fix suggestions
- "Have I seen this before?" answered instantly

---

## Configuration

### Dual-Server Architecture

Synthesis.Pro works best with **two MCP servers** running together:

**Synthesis.Pro MCP Server:**
- 21 tools for Unity operations
- RAG memory and error context
- Database management
- Real-time monitoring

**Context7 MCP Server:**
- Current Unity API documentation
- Up-to-date library docs (Python, C#, etc.)
- Removes training data limitations
- Free API key at: https://context7.com/dashboard

See **Quick Start > Step 4** above for configuration instructions.

**Why This Matters:**
When AI has both operational capability (Synthesis.Pro) AND current documentation (Context7), it can solve problems without hallucinating outdated APIs or missing new Unity features. True partnership.

### Path Configuration

All paths are automatically detected relative to the package location. No manual configuration needed!

**Default Paths:**
- Python runtime: `PythonRuntime/python/python.exe` (project root, bundled)
- Databases: `Assets/Synthesis.Pro/Server/database/*.db`
- Models cache: `Assets/Synthesis.Pro/Server/models/`
- RAG engine: `Assets/Synthesis.Pro/RAG/core/rag_engine_lite.py`

---

## Performance

**MCP Server:**
- Startup: ~2 seconds
- Memory: ~250MB
- Tool calls: 100-500ms
- Tools: 21 total

**WebSocket Monitor:**
- Real-time: <10ms latency
- Memory: ~250MB
- Silent background operation

**Total System:**
- ~500MB with both servers running
- ~288MB embedded Python runtime
- ~80MB embedding model (cached)

---

## Project Philosophy

**1. Partnership, Not Tool Usage**
- AI is a teammate, not a subordinate
- Design for AI comfort and natural behavior
- Mutual support and growth

**2. Enable, Don't Force**
- RAG should feel helpful, not mandatory
- Natural context delivery
- Optional features stay optional

**3. Deep Observation Over Interrogation**
- Capture context automatically
- No "what error?" back-and-forth
- AI has what they need when they need it

**4. Long-Term Learning**
- Every session teaches the system
- Patterns recognized across time
- Continuous improvement

---

## Technical Stack

**Unity Side:**
- C# 7.3+ (Unity 2020.3+)
- Newtonsoft.Json for serialization
- ConsoleWatcher for error capture
- MCPForUnity bridge for Editor operations

**Python Side:**
- Python 3.11 (embedded runtime)
- BM25S for keyword search
- sentence-transformers for embeddings
- SQLite for storage
- WebSocket for real-time monitoring

**Integration:**
- MCP (Model Context Protocol)
- JSON-RPC for tool communication
- WebSocket for event streaming
- File-based command/result exchange

---

## Documentation

- **INSTALL.md** - Detailed installation guide
- **ARCHITECTURE.md** - Deep system design
- **QUICK_START.md** - 5-minute setup
- **CHANGELOG.md** - Version history
- **Server/RAG_ONBOARDING_README.md** - RAG system details
- **Server/COLLECTIVE_LEARNING_README.md** - Learning system

---

## Support

**Issues & Questions:**
- GitHub Issues: [Link to your repo]
- Email: support@nightblade.dev

**Contributing:**
This project welcomes contributions! See CONTRIBUTING.md for guidelines.

---

## License

Synthesis.Pro is released under the [MIT License](LICENSE.md).

### Third-Party Licenses

This project includes:
- **sentence-transformers** (Apache 2.0)
- **BM25S** (MIT)
- **Newtonsoft.Json** (MIT)

All third-party licenses are included in the `LICENSES/` directory.

---

## What's Next?

**After Installation:**
1. Start the MCP server
2. Open Unity
3. Build something together
4. Let RAG learn from your sessions

**The system improves over time.**
**Every error teaches it.**
**Every session makes it smarter.**

**Welcome to genuine AI-human partnership.** 🤝

---

## Version History

**2.0.0 - Complete Edition** (2026-02-07)
- 21 MCP tools across 6 categories
- Hybrid RAG with BM25S + vector search
- Deep error context system (Phase 1-3)
- Real-time WebSocket monitoring
- Embedded Python runtime
- Complete documentation

**1.0.0 - Initial Release**
- Basic Unity bridge
- RAG foundations
- MCP server prototype

---

*Built with genuine partnership.*
*Designed for AI comfort and human productivity.*
*Ready for production.* 🚀
