"""
Synthesis.MCP Bridge
Connects Unity MCP servers to Synthesis.Pro's Python backend
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import sys

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Server"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "RAG" / "core"))


class MCPBridge:
    """Bridge between Synthesis.Pro and Unity MCP servers"""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "Config" / "mcp_config.json"

        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.servers = {}
        self.rag = None

    async def start_mcp_server(self, server_name: str):
        """Start an MCP server subprocess"""
        server_config = self.config['servers'].get(server_name)

        if not server_config or not server_config.get('enabled'):
            print(f"[MCP] Server {server_name} not enabled")
            return None

        print(f"[MCP] Starting {server_name} server...")

        env = {**subprocess.os.environ, **server_config.get('env', {})}

        process = await asyncio.create_subprocess_exec(
            server_config['command'],
            *server_config['args'],
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        self.servers[server_name] = {
            'process': process,
            'config': server_config
        }

        print(f"[MCP] {server_name} started (PID: {process.pid})")
        return process

    async def execute_csharp(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute C# code in Unity via MCP server

        Args:
            code: C# code to execute
            context: Optional context from RAG or ConsoleWatcher

        Returns:
            Execution result with success status and output
        """
        if 'arodoid' not in self.servers:
            return {
                'success': False,
                'error': 'Arodoid MCP server not running'
            }

        # Validate code against security rules
        if not self._validate_code(code):
            return {
                'success': False,
                'error': 'Code failed security validation'
            }

        print(f"[MCP] Executing C# code...")

        # Log to RAG if available
        if self.rag and self.config['integration'].get('log_executions'):
            await self._log_execution(code, context)

        # TODO: Implement actual MCP protocol communication
        # For now, return structure
        return {
            'success': True,
            'output': 'Execution placeholder - MCP protocol implementation needed',
            'context': context
        }

    def _validate_code(self, code: str) -> bool:
        """Validate C# code against security rules"""
        security = self.config.get('security', {})

        if not security.get('sandbox_filesystem'):
            return True

        # Check for blocked filesystem access
        blocked_paths = security.get('blocked_paths', [])
        for blocked in blocked_paths:
            if blocked.lower() in code.lower():
                print(f"[SECURITY] Blocked path detected: {blocked}")
                return False

        return True

    async def _log_execution(self, code: str, context: Optional[Dict[str, Any]]):
        """Log execution to RAG for learning"""
        if not self.rag:
            return

        log_entry = {
            'type': 'mcp_execution',
            'code': code,
            'context': context,
            'timestamp': 'auto'
        }

        # Store in private database
        # self.rag.add_observation(json.dumps(log_entry))

    async def initialize_rag(self):
        """Initialize RAG connection for context and logging"""
        try:
            from rag_engine_lite import SynthesisRAG

            server_dir = Path(__file__).parent.parent.parent / "Server"
            db_dir = server_dir / "database"

            self.rag = SynthesisRAG(
                database=str(db_dir / "synthesis_knowledge.db"),
                private_database=str(db_dir / "synthesis_private.db")
            )

            print("[MCP] RAG connection initialized")

        except Exception as e:
            print(f"[MCP] RAG initialization failed: {e}")
            print("[MCP] Continuing without RAG integration")

    async def start(self):
        """Start the MCP bridge"""
        print("=" * 60)
        print("Synthesis.MCP Bridge")
        print("=" * 60)
        print()

        # Initialize RAG
        await self.initialize_rag()

        # Start enabled MCP servers
        for server_name, server_config in self.config['servers'].items():
            if server_config.get('enabled'):
                await self.start_mcp_server(server_name)

        print()
        print("[MCP] Bridge ready for execution commands")
        print("=" * 60)

    async def stop(self):
        """Stop all MCP servers"""
        print("\n[MCP] Stopping servers...")

        for server_name, server_data in self.servers.items():
            process = server_data['process']
            process.terminate()
            await process.wait()
            print(f"[MCP] {server_name} stopped")


async def main():
    """Test the MCP bridge"""
    bridge = MCPBridge()

    try:
        await bridge.start()

        # Test execution
        test_code = """
        // Test C# execution
        Debug.Log("Hello from Synthesis.MCP!");
        """

        result = await bridge.execute_csharp(test_code, context={'test': True})
        print(f"\n[TEST] Execution result: {result}")

        # Keep running
        print("\n[MCP] Press Ctrl+C to stop")
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        print("\n[MCP] Shutdown requested")
    finally:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
