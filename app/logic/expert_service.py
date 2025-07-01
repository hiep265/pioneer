# app/logic/expert_service.py
from typing import List, Dict, Optional

from ..repositories.fb_scraper import FacebookCrawler
from .keyword_matcher import KeywordMatcher

class ExpertService:
    """
    Lớp logic nghiệp vụ để xử lý các hoạt động liên quan đến chuyên gia.
    """
    def __init__(self):
        """
        Khởi tạo các repository và service cần thiết.
        """
        self.fb_crawler = FacebookCrawler()
        self.kw_matcher = KeywordMatcher()

    def get_relevant_expert_posts(
        self,
        keywords: Optional[List[str]],
        days: int,
        limit: int
    ) -> List[Dict]:
        """
        Lấy, lọc và chấm điểm các bài đăng của chuyên gia.

        Args:
            keywords: Danh sách từ khóa để lọc.
            days: Số ngày gần nhất để lấy bài.
            limit: Số lượng bài đăng tối đa để trả về.

        Returns:
            Một danh sách các bài đăng đã được chấm điểm và sắp xếp.
        """
        # 1. Thu thập tất cả bài đăng từ repository
        all_posts = self.fb_crawler.fetch_posts(days=days, limit=limit)
        
        scored_posts = []
        for post in all_posts:
            # 2. Kết hợp văn bản từ bài đăng và bình luận
            post_text = post.get("text", "")
            comments_text = " ".join([c.get("text", "") for c in post.get("comments", [])])
            full_text = f"{post_text} {comments_text}"
            
            # 3. Chấm điểm và lấy lý do từ keyword matcher
            score, reason = self.kw_matcher.match_and_score(full_text, keywords or [])
            
            # 4. Chỉ giữ lại những bài có điểm > 0
            if score > 0:
                post["score"] = score
                post["reason"] = reason
                scored_posts.append(post)
                
        # 5. Sắp xếp theo điểm số và trả về số lượng giới hạn
        return sorted(scored_posts, key=lambda x: x.get("score", 0), reverse=True)[:limit]
