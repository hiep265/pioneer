FROM n8nio/n8n:latest

# Sao chép workflow và tài liệu vào container
COPY workflows /home/node/.n8n/workflows
COPY *.md /home/node/docs/

# Cài đặt các gói bổ sung nếu cần
USER root
RUN apt-get update && \
    apt-get install -y curl jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Chuyển về người dùng node
USER node

# Thiết lập biến môi trường mặc định
ENV N8N_PROTOCOL=http
ENV N8N_HOST=localhost
ENV N8N_PORT=5678
ENV N8N_EDITOR_BASE_URL=http://localhost:5678
ENV GENERIC_TIMEZONE=Asia/Ho_Chi_Minh

# Tạo script khởi động để thiết lập webhook Telegram
COPY --chown=node:node docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]