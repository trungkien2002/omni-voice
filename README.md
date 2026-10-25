# Omni Voice

## Mở ứng dụng

Bản cài Windows nằm trong `release/`: giữ `OmniVoice-Setup-1.0.0.exe` và `OmniVoice-Setup-1.0.0-1.bin` cùng thư mục, chạy EXE và làm theo hướng dẫn. Sau cài đặt, mở biểu tượng **Omni Voice**. Bộ cài gồm Python, thư viện CPU/CUDA, FFmpeg, model, audio tokenizer và toàn bộ giọng mẫu; không cần cài thêm Python hay tải model. Hỗ trợ Windows 10/11 x64.

Cấu hình bản cài nằm tại `%LOCALAPPDATA%\OmniVoice\config`, log tại `%LOCALAPPDATA%\OmniVoice\logs\app.log`. Bộ cài không mang theo hội thoại hoặc phiên cá nhân của máy dựng.

App tự lưu cấu hình sau khi thay đổi và khi đóng cửa sổ; lần mở sau khôi phục giọng từng vai, nội dung, tốc độ, âm lượng, khoảng nghỉ, nơi lưu, định dạng, thông số nâng cao và giao diện sáng/tối. Không cần bấm nút Lưu hoặc thiết lập lại. Đã kiểm tra khôi phục bằng hai tiến trình riêng với runtime đóng gói.

Nhấp đúp **run.bat** trong thư mục này. Môi trường Python, model và thư viện giọng đã được chuẩn bị trên máy hiện tại. Không cần chạy setup.bat mỗi lần sử dụng.

## Tạo một đoạn giọng đọc

1. Chọn **Một đoạn văn bản**, gõ/dán nội dung hoặc bấm **Mở tệp văn bản**.
2. Chọn giọng bên phải. Bấm **Nghe giọng mẫu** nếu muốn nghe trước bản thu mẫu.
3. Chọn nơi lưu nếu cần; mặc định là thư mục `outputs` trong dự án.
4. Bấm **Tạo giọng đọc**. Chờ thông báo hoàn tất, rồi bấm **Nghe kết quả** hoặc **Mở thư mục lưu**.

## Tạo bài nghe nhiều giọng / vai thoại

1. Chọn **Nhiều giọng / Vai thoại**, dán toàn bộ bài nghe hoặc mở TXT.
2. Viết mỗi lượt theo dạng `Lan: Hi, Duy.` hoặc `Duy: Yes, I am.` trên một dòng. Tool tự nhận diện các tên này; hỗ trợ nhiều nhân vật, không giới hạn ở hai người.
3. Chọn giọng trong bảng cho từng nhân vật và **Lời dẫn**. Với bài tiếng Anh, chọn bộ lọc **English**. Bấm **Mẫu** để nghe bản thu mẫu.
4. Đặt khoảng nghỉ giữa lượt nếu cần, chọn nơi lưu và bấm **BẮT ĐẦU TẠO GIỌNG ĐỌC**. Kết quả là một tệp âm thanh ghép theo đúng thứ tự.

Các dòng không có nhãn tên, như **Part II. Listen…** và **Now listen again**, được đọc bằng giọng **Lời dẫn**. Tên `Lan:`/`Duy:` không được đọc thành tiếng. Nếu nội dung đã lặp hai lần, tool giữ đủ hai lần; câu “You will hear the recording twice” không tự tạo thêm lần lặp.

Vai lấy từ nhãn thoại, không suy đoán từ phần giới thiệu. Ví dụ giới thiệu ghi Nam/Lan nhưng thoại ghi Lan/Duy thì bảng có Lan, Duy và Lời dẫn; tool cảnh báo để bạn kiểm tra, vẫn giữ nguyên lời giới thiệu. Hội thoại không có nhãn rõ ràng cần thêm tên trước mỗi lượt. Tính năng nhiều chương đã được bỏ.

## Các tiện ích

- Tốc độ và âm lượng đặt ngay trên màn chính.
- **Thiết lập nâng cao** có CPU/GPU, pitch, steps, guidance, temperature, postprocess và lời nhận diện kênh.
- Chèn khoảng nghỉ, từ điển phát âm và nghỉ theo dấu câu.
- Nạp SRT/VTT/ASS thành nội dung đọc có khoảng nghỉ; xuất thêm SRT cho audio mới.
- WAV, MP3, FLAC và OGG. Đầu ra SRT chia thời gian trong từng đoạn theo tỷ lệ chữ, chưa căn chỉnh từng từ.
- Lưu và khôi phục phiên làm việc, gồm nội dung hội thoại, giọng từng vai, khoảng nghỉ, giao diện sáng/tối, từ điển và thiết lập nghỉ. Đổi bộ lọc không làm mất giọng đã gán.

## Dừng và xử lý lỗi

**DỪNG LẠI** yêu cầu dừng sau thao tác model hiện đang chạy; có thể cần chờ thêm. Bài đang làm dở không được công bố. Kết quả trước đó được giữ; tên trùng được thêm số. Ứng dụng chờ worker kết thúc trước khi nhận lần tạo tiếp theo.

Nếu có lỗi, xem thông báo trên màn hình và `config/last_error.log`. Lỗi ở một vai sẽ dừng cả bài để tránh xuất bài thiếu lời thoại.

## Tài nguyên và cài đặt

- Python 3.12 riêng trong `.venv`; Torch/TorchAudio 2.8.0 CUDA 12.8, Transformers 5.17.0.
- Package OmniVoice, model và voices đã sao chép vào dự án. Ứng dụng không cần mã ToolTruyen để chạy và không gửi nội dung tới API.
- FFmpeg/FFprobe dùng từ PATH của máy; có fallback FFmpeg của CapCut. Nếu chuyển sang máy khác cần chuẩn bị lại Python, FFmpeg và môi trường bằng `setup.bat`.
- Model nằm trong `data/models/models--k2-fsa--OmniVoice`; đường dẫn thay thế được cấu hình trong `config/resources.json`.
- `requirements.lock.txt` ghi các phiên bản đã cài để tra cứu; `setup.bat` cài Torch theo index CUDA riêng rồi các dependencies ứng dụng.
- Bản nguồn vẫn chạy bằng `run.bat`. Bản cài có EXE và runtime nội bộ; xem `packaging/README.md` để dựng lại. Máy không có CUDA dùng CPU; khả năng dùng ổn định trên laptop RAM 8 GB chưa được xác minh.

## Mở rộng sau này

`app.py` quản lý giao diện; `dialogue.py` nhận diện nhãn vai/lời dẫn; `service.py` sinh từng lượt và ghép audio/SRT; `process/tts/` quản lý TTS; `omnivoice/` là package model kế thừa. Xem `docs/dialogue-spec.md` để biết quy tắc hội thoại.

## Kiểm tra đã thực hiện

12 unit tests qua: nhận diện vai, giữ hướng dẫn/phần lặp, phân giọng cho 3/4/6 nhân vật, thời gian SRT, lỗi/hủy không xuất bài thiếu. Kiểm tra riêng khôi phục phiên và giữ giọng khi đổi bộ lọc. Sinh thật qua UI/worker trên RTX 5070: đoạn đơn, hai bài mẫu đầy đủ (22 lượt mỗi bài, WAV/MP3), bài bốn nhân vật và lời dẫn. QMediaPlayer phát kết quả không lỗi; báo cáo tại `_qa/dialogue-real/runtime-report.json`. Đã xem giao diện sáng/tối và cửa sổ 1000×740/1220×900. Chưa đánh giá nghe thủ công chất lượng mọi giọng hoặc kiểm tra CPU/laptop RAM 8 GB; FLAC/OGG chưa thử sinh end-to-end trong lượt này.
