"""
Centralized path configuration for Synthesis.Pro
Single source of truth for all file and directory paths
"""

from pathlib import Path

class Paths:
    """All paths used by Synthesis.Pro - buttery and creamy, no hard-coding"""

    # Base directories
    SERVER = Path(__file__).parent.parent  # Assets/Synthesis.Pro/Server/
    CORE = SERVER / "core"
    DATABASE = SERVER / "database"
    RUNTIME = SERVER / "runtime"  # All runtime-generated files live here
    MODELS = SERVER / "models"
    CONTEXT_SYSTEMS = SERVER / "context_systems"
    RAG_INTEGRATION = SERVER / "rag_integration"

    # Runtime files (session-specific, current state)
    CONSOLE_ERRORS = RUNTIME / "console_errors_latest.json"
    AI_OBSERVATIONS = RUNTIME / "ai_observations.txt"
    SESSION_STATE = RUNTIME / "session_state.json"

    # Database files
    DB_PRIVATE = DATABASE / "synthesis_private.db"
    DB_KNOWLEDGE = DATABASE / "synthesis_knowledge.db"
    DB_PUBLIC = DATABASE / "synthesis_public.db"

    # Model files
    EMBEDDING_MODEL = MODELS / "models--sentence-transformers--all-MiniLM-L6-v2"

    @classmethod
    def ensure_runtime_exists(cls):
        """Ensure runtime directory exists - called on startup"""
        cls.RUNTIME.mkdir(parents=True, exist_ok=True)
        return cls.RUNTIME

    @classmethod
    def get_session_file(cls, filename: str) -> Path:
        """Get path to a session-specific file in runtime/"""
        return cls.RUNTIME / filename
