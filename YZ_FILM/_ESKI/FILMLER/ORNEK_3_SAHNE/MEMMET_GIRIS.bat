@echo off
chcp 65001 >nul
echo Memmet Chrome'u acilacak. Flow'a bir kez Google hesabinla giris yap.
python "%~dp0..\..\ARACLAR\memmet.py" "%~dp0." --giris
pause
