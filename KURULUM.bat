@echo off
rem yz_film_set:kurulum_onyukleyici (depoya islenmis sabit dosya; bat_yenile.py dokunmaz)
chcp 65001 >nul
title YZ FILM SETI - KURULUM
cd /d "%~dp0"
set "YZPY="
if exist "%~dp0.claude\bin\python_yolu.txt" set /p YZPY=<"%~dp0.claude\bin\python_yolu.txt"
if defined YZPY if not exist "%YZPY%" set "YZPY="
if not defined YZPY (
  py -3.10 -c "import sys" >nul 2>nul
  if not errorlevel 1 for /f "delims=" %%P in ('py -3.10 -c "import sys;print(sys.executable)"') do set "YZPY=%%P"
)
if not defined YZPY (
  where python >nul 2>nul
  if not errorlevel 1 for /f "delims=" %%P in ('python -c "import sys;print(sys.executable)"') do set "YZPY=%%P"
)
if not defined YZPY (
  echo.
  echo PYTHON BULUNAMADI.
  echo 1^) https://www.python.org/downloads/release/python-31011/ adresinden 'Windows installer 64-bit' indir.
  echo 2^) Kurarken en alttaki 'Add python.exe to PATH' kutusunu MUTLAKA isaretle.
  echo 3^) Kurulum bitince bu dosyaya tekrar cift tikla.
  pause
  exit /b 4
)
"%YZPY%" "%~dp0YZ_FILM\ARACLAR\kurulum.py" %*
pause
