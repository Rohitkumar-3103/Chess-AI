@echo off
title Chess AI
echo Starting Chess AI...
python src/main.py
if errorlevel 1 (
    echo.
    echo An error occurred. Make sure dependencies are installed:
    echo   pip install -r requirements.txt
    pause
)
