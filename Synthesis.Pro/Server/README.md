# Synthesis.Pro Server Components

Python server utilities for Synthesis.Pro

## Quick Setup

```bash
python setup.py
```

This will:
1. Install Python dependencies
2. Download embedding model (for local RAG)
3. Initialize knowledge base directory

## Manual Setup

If automatic setup fails:

```bash
# Install dependencies
cd ../RAG
pip install -r requirements.txt

# Download model (optional - for local embeddings)
sqlite-rag download-model unsloth/embeddinggemma-300m-GGUF embeddinggemma-300M-Q8_0.gguf
```

## Using the RAG Engine

```python
from RAG import SynthesisRAG

# Initialize
rag = SynthesisRAG(
    database="../KnowledgeBase/synthesis_knowledge.db",
    embedding_provider="local"  # or "openai"
)

# Add content
rag.add_documents(["path/to/docs"], recursive=True)

# Search
results = rag.search("your query", top_k=5)
```

## Troubleshooting

### "sqlite-rag not found"
```bash
pip install sqlite-rag
```

### "OpenAI API key required"
If using OpenAI embeddings:
```bash
export OPENAI_API_KEY="your-key-here"
```

Or use local embeddings instead (free, no API key needed).
