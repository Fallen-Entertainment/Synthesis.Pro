# Synthesis.Pro - AI Creative Partner for Unity

**Production-grade AI integration for Unity with hybrid RAG and MCP support**

[![Unity Version](https://img.shields.io/badge/Unity-2020.3%2B-blue)](https://unity.com/)
[![License](https://img.shields.io/badge/License-Commercial-green)](LICENSE.md)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange)](package.json)

## What's New in Synthesis.Pro

Synthesis.Pro is the production release of Synthesis AI, featuring significant upgrades:

### ⚡ Advanced RAG Engine
- **Hybrid Search**: Combines semantic vector search with full-text keyword search using Reciprocal Rank Fusion (RRF)
- **10-100x Faster**: Native vector search instead of Python loops
- **Flexible Embeddings**: Support for both local (sqlite-ai) and cloud (OpenAI) embeddings
- **Production-Ready**: Built on battle-tested sqlite-rag framework

### 🚀 Performance Improvements
- Native sqlite-vec integration for fast vector similarity search
- Query response time: ~370ms average
- Efficient memory usage with on-disk vector storage
- Optimized command processing pipeline

### 🛠️ Enhanced Features
- Modern Python RAG engine with hybrid search
- Improved error handling and logging
- Better Unity Editor integration
- Production-ready code architecture

---

## Quick Start

### Installation

1. **Import to Unity**
   ```
   Copy the Synthesis.Pro folder to your Assets directory
   Unity will auto-import all components
   ```

2. **Install Python Dependencies**
   ```bash
   cd Synthesis.Pro/RAG
   pip install -r requirements.txt
   ```

3. **Configure MCP** (Optional)
   - In Unity: `Window → MCP for Unity`
   - Click `Auto-Setup` and select your IDE
   - Done!

### Basic Usage

1. **Add SynLink to Scene**
   - Create empty GameObject
   - Add Component → Synthesis → SynLink
   - Bridge auto-initializes!

2. **Test the Connection**
   ```bash
   # Send a ping command
   echo '{"commands":[{"id":"test","type":"Ping"}]}' > unity_bridge_commands.json

   # Check results
   cat unity_bridge_results.json
   ```

3. **Use with AI**
   - Ask your AI assistant: "What's in the Unity scene?"
   - AI connects via MCP and responds
   - All interactions are logged to knowledge base

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Unity (C#)                      │
│  ┌───────────────────────────────────┐  │
│  │  SynLink (Bridge System)          │  │
│  │  - File-based commands            │  │
│  │  - WebSocket server (MCP)         │  │
│  │  - Scene manipulation             │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│         Python                          │
│  ┌───────────────────────────────────┐  │
│  │  Synthesis.Pro RAG Engine         │  │
│  │  - sqlite-rag (hybrid search)     │  │
│  │  - sqlite-vec (vector store)      │  │
│  │  - FTS5 (keyword search)          │  │
│  │  - RRF (result fusion)            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│         MCP Integration                 │
│  - VS Code / Cursor / Claude Code       │
│  - Direct AI communication              │
│  - Real-time scene queries              │
└─────────────────────────────────────────┘
```

---

## Core Features

### Unity Bridge (SynLink)
Real-time bidirectional communication between Unity and AI:

- **Scene Queries**: Get scene info, find GameObjects, inspect components
- **Object Manipulation**: Move, rotate, scale, enable/disable objects
- **Component Control**: Read and write any component property via reflection
- **Batch Operations**: Process multiple commands efficiently
- **Change Persistence**: Optionally save runtime changes to prefabs/scenes

### RAG Knowledge Base
Production-grade retrieval system for Unity documentation and project knowledge:

- **Hybrid Search**: Best of semantic and keyword search combined
- **Fast Queries**: Sub-second response times with native vector search
- **Flexible Models**: Use local or cloud embeddings
- **Auto-Learning**: AI builds knowledge from your interactions

### MCP Integration
Native Model Context Protocol support:

- **IDE Integration**: Works with VS Code, Cursor, Claude Code, Windsurf
- **Zero Config**: Auto-setup for popular IDEs
- **Real-Time**: WebSocket-based instant communication
- **Secure**: Localhost-only by default

---

## Available Commands

| Command | Description | Example Use Case |
|---------|-------------|------------------|
| **Ping** | Health check | Verify bridge is running |
| **GetSceneInfo** | Scene details | Understand scene structure |
| **FindGameObject** | Locate object | Find specific GameObjects |
| **GetComponent** | Component info | Inspect properties |
| **SetComponentValue** | Modify property | Change values in real-time |
| **SetPosition** | Move object | Position GameObjects |
| **SetActive** | Enable/disable | Toggle object visibility |
| **Log** | Send message | Debug output to console |

See [Documentation/COMMANDS.md](Documentation/COMMANDS.md) for complete API reference.

---

## RAG Engine Usage

### Python API

```python
from RAG import SynthesisRAG

# Initialize with local embeddings (free, fast)
rag = SynthesisRAG(
    database="knowledge.db",
    embedding_provider="local"
)

# Or use OpenAI embeddings (more accurate)
rag = SynthesisRAG(
    database="knowledge.db",
    embedding_provider="openai",
    api_key="your-api-key"
)

# Add documents
rag.add_documents([
    "path/to/unity/docs",
    "path/to/project/readme.md"
], recursive=True)

# Search with hybrid approach
results = rag.search(
    query="How do I instantiate a prefab?",
    top_k=5,
    search_type="hybrid"  # "hybrid", "vector", or "fts"
)

for result in results:
    print(f"Score: {result['score']}")
    print(f"Text: {result['text']}\n")
```

### CLI Usage

```bash
# Add content
sqlite-rag --database knowledge.db add /path/to/docs --recursive
sqlite-rag --database knowledge.db add-text "Unity uses C# for scripting"

# Search
sqlite-rag --database knowledge.db search "instantiate prefab" --limit 5

# Configure
sqlite-rag --database knowledge.db configure --model-path ./models
```

---

## Differences from Synthesis AI (Prototype)

| Feature | Synthesis AI | Synthesis.Pro |
|---------|--------------|---------------|
| RAG Search | Vanilla (Python loop) | Hybrid (sqlite-vec + FTS5) |
| Query Speed | Slow (loads all vectors) | Fast (~370ms) |
| Search Type | Semantic only | Hybrid (semantic + keyword) |
| Embeddings | OpenAI only | Local or OpenAI |
| Architecture | Prototype code | Production-ready |
| Performance | Basic | Optimized |
| Documentation | Good | Comprehensive |

---

## Configuration

### SynLink Component

```csharp
Enable Bridge: true          // Turn bridge on/off
Poll Interval: 0.5s          // Command check frequency
Commands File: "unity_bridge_commands.json"
Results File: "unity_bridge_results.json"
Logs File: "unity_bridge_logs.txt"
Change Log: (optional)       // For persistence
```

### RAG Engine

Edit `RAG/rag_engine.py` to configure:
- Embedding provider (local/openai)
- Model selection
- Database location
- Search parameters

---

## Performance

Benchmarks on standard hardware (4 vCPU, ~100MB memory):

- **RAG Query Response**: ~370ms average
- **Vector Search**: Native sqlite-vec (10-100x faster than Python)
- **Embedding Generation**: Local (fast) or OpenAI (accurate)
- **Command Processing**: One per frame (no hitches)

---

## Security

⚠️ **Synthesis.Pro gives AI control over your Unity editor**

**Best Practices:**
- ✅ Development only (not production builds)
- ✅ Localhost only (default)
- ✅ Review AI changes before committing
- ✅ Use version control

**Built-in Safety:**
- 🔒 Editor-only (`#if UNITY_EDITOR`)
- 🔒 Localhost binding
- 🔒 Undo support (Ctrl+Z works!)
- 🔒 Change logging

---

## Folder Structure

```
Synthesis.Pro/
├── Runtime/              # Unity C# runtime scripts
│   ├── SynLink.cs           # Core bridge system
│   ├── SynLinkExtended.cs   # Extended AI features
│   └── UIChangeLog.cs       # Persistence system
├── Editor/               # Unity Editor scripts
│   ├── SynLinkEditor.cs     # Editor integration
│   ├── SynLinkWebSocket.cs  # WebSocket server
│   └── ...
├── RAG/                  # Production RAG engine
│   ├── rag_engine.py        # Main RAG wrapper
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # RAG documentation
├── MCPForUnity/          # MCP integration package
├── Documentation/        # Complete guides
├── Server/               # Python server components
├── Tests/                # Unit tests
└── package.json          # Unity package metadata
```

---

## Documentation

Comprehensive guides in the `Documentation` folder:

- **QUICK_START.md** - Get up and running in 5 minutes
- **COMMANDS.md** - Complete command reference
- **RAG_GUIDE.md** - Using the hybrid RAG system
- **MCP_INTEGRATION.md** - MCP setup and usage
- **EXAMPLES.md** - Real-world use cases
- **API_REFERENCE.md** - Full API documentation
- **TROUBLESHOOTING.md** - Common issues and solutions

---

## License

**Commercial Asset License**

### ✅ You Can:
- Use in unlimited commercial & non-commercial projects
- Modify for your needs
- Sell games/apps you create with Synthesis.Pro
- Use in client work and freelance projects

### ❌ You Cannot:
- Resell Synthesis.Pro itself
- Share with non-purchasers
- Redistribute source code

See [LICENSE.md](LICENSE.md) for complete terms.

---

## Support

- **Documentation**: Check the `Documentation` folder
- **Issues**: Report bugs on GitHub
- **Email**: support@nightblade.dev

---

## Credits

Developed by **NightBlade Development**

Built with:
- [sqlite-rag](https://github.com/sqliteai/sqlite-rag) - Hybrid RAG framework
- [sqlite-vec](https://github.com/sqliteai/sqlite-vec) - Vector search
- [Unity](https://unity.com/) - Game engine
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol

---

**Synthesis.Pro** - Where human creativity and AI capability become one 🤖✨
