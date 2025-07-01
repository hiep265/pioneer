#!/bin/bash
set -e

# Kiểm tra biến môi trường bắt buộc
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
  echo "Error: TELEGRAM_BOT_TOKEN is not set"
  exit 1
fi

# Thiết lập webhook Telegram nếu WEBHOOK_URL được cung cấp
if [ -n "$WEBHOOK_URL" ]; then
  echo "Setting up Telegram webhook to $WEBHOOK_URL/webhook/telegram"
  curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook?url=$WEBHOOK_URL/webhook/telegram"
  
  # Kiểm tra trạng thái webhook
  WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo")
  echo "Webhook info: $WEBHOOK_INFO"
  
  # Kiểm tra xem webhook có được thiết lập thành công không
  if echo "$WEBHOOK_INFO" | grep -q "\"ok\":true"; then
    echo "Webhook setup successful"
  else
    echo "Warning: Webhook setup may have failed. Please check the webhook info above."
  fi
fi

# Kiểm tra kết nối đến API
if [ -n "$API_URL" ]; then
  echo "Checking connection to API at $API_URL/health"
  MAX_RETRIES=30
  RETRY_COUNT=0
  
  while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "$API_URL/health" | grep -q "status"; then
      echo "API connection successful"
      break
    else
      echo "Waiting for API to be available... ($(($RETRY_COUNT + 1))/$MAX_RETRIES)"
      RETRY_COUNT=$((RETRY_COUNT + 1))
      sleep 2
    fi
  done
  
  if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "Warning: Could not connect to API after $MAX_RETRIES attempts"
  fi
fi

# Khởi động n8n
echo "Starting n8n..."
exec node /usr/local/lib/node_modules/n8n/bin/n8n start