@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Omni Voice
if not exist ".venv\Scripts\python.exe" (
    echo Chưa có môi trường Python. Hãy chạy setup.bat trước.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -X utf8 main.py
if errorlevel 1 (
    echo.
    echo Không mở được Omni Voice. Vui lòng giữ thông báo lỗi này để kiểm tra.
    pause
)
