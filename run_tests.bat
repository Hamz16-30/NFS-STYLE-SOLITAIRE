@echo off
title Klondike Solitaire - Automated Test Suite (TC-01 to TC-22)
cd /d "%~dp0klondike_solitaire"
if exist "..\.python\python.exe" (
    "..\.python\python.exe" main.py --test
) else (
    python main.py --test
)
pause
