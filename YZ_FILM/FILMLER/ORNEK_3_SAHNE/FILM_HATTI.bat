@echo off
chcp 65001 >nul
echo Film hatti calisiyor. Kredi harcayan asamadan once onay sorar.
python "%~dp0..\..\ARACLAR\film.py" "%~dp0."
pause
