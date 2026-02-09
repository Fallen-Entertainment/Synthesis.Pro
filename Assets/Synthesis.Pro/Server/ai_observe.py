"""
AI Observation Saver
Simple, reliable way to save AI observations to private RAG for cross-session learning.

Usage:
    1. Write observation to ai_observation.txt
    2. Run: ../../PythonRuntime/python/python.exe ai_observe.py
    3. Done!
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add paths for RAG imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "RAG" / "core"))

try:
    from rag_engine_lite import SynthesisRAG
except ImportError:
    print("[ERROR] ERROR: RAG engine not available")
    sys.exit(1)


def detect_observation_type(text: str) -> str:
    """Auto-detect observation type from content"""
    text_lower = text.lower()

    if any(word in text_lower for word in ["learned", "pattern", "recognize", "tend to", "my behavior"]):
        return "self_reflection"
    elif any(word in text_lower for word in ["error", "mistake", "wrong", "bug", "issue"]):
        return "error_learning"
    elif any(word in text_lower for word in ["discovered", "found", "realized", "understand"]):
        return "insight"
    elif any(word in text_lower for word in ["decided", "chose", "prefer", "like"]):
        return "preference"
    else:
        return "observation"


def extract_keywords(text: str, max_keywords: int = 5) -> list:
    """Extract likely search keywords from observation"""
    # Simple keyword extraction - look for capitalized phrases and important words
    important_words = []

    # Common important words in observations
    markers = ["pattern", "learned", "error", "issue", "discovered", "realized",
               "decided", "prefer", "behavior", "tendency", "approach"]

    for word in markers:
        if word in text.lower():
            important_words.append(word)

    return important_words[:max_keywords]


def backup_observations_to_protected():
    """Automatically backup observations to protected directory"""
    script_dir = Path(__file__).parent
    protected_dir = script_dir / "database" / "ai_memory_protected"

    # Ensure protected directory exists
    protected_dir.mkdir(parents=True, exist_ok=True)

    # Files to backup
    source_files = [
        script_dir / "ai_observations.txt",
        script_dir / "ai_observation_last.txt"
    ]

    try:
        import shutil
        for source in source_files:
            if source.exists():
                dest = protected_dir / source.name
                shutil.copy2(source, dest)

        # Update backup log
        log_file = protected_dir / "BACKUP_LOG.txt"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Backup created: {datetime.now().isoformat()}\n")

        return True
    except Exception as e:
        print(f"[WARN]  Backup failed: {e}")
        return False


def save_observation():
    """Save AI observation from file to private RAG"""

    # File paths
    script_dir = Path(__file__).parent
    observation_file = script_dir / "ai_observation.txt"
    archive_file = script_dir / "ai_observation_last.txt"

    # Check if observation file exists
    if not observation_file.exists():
        print("[ERROR] No observation file found")
        print(f"[NOTE] Create: {observation_file}")
        print("   Write your observation, then run this script again")
        return False

    # Read observation
    try:
        with open(observation_file, 'r', encoding='utf-8') as f:
            observation = f.read().strip()
    except Exception as e:
        print(f"[ERROR] Error reading observation file: {e}")
        return False

    # Check if empty
    if not observation:
        print("[WARN]  Observation file is empty")
        print("[NOTE] Write your observation first, then run this script")
        return False

    # Initialize RAG
    print("[INFO] Initializing RAG...")
    db_dir = script_dir / "database"
    try:
        rag = SynthesisRAG(
            database=str(db_dir / "synthesis_knowledge.db"),
            private_database=str(db_dir / "synthesis_private.db")
        )
    except Exception as e:
        print(f"[ERROR] Error initializing RAG: {e}")
        return False

    # Detect metadata
    obs_type = detect_observation_type(observation)
    date = datetime.now().strftime('%Y-%m-%d')
    keywords = extract_keywords(observation)

    metadata = json.dumps({
        'type': obs_type,
        'date': date,
        'saved_at': datetime.now().isoformat(),
        'keywords': keywords
    })

    # Save to private RAG
    print(f"[SAVE] Saving observation...")
    try:
        rag.add_text(observation, private=True, metadata=metadata)
    except Exception as e:
        print(f"[ERROR] Error saving to RAG: {e}")
        return False

    # Archive the observation
    try:
        with open(archive_file, 'w', encoding='utf-8') as f:
            f.write(f"# Saved: {datetime.now().isoformat()}\n\n")
            f.write(observation)
    except:
        pass  # Archive failure is not critical

    # Clear observation file
    try:
        with open(observation_file, 'w', encoding='utf-8') as f:
            f.write("# Write your next observation here\n\n")
    except:
        pass  # Clear failure is not critical

    # Automatic backup to protected directory
    backup_success = backup_observations_to_protected()

    # Success!
    print("\n" + "="*60)
    print("[OK] Observation saved to private RAG")
    if backup_success:
        print("[OK] Automatic backup created (protected)")
    print("="*60)
    print(f"[NOTE] Type: {obs_type}")
    print(f"[DATE] Date: {date}")
    if keywords:
        print(f"[SEARCH] Keywords: {', '.join(keywords)}")
    print(f"\n[TIP] Search later with: '{' '.join(keywords[:3])}'" if keywords else "")
    print(f"[FILE] Archived to: {archive_file.name}")
    if backup_success:
        print("[PROTECTED] Backup: database/ai_memory_protected/")
    print("="*60)

    return True


if __name__ == "__main__":
    # Suppress noisy model loading output
    os.environ['TQDM_DISABLE'] = '1'
    os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

    success = save_observation()
    sys.exit(0 if success else 1)
