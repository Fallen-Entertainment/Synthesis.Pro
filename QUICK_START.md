# Synthesis.Pro - Quick Start Guide

Get up and running in 5 minutes.

---

## What You Get

- **AI collaboration system** for Unity development
- **Deep error capture** with full context (13x more efficient debugging)
- **Long-term memory** that remembers everything across sessions
- **Real Unity operations** via AI (create, modify, query GameObjects)
- **Pattern matching** that learns from past errors

---

## Quick Start (5 Steps)

### 1. Start Background Monitor (Optional but Recommended)

Open a terminal and run:

```bash
cd "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\core"
../../../../PythonRuntime/python/python.exe websocket_server.py
```

**What this does:** Captures Unity errors automatically with full context and stores them in RAG memory.

**Leave it running** in the background. It's silent and just watches.

---

### 2. Open Unity

Start Unity Editor with your project. ConsoleWatcher will automatically connect to the background monitor.

---

### 3. Start MCP Server (Main Interface)

Open another terminal and run:

```bash
cd "d:\Unity Projects\Synthesis.Pro\Assets\Synthesis.Pro\Server\mcp"
../../../../PythonRuntime/python/python.exe synthesis_mcp_server.py
```

**Leave this running** - it's your AI interface.

---

### 4. (Optional) Enable Unity Editor Tools

If you want AI to interact with Unity directly:

1. In Unity: Window > MCP for Unity
2. Click "Start Bridge"
3. Verify "Running" status

---

### 5. Connect from Claude Code / Cursor

The MCP server should be automatically available in your AI client. Try asking:

- "Search RAG for error patterns"
- "What's the Unity project info?"
- "List all scenes"
- "Get current Unity Editor state" (needs Unity + bridge running)

---

## What Works Right Now

**Always Available:**
- ✅ RAG search (knowledge base queries)
- ✅ Error pattern analysis (historical context)
- ✅ Console history search
- ✅ Unity project info
- ✅ Scene file listing

**Needs Unity Running:**
- ✅ Real-time error capture (with WebSocket)
- ⚠️ Unity Editor state queries (needs MCPForUnity bridge)
- ⚠️ GameObject operations (needs MCPForUnity bridge)
- ⚠️ C# code execution (needs MCPForUnity bridge)

---

## Common Workflows

### Debug an Error

**Before Synthesis.Pro:**
```
AI: "What error?"
You: "NullReference"
AI: "Where?"
You: "PlayerController.cs line 42"
AI: "What scene?"
You: "MainGame"
AI: "What GameObject?"
... 10 more questions ...
```

**With Synthesis.Pro:**
```
AI: *checks RAG*
    "I see it - NullReference in PlayerController.cs:42
     on Player GameObject in MainGame scene.
     This is the 3rd time. Last time you fixed it
     by adding a null check in Start().
     Want me to apply the same fix?"
```

### Check What You Worked On Last

```
You: "What was I working on last session?"
AI: *uses search_rag tool*
    "Last session you were debugging the inventory system.
     You fixed an IndexOutOfRange in InventoryManager
     and were testing the save/load functionality."
```

### Create a GameObject from AI

```
You: "Create a cube at position (0, 5, 0)"
AI: *uses create_gameobject tool*
    "Created cube 'TestCube' at (0, 5, 0)"
```

---

## Troubleshooting

### "WebSocket not connected"
- Make sure websocket_server.py is running
- Check Unity ConsoleWatcher is enabled
- Restart Unity if needed

### "Unity bridge not available"
- Open Window > MCP for Unity
- Click "Start Bridge"
- Verify localhost:6400 is accessible

### "RAG engine not available"
- Check databases exist: `Assets/Synthesis.Pro/Server/database/*.db`
- Check Python runtime: `PythonRuntime/python/python.exe`
- Re-run first-time setup if needed

### "MCP tools not showing up"
- Verify synthesis_mcp_server.py is running
- Check Claude Code / Cursor MCP configuration
- Restart AI client if needed

---

## Tips

1. **Let the WebSocket run** - It's capturing errors silently in the background
2. **Trust the RAG** - It remembers everything, just ask
3. **Use Unity bridge** - The real power is in actual Unity operations
4. **Review error patterns** - Use `get_error_patterns` to see what keeps breaking
5. **Test with simple commands first** - "Get project info" before "Create 100 GameObjects"

---

## Next Steps

Once you're comfortable:
- Explore advanced MCP tools
- Review captured error patterns
- Try GameObject manipulation
- Execute custom C# code
- Build your own Unity workflows

---

## Architecture Details

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete system documentation.

---

**Built for effective collaboration. Enjoy!** 🚀
