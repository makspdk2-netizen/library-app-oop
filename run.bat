@echo off
cd /d "%~dp0"
python -c "import PyQt6" 2>nul || python -m pip install PyQt6
python main.py
pause
