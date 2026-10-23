@echo off
chcp 65001 >nul
python "%~dp0..\..\ARACLAR\memmet.py" "%~dp0." --asama gorsel --kurgu-yok
pause
