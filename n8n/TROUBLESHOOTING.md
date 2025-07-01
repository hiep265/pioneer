# Hướng dẫn khắc phục sự cố

## Sự cố với n8n

### n8n không khởi động

**Triệu chứng**: Không thể truy cập dashboard n8n tại http://localhost:5678

**Giải pháp**:
1. Kiểm tra xem n8n có đang chạy không bằng lệnh:
   ```
   ps aux | grep n8n  # Linux/Mac
   tasklist | findstr n8n  # Windows
   ```
2. Kiểm tra logs để tìm lỗi:
   ```
   n8n start --log-level=debug
   ```
3. Kiểm tra xem cổng 5678 có đang được sử dụng bởi ứng dụng khác không:
   ```
   netstat -ano | findstr 5678  # Windows
   lsof -i :5678  # Linux/Mac
   ```
4. Thử khởi động n8n với cổng khác:
   ```
   n8n start --port=5679
   ```

### Không thể import workflow

**Triệu chứng**: Gặp lỗi khi import file workflow

**Giải pháp**:
1. Kiểm tra xem file JSON có hợp lệ không
2. Thử mở file trong trình soạn thảo và kiểm tra cú pháp JSON
3. Đảm bảo phiên bản n8n của bạn tương thích với workflow
4. Thử tạo workflow mới và sao chép nội dung từ file JSON

### Workflow không kích hoạt

**Triệu chứng**: Workflow đã được import nhưng không chạy khi có sự kiện

**Giải pháp**:
1. Kiểm tra xem workflow có được kích hoạt không (nút "Active" phải được bật)
2. Kiểm tra logs để tìm lỗi
3. Kiểm tra các node trigger (Telegram Trigger, Schedule Trigger) xem có được cấu hình đúng không
4. Thử kích hoạt workflow thủ công bằng cách nhấp vào nút "Execute Workflow"

## Sự cố với Telegram Bot

### Bot không phản hồi

**Triệu chứng**: Gửi tin nhắn đến bot nhưng không nhận được phản hồi

**Giải pháp**:
1. Kiểm tra xem bot token có chính xác không
2. Kiểm tra xem webhook có được thiết lập đúng không:
   ```
   https://api.telegram.org/bot<your_bot_token>/getWebhookInfo
   ```
3. Đảm bảo URL webhook là công khai và có thể truy cập từ internet
4. Kiểm tra logs của n8n để tìm lỗi
5. Thử thiết lập lại webhook:
   ```
   https://api.telegram.org/bot<your_bot_token>/setWebhook?url=<your_webhook_url>
   ```

### Lỗi webhook

**Triệu chứng**: Webhook không được thiết lập hoặc gặp lỗi

**Giải pháp**:
1. Đảm bảo n8n đang chạy với tùy chọn `--tunnel` hoặc URL webhook của bạn là công khai
2. Kiểm tra thông tin webhook:
   ```
   https://api.telegram.org/bot<your_bot_token>/getWebhookInfo
   ```
3. Nếu có lỗi, hãy xóa webhook hiện tại và thiết lập lại:
   ```
   https://api.telegram.org/bot<your_bot_token>/deleteWebhook
   https://api.telegram.org/bot<your_bot_token>/setWebhook?url=<your_webhook_url>
   ```

## Sự cố với API

### Không thể kết nối đến API

**Triệu chứng**: Các node HTTP Request báo lỗi kết nối

**Giải pháp**:
1. Kiểm tra xem API có đang chạy không
2. Kiểm tra URL API trong các node HTTP Request
3. Thử gọi API trực tiếp bằng công cụ như Postman hoặc curl:
   ```
   curl http://localhost:8001/health
   ```
4. Kiểm tra xem có vấn đề về tường lửa hoặc mạng không

### API trả về lỗi

**Triệu chứng**: API phản hồi với mã lỗi (400, 500, etc.)

**Giải pháp**:
1. Kiểm tra logs của API để tìm lỗi
2. Kiểm tra tham số trong các node HTTP Request
3. Thử gọi API với các tham số khác nhau để xác định vấn đề
4. Cập nhật workflow để xử lý lỗi API một cách phù hợp

## Sự cố với định dạng tin nhắn

### Tin nhắn không hiển thị đúng

**Triệu chứng**: Tin nhắn Telegram hiển thị không đúng định dạng hoặc thiếu thông tin

**Giải pháp**:
1. Kiểm tra mã trong các node Function để định dạng tin nhắn
2. Đảm bảo bạn đang sử dụng đúng cú pháp Markdown cho Telegram
3. Kiểm tra xem dữ liệu từ API có đúng định dạng không
4. Thêm xử lý lỗi trong các node Function để đảm bảo tin nhắn luôn hợp lệ

### Lỗi Markdown

**Triệu chứng**: Telegram báo lỗi về cú pháp Markdown

**Giải pháp**:
1. Đảm bảo bạn đang thoát các ký tự đặc biệt trong Markdown (_, *, [, ], (, ), ~, `, >, #, +, -, =, |, {, }, ., !)
2. Kiểm tra xem bạn đã đóng tất cả các thẻ Markdown chưa
3. Thử sử dụng HTML thay vì Markdown bằng cách thay đổi `parse_mode` thành "HTML"

## Sự cố khác

### Workflow chạy chậm

**Triệu chứng**: Bot phản hồi rất chậm

**Giải pháp**:
1. Kiểm tra thời gian phản hồi của API
2. Tối ưu hóa các node Function để xử lý dữ liệu nhanh hơn
3. Thêm timeout cho các node HTTP Request
4. Cân nhắc việc sử dụng bộ nhớ đệm cho các yêu cầu phổ biến

### Hết bộ nhớ

**Triệu chứng**: n8n gặp lỗi "out of memory"

**Giải pháp**:
1. Tăng bộ nhớ cho n8n:
   ```
   NODE_OPTIONS=--max-old-space-size=4096 n8n start
   ```
2. Tối ưu hóa workflow để sử dụng ít bộ nhớ hơn
3. Tránh xử lý quá nhiều dữ liệu cùng một lúc

### Lỗi không xác định

Nếu bạn gặp lỗi không xác định:

1. Kiểm tra logs của n8n với mức độ debug:
   ```
   n8n start --log-level=debug
   ```
2. Kiểm tra logs của API
3. Thử khởi động lại n8n và API
4. Kiểm tra phiên bản n8n và cập nhật nếu cần