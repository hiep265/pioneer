# Hướng dẫn cài đặt n8n

## Cài đặt n8n

### Sử dụng npm

```bash
npm install n8n -g
```

### Sử dụng Docker

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here \
  n8nio/n8n
```

## Khởi động n8n

### Sử dụng npm

```bash
n8n start
```

### Sử dụng biến môi trường từ file .env

1. Sao chép file `.env.example` thành `.env`
2. Cập nhật các giá trị trong file `.env`
3. Khởi động n8n với biến môi trường từ file .env:

```bash
n8n start --tunnel
```

Tùy chọn `--tunnel` tạo một URL công khai để Telegram có thể gửi webhook đến n8n của bạn.

## Truy cập n8n Dashboard

Sau khi khởi động, bạn có thể truy cập n8n Dashboard tại:

```
http://localhost:5678
```

## Import Workflow

1. Mở n8n Dashboard
2. Chọn "Workflows" từ menu bên trái
3. Nhấp vào nút "Import from File"
4. Chọn file `workflows/news_selection.json`
5. Nhấp vào "Import"

## Cấu hình Telegram Webhook

Để Telegram có thể gửi tin nhắn đến n8n, bạn cần thiết lập webhook:

1. Nếu bạn đang chạy n8n cục bộ, hãy sử dụng tùy chọn `--tunnel` khi khởi động n8n để tạo URL công khai
2. Trong n8n Dashboard, mở workflow và tìm node "Telegram Trigger"
3. Cấu hình node này với Telegram Bot Token của bạn
4. Lưu và kích hoạt workflow

Hoặc bạn có thể thiết lập webhook thủ công bằng cách gọi API Telegram:

```
https://api.telegram.org/bot<your_bot_token>/setWebhook?url=<your_n8n_webhook_url>/webhook/telegram
```

## Kiểm tra kết nối

1. Mở Telegram và tìm bot của bạn
2. Gửi lệnh `/start`
3. Bot sẽ phản hồi với tin nhắn chào mừng nếu mọi thứ được thiết lập đúng

## Xử lý sự cố

### Webhook không hoạt động

- Kiểm tra xem n8n có đang chạy không
- Đảm bảo URL webhook là công khai và có thể truy cập từ internet
- Kiểm tra logs của n8n để tìm lỗi

### API không phản hồi

- Kiểm tra xem API Pioneer có đang chạy không
- Kiểm tra URL API trong các node HTTP Request
- Thử gọi API trực tiếp bằng công cụ như Postman

### Bot không phản hồi

- Kiểm tra xem bot token có chính xác không
- Đảm bảo webhook đã được thiết lập đúng
- Kiểm tra xem workflow có được kích hoạt không