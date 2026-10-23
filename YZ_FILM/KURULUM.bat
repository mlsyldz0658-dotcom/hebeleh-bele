@echo off
chcp 65001 >nul
title YZ_FILM KURULUM
where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo PYTHON BULUNAMADI.
  echo 1^) https://www.python.org/downloads/release/python-31011/ adresinden 'Windows installer 64-bit' indir.
  echo 2^) Kurarken en alttaki 'Add python.exe to PATH' kutusunu MUTLAKA isaretle.
  echo 3^) Kurulum bitince bu dosyaya tekrar cift tikla.
  pause
  exit /b
)
echo Kurulum basliyor. Ilk seferde internet hizina gore 10-40 dakika surebilir.
python "%~dp0ARACLAR\kurulum.py"
pause

