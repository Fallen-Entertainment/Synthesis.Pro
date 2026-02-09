"""
Synthesis.Pro MCP Server
MIT Licensed - Asset Store Compatible

Provides Unity Editor execution + RAG context integration
Managed by MCPForUnity framework
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Optional

# Add paths for our imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))

# MCP SDK (will be installed)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("[Synthesis MCP] ERROR: MCP SDK not installed. Run: pip install mcp")
    sys.exit(1)

# Our systems
try:
    from rag_engine_lite import SynthesisRAG
except ImportError:
    print("[Synthesis MCP] WARNING: RAG engine not available")
    SynthesisRAG = None

try:
    from unity_bridge import get_bridge
except ImportError:
    print("[Synthesis MCP] WARNING: Unity bridge not available")
    get_bridge = None


class SynthesisMCPServer:
    """MCP Server for Synthesis.Pro AI partnership features"""

    def __init__(self):
        self.server = Server("synthesis-pro")
        self.rag = None
        self.unity = get_bridge() if get_bridge else None
        self.setup_handlers()

    def setup_handlers(self):
        """Register all MCP tools"""

        # Tool: Search RAG for context
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="search_rag",
                    description="Search Synthesis.Pro knowledge base for context, patterns, and historical fixes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for knowledge base"
                            },
                            "scope": {
                                "type": "string",
                                "enum": ["public", "private", "both"],
                                "description": "Search scope: public (knowledge), private (observations), or both",
                                "default": "both"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_error_patterns",
                    description="Get error patterns and historical fixes from RAG",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "error_signature": {
                                "type": "string",
                                "description": "Error signature or type to search for"
                            }
                        },
                        "required": ["error_signature"]
                    }
                ),
                Tool(
                    name="execute_csharp",
                    description="Execute C# code in Unity Editor (via MCPForUnity integration)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "C# code to execute"
                            },
                            "context": {
                                "type": "object",
                                "description": "Optional context from RAG or ConsoleWatcher"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_console_context",
                    description="Get recent Unity console context captured by ConsoleWatcher",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "error_type": {
                                "type": "string",
                                "description": "Filter by error type (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of recent errors to retrieve",
                                "default": 5
                            }
                        }
                    }
                ),
                Tool(
                    name="get_unity_project_info",
                    description="Get Unity project information (version, packages, settings)",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="list_scenes",
                    description="List available scenes in the Unity project",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_unity_state",
                    description="Get current Unity Editor state (play mode, active scene, selection)",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_scene_hierarchy",
                    description="Get GameObject hierarchy for a scene",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scene_name": {
                                "type": "string",
                                "description": "Scene name (optional, uses active scene if not specified)"
                            },
                            "include_inactive": {
                                "type": "boolean",
                                "description": "Include inactive GameObjects",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="get_gameobject",
                    description="Get detailed information about a GameObject",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "GameObject path (e.g., 'Main Camera') or hierarchy path (e.g., 'Canvas/Button')"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="create_gameobject",
                    description="Create a new GameObject in Unity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "GameObject name"
                            },
                            "type": {
                                "type": "string",
                                "description": "GameObject type (e.g., 'Cube', 'Sphere', 'Empty', 'Light')",
                                "default": "Empty"
                            },
                            "parent": {
                                "type": "string",
                                "description": "Parent GameObject path (optional)"
                            },
                            "position": {
                                "type": "object",
                                "description": "Position (x, y, z)"
                            }
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="modify_gameobject",
                    description="Modify GameObject properties (transform, components, etc.)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "GameObject path"
                            },
                            "operation": {
                                "type": "string",
                                "description": "Operation: 'set_position', 'set_rotation', 'set_scale', 'set_active', 'add_component', 'set_property'"
                            },
                            "params": {
                                "type": "object",
                                "description": "Operation parameters"
                            }
                        },
                        "required": ["path", "operation", "params"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""

            if name == "search_rag":
                return await self.handle_search_rag(arguments)
            elif name == "get_error_patterns":
                return await self.handle_error_patterns(arguments)
            elif name == "execute_csharp":
                return await self.handle_execute_csharp(arguments)
            elif name == "get_console_context":
                return await self.handle_console_context(arguments)
            elif name == "get_unity_project_info":
                return await self.handle_unity_project_info(arguments)
            elif name == "list_scenes":
                return await self.handle_list_scenes(arguments)
            elif name == "get_unity_state":
                return await self.handle_unity_state(arguments)
            elif name == "get_scene_hierarchy":
                return await self.handle_scene_hierarchy(arguments)
            elif name == "get_gameobject":
                return await self.handle_get_gameobject(arguments)
            elif name == "create_gameobject":
                return await self.handle_create_gameobject(arguments)
            elif name == "modify_gameobject":
                return await self.handle_modify_gameobject(arguments)
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]

    async def initialize_rag(self):
        """Initialize RAG engine"""
        if SynthesisRAG is None:
            return False

        try:
            server_dir = Path(__file__).parent.parent
            db_dir = server_dir / "database"

            self.rag = SynthesisRAG(
                database=str(db_dir / "synthesis_knowledge.db"),
                private_database=str(db_dir / "synthesis_private.db")
            )

            print("[Synthesis MCP] [OK] RAG engine initialized")
            return True

        except Exception as e:
            print(f"[Synthesis MCP] [WARNING] RAG initialization failed: {e}")
            return False

    async def handle_search_rag(self, args: dict) -> list[TextContent]:
        """Search RAG knowledge base"""
        if not self.rag:
            await self.initialize_rag()

        if not self.rag:
            return [TextContent(
                type="text",
                text="RAG engine not available"
            )]

        try:
            query = args["query"]
            scope = args.get("scope", "both")
            top_k = args.get("top_k", 5)

            results = self.rag.search(query, top_k=top_k, scope=scope)

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No results found for: {query}"
                )]

            # Format results
            formatted = f"# RAG Search Results for: {query}\n\n"
            formatted += f"Scope: {scope} | Found: {len(results)} results\n\n"

            for i, result in enumerate(results, 1):
                formatted += f"## Result {i}\n"
                formatted += f"**Score:** {result.get('score', 0):.3f}\n"
                formatted += f"**Source:** {result.get('source', 'unknown')}\n\n"
                formatted += f"{result.get('text', '')}\n\n"
                formatted += "---\n\n"

            return [TextContent(type="text", text=formatted)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching RAG: {str(e)}"
            )]

    async def handle_error_patterns(self, args: dict) -> list[TextContent]:
        """Get error patterns from RAG"""
        if not self.rag:
            await self.initialize_rag()

        if not self.rag:
            return [TextContent(
                type="text",
                text="RAG engine not available"
            )]

        try:
            error_sig = args["error_signature"]

            # Search for similar errors in private database
            results = self.rag.search(
                f"[CONSOLE:ERROR] {error_sig}",
                top_k=10,
                scope="private"
            )

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No historical patterns found for: {error_sig}"
                )]

            formatted = f"# Error Pattern Analysis: {error_sig}\n\n"
            formatted += f"Found {len(results)} similar historical errors\n\n"

            for i, result in enumerate(results, 1):
                formatted += f"## Occurrence {i}\n"
                formatted += f"**Similarity:** {result.get('score', 0):.3f}\n\n"
                formatted += f"{result.get('text', '')}\n\n"
                formatted += "---\n\n"

            return [TextContent(type="text", text=formatted)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error analyzing patterns: {str(e)}"
            )]

    async def handle_execute_csharp(self, args: dict) -> list[TextContent]:
        """Execute C# code in Unity Editor"""
        if not self.unity:
            return [TextContent(
                type="text",
                text="Unity bridge not available. Ensure MCPForUnity is running."
            )]

        code = args["code"]
        context = args.get("context")

        try:
            result = await self.unity.execute_csharp(code)

            if not result:
                return [TextContent(
                    type="text",
                    text=f"Failed to execute C# code. Ensure Unity is running with MCPForUnity bridge started."
                )]

            response = f"# C# Execution Result\n\n"
            response += f"**Code:**\n```csharp\n{code}\n```\n\n"

            if context:
                response += f"**Context:** {context}\n\n"

            # Show execution result
            if result.get('success'):
                response += "**Status:** Success\n\n"
                if result.get('output'):
                    response += f"**Output:**\n```\n{result['output']}\n```\n"
            else:
                response += "**Status:** Failed\n\n"
                if result.get('error'):
                    response += f"**Error:**\n```\n{result['error']}\n```\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error executing C# code: {str(e)}"
            )]

    async def handle_console_context(self, args: dict) -> list[TextContent]:
        """Get recent console context"""
        if not self.rag:
            await self.initialize_rag()

        if not self.rag:
            return [TextContent(
                type="text",
                text="RAG engine not available"
            )]

        try:
            error_type = args.get("error_type", "")
            limit = args.get("limit", 5)

            # Search for recent console errors
            query = f"[CONSOLE:ERROR] {error_type}" if error_type else "[CONSOLE:ERROR]"
            results = self.rag.search(query, top_k=limit, scope="private")

            if not results:
                return [TextContent(
                    type="text",
                    text="No recent console errors found"
                )]

            formatted = f"# Recent Console Context\n\n"
            formatted += f"Showing {len(results)} recent errors\n\n"

            for i, result in enumerate(results, 1):
                formatted += f"## Error {i}\n"
                formatted += f"{result.get('text', '')}\n\n"
                formatted += "---\n\n"

            return [TextContent(type="text", text=formatted)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error retrieving console context: {str(e)}"
            )]

    async def handle_unity_project_info(self, args: dict) -> list[TextContent]:
        """Get Unity project information"""
        try:
            import json
            from pathlib import Path

            # Read ProjectSettings/ProjectVersion.txt
            server_dir = Path(__file__).parent.parent
            project_root = server_dir.parent.parent.parent  # Server->Synthesis.Pro(pkg)->Assets->Synthesis.Pro(root)
            project_settings = project_root / "ProjectSettings" / "ProjectVersion.txt"

            info = {"project": "Synthesis.Pro"}

            if project_settings.exists():
                with open(project_settings, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if 'm_EditorVersion:' in line:
                            info['unity_version'] = line.split(':', 1)[1].strip()

            # Try to get package info
            packages_manifest = project_root / "Packages" / "manifest.json"
            if packages_manifest.exists():
                with open(packages_manifest, 'r') as f:
                    manifest = json.load(f)
                    info['packages'] = list(manifest.get('dependencies', {}).keys())[:10]

            formatted = f"# Unity Project Information\n\n"
            formatted += f"**Unity Version:** {info.get('unity_version', 'Unknown')}\n\n"

            if 'packages' in info:
                formatted += f"**Installed Packages** (showing first 10):\n"
                for pkg in info['packages']:
                    formatted += f"- {pkg}\n"

            return [TextContent(type="text", text=formatted)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting project info: {str(e)}"
            )]

    async def handle_list_scenes(self, args: dict) -> list[TextContent]:
        """List available scenes in the project"""
        try:
            from pathlib import Path
            import os

            server_dir = Path(__file__).parent.parent
            project_root = server_dir.parent.parent.parent  # Server->Synthesis.Pro(pkg)->Assets->Synthesis.Pro(root)
            assets_dir = project_root / "Assets"

            # Find all .unity scene files
            scenes = []
            for root, dirs, files in os.walk(assets_dir):
                for file in files:
                    if file.endswith('.unity'):
                        full_path = Path(root) / file
                        rel_path = full_path.relative_to(project_root)
                        scenes.append(str(rel_path))

            formatted = f"# Unity Scenes\n\n"
            formatted += f"Found {len(scenes)} scenes:\n\n"

            for scene in sorted(scenes):
                formatted += f"- {scene}\n"

            return [TextContent(type="text", text=formatted)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing scenes: {str(e)}"
            )]

    async def handle_unity_state(self, args: dict) -> list[TextContent]:
        """Get current Unity Editor state"""
        if not self.unity:
            return [TextContent(
                type="text",
                text="Unity bridge not available. Ensure MCPForUnity is running."
            )]

        try:
            state = await self.unity.get_editor_state()

            if not state:
                return [TextContent(
                    type="text",
                    text="Could not retrieve Unity Editor state. Ensure Unity is running with MCPForUnity bridge started."
                )]

            response = "# Unity Editor State\n\n"
            response += f"**Play Mode:** {state.get('is_playing', 'Unknown')}\n"
            response += f"**Paused:** {state.get('is_paused', 'Unknown')}\n"
            response += f"**Active Scene:** {state.get('active_scene', 'Unknown')}\n\n"

            selected = state.get('selected_objects', [])
            if selected:
                response += f"**Selected Objects:** ({len(selected)})\n"
                for obj in selected[:10]:  # Limit to first 10
                    response += f"- {obj}\n"
            else:
                response += "**Selected Objects:** None\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting Unity state: {str(e)}"
            )]

    async def handle_scene_hierarchy(self, args: dict) -> list[TextContent]:
        """Get GameObject hierarchy for a scene"""
        if not self.unity:
            return [TextContent(
                type="text",
                text="Unity bridge not available. Ensure MCPForUnity is running."
            )]

        scene_name = args.get("scene_name")
        include_inactive = args.get("include_inactive", True)

        try:
            hierarchy = await self.unity.get_scene_hierarchy(scene_name, include_inactive)

            if not hierarchy:
                return [TextContent(
                    type="text",
                    text=f"Could not retrieve scene hierarchy. Ensure Unity is running with MCPForUnity bridge started."
                )]

            response = f"# Scene Hierarchy\n\n"
            response += f"**Scene:** {scene_name or 'Active Scene'}\n"
            response += f"**Include Inactive:** {include_inactive}\n"
            response += f"**Total GameObjects:** {len(hierarchy)}\n\n"

            # Show first 20 GameObjects
            for i, go in enumerate(hierarchy[:20], 1):
                name = go.get('name', 'Unknown')
                active = go.get('active', True)
                status = "[Active]" if active else "[Inactive]"
                response += f"{i}. {name} {status}\n"

            if len(hierarchy) > 20:
                response += f"\n... and {len(hierarchy) - 20} more\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting scene hierarchy: {str(e)}"
            )]

    async def handle_get_gameobject(self, args: dict) -> list[TextContent]:
        """Get detailed information about a GameObject"""
        if not self.unity:
            return [TextContent(
                type="text",
                text="Unity bridge not available. Ensure MCPForUnity is running."
            )]

        path = args["path"]

        try:
            go_info = await self.unity.get_gameobject(path, "by_name")

            if not go_info:
                return [TextContent(
                    type="text",
                    text=f"GameObject '{path}' not found. Ensure Unity is running with MCPForUnity bridge started."
                )]

            response = f"# GameObject: {go_info.get('name', path)}\n\n"

            # Transform
            transform = go_info.get('transform', {})
            if transform:
                pos = transform.get('position', {})
                rot = transform.get('rotation', {})
                scale = transform.get('scale', {})
                response += "**Transform:**\n"
                response += f"- Position: ({pos.get('x', 0):.2f}, {pos.get('y', 0):.2f}, {pos.get('z', 0):.2f})\n"
                response += f"- Rotation: ({rot.get('x', 0):.2f}, {rot.get('y', 0):.2f}, {rot.get('z', 0):.2f})\n"
                response += f"- Scale: ({scale.get('x', 1):.2f}, {scale.get('y', 1):.2f}, {scale.get('z', 1):.2f})\n\n"

            # Components
            components = go_info.get('components', [])
            if components:
                response += f"**Components:** ({len(components)})\n"
                for comp in components:
                    response += f"- {comp}\n"
                response += "\n"

            # Hierarchy
            parent = go_info.get('parent')
            children = go_info.get('children', [])
            response += "**Hierarchy:**\n"
            response += f"- Parent: {parent or 'None (root)'}\n"
            response += f"- Children: {len(children)}\n\n"

            # Other info
            response += "**Other:**\n"
            response += f"- Active: {go_info.get('active', True)}\n"
            response += f"- Tag: {go_info.get('tag', 'Untagged')}\n"
            response += f"- Layer: {go_info.get('layer', '0')}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting GameObject info: {str(e)}"
            )]

    async def handle_create_gameobject(self, args: dict) -> list[TextContent]:
        """Create a new GameObject in Unity"""
        if not self.unity:
            return [TextContent(
                type="text",
                text="Unity bridge not available. Ensure MCPForUnity is running."
            )]

        name = args["name"]
        obj_type = args.get("type", "Empty")
        parent = args.get("parent")
        position = args.get("position")

        try:
            # Map our types to Unity primitive types
            primitive_map = {
                "Cube": "Cube",
                "Sphere": "Sphere",
                "Capsule": "Capsule",
                "Cylinder": "Cylinder",
                "Plane": "Plane",
                "Quad": "Quad",
                "Empty": None
            }

            primitive_type = primitive_map.get(obj_type)

            result = await self.unity.create_gameobject(
                name=name,
                primitive_type=primitive_type,
                parent=parent,
                position=position
            )

            if not result:
                return [TextContent(
                    type="text",
                    text=f"Failed to create GameObject. Ensure Unity is running with MCPForUnity bridge started."
                )]

            response = f"# GameObject Created\n\n"
            response += f"**Name:** {name}\n"
            response += f"**Type:** {obj_type}\n"

            if parent:
                response += f"**Parent:** {parent}\n"

            if position:
                response += f"**Position:** ({position.get('x', 0)}, {position.get('y', 0)}, {position.get('z', 0)})\n"

            response += f"\n{result.get('message', 'GameObject created successfully')}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating GameObject: {str(e)}"
            )]

    async def handle_modify_gameobject(self, args: dict) -> list[TextContent]:
        """Modify GameObject properties"""
        if not self.unity:
            return [TextContent(
                type="text",
                text="Unity bridge not available. Ensure MCPForUnity is running."
            )]

        path = args["path"]
        operation = args["operation"]
        params = args["params"]

        try:
            result = await self.unity.modify_gameobject(
                target=path,
                operation=operation,
                params=params
            )

            if not result:
                return [TextContent(
                    type="text",
                    text=f"Failed to modify GameObject. Ensure Unity is running with MCPForUnity bridge started."
                )]

            response = f"# GameObject Modified\n\n"
            response += f"**GameObject:** {path}\n"
            response += f"**Operation:** {operation}\n"
            response += f"**Parameters:** {params}\n\n"
            response += f"{result.get('message', 'GameObject modified successfully')}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error modifying GameObject: {str(e)}"
            )]

    async def run(self):
        """Run the MCP server"""
        print("[Synthesis MCP] Starting Synthesis.Pro MCP Server...")
        print("[Synthesis MCP] Providing: RAG search, error patterns, Unity state, GameObject operations")

        # Initialize RAG
        await self.initialize_rag()

        # Run stdio server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = SynthesisMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
