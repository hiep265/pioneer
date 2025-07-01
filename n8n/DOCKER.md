# Hướng dẫn chạy n8n với Docker

## Yêu cầu

- Docker đã được cài đặt
- Docker Compose (tùy chọn, nhưng được khuyến nghị)

## Chạy n8n với Docker

### Sử dụng Docker CLI

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -e TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here \
  -e API_URL=http://host.docker.internal:8001 \
  n8nio/n8n
```

Lưu ý: `host.docker.internal` là cách để container Docker truy cập các dịch vụ chạy trên máy host. Nếu API của bạn cũng chạy trong Docker, bạn nên sử dụng Docker network.

### Sử dụng Docker Compose

Tạo file `docker-compose.yml` với nội dung sau:

```yaml
version: '3'

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
      - API_URL=http://host.docker.internal:8001
      - N8N_PROTOCOL=http
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_EDITOR_BASE_URL=http://localhost:5678
      - WEBHOOK_URL=https://your-public-url.com
      - GENERIC_TIMEZONE=Asia/Ho_Chi_Minh
    volumes:
      - ~/.n8n:/home/node/.n8n
```

Sau đó, chạy:

```bash
docker-compose up -d
```

## Chạy cả n8n và API trong Docker

Nếu bạn muốn chạy cả n8n và API Pioneer trong Docker, hãy tạo file `docker-compose.yml` như sau:

```yaml
version: '3'

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
      - API_URL=http://api:8001
      - N8N_PROTOCOL=http
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_EDITOR_BASE_URL=http://localhost:5678
      - WEBHOOK_URL=https://your-public-url.com
      - GENERIC_TIMEZONE=Asia/Ho_Chi_Minh
    volumes:
      - ~/.n8n:/home/node/.n8n
    depends_on:
      - api

  api:
    image: pioneer-api:latest  # Thay thế bằng image của API Pioneer
    build:
      context: ../  # Đường dẫn đến thư mục gốc của dự án Pioneer
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - PORT=8001
      - OPENAI_API_KEY=your_openai_api_key_here
      - APIFY_API_TOKEN=your_apify_token_here
    volumes:
      - ../app:/app  # Mount thư mục app để dễ dàng phát triển
```

## Sử dụng Ngrok cho Webhook

Nếu bạn đang phát triển cục bộ và cần một URL công khai cho webhook Telegram, bạn có thể sử dụng Ngrok:

```yaml
version: '3'

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
      - API_URL=http://api:8001
      - N8N_PROTOCOL=http
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_EDITOR_BASE_URL=http://localhost:5678
      - WEBHOOK_URL=https://your-ngrok-url.ngrok.io
      - GENERIC_TIMEZONE=Asia/Ho_Chi_Minh
    volumes:
      - ~/.n8n:/home/node/.n8n
    depends_on:
      - api

  api:
    image: pioneer-api:latest
    ports:
      - "8001:8001"
    environment:
      - PORT=8001
      - OPENAI_API_KEY=your_openai_api_key_here
      - APIFY_API_TOKEN=your_apify_token_here
    volumes:
      - ../app:/app

  ngrok:
    image: wernight/ngrok
    ports:
      - "4040:4040"
    environment:
      - NGROK_AUTH=your_ngrok_auth_token
      - NGROK_PORT=n8n:5678
    depends_on:
      - n8n
```

## Sao lưu dữ liệu n8n

Dữ liệu n8n được lưu trữ trong thư mục `~/.n8n` (hoặc thư mục bạn đã mount). Để sao lưu dữ liệu:

```bash
# Sao lưu
docker run --rm -v ~/.n8n:/data -v $(pwd):/backup alpine tar czf /backup/n8n-backup.tar.gz /data

# Khôi phục
docker run --rm -v ~/.n8n:/data -v $(pwd):/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/n8n-backup.tar.gz -C /"
```

## Cập nhật n8n

Để cập nhật n8n lên phiên bản mới nhất:

```bash
# Với Docker CLI
docker pull n8nio/n8n
docker stop n8n
docker rm n8n
# Sau đó chạy lại lệnh docker run

# Với Docker Compose
docker-compose pull
docker-compose up -d
```

## Xem logs

```bash
# Với Docker CLI
docker logs -f n8n

# Với Docker Compose
docker-compose logs -f n8n
```

## Khắc phục sự cố

### Không thể kết nối đến API

Nếu n8n không thể kết nối đến API:

1. Kiểm tra xem API có đang chạy không
2. Kiểm tra URL API trong biến môi trường
3. Nếu API chạy trên máy host, hãy sử dụng `host.docker.internal` thay vì `localhost`
4. Nếu API chạy trong container khác, hãy đảm bảo chúng ở cùng một network

### Webhook không hoạt động

Nếu webhook Telegram không hoạt động:

1. Kiểm tra xem URL webhook có thể truy cập từ internet không
2. Nếu bạn đang sử dụng Ngrok, hãy kiểm tra URL Ngrok
3. Đảm bảo bạn đã thiết lập đúng biến môi trường `WEBHOOK_URL`

### Container khởi động nhưng n8n không hoạt động

Nếu container khởi động nhưng n8n không hoạt động:

1. Kiểm tra logs của container
2. Kiểm tra xem có đủ bộ nhớ không
3. Kiểm tra xem các biến môi trường có được thiết lập đúng không