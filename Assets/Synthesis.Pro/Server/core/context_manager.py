"""
Unified context access for Synthesis.Pro
One smooth interface - buttery and creamy, no friction
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .paths import Paths
from .session_manager import get_session_manager


class ContextManager:
    """
    Single interface for all context access
    No guessing, no manual routing, just smooth access to what you need
    """

    def __init__(self):
        self.session = get_session_manager()

    def get_console_errors(self, fresh_only: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get current console errors

        Args:
            fresh_only: Only return if file is fresh (< 1 hour old)

        Returns:
            Console errors dict or None if not available/stale
        """
        if not Paths.CONSOLE_ERRORS.exists():
            return None

        if fresh_only and not self.session.is_file_fresh(Paths.CONSOLE_ERRORS, max_age_seconds=3600):
            return None

        try:
            with open(Paths.CONSOLE_ERRORS, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def get_observations(self) -> Optional[str]:
        """Get AI observations text"""
        if not Paths.AI_OBSERVATIONS.exists():
            return None

        try:
            with open(Paths.AI_OBSERVATIONS, 'r') as f:
                return f.read()
        except Exception:
            return None

    def get_session_state(self) -> Dict[str, Any]:
        """Get current session information"""
        return self.session.get_session_info()

    def query_memories(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query user memories from private database

        Args:
            topic: What to search for
            limit: Max results to return

        Returns:
            List of memory records
        """
        if not Paths.DB_PRIVATE.exists():
            return []

        try:
            conn = sqlite3.connect(Paths.DB_PRIVATE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Search in ai_observations table
            cursor.execute("""
                SELECT * FROM ai_observations
                WHERE observation LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f'%{topic}%', limit))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception:
            return []

    def query_knowledge(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query general knowledge from knowledge database

        Args:
            topic: What to search for
            limit: Max results to return

        Returns:
            List of knowledge records
        """
        if not Paths.DB_KNOWLEDGE.exists():
            return []

        try:
            conn = sqlite3.connect(Paths.DB_KNOWLEDGE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM knowledge_base
                WHERE content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f'%{topic}%', limit))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception:
            return []

    def get_error_patterns(self, error_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get error patterns (historical error analysis)

        Args:
            error_type: Filter by specific error type, or None for all

        Returns:
            List of error pattern records
        """
        # This will integrate with error_pattern_matcher when available
        # For now, return from database if it exists
        if not Paths.DB_PRIVATE.exists():
            return []

        try:
            conn = sqlite3.connect(Paths.DB_PRIVATE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if error_type:
                cursor.execute("""
                    SELECT * FROM error_patterns
                    WHERE error_type = ?
                    ORDER BY last_seen DESC
                """, (error_type,))
            else:
                cursor.execute("""
                    SELECT * FROM error_patterns
                    ORDER BY last_seen DESC
                    LIMIT 20
                """)

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception:
            return []

    def is_ready(self) -> Dict[str, bool]:
        """
        Check what context sources are available

        Returns:
            Dict of availability status for each source
        """
        return {
            'console_errors': Paths.CONSOLE_ERRORS.exists(),
            'observations': Paths.AI_OBSERVATIONS.exists(),
            'db_private': Paths.DB_PRIVATE.exists(),
            'db_knowledge': Paths.DB_KNOWLEDGE.exists(),
            'session_active': self.session.session_id is not None
        }


# Global context manager instance
_context_manager: Optional[ContextManager] = None

def get_context() -> ContextManager:
    """Get the global context manager instance - your buttery interface"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
