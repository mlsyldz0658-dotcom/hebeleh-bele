@echo off
chcp 65001 >nul
echo Memmet calisiyor: gorseller, videolar, seslendirme, CapCut projesi. Memmet Chrome penceresine dokunma.
python "%~dp0..\..\ARACLAR\memmet.py" "%~dp0."
pause
