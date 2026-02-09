"""
Session management for Synthesis.Pro
Handles session state, lifecycle, and cleanup
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .paths import Paths


class SessionManager:
    """Manages session state and runtime file lifecycle - keeps things fresh"""

    def __init__(self):
        Paths.ensure_runtime_exists()
        self.session_id = None
        self.start_time = None
        self._load_or_create_session()

    def _load_or_create_session(self):
        """Load existing session or create new one"""
        if Paths.SESSION_STATE.exists():
            try:
                with open(Paths.SESSION_STATE, 'r') as f:
                    state = json.load(f)
                    self.session_id = state.get('session_id')
                    self.start_time = state.get('start_time')
            except Exception:
                self._create_new_session()
        else:
            self._create_new_session()

    def _create_new_session(self):
        """Create a new session with fresh ID and timestamp"""
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now().isoformat()
        self._save_state()

    def _save_state(self):
        """Save current session state"""
        state = {
            'session_id': self.session_id,
            'start_time': self.start_time,
            'last_updated': datetime.now().isoformat()
        }
        with open(Paths.SESSION_STATE, 'w') as f:
            json.dump(state, f, indent=2)

    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time,
            'uptime_seconds': (datetime.now() - datetime.fromisoformat(self.start_time)).total_seconds()
        }

    def is_file_fresh(self, filepath: Path, max_age_seconds: int = 3600) -> bool:
        """Check if a runtime file is still fresh (not stale)"""
        if not filepath.exists():
            return False

        file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
        age_seconds = (datetime.now() - file_time).total_seconds()
        return age_seconds < max_age_seconds

    def cleanup_stale_files(self, max_age_seconds: int = 86400):
        """Remove stale runtime files older than max_age"""
        for file in Paths.RUNTIME.glob('*'):
            if file.name == '.gitkeep' or file.name == 'session_state.json':
                continue

            if not self.is_file_fresh(file, max_age_seconds):
                try:
                    file.unlink()
                except Exception:
                    pass

    def mark_activity(self):
        """Update session state to mark activity"""
        self._save_state()


# Global session manager instance
_session_manager: Optional[SessionManager] = None

def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
