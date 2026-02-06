# Synthesis.Pro Installation Guide

Quick guide to get Synthesis.Pro up and running.

## Prerequisites

- Unity 2020.3 or newer
- Python 3.8+ (for RAG engine)
- (Optional) OpenAI API key (if using cloud embeddings)

## Installation Steps

### 1. Unity Setup

```bash
# Copy Synthesis.Pro to your Unity project
cp -r Synthesis.Pro /path/to/your/unity/project/Assets/
```

Unity will automatically import all components.

### 2. Python Setup

```bash
cd Assets/Synthesis.Pro/Server
python setup.py
```

This installs:
- sqlite-rag (hybrid RAG framework)
- sqlite-vec (vector search)
- openai (for cloud embeddings)

### 3. Unity Configuration

1. Open your Unity project
2. Create a new GameObject in your scene
3. Add Component → Synthesis → SynLink
4. Bridge initializes automatically!

Check Unity Console for:
```
[SynLink] 🌉 Unity Bridge Initialized!
```

### 4. Test the System

Create a test command file in your project root:

```json
{
  "commands": [
    {
      "id": "test-1",
      "type": "Ping"
    }
  ]
}
```

Save as `unity_bridge_commands.json`

Check `unity_bridge_results.json` for the response!

## Optional: MCP Integration

For IDE integration (VS Code, Cursor, Claude Code):

1. In Unity: `Window → MCP for Unity`
2. Click `Auto-Setup`
3. Select your IDE
4. Done!

## Embedding Models

### Option A: Local Embeddings (Recommended)

Free, fast, no API key needed:

```bash
sqlite-rag download-model unsloth/embeddinggemma-300m-GGUF embeddinggemma-300M-Q8_0.gguf
```

### Option B: OpenAI Embeddings

More accurate, requires API key:

```bash
export OPENAI_API_KEY="your-key-here"
```

Or set in Python:
```python
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"
```

## Verify Installation

```python
# Test RAG engine
from RAG import SynthesisRAG

rag = SynthesisRAG(embedding_provider="local")
rag.add_text("Synthesis.Pro is working!")
results = rag.search("working", top_k=1)
print(results)  # Should return your test text
```

## Troubleshooting

### "Module not found: RAG"
```bash
cd Synthesis.Pro/RAG
pip install -r requirements.txt
```

### "sqlite-rag command not found"
```bash
pip install sqlite-rag
```

### "Bridge not responding"
- Check Unity Console for errors
- Verify SynLink component has "Enable Bridge" checked
- Ensure command file is in project root (not Assets folder)

### "Changes not persisting"
- Create UIChangeLog asset: Right-click → Create → Synthesis → UI Change Log
- Assign to SynLink component
- Changes will now save when exiting Play mode

## Next Steps

- Read [README.md](README.md) for feature overview
- Check [Documentation/](Documentation/) for detailed guides
- Try the example commands
- Integrate with your AI assistant!

## Support

- Documentation: `Documentation/` folder
- Issues: GitHub Issues
- Email: support@nightblade.dev

---

**Ready to create? Let's build something amazing! 🚀**
