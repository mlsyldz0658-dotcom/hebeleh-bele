@echo off
setlocal
title Kurgu Koprusu V5
set "KURGU_SCRIPT=%~dp0kurgu_koprusu.py"
if not exist "%KURGU_SCRIPT%" (
 echo kurgu_koprusu.py bulunamadi. Paketi once klasore cikarin.
 pause
 exit /b 1
)
where py >nul 2>&1
if errorlevel 1 (
 echo Python baslaticisi bulunamadi. Bu ekranin goruntusunu paylasin.
 pause
 exit /b 1
)
echo CapCut kapali olmalidir. Acilan pencereden JSON planini secin.
py "%KURGU_SCRIPT%"
set "KURGU_EXIT=%ERRORLEVEL%"
if not "%KURGU_EXIT%"=="0" echo Hata olustu. Yukaridaki mesaji veya kurgu_koprusu_hata.txt dosyasini paylasin.
echo.
pause
exit /b %KURGU_EXIT%
