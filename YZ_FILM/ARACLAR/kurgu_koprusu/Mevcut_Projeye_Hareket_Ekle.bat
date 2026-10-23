@echo off
setlocal
title Kurgu Koprusu V5 - Mevcut proje
py "%~dp0mevcut_projeye_hareket.py"
if errorlevel 1 echo Hata oldu. Ekrani veya hareket_hata.txt dosyasini paylasin.
pause
