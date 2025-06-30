from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Optional

from ..services.news_service import NewsService

# Khởi tạo APIRouter cho các endpoint liên quan đến tin tức.
# Router này sẽ được gắn vào ứng dụng FastAPI chính.
router = APIRouter()

# Dependency Injection (DI) cho NewsService.
# Hàm này cung cấp một thể hiện (instance) của NewsService.
# FastAPI sẽ tự động gọi hàm này khi cần NewsService trong các endpoint.
def get_news_service():
    return NewsService()

@router.get("/top3", response_model=List[Dict], summary="Lấy 3 bài báo tin tức hàng đầu")
def get_top3_news(
    news_service: NewsService = Depends(get_news_service),
    keywords: Optional[List[str]] = Query(None, description="Danh sách các từ khóa để lọc bài báo (ví dụ: Trump, US, tariffs)")
):
    """
    **Mô tả:**
    Endpoint này thực hiện toàn bộ quy trình để lấy 3 bài báo tin tức hàng đầu:
    1.  Tìm nạp tin tức từ các nguồn RSS đã định cấu hình, có thể lọc theo từ khóa.
    2.  Loại bỏ các bài báo trùng lặp dựa trên độ tương đồng tiêu đề.
    3.  Chấm điểm từng bài báo về mức độ liên quan bằng cách sử dụng mô hình OpenAI GPT.
    4.  Sắp xếp các bài báo theo điểm số giảm dần và trả về 3 bài có điểm cao nhất.

    **Tham số:**
    - `keywords`: Một danh sách các từ khóa (ví dụ: `Trump`, `US`, `tariffs`, `tradewar`, `tax`, `e-commerce`).
      Nếu được cung cấp, chỉ những bài báo có tiêu đề hoặc tóm tắt chứa ít nhất một trong các từ khóa này mới được xem xét.

    **Tác dụng:**
    Cung cấp một cách nhanh chóng và tự động để có được cái nhìn tổng quan về các tin tức quan trọng nhất,
    được đánh giá bởi trí tuệ nhân tạo, giúp người dùng tiết kiệm thời gian và tập trung vào thông tin có giá trị.

    **Ví dụ sử dụng:**
    - Lấy 3 bài báo hàng đầu bất kỳ: `/news/top3`
    - Lấy 3 bài báo hàng đầu liên quan đến Trump và US: `/news/top3?keywords=Trump&keywords=US`

    **Phản hồi:**
    Trả về một danh sách 3 đối tượng bài báo, mỗi đối tượng bao gồm tiêu đề, tóm tắt, liên kết, nguồn và điểm số liên quan.
    """
    return news_service.get_top_articles(count=3, keywords=keywords)
