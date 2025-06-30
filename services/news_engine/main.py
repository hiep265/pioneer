from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .controllers import news_controller

# Khởi tạo ứng dụng FastAPI
# Đây là điểm khởi đầu của ứng dụng NewsEngine API.
app = FastAPI(
    title="NewsEngine API",
    description="Một API có cấu trúc để tìm nạp, chấm điểm và xếp hạng các bài báo tin tức.",
    version="0.2.0"
)

# Cấu hình CORS (Cross-Origin Resource Sharing)
# Cho phép các ứng dụng frontend từ bất kỳ nguồn gốc nào (allow_origins=["*"]) có thể truy cập API này.
# Điều này quan trọng cho việc phát triển frontend sau này.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các nguồn gốc
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức HTTP (GET, POST, PUT, DELETE, v.v.)
    allow_headers=["*"],  # Cho phép tất cả các tiêu đề HTTP
)

# Bao gồm các router từ các controller
# Điều này giúp tổ chức các endpoint API theo từng module (ví dụ: /news cho các endpoint liên quan đến tin tức).
app.include_router(news_controller.router, prefix="/news", tags=["News"])

@app.get("/health", summary="Kiểm tra trạng thái API", tags=["Giám sát"])
def health_check():
    """
    Endpoint kiểm tra trạng thái đơn giản.
    Dùng để xác định xem API có đang hoạt động bình thường hay không.
    """
    return {"status": "ok"}

# Để chạy ứng dụng này cục bộ, sử dụng lệnh sau trong terminal (sau khi kích hoạt môi trường ảo):
# uvicorn services.news_engine.main:app --reload --port 8001
