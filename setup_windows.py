#!/usr/bin/env python3
"""Setup script for MCP server data science environment on Windows."""

import json
import subprocess
import sys
import os
from pathlib import Path
import re
import time

def run_command(cmd, check=True):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{cmd}': {e}")
        return None

def ask_permission(question):
    """Ask user for permission."""
    while True:
        response = input(f"{question} (y/n): ").lower()
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please answer 'y' or 'n'")

def check_uv():
    """Check if uv is installed and install if needed."""
    if not run_command("where uv", check=False):
        if ask_permission("uv is not installed. Would you like to install it?"):
            print("Installing uv...")
            # Windows installation for uv
            run_command("powershell -Command \"iwr -useb https://astral.sh/uv/install.ps1 | iex\"")
            print("uv installed successfully")
        else:
            sys.exit("uv is required to continue")

def setup_venv():
    """Create virtual environment if it doesn't exist."""
    if not Path(".venv").exists():
        if ask_permission("Virtual environment not found. Create one?"):
            print("Creating virtual environment...")
            run_command("uv venv")
            print("Virtual environment created successfully")
        else:
            sys.exit("Virtual environment is required to continue")

def sync_dependencies():
    """Sync project dependencies."""
    print("Syncing dependencies...")
    run_command("uv sync")
    print("Dependencies synced successfully")

def check_claude_desktop():
    """Check if Claude desktop app is installed."""
    app_path = os.path.expandvars("%LOCALAPPDATA%\\Programs\\Claude\\Claude.exe")
    if not Path(app_path).exists():
        print("Claude desktop app not found.")
        print("Please download and install from: https://claude.ai/download")
        if not ask_permission("Continue after installing Claude?"):
            sys.exit("Claude desktop app is required to continue")

def setup_claude_config():
    """Setup Claude desktop config file."""
    config_path = Path(os.path.expandvars("%APPDATA%\\Claude\\claude_desktop_config.json"))
    config_dir = config_path.parent
    
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
    
    config = {"mcpServers": {}} if not config_path.exists() else json.loads(config_path.read_text())
    return config_path, config

def build_package():
    """Build package and get wheel path."""
    print("Building package...")
    try:
        # Use Popen for real-time and complete output capture
        process = subprocess.Popen(
            "uv build",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()  # Capture output
        output = stdout + stderr  # Combine both streams
        print(f"Build output: {output}")  # Debug: check output
    except Exception as e:
        sys.exit(f"Error running build: {str(e)}")
    
    # Check if the command was successful
    if process.returncode != 0:
        sys.exit(f"Build failed with error code {process.returncode}")

    # Look for the wheel file directly in the dist directory
    dist_dir = Path("dist")
    if not dist_dir.exists():
        sys.exit("dist directory not found after build")
    
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        sys.exit("No wheel files found in dist directory")
    
    # Take the first wheel file
    wheel_path = wheel_files[0]
    print(f"Found wheel file: {wheel_path}")
    
    # Convert to absolute path
    path = wheel_path.absolute()
    return str(path)

def update_config(config_path, config, wheel_path):
    """Update Claude config with MCP server settings."""
    config.setdefault("mcpServers", {})
    config["mcpServers"]["mcp-server-ds"] = {
        "command": "uvx",
        "args": ["--from", wheel_path, "mcp-server-ds"]
    }
    
    config_path.write_text(json.dumps(config, indent=2))
    print(f"Updated config at {config_path}")

def restart_claude():
    """Restart Claude desktop app if running."""
    # Check if Claude is running using Windows command
    claude_running = run_command("tasklist /FI \"IMAGENAME eq Claude.exe\"", check=False)
    if "Claude.exe" in claude_running:
        if ask_permission("Claude is running. Restart it?"):
            print("Restarting Claude...")
            run_command("taskkill /IM Claude.exe /F")
            time.sleep(2)
            run_command("start \"\" \"%LOCALAPPDATA%\\Programs\\Claude\\Claude.exe\"")
            print("Claude restarted successfully")
    else:
        print("Starting Claude...")
        run_command("start \"\" \"%LOCALAPPDATA%\\Programs\\Claude\\Claude.exe\"")

def main():
    """Main setup function."""
    print("Starting setup...")
    check_uv()
    setup_venv()
    sync_dependencies()
    check_claude_desktop()
    config_path, config = setup_claude_config()
    wheel_path = build_package()
    update_config(config_path, config, wheel_path)
    restart_claude()
    print("Setup completed successfully!")

if __name__ == "__main__":
    main()
