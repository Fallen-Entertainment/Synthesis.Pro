"""
Synthesis.Pro Core Systems
Buttery and creamy interfaces for smooth AI access
"""

from .paths import Paths
from .session_manager import SessionManager, get_session_manager
from .context_manager import ContextManager, get_context

__all__ = [
    'Paths',
    'SessionManager',
    'get_session_manager',
    'ContextManager',
    'get_context',
]
