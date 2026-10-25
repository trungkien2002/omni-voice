# Bài nghe nhiều vai — đặc tả hiện hành

Ngày cập nhật: 2026-10-10. Yêu cầu đã xác nhận và triển khai.

- Giữ giao diện người dùng đã thiết kế: ba bước, màu/nút lớn, chế độ sáng/tối, nâng cao thu gọn. Thay tab nhiều chương bằng **Nhiều giọng / Vai thoại**; đọc đoạn đơn vẫn hoạt động.
- Nhận diện cục bộ nhãn `Tên: lời thoại` hoặc dấu `：` đầu dòng, hỗ trợ nhiều vai. Hợp nhất tên khác chữ hoa/thường và Unicode tương đương; giữ cách viết đầu tiên. Dòng nối thụt đầu dòng nối vào lượt trước; các dòng không gắn nhãn là Lời dẫn. Không dùng AI/API suy đoán người nói từ hội thoại không nhãn.
- Các tiền tố hướng dẫn Part/Section/Question/Note/Listen/Hướng dẫn được coi là lời dẫn. Nhãn vai có tối đa 48 ký tự/5 từ. Cần chuẩn bị văn bản rõ nhãn; không cam kết nhận diện mọi định dạng kịch bản tự do.
- Nhân vật lấy từ nhãn thoại. Không tạo vai chỉ vì tên được nhắc trong lời giới thiệu. Cảnh báo khi giới thiệu conversation between khác nhãn; không sửa câu nguồn.
- Người dùng chọn giọng riêng cho mọi vai, kể cả Lời dẫn. Có lọc ngôn ngữ/giới tính và nghe audio mẫu. Không tự chọn ngẫu nhiên; chặn tạo nếu thiếu giọng hoặc mất tệp giọng.
- Giữ mọi lượt theo thứ tự, kể cả các câu lặp và Now listen again. Không đọc tên nhãn thành tiếng, không tự nhân đôi dựa trên hướng dẫn “hear twice”. Lời dẫn và các vai ghép vào một bài.
- Khoảng nghỉ chung giữa lượt từ 0–5 giây, mặc định 0,4. Speed/pitch/volume/model settings áp dụng chung; chưa có thông số riêng cho từng vai hoặc chỉnh lời thoại từng hàng.
- Sinh từng lượt bằng giọng đã gán. Cache prompt theo giọng và cache audio lượt trùng `(vai, nội dung)` trong một job; vẫn ghép lại đủ mọi lượt. Ghép audio theo khối, không giữ toàn bộ bài dài trong RAM; một model dùng chung, không nạp model riêng cho mỗi vai.
- WAV/MP3/FLAC/OGG và SRT tùy chọn. Mốc lượt/subtitle dịch theo thời lượng audio thật và khoảng nghỉ; bên trong chunk SRT vẫn chia theo chữ, chưa căn chỉnh từ. Watermark nếu bật dùng giọng Lời dẫn, hoặc giọng chung khi bài không có lời dẫn.
- Xuất audio/SRT sau khi tất cả lượt hợp lệ. Lỗi/hủy không xuất bài dang dở, giữ kết quả trước đó; tên trùng thêm số. Phiên schema 2 lưu nội dung và giọng từng vai; phiên batch cũ mở về đoạn đơn.
- Bảng vai cuộn khi nhiều người; phần chọn giọng/cài đặt có thể cuộn ở cửa sổ nhỏ, giữ bước 3 tạo/dừng/nghe luôn hiển thị.

## Bằng chứng nghiệm thu

12 unit tests đã qua, gồm hai bài đầy đủ người dùng gửi (22 lượt/bài), vai Unicode, 3/4/6 nhân vật, routing âm thanh, SRT, lỗi và hủy. Kiểm tra phiên riêng giữ giọng sau mở lại/đổi bộ lọc, theme, từ điển và khoảng nghỉ. Sinh thật qua Qt UI/worker trên RTX 5070: đoạn đơn; Lan/Duy WAV 67,389 giây; Mai/Nam MP3 56,243 giây; bốn nhân vật + lời dẫn WAV 7,913 giây. QMediaPlayer duration 7913 ms, position tăng, không báo lỗi. Chưa xác minh chất lượng nghe thủ công mọi giọng hoặc CPU/laptop 8 GB.
