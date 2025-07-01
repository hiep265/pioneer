# Hướng dẫn thiết lập Telegram Bot

## Tạo Telegram Bot mới

1. Mở Telegram và tìm kiếm `@BotFather`
2. Bắt đầu cuộc trò chuyện và gửi lệnh `/start`
3. Gửi lệnh `/newbot` để tạo bot mới
4. Nhập tên hiển thị cho bot (ví dụ: Pioneer News Bot)
5. Nhập tên người dùng cho bot, phải kết thúc bằng "bot" (ví dụ: pioneer_news_bot)
6. BotFather sẽ cung cấp cho bạn một token API. Lưu token này lại, bạn sẽ cần nó để cấu hình n8n

## Cấu hình bot

### Thiết lập mô tả và ảnh đại diện

1. Gửi lệnh `/setdescription` đến BotFather
2. Chọn bot của bạn
3. Nhập mô tả (ví dụ: "Bot tìm kiếm tin tức và bài viết chuyên gia từ hệ thống Pioneer")

4. Gửi lệnh `/setuserpic` đến BotFather
5. Chọn bot của bạn
6. Gửi một hình ảnh làm ảnh đại diện cho bot

### Thiết lập lệnh

1. Gửi lệnh `/setcommands` đến BotFather
2. Chọn bot của bạn
3. Gửi danh sách lệnh theo định dạng sau:

```
start - Khởi động bot và nhận hướng dẫn
news - Xem tin tức hàng đầu
news_keyword - Tìm tin tức theo từ khóa
expert - Tìm bài viết chuyên gia theo từ khóa
expert_content - Tìm bài viết chuyên gia tương tự với nội dung
```

## Thiết lập Webhook

### Sử dụng n8n Tunnel

Khi bạn khởi động n8n với tùy chọn `--tunnel`, n8n sẽ tự động tạo một URL công khai và thiết lập webhook cho Telegram. Tuy nhiên, bạn cũng có thể thiết lập webhook thủ công.

### Thiết lập webhook thủ công

1. Lấy URL webhook từ n8n:
   - Mở workflow trong n8n Dashboard
   - Nhấp vào node Telegram Trigger
   - Sao chép URL webhook từ trường "Webhook URL"

2. Thiết lập webhook bằng cách truy cập URL sau trong trình duyệt (thay thế các giá trị):

```
https://api.telegram.org/bot<your_bot_token>/setWebhook?url=<your_webhook_url>
```

3. Kiểm tra trạng thái webhook:

```
https://api.telegram.org/bot<your_bot_token>/getWebhookInfo
```

## Kiểm tra bot

1. Mở Telegram và tìm kiếm bot của bạn theo tên người dùng
2. Bắt đầu cuộc trò chuyện và gửi lệnh `/start`
3. Bot sẽ phản hồi với tin nhắn chào mừng nếu mọi thứ được thiết lập đúng

## Xử lý sự cố

### Bot không phản hồi

- Kiểm tra xem n8n có đang chạy không
- Kiểm tra xem workflow có được kích hoạt không
- Kiểm tra logs của n8n để tìm lỗi
- Kiểm tra thông tin webhook bằng cách gọi `getWebhookInfo`

### Lỗi webhook

- Đảm bảo URL webhook là công khai và có thể truy cập từ internet
- Kiểm tra xem token bot có chính xác không
- Thử thiết lập lại webhook

## Tính năng nâng cao

### Bot trong nhóm

Để sử dụng bot trong nhóm Telegram:

1. Gửi lệnh `/setjoingroups` đến BotFather
2. Chọn bot của bạn
3. Chọn "Enable"

4. Thêm bot vào nhóm
5. Cấu hình workflow để xử lý tin nhắn từ nhóm

### Chế độ riêng tư

Để kiểm soát ai có thể tương tác với bot:

1. Gửi lệnh `/setprivacy` đến BotFather
2. Chọn bot của bạn
3. Chọn "Enable" để bot chỉ nhận tin nhắn bắt đầu bằng "/" trong nhóm
   Hoặc chọn "Disable" để bot nhận tất cả tin nhắn trong nhóm

### Inline mode

Để cho phép người dùng gọi bot từ bất kỳ cuộc trò chuyện nào:

1. Gửi lệnh `/setinline` đến BotFather
2. Chọn bot của bạn
3. Nhập văn bản gợi ý (ví dụ: "Tìm tin tức hoặc bài viết chuyên gia")

4. Cập nhật workflow để xử lý inline query