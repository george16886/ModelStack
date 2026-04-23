@echo off
setlocal enabledelayedexpansion
title AI Model Launcher

REM Smart launcher: detect best available runtime
REM Priority: Python TUI > PowerShell > Batch fallback

REM Check Python + textual
python -c "import textual" >nul 2>nul
if !errorlevel!==0 (
    echo  Starting Python TUI...
    python "%~dp0launcher.py"
    goto :eof
)

REM Fallback: PowerShell
where powershell >nul 2>nul
if !errorlevel!==0 (
    echo  Starting PowerShell version...
    powershell -ExecutionPolicy Bypass -File "%~dp0launcher.ps1"
    goto :eof
)

REM Final fallback: original batch menu
echo  No Python or PowerShell found. Please install Python and run:
echo  pip install textual rich
pause