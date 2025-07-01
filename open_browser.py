from datetime import datetime, timedelta
from apify_client import ApifyClient
import json
import os

# Lưu ý bảo mật: nên export token ra biến môi trường APIFY_TOKEN
API_TOKEN = os.getenv("APIFY_TOKEN", "apify_api_fo5wMMlWcreK4mKTGLN3KyVUbezahc3fA77C")
ACTOR_ID  = "apify/facebook-posts-scraper"

client = ApifyClient(API_TOKEN)

# Tính ngày cách đây 10 ngày
ten_days_ago = (datetime.utcnow() - timedelta(days=10)).strftime("%Y-%m-%d")

run_input = {
    "startUrls": [{"url": "https://www.facebook.com/tuanqho"}],
    # đủ lớn để không cắt bớt kết quả
    "resultsLimit": 1000,
    # Chỉ lấy bài đăng mới hơn thời điểm 10 ngày trước
    "onlyPostsNewerThan": ten_days_ago,
    "proxyConfig": {"useApifyProxy": True}
}

# Chạy actor và chờ hoàn tất
run = client.actor(ACTOR_ID).call(run_input=run_input)

# Lấy toàn bộ item trong dataset
items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

# ----------- Xuất ra JSON -----------
json_str = json.dumps(items, ensure_ascii=False, indent=2)
print(json_str)

# Nếu muốn ghi file:
# with open("posts_last_10_days.json", "w", encoding="utf-8") as f:
#     f.write(json_str)
