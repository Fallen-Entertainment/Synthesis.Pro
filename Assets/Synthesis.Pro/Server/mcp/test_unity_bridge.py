"""
Quick test for Unity Bridge connectivity
Run this to verify Unity Editor and MCPForUnity bridge are accessible
"""

import asyncio
import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent))

from unity_bridge import get_bridge


async def test_connection():
    """Test Unity bridge connection"""
    print("="*60)
    print("Unity Bridge Connection Test")
    print("="*60)
    print()

    bridge = get_bridge()

    # Test 1: Check connection
    print("[TEST 1] Checking Unity bridge connectivity...")
    connected = await bridge.is_connected()

    if connected:
        print("[OK] Unity bridge is accessible")
    else:
        print("[FAIL] Cannot connect to Unity bridge")
        print()
        print("Troubleshooting:")
        print("1. Ensure Unity Editor is open")
        print("2. Open Window > MCP for Unity")
        print("3. Click 'Start Bridge'")
        print("4. Verify bridge shows 'Running' status")
        return False

    print()

    # Test 2: Get Editor State
    print("[TEST 2] Getting Unity Editor state...")
    state = await bridge.get_editor_state()

    if state:
        print("[OK] Retrieved Editor state")
        print(f"     Play Mode: {state.get('is_playing', 'Unknown')}")
        print(f"     Active Scene: {state.get('active_scene', 'Unknown')}")
    else:
        print("[WARNING] Could not retrieve Editor state")
        print("         Unity may be running but bridge might need configuration")

    print()

    # Test 3: Get Project Info
    print("[TEST 3] Getting Unity project info...")
    project_info = await bridge.get_project_info()

    if project_info:
        print("[OK] Retrieved project info")
        print(f"     Unity Version: {project_info.get('unity_version', 'Unknown')}")
    else:
        print("[WARNING] Could not retrieve project info")

    print()

    # Test 4: List Scenes
    print("[TEST 4] Listing scenes...")
    scenes = await bridge.list_scenes()

    if scenes:
        print(f"[OK] Found {len(scenes)} scenes")
        for scene in scenes[:3]:
            print(f"     - {scene}")
    else:
        print("[WARNING] Could not list scenes")

    print()
    print("="*60)
    print("Test Complete")
    print("="*60)
    print()

    if connected:
        print("[SUCCESS] Unity bridge is working!")
        print()
        print("You can now:")
        print("1. Start the MCP server: python synthesis_mcp_server.py")
        print("2. Register with Claude Code (see REGISTRATION.md)")
        print("3. Use Unity tools from your MCP client")
        return True
    else:
        print("[FAILED] Unity bridge not accessible")
        return False


async def main():
    """Main entry point"""
    try:
        success = await test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
