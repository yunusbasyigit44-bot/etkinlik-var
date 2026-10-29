@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Etkinlikler toplaniyor...
py -X utf8 -I toplayici\topla.py
echo.
pause
