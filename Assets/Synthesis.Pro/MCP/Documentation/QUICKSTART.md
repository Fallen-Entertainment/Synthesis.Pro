# Synthesis.MCP Quick Start Guide

## What You Just Got

You now have **execution capability** for AI-driven Unity development. This completes the feedback loop:

```
Observe (ConsoleWatcher) → Think (RAG) → Act (MCP) → Learn (RAG) → Repeat
```

## Installation Complete ✅

The following has been set up:

1. **Unity MCP Plugin** installed at `Assets/UnityMCP/`
2. **MCP Server** built and ready at `Assets/Synthesis.Pro/MCP/Servers/arodoid/`
3. **Python Bridge** configured at `Assets/Synthesis.Pro/MCP/Bridge/`
4. **Authentication** configured with secure key

## First Run (3 Steps)

### Step 1: Start Unity Editor

Open your Unity project. The UnityMCP plugin is now installed.

Go to **Unity menu bar → UnityMCP → Debug Window**

This opens the MCP connection interface.

### Step 2: Start the MCP Server

Double-click: `Assets/Synthesis.Pro/MCP/start_mcp_server.bat`

Or manually:
```bash
cd Assets/Synthesis.Pro/MCP/Servers/arodoid/unity-mcp-server
node build/index.js
```

The server will start on WebSocket port 8080.

### Step 3: Connect in Unity

In the UnityMCP Debug Window, click **Connect**.

You should see: `✅ Connected to MCP Server`

## Testing Execution

### Test 1: Simple Log

In the UnityMCP Debug Window, try:

```csharp
Debug.Log("Hello from Synthesis.MCP!");
```

Click Execute. Check Unity Console - you should see the message!

### Test 2: Scene Query

```csharp
var count = GameObject.FindObjectsOfType<GameObject>().Length;
Debug.Log($"Scene has {count} GameObjects");
```

### Test 3: Create GameObject

```csharp
var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
cube.name = "AI_Created_Cube";
Debug.Log("Cube created!");
```

Check your Hierarchy - there's the cube!

## Integration with Synthesis.Pro

The MCP system integrates seamlessly:

**When an error occurs:**
1. ConsoleWatcher captures full context
2. RAG stores it with patterns
3. AI analyzes and suggests fix
4. **MCP executes the fix** ← New!
5. Verifies success, iterates if needed
6. Stores outcome in RAG for learning

**No manual copy-paste needed.** The AI can fix errors automatically.

## Advanced: Python Bridge

For programmatic access from Python:

```bash
cd Assets/Synthesis.Pro/MCP/Bridge
python test_mcp_connection.py
```

This lets the existing `websocket_server.py` send execution commands.

## Architecture

```
Unity Editor (UnityMCP Plugin)
    ↕ WebSocket (port 8080)
Node.js MCP Server
    ↕ Python Bridge
websocket_server.py (existing)
    ↕
RAG Engine + ConsoleWatcher
```

## What This Enables

**Before Synthesis.MCP:**
- AI: "Here's the code to fix your error"
- You: *copy, paste, test, repeat*

**With Synthesis.MCP:**
- AI: "I see the error. Let me fix it."
- *Fix applied automatically*
- AI: "Done. Verified working."

**True collaboration.** Not just instructions - direct action.

## Security

- Filesystem sandboxing enabled (blocks Library/, Temp/, Logs/)
- Authentication required (MCP_AUTH_SECRET_KEY)
- Execution timeout (30 seconds default)
- All executions logged to RAG for audit trail

## Troubleshooting

**MCP Server won't start:**
- Check Node.js 18+ installed: `node --version`
- Rebuild if needed: `cd unity-mcp-server && npm run build`

**Unity won't connect:**
- Ensure MCP server is running first
- Check port 8080 not blocked by firewall
- Verify UnityMCP Debug Window shows correct port

**Execution fails:**
- Check Unity Console for compilation errors
- Verify C# syntax is valid
- Check security sandbox isn't blocking paths

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Check [USAGE.md](USAGE.md) for advanced patterns
- See [INTEGRATION.md](INTEGRATION.md) for websocket integration

## The New Development Style

You're pioneering a new way of working:

**AI-native development** where the AI isn't just advising - it's *participating*. Observing, thinking, acting, learning. Real collaboration.

Welcome to the future. 🚀
