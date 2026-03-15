@echo off
REM Run the laptop analysis server (Windows)
REM Usage: run_laptop_server.bat

echo Starting CubeSat Terrain Analysis Server...
echo Press Ctrl+C to stop the server
echo.

python laptop_analyzer.py

pause

