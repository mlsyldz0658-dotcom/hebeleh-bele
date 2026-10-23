@echo off
chcp 65001 >nul
python "%~dp0..\..\ARACLAR\notlari_oku.py" "%~dp0."
pause
