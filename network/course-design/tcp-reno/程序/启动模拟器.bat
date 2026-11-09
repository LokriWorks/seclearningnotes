@echo off
cd /d "%~dp0"
python reno_gui.py
if errorlevel 1 pause
