@echo off
title Klondike Solitaire - Midnight Run (CSC200)
cd /d "%~dp0klondike_solitaire"
if exist "..\.python\python.exe" (
    "..\.python\python.exe" main.py --gui
) else (
    python main.py --gui
)
pause
