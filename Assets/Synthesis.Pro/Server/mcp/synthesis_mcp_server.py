"""
Synthesis.Pro MCP Server - Complete Edition
MIT Licensed - Asset Store Compatible

Provides Unity Editor execution + RAG context integration + Database management
Managed by MCPForUnity framework
"""

import asyncio
import sys
import shutil
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

# Add paths for our imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "rag_integration"))

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

try:
    from rag_onboarding import RAGOnboardingSystem
except ImportError:
    print("[Synthesis MCP] WARNING: RAG onboarding not available")
    RAGOnboardingSystem = None

try:
    from core.database_manager import DatabaseManager
except ImportError:
    print("[Synthesis MCP] WARNING: Database manager not available")
    DatabaseManager = None


class SynthesisMCPServer:
    """MCP Server for Synthesis.Pro AI partnership features"""

    def __init__(self):
        self.server = Server("synthesis-pro")
        self.rag = None
        self.unity = get_bridge() if get_bridge else None
        self.onboarding = None
        self.db_manager = None

        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'tools_called': 0,
            'rag_queries': 0,
            'unity_operations': 0
        }

        self.setup_handlers()

    def setup_handlers(self):
        """Register all MCP tools"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                # RAG & Knowledge Tools
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

                # Database Management Tools
                Tool(
                    name="backup_private_db",
                    description="Create timestamped backup of private database",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="restore_private_db",
                    description="Restore private database from backup",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "backup_file": {
                                "type": "string",
                                "description": "Backup filename to restore from"
                            }
                        },
                        "required": ["backup_file"]
                    }
                ),
                Tool(
                    name="clear_private_db",
                    description="Clear private database (requires confirmation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "confirm": {
                                "type": "boolean",
                                "description": "Must be true to proceed"
                            }
                        },
                        "required": ["confirm"]
                    }
                ),
                Tool(
                    name="list_backups",
                    description="List available database backups",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="audit_public_db",
                    description="Audit public database for sensitive content",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="check_db_updates",
                    description="Check if database or model updates are available",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="update_public_db",
                    description="Update database and model to latest versions",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),

                # Health Check Tools
                Tool(
                    name="ping",
                    description="Health check - verify server is responsive",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_stats",
                    description="Get server statistics and usage metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_capabilities",
                    description="Get server capabilities and available features",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),

                # Unity Project Tools
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

                # Unity Editor Tools (Require Unity + MCPForUnity)
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
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls"""
            self.stats['tools_called'] += 1

            # RAG & Knowledge
            if name == "search_rag":
                self.stats['rag_queries'] += 1
                return await self.handle_search_rag(arguments)
            elif name == "get_error_patterns":
                self.stats['rag_queries'] += 1
                return await self.handle_error_patterns(arguments)
            elif name == "get_console_context":
                self.stats['rag_queries'] += 1
                return await self.handle_console_context(arguments)

            # Database Management
            elif name == "backup_private_db":
                return await self.handle_backup_private_db(arguments)
            elif name == "restore_private_db":
                return await self.handle_restore_private_db(arguments)
            elif name == "clear_private_db":
                return await self.handle_clear_private_db(arguments)
            elif name == "list_backups":
                return await self.handle_list_backups(arguments)
            elif name == "audit_public_db":
                return await self.handle_audit_public_db(arguments)
            elif name == "check_db_updates":
                return await self.handle_check_db_updates(arguments)
            elif name == "update_public_db":
                return await self.handle_update_public_db(arguments)

            # Health Checks
            elif name == "ping":
                return await self.handle_ping(arguments)
            elif name == "get_stats":
                return await self.handle_get_stats(arguments)
            elif name == "get_capabilities":
                return await self.handle_get_capabilities(arguments)

            # Unity Project
            elif name == "get_unity_project_info":
                return await self.handle_unity_project_info(arguments)
            elif name == "list_scenes":
                return await self.handle_list_scenes(arguments)

            # Unity Editor
            elif name == "get_unity_state":
                self.stats['unity_operations'] += 1
                return await self.handle_unity_state(arguments)
            elif name == "get_scene_hierarchy":
                self.stats['unity_operations'] += 1
                return await self.handle_scene_hierarchy(arguments)
            elif name == "get_gameobject":
                self.stats['unity_operations'] += 1
                return await self.handle_get_gameobject(arguments)
            elif name == "create_gameobject":
                self.stats['unity_operations'] += 1
                return await self.handle_create_gameobject(arguments)
            elif name == "modify_gameobject":
                self.stats['unity_operations'] += 1
                return await self.handle_modify_gameobject(arguments)
            elif name == "execute_csharp":
                self.stats['unity_operations'] += 1
                return await self.handle_execute_csharp(arguments)
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]

    async def initialize_rag(self):
        """Initialize RAG engine and onboarding system"""
        if SynthesisRAG is None:
            return False

        try:
            server_dir = Path(__file__).parent.parent
            db_dir = server_dir / "database"

            self.rag = SynthesisRAG(
                database=str(db_dir / "synthesis_knowledge.db"),
                private_database=str(db_dir / "synthesis_private.db")
            )

            # Initialize RAG onboarding for session previews
            if RAGOnboardingSystem and self.rag:
                self.onboarding = RAGOnboardingSystem(
                    rag_engine=self.rag,
                    user_id="mcp_session",
                    presentation_style="natural"
                )

                # Generate session preview
                session_id = f"mcp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                preview = self.onboarding.start_session(session_id)

                if preview:
                    print("\n" + "="*60)
                    print(preview)
                    print("="*60 + "\n")

            # Initialize database manager
            if DatabaseManager:
                self.db_manager = DatabaseManager()

            print("[Synthesis MCP] [OK] RAG engine initialized")
            return True

        except Exception as e:
            print(f"[Synthesis MCP] [WARNING] RAG initialization failed: {e}")
            return False

    # ====================
    # RAG & Knowledge Tools
    # ====================

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

    # ====================
    # Database Management Tools
    # ====================

    async def handle_backup_private_db(self, args: dict) -> list[TextContent]:
        """Backup private database"""
        if not self.rag:
            await self.initialize_rag()

        if not self.rag:
            return [TextContent(
                type="text",
                text="RAG engine not available"
            )]

        try:
            private_db_path = Path(self.rag.private_database)

            if not private_db_path.exists():
                return [TextContent(
                    type="text",
                    text="Private database does not exist yet"
                )]

            # Create backups directory
            backup_dir = private_db_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)

            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"synthesis_private_backup_{timestamp}.db"
            backup_path = backup_dir / backup_filename

            # Copy database
            shutil.copy2(private_db_path, backup_path)

            # Get backup size
            backup_size = backup_path.stat().st_size

            response = f"# Database Backup Created\n\n"
            response += f"**Backup File:** {backup_filename}\n"
            response += f"**Size:** {backup_size:,} bytes\n"
            response += f"**Location:** {backup_path}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error backing up database: {str(e)}"
            )]

    async def handle_restore_private_db(self, args: dict) -> list[TextContent]:
        """Restore private database from backup"""
        if not self.rag:
            await self.initialize_rag()

        if not self.rag:
            return [TextContent(
                type="text",
                text="RAG engine not available"
            )]

        backup_filename = args["backup_file"]

        try:
            private_db_path = Path(self.rag.private_database)
            backup_dir = private_db_path.parent / "backups"
            backup_path = backup_dir / backup_filename

            if not backup_path.exists():
                return [TextContent(
                    type="text",
                    text=f"Backup file not found: {backup_filename}"
                )]

            # Create safety backup before overwriting
            if private_db_path.exists():
                safety_backup = backup_dir / f"pre_restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(private_db_path, safety_backup)

            # Restore from backup
            shutil.copy2(backup_path, private_db_path)

            response = f"# Database Restored\n\n"
            response += f"**Restored From:** {backup_filename}\n"
            response += f"**Safety backup created** (in case you need to undo)\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error restoring database: {str(e)}"
            )]

    async def handle_clear_private_db(self, args: dict) -> list[TextContent]:
        """Clear private database"""
        if not self.rag:
            await self.initialize_rag()

        if not self.rag:
            return [TextContent(
                type="text",
                text="RAG engine not available"
            )]

        confirm = args.get("confirm", False)
        if not confirm:
            return [TextContent(
                type="text",
                text="❌ Confirmation required. Set 'confirm': true to proceed."
            )]

        try:
            private_db_path = Path(self.rag.private_database)

            if not private_db_path.exists():
                return [TextContent(
                    type="text",
                    text="Private database does not exist (already clear)"
                )]

            # Delete the database
            private_db_path.unlink()

            response = f"# Database Cleared\n\n"
            response += f"⚠️  **Private database deleted:** {private_db_path.name}\n"
            response += f"All private observations and console history have been removed.\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error clearing database: {str(e)}"
            )]

    async def handle_list_backups(self, args: dict) -> list[TextContent]:
        """List available backups"""
        if not self.rag:
            await self.initialize_rag()

        if not self.rag:
            return [TextContent(
                type="text",
                text="RAG engine not available"
            )]

        try:
            private_db_path = Path(self.rag.private_database)
            backup_dir = private_db_path.parent / "backups"

            if not backup_dir.exists():
                return [TextContent(
                    type="text",
                    text="No backups found"
                )]

            # List all .db files in backup directory
            backups = []
            for backup_file in sorted(backup_dir.glob("*.db"), reverse=True):
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                })

            if not backups:
                return [TextContent(
                    type="text",
                    text="No backups found"
                )]

            formatted = f"# Database Backups\n\n"
            formatted += f"Found {len(backups)} backup(s):\n\n"

            for backup in backups:
                formatted += f"**{backup['filename']}**\n"
                formatted += f"- Size: {backup['size']:,} bytes\n"
                formatted += f"- Modified: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            return [TextContent(type="text", text=formatted)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing backups: {str(e)}"
            )]

    async def handle_audit_public_db(self, args: dict) -> list[TextContent]:
        """Audit public database"""
        if not self.rag:
            await self.initialize_rag()

        if not self.rag:
            return [TextContent(
                type="text",
                text="RAG engine not available"
            )]

        try:
            audit_results = self.rag.audit_public_database()

            formatted = f"# Public Database Audit\n\n"
            formatted += f"**Total Documents:** {audit_results['total_documents']}\n"
            formatted += f"**Flagged Count:** {audit_results['flagged_count']}\n"
            formatted += f"**Status:** {'✅ PASSED' if audit_results['passed'] else '❌ FAILED'}\n\n"

            if audit_results['flagged_entries']:
                formatted += "## Flagged Entries\n\n"
                for entry in audit_results['flagged_entries']:
                    formatted += f"**ID:** {entry['id']}\n"
                    formatted += f"**Reason:** {entry['reason']}\n"
                    formatted += f"**Preview:** {entry['preview']}\n\n"

            return [TextContent(type="text", text=formatted)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error auditing database: {str(e)}"
            )]

    async def handle_check_db_updates(self, args: dict) -> list[TextContent]:
        """Check for database updates"""
        if not self.db_manager:
            return [TextContent(
                type="text",
                text="Database manager not available"
            )]

        try:
            updates = self.db_manager.check_for_updates()

            formatted = f"# Database Update Check\n\n"

            db_update = updates.get('database')
            model_update = updates.get('model')

            if db_update or model_update:
                formatted += "## Updates Available:\n\n"
                if db_update:
                    formatted += f"- **Database:** {db_update}\n"
                if model_update:
                    formatted += f"- **Model:** {model_update}\n"
            else:
                formatted += "✅ Everything is up to date\n"

            return [TextContent(type="text", text=formatted)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error checking updates: {str(e)}"
            )]

    async def handle_update_public_db(self, args: dict) -> list[TextContent]:
        """Update public database and model"""
        if not self.db_manager:
            return [TextContent(
                type="text",
                text="Database manager not available"
            )]

        try:
            # Check if updates are available
            updates = self.db_manager.check_for_updates()
            if not updates.get('database') and not updates.get('model'):
                return [TextContent(
                    type="text",
                    text="Everything is already up to date"
                )]

            # Perform update
            success = self.db_manager.update_all()

            if success:
                # Reinitialize RAG
                await self.initialize_rag()

                formatted = "# Update Complete\n\n"
                formatted += "✅ Database and model updated successfully\n"
                return [TextContent(type="text", text=formatted)]
            else:
                return [TextContent(
                    type="text",
                    text="❌ Update failed"
                )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error updating: {str(e)}"
            )]

    # ====================
    # Health Check Tools
    # ====================

    async def handle_ping(self, args: dict) -> list[TextContent]:
        """Health check"""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()

        response = f"# Server Health Check\n\n"
        response += f"**Status:** ✅ Online\n"
        response += f"**Uptime:** {uptime:.0f} seconds\n"
        response += f"**RAG Engine:** {'✅ Available' if self.rag else '❌ Not available'}\n"
        response += f"**Unity Bridge:** {'✅ Available' if self.unity else '❌ Not available'}\n"

        return [TextContent(type="text", text=response)]

    async def handle_get_stats(self, args: dict) -> list[TextContent]:
        """Get server statistics"""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()

        response = f"# Server Statistics\n\n"
        response += f"**Started:** {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        response += f"**Uptime:** {uptime:.0f} seconds ({uptime/60:.1f} minutes)\n"
        response += f"**Tools Called:** {self.stats['tools_called']}\n"
        response += f"**RAG Queries:** {self.stats['rag_queries']}\n"
        response += f"**Unity Operations:** {self.stats['unity_operations']}\n"

        return [TextContent(type="text", text=response)]

    async def handle_get_capabilities(self, args: dict) -> list[TextContent]:
        """Get server capabilities"""
        response = f"# Server Capabilities\n\n"
        response += f"**Version:** 2.0 (Complete Edition)\n"
        response += f"**Name:** Synthesis.Pro MCP Server\n\n"

        response += f"## Available Features:\n"
        response += f"- ✅ RAG search (hybrid BM25S + vector)\n"
        response += f"- ✅ Error pattern analysis\n"
        response += f"- ✅ Console history\n"
        response += f"- ✅ Database management\n"
        response += f"- ✅ Unity project introspection\n"
        response += f"- {'✅' if self.unity else '⚠️'} Unity Editor operations (requires Unity + MCPForUnity)\n\n"

        response += f"## Systems Status:\n"
        response += f"- RAG Engine: {'✅ Initialized' if self.rag else '❌ Not available'}\n"
        response += f"- Unity Bridge: {'✅ Initialized' if self.unity else '❌ Not available'}\n"
        response += f"- RAG Onboarding: {'✅ Initialized' if self.onboarding else '❌ Not available'}\n"
        response += f"- Database Manager: {'✅ Initialized' if self.db_manager else '❌ Not available'}\n"

        return [TextContent(type="text", text=response)]

    # ====================
    # Unity Project Tools
    # ====================

    async def handle_unity_project_info(self, args: dict) -> list[TextContent]:
        """Get Unity project information"""
        try:
            import json
            from pathlib import Path

            # Read ProjectSettings/ProjectVersion.txt
            server_dir = Path(__file__).parent.parent
            project_root = server_dir.parent.parent.parent
            project_settings = project_root / "ProjectSettings" / "ProjectVersion.txt"

            info = {"project": "Synthesis.Pro"}

            if project_settings.exists():
                with open(project_settings, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if 'm_EditorVersion:' in line:
                            info['unity_version'] = line.split(':', 1)[1].strip()

            # Get package info
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
        """List available scenes"""
        try:
            from pathlib import Path
            import os

            server_dir = Path(__file__).parent.parent
            project_root = server_dir.parent.parent.parent
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

    # ====================
    # Unity Editor Tools (Continue with existing handlers from original file)
    # ====================

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
                for obj in selected[:10]:
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

    async def run(self):
        """Run the MCP server"""
        print("=" * 70)
        print("[Synthesis MCP] Starting Synthesis.Pro MCP Server (Complete Edition)")
        print("=" * 70)
        print()
        print("[Features]")
        print("  • RAG search + error patterns + console history")
        print("  • Database management (backup, restore, audit)")
        print("  • Health monitoring (ping, stats, capabilities)")
        print("  • Unity project introspection")
        print("  • Unity Editor operations (requires Unity + MCPForUnity)")
        print()

        # Initialize RAG (includes onboarding with session preview)
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
