@echo off
chcp 65001 >nul
echo Kredisiz deneme: sahte gorsel/video/ses ile hatti dener.
python "%~dp0..\..\ARACLAR\film.py" "%~dp0." --saglayici sahte
pause
