from fastapi import APIRouter, Query, Depends, Body
from typing import List, Dict, Optional

from ..logic.expert_service import ExpertService

router = APIRouter()

# Dependency Injection cho ExpertService
def get_expert_service():
    return ExpertService()

@router.get("/expert-posts", response_model=List[Dict], summary="Thu thập bài đăng của chuyên gia Facebook")
def get_expert_posts(
    keywords: Optional[List[str]] = Query(None, description="Danh sách các từ khóa để lọc bài đăng (ví dụ: Trump, US, tariffs)"),
    days: int = Query(10, description="Số ngày gần nhất để thu thập bài đăng"),
    limit: int = Query(50, description="Số lượng bài đăng tối đa để thu thập"),
    content: Optional[str] = Query(None, description="Nội dung bài báo để so sánh với các bài đăng"),
    expert_service: ExpertService = Depends(get_expert_service)
):
    """
    **Mô tả:**
    Endpoint này thu thập các bài đăng và bình luận từ trang Facebook của chuyên gia,
    lọc chúng dựa trên các từ khóa và trả về các bài đăng có liên quan nhất.
    Nếu cung cấp tham số content, sẽ so sánh nội dung với các bài đăng và sắp xếp theo độ tương đồng.
    Toàn bộ logic xử lý được thực hiện trong ExpertService.

    **Tham số:**
    - `keywords`: Danh sách từ khóa để lọc.
    - `days`: Số ngày gần nhất để thu thập.
    - `limit`: Số lượng bài đăng tối đa để trả về.
    - `content`: Nội dung bài báo để so sánh với các bài đăng (tùy chọn).

    **Phản hồi:**
    Trả về một danh sách các bài đăng đã được chấm điểm và sắp xếp.
    Nếu cung cấp content, các bài đăng sẽ được sắp xếp theo độ tương đồng với nội dung.
    """
    return expert_service.get_relevant_expert_posts(
        keywords=keywords,
        days=days,
        limit=limit,
        content=content
    )
