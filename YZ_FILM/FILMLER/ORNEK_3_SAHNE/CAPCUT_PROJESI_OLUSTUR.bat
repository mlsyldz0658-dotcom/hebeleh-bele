@echo off
chcp 65001 >nul
echo CapCut'i kapat, sonra bir tusa bas.
pause >nul
python "%~dp0..\..\ARACLAR\seslendir.py" "%~dp0."
if errorlevel 1 goto hata
python "%~dp0..\..\ARACLAR\capcut_film.py" "%~dp0."
if errorlevel 1 goto hata
echo TAMAM. CapCut'i ac; proje en ustte.
pause
exit /b
:hata
echo HATA OLDU. Ekran goruntusunu Claude'a gonder.
pause
