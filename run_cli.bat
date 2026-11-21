@echo off
title Klondike Solitaire - Console Interface
cd /d "%~dp0klondike_solitaire"
if exist "..\.python\python.exe" (
    "..\.python\python.exe" main.py --cli
) else (
    python main.py --cli
)
pause
