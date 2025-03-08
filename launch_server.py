#!/usr/bin/env python3
"""Launcher for MCP server"""

try:
    from mcp_server_ds import main
    print("Starting MCP server...")
    main()
except Exception as e:
    print(f"Error starting server: {e}")
    input("Press Enter to exit...")
