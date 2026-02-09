# Synthesis.MCP Installation Guide

## Prerequisites

- Node.js 18+ (for MCP servers)
- Unity 2022.3+ (Synthesis.Pro requirement)
- Synthesis.Pro already installed and working

**Note:** Python 3.11 is bundled with Synthesis.Pro at `PythonRuntime/python/` - no separate installation needed!

## Step 1: Install Node.js Dependencies

The MCP servers will be installed on-demand via npx, but you can pre-install them:

```bash
# Optional: Pre-install globally
npm install -g @arodoid/unity-mcp
npm install -g @coplaydev/unity-mcp
```

## Step 2: Configure Authentication

1. Generate a secure secret key:
```bash
# On Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

2. Add to `MCP/Config/mcp_config.json`:
```json
{
  "servers": {
    "arodoid": {
      "env": {
        "MCP_AUTH_SECRET_KEY": "your-generated-key-here"
      }
    }
  }
}
```

## Step 3: Install Python Bridge Dependencies

```bash
cd Assets/Synthesis.Pro/MCP/Bridge
pip install -r requirements.txt
```

Required packages:
- websockets
- asyncio
- json5

## Step 4: Test MCP Server Connection

```bash
# Start the Arodoid MCP server manually
npx -y @arodoid/unity-mcp

# In another terminal, test the bridge
cd Assets/Synthesis.Pro/MCP/Bridge
python test_mcp_connection.py
```

## Step 5: Integrate with Synthesis.Pro

The MCP bridge will automatically connect to the existing websocket_server.py.

Start the integrated server:
```bash
cd Assets/Synthesis.Pro/Server/core
../../../../PythonRuntime/python/python.exe websocket_server.py
```

The MCP execution layer will now be available alongside RAG and ConsoleWatcher.

## Verification

Test the complete flow:

1. Open Unity Editor with Synthesis.Pro
2. Trigger a test error
3. Check RAG context captures it
4. Send a C# execution command via MCP
5. Verify execution in Unity

## Troubleshooting

**MCP server won't start:**
- Check Node.js version: `node --version` (need 18+)
- Verify npx is available: `npx --version`
- Check MCP_AUTH_SECRET_KEY is set

**Bridge connection fails:**
- Ensure websocket_server.py is running
- Check port 8765 is not blocked
- Verify paths in mcp_config.json are correct

**Unity execution fails:**
- Unity Editor must be open
- Check Unity console for MCP connection status
- Verify C# syntax in execution commands

## Security Notes

- Keep MCP_AUTH_SECRET_KEY private (add to .gitignore)
- Review filesystem sandbox settings before production use
- Monitor execution logs for suspicious activity
- Follow principle of least privilege for allowed_paths

## Next Steps

See [USAGE.md](USAGE.md) for examples and [ARCHITECTURE.md](ARCHITECTURE.md) for technical details.
