# Synthesis.Pro RAG Engine

Modern RAG system powered by sqlite-rag with hybrid search capabilities.

## Features

- **Hybrid Search**: Combines semantic vector search with full-text keyword search
- **Local or Cloud Embeddings**: Support for both local (sqlite-ai) and OpenAI embeddings
- **Fast**: ~370ms average query response
- **Lightweight**: SQLite-based, no heavy dependencies
- **Production-Ready**: Built on proven sqlite-rag framework

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from rag_engine import SynthesisRAG

# Initialize
rag = SynthesisRAG(database="knowledge.db", embedding_provider="local")

# Add documents
rag.add_documents(["path/to/docs"])

# Search
results = rag.search("your query", top_k=5)
```

## Architecture

- **sqlite-rag**: Core RAG framework with hybrid search
- **sqlite-vec**: Fast vector similarity search
- **FTS5**: Full-text keyword search
- **RRF**: Reciprocal Rank Fusion for result merging
