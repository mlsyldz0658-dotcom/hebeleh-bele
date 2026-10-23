@echo off
chcp 65001 >nul
set /p AD=Yeni filmin adi (bosluksuz, ornek EMBERFALL): 
python "%~dp0ARACLAR\yeni_film.py" "%AD%"
pause

