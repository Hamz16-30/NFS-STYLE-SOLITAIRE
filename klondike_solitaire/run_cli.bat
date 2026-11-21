@echo off
title Klondike Solitaire - Console Interface
cd /d "%~dp0"
if exist "..\.python\python.exe" (
    "..\.python\python.exe" main.py --cli
) else (
    python main.py --cli
)
pause
