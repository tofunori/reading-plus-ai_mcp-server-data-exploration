@echo off
echo Starting MCP Server...

REM Get the directory of this batch file
SET script_dir=%~dp0

REM Activate environment if needed
IF EXIST "%script_dir%.venv\Scripts\activate.bat" (
    call "%script_dir%.venv\Scripts\activate.bat"
)

REM Try to run the server
python -m mcp_server_ds

REM If that fails, try the explicit module
IF %ERRORLEVEL% NEQ 0 (
    echo First attempt failed, trying alternative method...
    python -c "from mcp_server_ds import main; main()"
)

REM Keep the window open to see any errors
pause
