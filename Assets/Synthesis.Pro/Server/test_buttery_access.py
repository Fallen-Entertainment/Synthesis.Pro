#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the buttery and creamy unified context access
Demonstrates how smooth it is to get what you need
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding for emojis
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

# Add Server directory to path so we can import core as a package
sys.path.insert(0, str(Path(__file__).parent))

from core import get_context

def test_buttery_access():
    """Show how smooth the unified interface is"""

    print("🧈 Testing Buttery Context Access\n")

    # Get the context manager - one smooth interface
    ctx = get_context()

    # Check what's available
    print("1️⃣ Checking availability...")
    status = ctx.is_ready()
    for source, available in status.items():
        icon = "✅" if available else "❌"
        print(f"   {icon} {source}: {available}")

    # Get session info - no path construction needed
    print("\n2️⃣ Session information...")
    session = ctx.get_session_state()
    print(f"   Session ID: {session['session_id']}")
    print(f"   Started: {session['start_time']}")
    print(f"   Uptime: {session['uptime_seconds']:.1f}s")

    # Get console errors - automatic freshness check
    print("\n3️⃣ Console errors (fresh only)...")
    errors = ctx.get_console_errors(fresh_only=True)
    if errors:
        print(f"   Found {len(errors.get('parameters', {}).get('entries', []))} entries")
    else:
        print("   No fresh errors (file doesn't exist or is stale)")

    # Query memories - automatic database routing
    print("\n4️⃣ Querying memories for 'partnership'...")
    memories = ctx.query_memories("partnership", limit=3)
    if memories:
        print(f"   Found {len(memories)} memory entries")
        for mem in memories[:2]:  # Show first 2
            print(f"   - {mem.get('timestamp', 'unknown')}: {mem.get('observation', '')[:60]}...")
    else:
        print("   No matching memories found")

    # Query knowledge - also automatic routing
    print("\n5️⃣ Querying knowledge for 'Unity'...")
    knowledge = ctx.query_knowledge("Unity", limit=3)
    if knowledge:
        print(f"   Found {len(knowledge)} knowledge entries")
    else:
        print("   No matching knowledge found")

    # Get error patterns - historical pattern matching
    print("\n6️⃣ Recent error patterns...")
    patterns = ctx.get_error_patterns()
    if patterns:
        print(f"   Found {len(patterns)} error patterns")
        for pattern in patterns[:3]:  # Show first 3
            print(f"   - {pattern.get('error_type', 'unknown')}: seen {pattern.get('occurrence_count', 0)} times")
    else:
        print("   No error patterns found yet")

    print("\n✨ Buttery and creamy! One interface, zero friction.\n")

if __name__ == "__main__":
    try:
        test_buttery_access()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
