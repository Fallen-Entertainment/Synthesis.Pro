"""
Unity Bridge for Synthesis.Pro MCP Server
Communicates with MCPForUnity's HTTP endpoint to query and manipulate Unity Editor
"""

import json
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path


class UnityBridge:
    """Bridge to Unity Editor via MCPForUnity HTTP endpoint"""

    def __init__(self, base_url: str = "http://localhost:6400"):
        """
        Initialize Unity bridge

        Args:
            base_url: MCPForUnity HTTP endpoint base URL
        """
        self.base_url = base_url.rstrip('/')
        self.mcp_url = f"{self.base_url}/mcp"

    async def _call_mcp(self, method: str, params: Dict[str, Any] = None) -> Any:
        """
        Call MCPForUnity JSON-RPC endpoint

        Args:
            method: MCP method name
            params: Method parameters

        Returns:
            Method result or None if failed
        """
        try:
            import aiohttp

            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params or {}
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.mcp_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("result")
                    else:
                        print(f"[Unity Bridge] HTTP {response.status}: {await response.text()}")
                        return None

        except ImportError:
            print("[Unity Bridge] aiohttp not installed. Install with: pip install aiohttp")
            return None
        except asyncio.TimeoutError:
            print("[Unity Bridge] Request timed out. Is Unity Editor running with MCPForUnity bridge started?")
            return None
        except Exception as e:
            print(f"[Unity Bridge] Error calling {method}: {e}")
            return None

    async def is_connected(self) -> bool:
        """Check if Unity bridge is accessible"""
        try:
            result = await self._call_mcp("tools/list")
            return result is not None
        except:
            return False

    async def get_editor_state(self) -> Optional[Dict[str, Any]]:
        """
        Get current Unity Editor state

        Returns:
            Dict with:
                - is_playing: bool
                - is_paused: bool
                - active_scene: str
                - selected_objects: List[str]
        """
        # MCPForUnity provides this via resources/read
        result = await self._call_mcp("resources/read", {
            "uri": "unity://editor/state"
        })
        return result

    async def get_scene_hierarchy(self, scene_name: Optional[str] = None, include_inactive: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Get GameObject hierarchy for a scene

        Args:
            scene_name: Scene name (None = active scene)
            include_inactive: Include inactive GameObjects

        Returns:
            List of GameObjects with hierarchy structure
        """
        params = {
            "includeInactive": include_inactive
        }

        if scene_name:
            params["sceneName"] = scene_name

        # MCPForUnity provides scene hierarchy via resources
        result = await self._call_mcp("resources/read", {
            "uri": "unity://scene/hierarchy",
            **params
        })
        return result

    async def get_gameobject(self, target: str, search_method: str = "by_name") -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a GameObject

        Args:
            target: GameObject identifier (name, path, ID)
            search_method: Search method: by_name, by_path, by_id, by_tag, by_component

        Returns:
            GameObject info including transform, components, children
        """
        result = await self._call_mcp("resources/read", {
            "uri": f"unity://scene/gameobject/{target}",
            "searchMethod": search_method
        })
        return result

    async def execute_csharp(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Execute C# code in Unity Editor

        Args:
            code: C# code to execute

        Returns:
            Execution result with output/errors
        """
        result = await self._call_mcp("tools/call", {
            "name": "unity.execute_csharp",
            "arguments": {
                "code": code
            }
        })
        return result

    async def create_gameobject(
        self,
        name: str,
        primitive_type: Optional[str] = None,
        parent: Optional[str] = None,
        position: Optional[Dict[str, float]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new GameObject in Unity

        Args:
            name: GameObject name
            primitive_type: Primitive type (Cube, Sphere, Capsule, Cylinder, Plane, Quad) or None for Empty
            parent: Parent GameObject path (optional)
            position: Position dict with x, y, z (optional)

        Returns:
            Created GameObject info
        """
        params = {
            "name": name
        }

        if primitive_type:
            params["primitiveType"] = primitive_type

        if parent:
            params["parent"] = parent

        if position:
            params["position"] = position

        result = await self._call_mcp("tools/call", {
            "name": "unity.create_gameobject",
            "arguments": params
        })
        return result

    async def modify_gameobject(
        self,
        target: str,
        operation: str,
        params: Dict[str, Any],
        search_method: str = "by_name"
    ) -> Optional[Dict[str, Any]]:
        """
        Modify GameObject properties

        Args:
            target: GameObject identifier
            operation: Operation type:
                - set_position: Set transform position (params: x, y, z)
                - set_rotation: Set transform rotation (params: x, y, z or euler angles)
                - set_scale: Set transform scale (params: x, y, z)
                - set_active: Enable/disable GameObject (params: active: bool)
                - add_component: Add a component (params: componentType: str)
                - set_property: Set component property (params: component, property, value)
            params: Operation-specific parameters
            search_method: GameObject search method

        Returns:
            Operation result
        """
        tool_params = {
            "target": target,
            "searchMethod": search_method,
            **params
        }

        # Map operation to MCPForUnity tool name
        tool_name_map = {
            "set_position": "unity.set_transform_position",
            "set_rotation": "unity.set_transform_rotation",
            "set_scale": "unity.set_transform_scale",
            "set_active": "unity.set_gameobject_active",
            "add_component": "unity.add_component",
            "set_property": "unity.set_property"
        }

        tool_name = tool_name_map.get(operation)
        if not tool_name:
            print(f"[Unity Bridge] Unknown operation: {operation}")
            return None

        result = await self._call_mcp("tools/call", {
            "name": tool_name,
            "arguments": tool_params
        })
        return result

    async def get_project_info(self) -> Optional[Dict[str, Any]]:
        """
        Get Unity project information

        Returns:
            Project info including Unity version, packages, settings
        """
        result = await self._call_mcp("resources/read", {
            "uri": "unity://project/info"
        })
        return result

    async def list_scenes(self) -> Optional[List[str]]:
        """
        List all scenes in the project

        Returns:
            List of scene paths
        """
        # Use our own implementation since we can read filesystem directly
        # This is more reliable than querying Unity
        try:
            server_dir = Path(__file__).parent.parent
            project_root = server_dir.parent.parent.parent
            assets_dir = project_root / "Assets"

            scenes = []
            for scene_file in assets_dir.rglob("*.unity"):
                rel_path = scene_file.relative_to(project_root)
                scenes.append(str(rel_path))

            return sorted(scenes)
        except Exception as e:
            print(f"[Unity Bridge] Error listing scenes: {e}")
            return None

    async def run_tests(self, test_filter: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Execute Unity tests

        Args:
            test_filter: Filter pattern for tests to run (optional)

        Returns:
            Test results with pass/fail counts and details
        """
        params = {}
        if test_filter:
            params["filter"] = test_filter

        result = await self._call_mcp("tools/call", {
            "name": "unity.run_tests",
            "arguments": params
        })
        return result


# Singleton instance
_bridge = None


def get_bridge() -> UnityBridge:
    """Get or create Unity bridge singleton"""
    global _bridge
    if _bridge is None:
        _bridge = UnityBridge()
    return _bridge
