@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Cài đặt Omni Voice
if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv
    if errorlevel 1 (
        echo Cần Python 3.12 để tạo môi trường. Hãy cài Python 3.12 và chạy lại.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" -m pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Đã cài đặt. Mở run.bat để sử dụng.
pause
exit /b 0
:failed
echo Cài đặt chưa hoàn tất. Hãy kiểm tra thông báo phía trên.
pause
exit /b 1
