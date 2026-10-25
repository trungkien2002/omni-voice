# Đóng gói Omni Voice cho Windows

## Cấu trúc

- `Launcher.cs`: EXE giao diện Windows khởi chạy Python nội bộ, không mở console. Chỉ dùng .NET Framework có sẵn trên Windows 10/11.
- `build.py`: sao chép Python 3.12 và dependencies hiện dùng, model + audio tokenizer + voices + FFmpeg, biên dịch launcher và gọi Inno Setup.
- `OmniVoice.iss`: bộ cài theo người dùng, không yêu cầu quyền admin; shortcut Desktop/Start Menu và trình gỡ cài đặt. Bộ cài lớn có EXE + một tệp BIN dữ liệu.
- `stage/OmniVoice/`: cây ứng dụng độc lập; EXE cần toàn bộ cây này. Không chuyển riêng EXE nhỏ sang máy khác.
- `../release/`: bộ cài để chuyển cho người dùng.

## Dựng lại

1. Dùng môi trường `.venv` đã chuẩn bị và toàn bộ model/voices trong `data/`.
2. Đặt compiler Inno Setup tại `packaging/tools/inno/ISCC.exe`, và license OmniVoice chính thức tại `packaging/OmniVoice-LICENSE.txt`.
3. Chạy `.venv\Scripts\python.exe -X utf8 packaging\build.py`.
4. Chuyển toàn bộ EXE/BIN trong `release/` cùng nhau.

Build giữ nguồn và bản run.bat. Python runtime, DLL và thư viện nằm trong `_runtime`; Python dùng `python312._pth` để bỏ đường dẫn Python hệ thống/registry/user site. Launcher loại PYTHONHOME/PYTHONPATH và dùng PATH nội bộ. Bản cài lưu phiên/log tại `%LOCALAPPDATA%\OmniVoice`; tài nguyên cài đặt được dùng chỉ để đọc. Không đóng gói phiên cá nhân, file hội thoại hoặc audio của người dùng.

## Kiểm tra

`OmniVoice.exe --self-test "đường dẫn báo cáo.json"` chạy kiểm tra có chủ đích: hashes model, dependency origins, FFmpeg, quét voices, job hội thoại MP3, job CPU WAV và ảnh UI. Python socket bị chặn, cache HF riêng trống. Khi QA, đặt LOCALAPPDATA riêng và thư mục báo cáo riêng để tránh phiên đang dùng. Tham số này không dùng trong shortcut bình thường.

Đầu ra chưa ký số. Không kiểm chứng máy Windows sạch/VM hoặc máy RAM 8 GB chỉ bằng kiểm tra trên máy phát triển.
