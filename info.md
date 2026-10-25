# Omni Voice — dự án độc lập

## Yêu cầu đã xác nhận

- Dự án mới đặt tại `D:\DATAF\omni voice`, tách khỏi ToolTruyen Studio.
- Chỉ tập trung phần chuyển văn bản thành giọng đọc bằng OmniVoice của ToolTruyen.
- Đã có bản nguồn chạy bằng `run.bat` và bộ cài EXE + BIN Windows đầy đủ model, không cần cài thêm Python/thư viện/FFmpeg hoặc tải model. Kiểm thử cài, sinh offline CPU/GPU và gỡ cài đã qua trên máy dựng.
- Giao diện tiếng Việt rõ ràng, dễ thao tác để mẹ người dùng sử dụng; có nền tảng để thêm chức năng sau.
- Nguồn khảo sát: `D:\DATAF\1. ToolTruyen`, đặc biệt `app/tabs/tab_omnivoice.py` và `process/tts/`.

## Cách hiểu phạm vi

- “Chuyển đổi giọng nói” trong dự án này được hiểu là TTS: văn bản thành audio với giọng mẫu OmniVoice. Chưa có yêu cầu đổi giọng của một bản ghi âm có sẵn.
- Hiện có đọc đoạn đơn và nhiều giọng/vai thoại; giọng mẫu/nghe thử, speed/pitch/volume, thiết lập model, ngắt nghỉ/từ điển, import phụ đề cho đoạn đơn, WAV/MP3/FLAC/OGG/SRT, watermark, dừng và lưu phiên. Nhiều chương/skip/ghép chương đã được bỏ theo yêu cầu mới.
- Crawl, tách/làm sạch truyện, TTS engine khác, Story Maker và dựng video không thuộc phần ứng dụng mới đã yêu cầu.
- Tab Voice Clone riêng chưa được yêu cầu đưa vào. Dùng giọng mẫu để conditioning vẫn thuộc TTS OmniVoice; công cụ tạo thư viện giọng mới là phạm vi riêng.

## Tài liệu

- `docs/dialogue-spec.md`: đặc tả hiện hành cho nhiều vai/lời dẫn.
- `docs/omnivoice-spec.md`: khảo sát nguồn và đề xuất ban đầu; nhiều chương không còn thuộc phạm vi hiện tại.
- `progress.md`: trạng thái và các bước tiếp theo.

## Triển khai hiện tại

- Python 3.12.14/PySide6; môi trường riêng `.venv`; Torch và TorchAudio 2.8.0+cu128, Transformers 5.17.0. Không dùng bộ Torch/TorchAudio lệch phiên bản của Python hệ thống.
- `main.py` khởi chạy; `app.py` là UI; `dialogue.py` nhận diện nhãn vai/lời dẫn; `service.py` quản lý worker/job/ghép từng lượt; `process/tts/` là nghiệp vụ TTS; `omnivoice/` giữ package nguồn và ghi chú bản quyền.
- Giữ giao diện người dùng thiết kế: ba bước, font Segoe UI, nút lớn, preset tốc độ, trạng thái theo màu, nền tối dịu mắt/sáng lưu phiên, nâng cao thu gọn. Hai tab đoạn đơn và nhiều vai; bước 3 tạo/dừng/nghe cố định. Bảng vai và phần cài đặt có cuộn khi nhiều vai/cửa sổ nhỏ.
- Model và 240 tệp mẫu/metadata được sao chép riêng vào `data/`; quét được 82 giọng, 63 giọng có metadata tiếng Việt. Hash weights nguồn và bản sao khớp.
- Sinh audio offline, không gửi văn bản tới API và không tự tải model. FFmpeg/FFprobe là dependency máy; ưu tiên PATH.
- Đầu ra mặc định `outputs/`; tên trùng thêm số. Tệp tạm chỉ công bố sau khi toàn bộ audio/SRT hợp lệ; lỗi/hủy không xuất bài thiếu. Hội thoại xuất một audio/SRT, không công bố file lượt tạm.
- Dừng là yêu cầu hủy hợp tác giữa các bước; chờ model.generate hiện tại xong. UI không cho chạy job mới trước khi worker kết thúc.
- Sửa tại bản mới: CPU thực sự truyền vào runtime, ngắt nghỉ dấu câu vào plan, từ điển và pauses lưu phiên, watermark tăng timeline cả khi không xuất SRT, lỗi sinh không bị báo hoàn thành, không bỏ chunk lỗi rồi xuất kết quả thiếu.
- SRT vẫn chia thời gian trong chunk theo tỷ lệ chữ; import phụ đề chỉ giữ khoảng trống giữa cue, không căn chỉnh lồng tiếng chính xác.

## Nhiều giọng / vai thoại

- Nhận diện tên từ nhãn đầu dòng `Tên: lời thoại`, không suy đoán từ lời giới thiệu. Hỗ trợ nhiều vai; người dùng tự gán giọng và nghe mẫu từng vai.
- Dòng không có nhãn là **Lời dẫn**, gồm hướng dẫn Part II… và Now listen again. Giữ nguyên mọi lượt lặp đã dán, không tự nhân đôi và không đọc tên nhãn.
- Ví dụ giới thiệu Nam/Lan nhưng nhãn Lan/Duy: cảnh báo khác tên, giữ nguyên hướng dẫn, chỉ tạo vai Lan/Duy/Lời dẫn.
- Sinh từng lượt và ghép theo thứ tự với khoảng nghỉ 0–5 giây (mặc định 0,4); timeline dựa trên số mẫu thực. Cache prompt/âm thanh trùng trong job, vẫn giữ đủ các lần lặp. Ghép theo khối và dùng chung một model.
- Phiên schema 2 lưu hội thoại, giọng từng vai, khoảng nghỉ và thiết lập cũ; bộ lọc không xóa giọng đã gán. Phiên batch cũ mở về đoạn đơn.
- Chưa suy đoán vai từ văn bản không nhãn, chưa có speed/pitch riêng từng vai. Không gọi API ngoài.

## Bằng chứng kiểm tra và giới hạn

- 12 unit tests qua: hai mẫu đầy đủ 22 lượt/bài, Unicode/tên, 3/4/6 vai, định tuyến giọng, timeline/SRT, lỗi/hủy, ngắt nghỉ/watermark. Kiểm tra riêng khôi phục phiên/bộ lọc giữ giọng, khoảng nghỉ, theme và từ điển.
- Sinh thật qua Qt UI/worker trên RTX 5070: single WAV; Lan/Duy WAV 67,389 giây; Mai/Nam MP3 56,243 giây; bốn vai + lời dẫn WAV 7,913 giây. Hai bài mẫu giữ đúng 22 lượt theo thứ tự. Báo cáo `_qa/dialogue-real/runtime-report.json`.
- QMediaPlayer phát bài nhiều vai: duration 7913 ms, position tăng, không lỗi; UI bật lại sau xử lý. Đã xem giao diện sáng/tối ở 1000×740 và 1220×900.
- Chưa nghe thủ công chất lượng mọi giọng, chưa kiểm tra bài rất dài, laptop RAM 8 GB/FLAC/OGG end-to-end. Sinh đoạn ngắn CPU trên máy dựng đã qua kiểm thử bộ cài. SRT chưa căn chỉnh từng từ.

## Kiểm tra phản ánh Nam thay đổi giọng giữa câu (2026-10-10)

- Người dùng xác nhận bài Mai/Nam tiếng Anh, Nam gán Anh Khôi (mẫu tiếng Việt), Mai gán Bé My (tiếng Việt), Lời dẫn Adam Stone; 32 steps, temperature 0,1, pitch/speed 1.
- Chạy lại đúng cấu hình, ghi vết prompt thực sự truyền vào model: 5 câu Nam khác nhau đều dùng cùng tệp Anh_Khoi.wav, cùng một prompt/cache và cùng hash tokens; tokens không bị sửa sau sinh. Không phát hiện chuyển sang giọng tự động hoặc gán nhầm vai trong lần tái hiện.
- 10 lượt thoại lặp ở nửa sau có waveform giống hệt nửa đầu. Báo cáo kiểm tra `_qa/voice-consistency/report.json`, audio lượt riêng để đối chiếu. Đây là kiểm tra routing/conditioning, không chứng minh cảm nhận giọng đồng nhất hoặc người dùng nghe nhầm.
- Mỗi câu được sinh độc lập; chưa có kiểm tra embedding nhận diện speaker. F0 trung vị 5 câu Nam trong bản tái hiện khoảng 130–150 Hz; pitch một mình không xác định danh tính giọng.
- Tài liệu chính thức khuyến nghị giọng mẫu cùng ngôn ngữ cho phát âm chuẩn, và ghi rõ clone khác ngôn ngữ mang accent của mẫu: https://github.com/k2-fsa/OmniVoice#voice-cloning. Việc này chưa chứng minh nguyên nhân âm sắc khác giữa câu.
- Đã chuẩn bị bản đối chiếu 5 câu Nam với Anh Khôi và giọng tiếng Anh Adam Stone, cùng các thông số khác. Chưa kết luận đổi giọng sẽ giải quyết độ ổn định; chờ đánh giá nghe. Lượt này chưa sửa engine/UI hoặc lựa chọn giọng lưu của người dùng.

## Khả năng dùng trên laptop RAM 8 GB (đánh giá, chưa benchmark)

- Người dùng hỏi về ASUS ExpertBook B1402CVA-NK0157W RAM 8 GB. Datasheet ASUS cho dòng B1402CVA có đồ họa Intel tích hợp và khe SO-DIMM; cần xác minh cấu hình của máy thực tế trước khi nâng RAM: https://www.asus.com/event/datasheet/asusexpertbookb1-b1402cva.pdf.
- Bản app hiện chỉ chọn CUDA NVIDIA hoặc CPU; không dùng GPU Intel tích hợp. Trên máy không có CUDA, model chạy CPU float32.
- Model và audio tokenizer cục bộ có tổng dung lượng khoảng 3,27 GB trên đĩa; đây không phải mức RAM đỉnh. Cần thêm RAM cho model chạy, tensors, Python và Windows.
- RAM 8 GB có thể mở UI nhưng khả năng sinh ổn định chưa được xác minh; rủi ro thiếu RAM/pagefile và tốc độ CPU thấp, nhất là đọc dài. Khuyến nghị thực dụng là thử đoạn ngắn, 8–16 steps; nếu dùng thường xuyên cân nhắc 16 GB RAM trở lên, không coi đó là mức tối thiểu chính thức hay cam kết tốc độ.

## Bộ cài Windows đầy đủ tài nguyên

- Yêu cầu được xác nhận 2026-10-10: cung cấp EXE và bộ cài, gồm model + audio tokenizer + thư viện giọng; người dùng không phải cài thêm công cụ hay tải tài nguyên.
- Bản cài Windows 10/11 x64, gồm CPython 3.12 riêng, toàn bộ dependencies đang chạy (Torch CPU/CUDA), FFmpeg/FFprobe và DLL runtime. Launcher Windows EXE gọi runtime nội bộ, Python được cách ly bằng python312._pth; không dựa Python/PATH hệ thống.
- Inno Setup cài theo người dùng vào LocalAppData\Programs\Omni Voice, shortcut Desktop/Start Menu và trình gỡ cài đặt, không yêu cầu admin. Model lớn nằm trong dữ liệu BIN đi cùng Setup.exe; phải chuyển toàn bộ bộ cài cùng nhau.
- Giữ phiên người dùng trong LocalAppData\OmniVoice; không đưa session/hội thoại cá nhân/audio đã sinh vào bộ cài. Bản run.bat giữ cấu hình cũ tại dự án.
- `paths.py` tách tài nguyên ROOT và STATE_ROOT ghi được; `bootstrap.py` ghi lỗi startup ra logs/app.log. Mã build tại packaging/build.py, Launcher.cs và OmniVoice.iss; artifacts ở release/.
- Chưa ký số, chưa kiểm chứng Windows sạch/VM hay laptop 8 GB. Đóng gói đầy đủ dependencies không bảo đảm đủ RAM; không tuyên bố khắc phục độ ổn định âm sắc của OmniVoice.

- Đã dựng `release/OmniVoice-Setup-1.0.0.exe` và dữ liệu `OmniVoice-Setup-1.0.0-1.bin` (khoảng 7 GB). Kiểm thử bộ cài: cài thành công, EXE dùng runtime nội bộ, xác minh model, quét 82 giọng, sinh MP3 nhiều vai bằng GPU và WAV bằng CPU offline; gỡ cài thành công. Báo cáo `_qa/packaging/installer-report.json` và `installed-report.json`; không có kết nối mạng trong kiểm thử sinh.

## Ghi nhớ cấu hình

- Yêu cầu xác nhận 2026-10-10: mở app lần sau không phải thiết lập lại. Tính năng tự lưu hiện có được giữ trong bộ cài, lưu sau khoảng 700 ms khi thay đổi và khi đóng cửa sổ, ghi JSON qua tệp tạm và thay thế nguyên tử.
- Lưu nội dung/chế độ, giọng chung và từng vai/lời dẫn, bộ lọc, tốc độ/cao độ/âm lượng, khoảng nghỉ, định dạng/nơi lưu, thông số model, phụ đề, watermark, từ điển/nghỉ theo dấu câu và giao diện sáng/tối.
- Bản cài lưu tại `%LOCALAPPDATA%\OmniVoice\config\session.json`; bản run.bat lưu tại `config/session.json` trong dự án. Không cần nút Lưu. Đã kiểm tra tự lưu trước khi đóng và khôi phục trong tiến trình mới với runtime đóng gói; `_qa/packaging/config-restore-report.json`.

## Sử dụng từ xa trên laptop của mẹ

- Yêu cầu 2026-10-11: hai máy ở xa, dùng Internet; mẹ không thể tự cài hoặc cấu hình phần mềm kết nối, người dùng không có mặt để thiết lập. Trải nghiệm phía mẹ phải chỉ mở lên và sử dụng, giữ thao tác chọn giọng/vai và ghi nhớ cấu hình.
- Phương án đang đề xuất, chưa được duyệt/triển khai: giao diện web tương tự app, model chạy trên máy người dùng; mẹ mở đường link riêng trong trình duyệt sẵn có. Tunnel và dịch vụ chỉ thiết lập phía máy xử lý; cần cơ chế truy cập riêng. Máy xử lý phải bật và có Internet. Chưa thay thế bộ cài offline hiện có.

## Lưu trữ GitHub (2026-10-25)

- Người dùng yêu cầu đưa dự án lên GitHub. Repository riêng tư: https://github.com/trungkien2002/omni-voice ; nhánh chính main.
- Git lưu mã nguồn, tài liệu, script đóng gói/kiểm thử và thư viện giọng. Loại trừ .venv, model, release/, release.rar, _backups, _qa, outputs, session cá nhân và tệp bí mật; các tệp này vẫn giữ trên máy.
- Clone repository chưa đủ để chạy offline: cần chuẩn bị dependency và model theo README; bộ cài đầy đủ vẫn ở máy cục bộ.
