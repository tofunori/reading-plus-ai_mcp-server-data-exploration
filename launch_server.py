#!/usr/bin/env python3
"""Launcher for MCP server"""

import sys
import os

# Add the src directory to Python's path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'src'))

try:
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")
    
    # Try to import the module
    from mcp_server_ds import main
    print("Starting MCP server...")
    main()
except Exception as e:
    print(f"Error starting server: {e}")
    
    # Try installing the package
    print("Attempting to install package...")
    os.system(f"{sys.executable} -m pip install -e {script_dir}")
    
    try:
        from mcp_server_ds import main
        print("Starting MCP server after install...")
        main()
    except Exception as e2:
        print(f"Second attempt failed: {e2}")
    
    input("Press Enter to exit...")
