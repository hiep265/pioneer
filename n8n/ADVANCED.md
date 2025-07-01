# Hướng dẫn cấu hình nâng cao cho n8n

## Tùy chỉnh Workflow

### Thay đổi URL API

Nếu API của bạn không chạy ở địa chỉ mặc định (http://localhost:8001), bạn cần cập nhật URL trong các node HTTP Request:

1. Mở workflow trong n8n Dashboard
2. Nhấp vào các node sau để chỉnh sửa:
   - Get Top News
   - Get News By Keyword
   - Get Expert Posts By Keyword
   - Get Expert Posts By Content
   - Health Check
3. Cập nhật URL trong trường "URL" của mỗi node
4. Lưu thay đổi

### Sử dụng biến môi trường cho URL API

Thay vì cố định URL trong mỗi node, bạn có thể sử dụng biến môi trường:

1. Thêm biến môi trường `API_URL` trong n8n
2. Cập nhật URL trong các node HTTP Request thành `{{ $env.API_URL }}/news/top3` (và tương tự cho các endpoint khác)

### Tùy chỉnh định dạng tin nhắn

Bạn có thể thay đổi cách hiển thị tin nhắn bằng cách chỉnh sửa các node Function:

1. Mở workflow trong n8n Dashboard
2. Nhấp vào các node sau để chỉnh sửa:
   - Format News
   - Format News By Keyword
   - Format Expert Posts By Keyword
   - Format Expert Posts By Content
3. Chỉnh sửa mã JavaScript trong trường "Function Code"
4. Lưu thay đổi

### Thêm lệnh mới

Để thêm lệnh mới cho bot:

1. Thêm node If mới sau node Expert Content Command
2. Cấu hình điều kiện để kiểm tra lệnh mới (ví dụ: `{{ $json.message.text.startsWith('/new_command') }}`)
3. Thêm node Function để xử lý tham số của lệnh
4. Thêm node HTTP Request để gọi API tương ứng
5. Thêm node Function để định dạng kết quả
6. Kết nối các node với nhau và với node Send Formatted Message

## Xử lý lỗi nâng cao

### Thêm timeout cho HTTP Request

Để tránh việc workflow bị treo khi API không phản hồi:

1. Mở các node HTTP Request
2. Mở tab "Options"
3. Thêm trường "Timeout" và đặt giá trị (ví dụ: 10000 cho 10 giây)

### Xử lý lỗi API

Để xử lý khi API trả về lỗi:

1. Thêm node Error Trigger sau mỗi node HTTP Request
2. Kết nối node Error Trigger với một node Function để định dạng thông báo lỗi
3. Kết nối node Function với node Send Error Message

## Tính năng nâng cao

### Lưu trữ lịch sử tìm kiếm

Để lưu trữ lịch sử tìm kiếm của người dùng:

1. Thêm node Function sau mỗi node Extract để lưu thông tin tìm kiếm
2. Sử dụng n8n Data Storage hoặc kết nối với cơ sở dữ liệu bên ngoài

### Thêm nút nhấn (Inline Keyboard)

Để thêm các nút tương tác trong tin nhắn Telegram:

1. Mở các node Format
2. Thêm trường `inlineKeyboard` vào đối tượng trả về
3. Ví dụ:

```javascript
return [{
  json: {
    chatId: items[0].json.chatId,
    message: message,
    inlineKeyboard: [
      [
        { text: "Xem thêm", callback_data: "more" },
        { text: "Chia sẻ", callback_data: "share" }
      ]
    ]
  }
}];
```

4. Cập nhật node Send Formatted Message để sử dụng inline keyboard:
   - Thêm trường `reply_markup` vào `additionalFields`
   - Đặt giá trị là `{{ JSON.stringify({inline_keyboard: $json.inlineKeyboard}) }}`

### Xử lý Callback Query

Để xử lý khi người dùng nhấp vào nút:

1. Cập nhật node Telegram Trigger để lắng nghe cả `callback_query`
2. Thêm node If để kiểm tra loại cập nhật (message hoặc callback_query)
3. Thêm các node để xử lý callback_query dựa trên `callback_data`

## Tích hợp với các dịch vụ khác

### Lưu trữ dữ liệu với Google Sheets

1. Cài đặt và cấu hình Google Sheets node trong n8n
2. Thêm node Google Sheets sau các node Format để lưu kết quả

### Gửi thông báo qua Email

1. Cài đặt và cấu hình Email node trong n8n
2. Thêm node Email sau các node Format để gửi kết quả qua email

### Tích hợp với Slack

1. Cài đặt và cấu hình Slack node trong n8n
2. Thêm node Slack sau các node Format để gửi kết quả đến kênh Slack

## Giám sát và bảo trì

### Giám sát lỗi

1. Thêm node Error Trigger ở cấp workflow
2. Kết nối với node Email hoặc Slack để gửi thông báo khi có lỗi

### Lưu nhật ký (Logging)

1. Thêm node Function sau các node chính để ghi log
2. Sử dụng n8n Data Storage hoặc kết nối với dịch vụ logging bên ngoài

### Tự động khởi động lại khi gặp lỗi

1. Cấu hình n8n để tự động khởi động lại workflow khi gặp lỗi
2. Sử dụng tùy chọn `--error-workflow` khi khởi động n8n