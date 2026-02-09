# Synthesis.MCP

**MCP Integration Layer for Synthesis.Pro**

Synthesis.MCP completes the feedback loop by adding execution capabilities to Synthesis.Pro's observation and context systems.

## Architecture

```
Synthesis.Pro (Observation) → Synthesis.MCP (Execution) → Unity (Results)
     ↑                                                           ↓
     └─────────────────── Feedback Loop ───────────────────────┘
```

**Complete Flow:**
1. Error occurs → ConsoleWatcher captures full context
2. RAG stores context with patterns and history
3. AI analyzes via context
4. **Synthesis.MCP executes the fix** via C# command
5. Verifies success, iterates if needed

## Components

### Servers/
Unity MCP server integrations:
- **Arodoid/** - Real-time C# execution in Unity Editor
- **CoplayDev/** - Structured asset workflow automation

### Bridge/
Integration layer connecting MCP servers to Synthesis.Pro's Python backend and Unity components.

### Config/
MCP server configurations, authentication, and permissions.

## Integration Points

**With Synthesis.Pro:**
- Shares RAG database for context awareness
- Receives error context from ConsoleWatcher
- Sends execution results back to RAG for learning

**With Unity:**
- Direct C# code execution (Arodoid)
- Asset creation and manipulation (CoplayDev)
- Scene state verification

## Philosophy

Following Synthesis.Pro's core principles:
- **Enable, don't force** - Execution when helpful, not mandatory
- **AI effectiveness first** - Clear, structured command interfaces
- **Collaborative model** - AI autonomy with human oversight
- **Zero friction** - Seamless integration with existing workflows

## Quick Start

1. Install Unity MCP servers (see Documentation/)
2. Configure MCP_AUTH_SECRET_KEY in Config/
3. Start MCP bridge: `python Bridge/mcp_bridge.py`
4. Test execution via websocket_server.py integration

See Documentation/ for detailed setup and usage guides.
