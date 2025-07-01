# news_service.py
from typing import List, Dict, Optional

from ..repositories.news_repository import NewsRepository
from ..repositories.scoring_repository import ScoringRepository


class NewsService:
    """
    Lớp facade: lấy tin, chấm điểm, trả về Top-N.
    Dedup đã được NewsRepository xử lý ⇒ không cần làm lại ở đây.
    """

    def __init__(self) -> None:
        self.news_repo = NewsRepository()
        self.scoring_repo = ScoringRepository()

    # ------------------------------------------------------------------
    def get_top_articles(
        self,
        count: int = 3,
        keywords: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        • keywords: list[str] – chuỗi/ngữ cụm để lọc semantic (NewsRepository lo).
        • count:    số bài đầu ra.
        """
        # 1. Fetch & dedup (đã tích hợp trong repo)
        articles = self.news_repo.fetch_all(
            max_per_source=15,      # bạn chỉnh tuỳ ý
            keywords=keywords,
        )

        for art in articles:
                score, reason = self.scoring_repo.get_score(art, keywords or [])
                art["score"]  = score
                art["reason"] = reason

        # 3. Sắp xếp & cắt Top-N
        return sorted(
            articles,
            key=lambda a: a.get("score", 0),
            reverse=True,
        )[:count]
