# Pioneer News & Expert Bot - n8n Workflow

## Giới thiệu

Đây là workflow n8n để kết nối API tin tức và chuyên gia của dự án Pioneer với Telegram Bot. Workflow này cho phép người dùng tương tác với bot Telegram để:

- Xem tin tức hàng đầu
- Tìm tin tức theo từ khóa
- Tìm bài viết chuyên gia theo từ khóa
- Tìm bài viết chuyên gia tương tự với nội dung đã cung cấp

## Tài liệu

Dự án này bao gồm các tài liệu hướng dẫn sau:

- [Hướng dẫn cài đặt](SETUP.md) - Cách cài đặt n8n
- [Hướng dẫn sử dụng](USAGE.md) - Cách sử dụng bot Telegram
- [Hướng dẫn cấu hình nâng cao](ADVANCED.md) - Cách tùy chỉnh workflow
- [Hướng dẫn thiết lập Telegram Bot](TELEGRAM_BOT.md) - Cách tạo và cấu hình bot Telegram
- [Hướng dẫn chạy với Docker](DOCKER.md) - Cách chạy n8n trong Docker
- [Hướng dẫn khắc phục sự cố](TROUBLESHOOTING.md) - Cách giải quyết các vấn đề phổ biến

## Cài đặt nhanh

### Sử dụng npm

```bash
# Cài đặt n8n
npm install n8n -g

# Sao chép file .env.example thành .env và cập nhật các giá trị
cp .env.example .env

# Khởi động n8n
n8n start
```

### Sử dụng Docker

```bash
# Sao chép file .env.example thành .env và cập nhật các giá trị
cp .env.example .env

# Khởi động với Docker Compose
docker-compose up -d
```

## Cấu trúc thư mục

```
.
├── workflows/              # Thư mục chứa workflow n8n
│   └── news_selection.json # Workflow chính
├── .env.example            # Mẫu file biến môi trường
├── docker-compose.yml      # Cấu hình Docker Compose
├── Dockerfile              # Dockerfile để đóng gói n8n
├── docker-entrypoint.sh    # Script khởi động cho Docker
├── SETUP.md                # Hướng dẫn cài đặt
├── USAGE.md                # Hướng dẫn sử dụng
├── ADVANCED.md             # Hướng dẫn cấu hình nâng cao
├── TELEGRAM_BOT.md         # Hướng dẫn thiết lập Telegram Bot
├── DOCKER.md               # Hướng dẫn chạy với Docker
└── TROUBLESHOOTING.md      # Hướng dẫn khắc phục sự cố
```

## Các lệnh Telegram

- `/start` - Khởi động bot và nhận hướng dẫn
- `/news` - Xem tin tức hàng đầu
- `/news_keyword [từ khóa]` - Tìm tin tức theo từ khóa
- `/expert [từ khóa]` - Tìm bài viết chuyên gia theo từ khóa
- `/expert_content [nội dung]` - Tìm bài viết chuyên gia tương tự với nội dung

## Yêu cầu

- n8n (phiên bản 0.214.0 trở lên)
- API Pioneer đang chạy (mặc định tại http://localhost:8001)
- Telegram Bot Token

## Đóng góp

Nếu bạn muốn đóng góp vào dự án, hãy tạo pull request hoặc báo cáo vấn đề trong phần Issues.

## Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.