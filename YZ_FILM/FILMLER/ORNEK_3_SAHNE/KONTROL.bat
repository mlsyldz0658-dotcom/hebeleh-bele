@echo off
chcp 65001 >nul
python "%~dp0..\..\ARACLAR\kontrol.py" "%~dp0."
pause
