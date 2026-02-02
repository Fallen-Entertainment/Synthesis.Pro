# Synthesis.Pro WebSocket Server

Real-time communication bridge between Unity and AI systems.

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Installation

1. **Install Dependencies**

```bash
cd "d:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Server"
pip install -r requirements.txt
```

2. **Set Environment Variables**

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your_api_key_here"

# Windows CMD
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

3. **Run Server**

```bash
python websocket_server.py
```

You should see:

```
============================================================
🚀 Synthesis.Pro WebSocket Server
============================================================
[12:34:56] INFO - 🚀 Starting Synthesis.Pro WebSocket Server
[12:34:56] INFO - 📡 Listening on ws://localhost:8765
[12:34:56] INFO - 🔒 Security: localhost-only binding
[12:34:56] INFO - Initializing RAG engine...
[12:34:56] INFO - ✅ RAG engine initialized (dual database mode)
[12:34:56] INFO - ✅ Server ready! Waiting for Unity connections...
```

## 📡 Architecture

```
Unity Editor (C#) <--WebSocket--> Python Server <--> RAG Engine
                                        |
                                        +--> OpenAI API
                                        +--> Knowledge Base (SQLite)
```

### Communication Flow

1. **Unity → Server**: Sends commands as JSON via WebSocket
2. **Server**: Routes commands to appropriate handlers
3. **Server → Unity**: Returns results as JSON via WebSocket

## 🔧 Configuration

### Server Settings

Edit `websocket_server.py` to change:

```python
server = SynthesisWebSocketServer(
    host="localhost",  # Bind address (localhost for security)
    port=8765          # WebSocket port
)
```

### Unity Settings

In Unity, configure the `SynthesisWebSocketClient` component:

- **Server Host**: localhost
- **Server Port**: 8765
- **Auto Connect**: ✓ (recommended)
- **Auto Reconnect**: ✓ (recommended)
- **Reconnect Delay**: 5 seconds

## 📝 Available Commands

### Built-in Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `ping` | Health check | None |
| `get_capabilities` | Server features | None |
| `get_stats` | Server statistics | None |
| `chat` | AI conversation | `message`, `context` |
| `search_knowledge` | Search RAG | `query`, `top_k`, `private` |

### Example: Ping

**Request:**
```json
{
  "id": "ping_123",
  "type": "ping",
  "parameters": {}
}
```

**Response:**
```json
{
  "commandId": "ping_123",
  "success": true,
  "message": "Pong! Server is alive!",
  "data": {
    "server_time": "2026-02-02T12:34:56",
    "active_connections": 1,
    "uptime_seconds": 123.45
  },
  "timestamp": "2026-02-02T12:34:56"
}
```

## 🔒 Security

- Localhost-only binding (no external access)
- API keys from environment variables only
- Input validation on all commands
- No sensitive data in logs

## 📊 Monitoring

Get server statistics with `get_stats` command. Server logs show:
- Connection events
- Command processing
- Errors and warnings

## 🧪 Testing

Start server, then in Unity:
1. Add `SynthesisWebSocketClient` to GameObject
2. Press Play
3. Check Console for "Connected to Synthesis.Pro server!"

## 🔧 Troubleshooting

**Connection Refused**: Ensure server is running and port 8765 is free

**RAG Not Available**: Install dependencies with `pip install -r requirements.txt`

**API Key Missing**: Set `OPENAI_API_KEY` environment variable

---

**Status**: ✅ Phase 2 - Communication Layer
