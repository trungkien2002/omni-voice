# Tiến trình Omni Voice

## Trạng thái hiện tại

- 2026-10-25: đã đẩy mã nguồn và thư viện giọng lên main tại repository GitHub công khai https://github.com/trungkien2002/omni-voice.

- Đã triển khai ứng dụng Omni Voice riêng, giữ `run.bat` và hoàn thành bộ cài EXE + BIN offline trong `release/`, gồm model và runtime.
- Đã thay nhiều chương bằng nhiều giọng/vai thoại, giữ giao diện người dùng đã thiết kế. Lời dẫn/phần nghe lại ghép cùng các vai; sinh WAV/MP3 thật qua UI trên GPU đã qua.
- Cấu hình tự lưu và khôi phục giữa hai tiến trình đã qua kiểm tra. Tiếp theo: dùng bộ cài trên máy đích và nghe chất lượng/giọng đã chọn; laptop RAM 8 GB và Windows sạch chưa kiểm chứng.

## 2026-10-10

- Thiết kế lại toàn bộ giao diện Omni Voice tối ưu cho người lớn tuổi / gia đình sử dụng:
  * Chia bố cục rõ ràng thành 3 bước thao tác mạch lạc ([BƯỚC 1] Chọn nội dung -> [BƯỚC 2] Chọn giọng & cách đọc -> [BƯỚC 3] Bắt đầu & nghe kết quả).
  * Nút bấm to bản, màu sắc nổi bật có độ tương phản cao (Nút tạo màu xanh đậm, Nút dừng màu đỏ, Nút nghe thử màu xanh dương, Nút nghe kết quả màu xanh lá, Nút mở thư mục màu đá phiến).
  * Thêm các nút chọn nhanh tốc độ đọc (Chậm 0.8x, Chuẩn 1.0x, Nhanh 1.2x) để mẹ dễ bấm chỉ với 1 click.
  * Hộp trạng thái to rõ, có màu sắc trực quan (Xanh lá khi sẵn sàng/xong, Vàng khi đang chạy, Đỏ khi lỗi).
  * Thu gọn thông số kỹ thuật (GPU, Pitch, Steps, Guidance, Watermark) vào mục Cài đặt nâng cao để không làm rối mắt.
  * Bố cục vừa vặn hiển thị 100% trên màn hình chuẩn và nhỏ (1000x740, 1220x900) mà không bị che khuất hoặc sinh thanh cuộn dọc không cần thiết.
  * Tạo bộ icon dấu tích checkmark và mũi tên dropdown sắc nét, loại bỏ triệt để lỗi hiển thị ô vuông ký tự.
  * Thêm tông màu nền tối dịu mắt (Eye-care Slate) làm mặc định để chống chói mắt cho người lớn tuổi, đồng thời bổ sung nút chuyển đổi Sáng / Tối linh hoạt trên thanh tiêu đề và ghi nhớ phiên làm việc.
  * Đã chụp ảnh giao diện và chạy 5/5 unit tests thành công.
- Người dùng yêu cầu triển khai ngay, launcher run.bat, giao diện dễ nhìn/dễ dùng cho mẹ và mở rộng sau. Đã xây UI PySide6 tiếng Việt, chia chế độ đơn/batch, ẩn thông số nâng cao và giữ nút tạo/dừng/nghe cố định.
- Tạo môi trường Python 3.12 riêng. Bộ Transformers 4.57.1 thử ban đầu thiếu HiggsAudioV2TokenizerModel; chuyển sang 5.17.0 và xác minh import/nạp model. Torch/TorchAudio 2.8.0+cu128 hoạt động trên RTX 5070.
- Tách TTS và bổ sung điều phối đầu ra: lỗi/hủy không đánh dấu hoàn thành; xác minh audio/SRT; không ghi đè kết quả cũ; skip theo fingerprint; ghép giữ file lẻ. Sửa device, punctuation, session và watermark tại bản mới.
- Sao chép package, voices và model riêng; SHA-256 model weights khớp bản nguồn. Không sao chép settings/session của ToolTruyen và không sửa mã nguồn gốc.
- 5 unit tests qua, pip check sạch, kiểm tra cú pháp/import thành công. Sinh WAV thật 24 kHz; kiểm tra qua Qt: WAV+SRT, 2 chương MP3, ghép MP3/SRT, giữ file lẻ, UI bật lại sau xử lý. QMediaPlayer không lỗi và timeline phát tăng.
- Xem ảnh Qt ở 1220×900/1000×740; hướng dẫn trong README.md, phiên bản dependencies trong requirements.lock.txt. Ranh giới: chưa nghe thủ công toàn bộ giọng/kiểm thử truyện dài/CPU/FLAC/OGG end-to-end.
- Kiểm tra launcher trực tiếp phát hiện batch cần xuống dòng CRLF trên Windows; đã sửa run.bat/setup.bat sang CRLF và chạy lại run.bat để mở cửa sổ ứng dụng.
- Người dùng yêu cầu dự án mới chỉ cho TTS OmniVoice và chọn chuẩn bị thư mục/đặc tả trước.
- Đọc kỹ UI, single/batch worker, danh sách giọng, điều khiển, watermark, session, manifest, ghép audio, engine, model manager, phụ đề, từ điển và ngắt nghỉ của nguồn.
- Ghi rõ các tính năng có UI nhưng chưa nối đầy đủ: CPU, ngắt nghỉ dấu câu, tiến độ model. Ghi rõ tags cảm xúc không sinh âm thanh cảm xúc trong luồng hiện tại.
- Tạo `info.md`, `docs/omnivoice-spec.md`, `progress.md`. Không sửa mã ToolTruyen, không sao chép cấu hình phiên/bí mật, không chạy model hoặc gọi dịch vụ ngoài.
- Đối chiếu mã runtime, dung lượng model và datasheet ASUS khi người dùng hỏi chạy B1402CVA-NK0157W RAM 8 GB. Kết luận có CPU fallback nhưng chưa xác nhận sinh audio ổn định trên laptop này; không lấy kết quả RTX 5070 làm bằng chứng cho 8 GB/CPU. Chưa sửa mã hoặc triển khai bản laptop.

## 2026-10-10 — Thay nhiều chương bằng bài nghe nhiều vai

- Theo yêu cầu mới, giữ thiết kế ba bước/sáng tối/nút lớn người dùng đã làm; bỏ toàn bộ tab và luồng batch/skip/ghép chương. Sao lưu mã trước thay đổi tại `_backups/2026-10-10-dialogue/`.
- Thêm `dialogue.py` nhận diện nhãn nhân vật và Lời dẫn, cảnh báo tên giới thiệu khác thoại. Giữ hướng dẫn/Now listen again và đủ mọi lần lặp, không đọc nhãn tên.
- Bảng giọng riêng từng vai, nghe mẫu, lọc giọng, khoảng nghỉ; lưu/khôi phục lựa chọn. Thiếu giọng chặn tạo. Phần cài đặt cuộn ở màn nhỏ, bước 3 luôn hiển thị; sửa widget khóa nhập trong khi chạy và widget bảng cũ còn hiện khi nhận diện lại.
- Worker sinh lượt bằng giọng tương ứng, cache lượt lặp và prompt, ghép streaming thành một bài audio/SRT theo thời lượng thật. Lỗi/hủy không công bố bài thiếu và không ghi đè kết quả cũ.
- 12/12 unit tests qua; kiểm tra khôi phục phiên/filter/theme/dictionary/gap qua. Compile kiểm tra thành công.
- Sinh thật bằng UI/Qt worker trên RTX 5070: đoạn đơn; hai ví dụ đầy đủ Lan/Duy (WAV 67,389 giây), Mai/Nam (MP3 56,243 giây), mỗi bài 22 lượt; bốn nhân vật + lời dẫn (WAV 7,913 giây). Báo cáo tại `_qa/dialogue-real/runtime-report.json`, không sửa phiên lưu của người dùng khi QA.
- QMediaPlayer phát không lỗi, position tăng; UI mở lại sau worker. Xem ảnh sáng/tối 1000×740 và bốn vai 1220×900. README/đặc tả/info được cập nhật; đặc tả khảo sát ban đầu được đánh dấu tham chiếu cũ.
- Giới hạn: chưa nghe thủ công mọi giọng, chưa benchmark CPU/laptop 8 GB hoặc thử FLAC/OGG end-to-end; hội thoại cần nhãn Tên: rõ ràng, chưa suy đoán vai tự do.

## 2026-10-10 — Điều tra phản ánh giọng Nam thay đổi

- Đọc phiên đang lưu và được người dùng xác nhận: Nam = Anh Khôi, Mai = Bé My, bài Mai/Nam tiếng Anh. Không đổi thiết lập hoặc âm thanh gốc trong Downloads.
- Thêm script QA `qa_voice_consistency.py`, ghi vết conditioning khi chạy lại bài 22 lượt: Nam 5 câu khác nhau cùng prompt/hash/tệp, prompt không bị sửa; routing đúng toàn bộ bài, waveform 10 câu nghe lại giống lần đầu. Chưa có bằng chứng lỗi gán giọng trong lần tái hiện.
- Phân tích F0 khoảng 130–150 Hz giữa 5 câu tái hiện, chỉ là chẩn đoán cao độ, không kết luận danh tính speaker. Không dùng kết quả kỹ thuật để phủ nhận cảm nhận của người dùng.
- Tham khảo hướng dẫn chính thức về dùng mẫu cùng ngôn ngữ. Tạo mẫu A/B chỉ gồm 5 câu Nam (Anh Khôi so với Adam Stone tiếng Anh), giữ các thông số khác; script `qa_voice_comparison.py`, lưu riêng `_qa/voice-consistency/`.
- Có lỗi encoding console cp1252 trong script kiểm tra ban đầu; chỉ ảnh hưởng in log, kiểm tra/sinh audio và assertions hoàn tất. Đã sửa script stdout UTF-8 cho lần chạy sau.
- Chưa sửa mã sản phẩm vì chưa xác định lỗi routing; cần đánh giá nghe đối chiếu trước khi chọn biện pháp ổn định giọng. Không khẳng định người dùng nghe nhầm hoặc chất lượng clone được bảo đảm.

## 2026-10-10 — Đóng gói bộ cài offline

- Người dùng yêu cầu EXE + bộ cài, kèm model và không cần người dùng cài thêm dependency.
- Dựng cây runtime riêng, launcher Windows, model/audio tokenizer/82 giọng, FFmpeg, DLL runtime; tách nơi lưu cấu hình của bản cài khỏi tài nguyên. Nguồn run.bat và phiên cá nhân được giữ.
- Compiler Inno Setup 7.1 được tải từ phát hành chính thức; Authenticode Valid, Pyrsys B.V. Chuyển nén sang ZIP để giảm thời gian build model lớn. Bộ cài EXE + BIN, không tải tài nguyên lúc cài.
- 12 unit tests và QA khôi phục phiên sau thay đổi đường dẫn đều qua. Stage test đã xác minh hashes model/dependencies nội bộ/FFmpeg, quét 82 voices và sinh dialogue MP3; CPU/kiểm thử bộ cài còn đang chạy.
- Sửa ffprobe scan để không bật console khi dùng EXE. Script QA đầu có runtime file đang dùng gây lỗi ghi đè khi dựng lại; chỉ dừng process QA thuộc stage rồi dựng lại, không đóng cửa sổ người dùng.

- Hoàn tất build EXE 5,6 MB + BIN 6,97 GB. Kiểm thử cài, EXE chạy runtime nội bộ từ thư mục làm việc Windows, sinh thật MP3 nhiều vai GPU và WAV CPU offline, gỡ cài: tất cả exit 0; model và đăng ký uninstall được gỡ. Không thử Windows sạch/VM hoặc máy 8 GB.
- Người dùng bổ sung yêu cầu ghi nhớ config. Xác nhận tính năng đã có và nằm trong bộ cài; kiểm tra hai tiến trình riêng: tự lưu trước đóng, mở lại khôi phục toàn bộ options, giọng từng vai, nội dung, khoảng nghỉ, nơi lưu, từ điển, SRT và theme. Script `qa_config_restart.py`, báo cáo `_qa/packaging/config-restore-report.json`. Giữ cấu hình cá nhân của bản nguồn.
- Cập nhật README, hướng dẫn trong release và thông tin dự án. Bộ cài chưa ký số; cần giữ EXE và BIN cùng thư mục khi phân phối.

## 2026-10-11 — Yêu cầu dùng từ xa không setup phía mẹ

- Xác nhận hai máy ở xa; mẹ không thể tự cài/setup Tailscale hay phần mềm kết nối. Yêu cầu phía mẹ chỉ mở và dùng.
- Đề xuất giao diện web qua link riêng, xử lý model trên máy người dùng, kết nối/tunnel chuẩn bị ở phía máy xử lý. Đã đối chiếu tài liệu Cloudflare về truy cập ứng dụng web công khai bằng trình duyệt. Chưa triển khai hoặc công bố endpoint; chờ chọn phương án.



## 2026-10-25 — Lưu trữ GitHub

- Khởi tạo Git/main, tạo repo riêng tư theo yêu cầu đưa folder lên GitHub.
- Bổ sung .gitignore cho backup, release.rar, môi trường và khóa bí mật; giữ nguyên tệp cục bộ. Danh sách trước commit có 336 tệp, không có tệp vượt 100 MB; kiểm tra mẫu token/private key trong nguồn không có kết quả.
- Chỉ thay đổi lưu trữ/tài liệu, không sửa runtime và không chạy lại kiểm thử sinh giọng.

- Push đầu tiên thành công; main theo dõi origin/main. Đối chiếu commit trên remote sau push để xác nhận đồng bộ.


## 2026-10-25 — Kiểm tra bí mật và công khai repository

- Kiểm tra tên/nội dung 336 tệp và lịch sử hai commit: không phát hiện API key, token, password, private key hay URL chứa credential. Kiểm tra văn bản giọng mẫu không có mẫu thông tin tài khoản riêng tư; chưa nghe toàn bộ 82 WAV.
- Xác nhận session.json không được track; config/resources.json chỉ chứa đường dẫn model tương đối. Tên openai/whisper là model ID, không phải khóa API.
- Đã chuyển GitHub sang public theo yêu cầu; API xác nhận private=false. Không thay đổi mã ứng dụng.

