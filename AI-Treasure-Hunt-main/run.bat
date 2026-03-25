@echo off
REM AI Treasure Hunt — quick launcher
REM Uses Python 3.10 which has pygame installed

set PYEXE="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
if not exist %PYEXE% set PYEXE=python

cd /d "%~dp0"
echo Starting AI Treasure Hunt...
%PYEXE% main.py
pause
