# Đặc tả tham chiếu OmniVoice

> Tài liệu khảo sát nguồn và đề xuất ban đầu. Yêu cầu mới đã bỏ nhiều chương, thay bằng nhiều giọng/vai thoại; đặc tả hiện hành nằm trong [dialogue-spec.md](dialogue-spec.md). Các đề xuất nhiều chương/skip/manifest bên dưới không còn là phạm vi ứng dụng hiện tại.

Ngày khảo sát: 2026-10-10. Đây là đặc tả chuẩn bị, không phải xác nhận ứng dụng mới đã triển khai. Phạm vi tổng thể đã được người dùng xác nhận; danh sách tiện ích và giải pháp kỹ thuật bên dưới là đề xuất.

## 1. Mục tiêu

Ứng dụng riêng cho chuyển văn bản thành giọng đọc OmniVoice. Hai cách sử dụng tham chiếu: nhập/nạp một đoạn văn bản và chạy nhiều tệp TXT theo chương. Cho phép chọn giọng, điều chỉnh cách đọc, chọn đầu ra và theo dõi xử lý.

## 2. Chức năng nguồn đã đọc

| Nhóm | Hành vi trong mã hiện tại | Ghi chú cho ứng dụng mới |
|---|---|---|
| Nhập văn bản | Gõ/dán; nạp TXT, nhận diện encoding, xử lý TXT chứa HTML | Đề xuất giữ làm chức năng cốt lõi |
| Thư mục chương | Quét TXT ở cấp thư mục đã chọn, sắp theo số trong tên, chọn phạm vi theo vị trí danh sách | Chưa quét thư mục con; phạm vi không nhất thiết là số chương ghi trong nội dung |
| Giọng mẫu | Quét audio/metadata; lọc giới tính và ngôn ngữ; hiện tên/phong cách; nghe mẫu bằng winsound | Nghe mẫu là phát bản thu mẫu, không sinh thử văn bản mới |
| Clone prompt | Dùng audio mẫu và transcript để tạo voice_clone_prompt | Không phải chức năng biến đổi audio đầu vào thành audio đổi giọng |
| Speed | 0,5–2,0; mặc định 1,0; truyền vào model | Đề xuất giữ |
| Pitch | 0,5–2,0; mặc định 1,0; hậu xử lý bằng torchaudio | Lỗi hậu xử lý hiện có thể chỉ log và giữ pitch cũ |
| Volume | 0,1–2,0; mặc định 1,0; nhân biên độ và giới hạn clipping | Đề xuất giữ |
| Steps | 1/2/4/8/16/32/64; mặc định 32 | Engine chuyển thành num_step |
| Guidance | 1,0–4,0 theo bước 0,5; mặc định 3,0 | Truyền guidance_scale |
| Temperature | 0,1–1,0; mặc định 0,1 | Truyền class_temperature |
| Postprocess | Checkbox mặc định bật | Truyền postprocess_output |
| CPU/GPU | Có combo GPU auto/CPU và lưu phiên | Chưa truyền lựa chọn CPU vào runtime; model tự chọn CUDA nếu có |
| Ngắt nghỉ thủ công | Break tag theo giây/ms, chèn khoảng audio im lặng | Đề xuất giữ |
| Audio tags | pause/breath/sigh/laugh… đổi thành khoảng im lặng; whisper/shouting… bị bỏ | Không được mô tả là sinh tiếng cười, thở hoặc đọc cảm xúc thật |
| Ngắt nghỉ dấu câu | Dialog cấu hình chấm/phẩy/chấm phẩy/hai chấm/hỏi/cảm thán/xuống dòng | Hàm add_text_with_punctuation được import nhưng không áp dụng vào plan trong engine hiện tại |
| Từ điển | Danh sách thay chuỗi văn bản trước khi sinh audio | Config đang ở bộ nhớ module; session không lưu danh sách này |
| Import phụ đề | SRT/VTT/ASS thành chữ và break dựa trên khoảng trống giữa cue | Không ép lời đọc vào đúng độ dài từng cue gốc; không phải đồng bộ lồng tiếng chính xác |
| Xuất audio | 24 kHz; WAV/MP3/FLAC/OGG; chọn thư mục | Single dùng output.<format>; định dạng chuyển đổi cần FFmpeg |
| Xuất SRT | Chia lời thành cụm tối đa khoảng 10 từ; chia thời gian theo tỷ lệ ký tự trong audio chunk | Thời gian ước lượng trong chunk, không phải word alignment |
| Watermark | Sinh đoạn đọc nhận diện kênh, cache audio, chèn ở ranh giới chunk | Chu kỳ 5/10/15/20/30/45/60 phút, mặc định 10; không chèn chính xác tới từng giây |
| Batch tuần tự | QThread sinh chương; chọn phạm vi; tiến sang chương kế | Đề xuất một job sinh audio tại một thời điểm |
| Bỏ qua đã làm | Manifest .completed_chapters.json hoặc file audio >1 KB | Chưa kiểm tra khả năng giải mã hay khớp văn bản/cấu hình/giọng |
| Ghép chương | Gộp mỗi N chương hoặc tất cả; dịch SRT theo thời lượng audio | Hiện xóa file audio/SRT thành phần sau khi ghép báo thành công |
| Dừng | Cờ dừng; kiểm tra giữa các bước/chunk, chờ worker tối đa 3 giây trên UI | Không ngắt ngay một lần gọi model.generate đang chạy |
| Lưu phiên | Text đơn, thư mục chương/ra, giọng, bộ lọc, điều khiển, batch, watermark | Chưa lưu từ điển/ngắt nghỉ dấu câu; các đường dẫn nguồn không nên mang nguyên sang app mới |
| Model/progress | Tự tìm/tải/giải nén model, runtime dùng lại trong phiên; có vùng model status trên UI | Callback tiến độ engine hiện là lambda rỗng; chưa thấy cập nhật widgets đầy đủ |

## 3. Luồng xử lý nguồn

1. Kiểm tra/tìm model; nếu chưa có, model manager có thể tải và giải nén.
2. Nạp model, chọn CUDA hoặc CPU tự động, dtype tương ứng float16/float32.
3. Đọc giọng mẫu/metadata và tạo conditioning prompt.
4. Bỏ các dòng phân cách rác; áp dụng từ điển; chuyển/bỏ audio tags.
5. Lập plan gồm text chunk và khoảng im lặng; split text dùng ngưỡng mặc định 420 ký tự.
6. Sinh từng chunk, tối đa 3 lần thử; chuẩn hóa audio, trim silence, điều chỉnh pitch/volume, chèn watermark nếu tới ngưỡng.
7. Ghép các mảng audio trong bộ nhớ, lưu định dạng đã chọn và SRT nếu bật.
8. Batch cập nhật manifest, tích lũy nhóm để ghép và chạy chương kế tiếp.

## 4. Các điểm phải xử lý khi tách (đề xuất)

- Thành công/thất bại/hủy cần kết quả rõ ràng. Engine hiện có nhánh chỉ yield lỗi rồi return, trong khi worker vẫn phát work_completed và batch ghi hoàn thành.
- Chunk lỗi không được âm thầm bỏ rồi báo toàn bộ thành công; không tạo phụ đề giả cho nội dung chưa có audio.
- Timeline phải tăng theo audio thực tế ngay cả khi SRT tắt để watermark hoạt động đúng.
- Truyền device vào runtime; đổi thiết bị phải có cơ chế nạp lại model thích hợp.
- Nối cấu hình dấu câu vào generation plan, lưu từ điển và cấu hình nghỉ cùng session.
- Dừng phải đợi worker thực sự kết thúc trước khi nhận job mới. Cleanup dùng đúng tệp của job hiện tại; mã nguồn dùng batch_index trên danh sách toàn bộ ở nhánh stop dù batch có thể chọn phạm vi con.
- Ghép thành công cần xác minh audio và SRT trước khi xử lý file thành phần. Đề xuất mặc định giữ file lẻ, việc xóa là lựa chọn riêng chưa được người dùng chốt.
- Bỏ qua chương dựa trên đầu ra đã xác minh; manifest cần đủ dữ liệu nhận diện input, giọng và cấu hình để tránh bỏ qua kết quả cũ không phù hợp.
- Đầu ra nên ghi tệp tạm rồi thay thế khi thành công; xử lý tên trùng cần rõ ràng để bảo vệ bản đã tạo trước đó.
- Dữ liệu model có thể rất lớn; quyết định sao chép hay dùng chung còn mở. Không sao chép config/settings.json hoặc session cũ như cấu hình mặc định của app mới.
- Tách log/progress và I/O ghép file khỏi luồng UI; thư viện tùy chọn bị thiếu phải có thông báo có thể xử lý.

## 5. Bản đồ mã cần tham chiếu

| Vai trò | Đường dẫn tương đối trong ToolTruyen |
|---|---|
| Giao diện và worker, batch/session/manifest | app/tabs/tab_omnivoice.py |
| Engine, runtime, config, split/normalize/save | process/tts/omnivoice_engine.py |
| Tìm/tải model | process/tts/model_manager.py |
| Quét giọng/metadata và prompt | process/tts/voice_manager.py |
| Hậu xử lý pitch/volume | process/tts/audio_controls.py |
| Break/audio tags | process/tts/break_tags.py |
| Ngắt nghỉ dấu câu | process/tts/punctuation.py; app/dialogs/punctuation_dialog.py |
| Từ điển | process/tts/pronunciation.py; app/dialogs/dictionary_dialog.py |
| Nhập phụ đề | process/tts/subtitle_parser.py |
| Xuất/shift phụ đề | process/tts/srt_generator.py |
| Ghép audio/chương | process/tts/audio_merger.py |
| Dialog break | app/dialogs/break_tags_dialog.py |
| Đọc TXT | process/reader/reader.py |
| Thành phần UI tham chiếu | app/theme.py; app/widgets/log_viewer.py; app/widgets/progress_widget.py |
| Package/model/giọng | omnivoice/; data/models/; data/voices/ |

## 6. Kiến trúc ứng dụng mới (đề xuất, chưa chốt)

- Một cửa sổ TTS, hai chế độ nội dung đơn và thư mục chương; không cần sidebar các công cụ truyện/video.
- Tách UI khỏi dịch vụ sinh audio, quản lý model/giọng, job queue, session và đầu ra.
- Model/voice paths và cấu hình thuộc dự án mới; có thể tham chiếu thư viện chung chỉ đọc nếu người dùng chọn.
- Môi trường Python riêng, dependencies tương thích model và GPU; chưa chọn phiên bản hoặc cài package trong giai đoạn chuẩn bị.

## 7. Tiêu chí nghiệm thu đề xuất cho giai đoạn triển khai

- Sinh một đoạn tiếng Việt với giọng đã chọn; audio giải mã được và có nội dung đầy đủ.
- Chạy một nhóm chương tên có số, đúng thứ tự/phạm vi; xác minh bỏ qua, lỗi và chạy lại.
- Device CPU và GPU auto thực sự có hiệu lực; báo đúng thiết bị đang chạy.
- Break, từ điển, ngắt nghỉ dấu câu có tác dụng; khôi phục cấu hình sau mở lại.
- WAV và các định dạng khác tạo được nếu FFmpeg sẵn sàng; lỗi thiếu công cụ hiển thị rõ.
- Watermark hoạt động cả khi bật/tắt SRT; phụ đề/ghép chương không trôi timeline do chương lỗi hoặc im lặng.
- Hủy không đánh dấu hoàn thành, không nhận job chồng và không xóa nhầm đầu ra đã thành công.
- Giao diện được kiểm tra trực quan; kiểm tra cú pháp/build không thay thế kiểm tra GUI và audio thực tế.

## 8. Ranh giới khảo sát

Đặc tả dựa trên mã nguồn đã đọc; chưa chạy model, nghe kết quả, xác minh GPU hoặc thử các luồng GUI. Các lỗi/giới hạn nêu trên là kết luận từ đường đi mã, chưa phải kết quả kiểm thử runtime.
