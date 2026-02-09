@echo off
echo ========================================
echo   Synthesis.MCP Server Launcher
echo ========================================
echo.

cd "%~dp0Servers\arodoid\unity-mcp-server"

echo Starting Unity MCP Server on port 8080...
echo.
echo Make sure Unity Editor is open with UnityMCP Debug Window active!
echo Press Ctrl+C to stop the server
echo.

node build/index.js
