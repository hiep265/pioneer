from typing import List, Dict, Optional
from fuzzywuzzy import fuzz

from ..repositories.news_repository import NewsRepository
from ..repositories.scoring_repository import ScoringRepository

class NewsService:
    def __init__(self):
        self.news_repo = NewsRepository()
        self.scoring_repo = ScoringRepository()

    def get_top_articles(self, count: int = 3, keywords: Optional[List[str]] = None) -> List[Dict]:
        # 1. Fetch news with optional keywords
        articles = self.news_repo.fetch_all(keywords=keywords)

        # 2. Deduplicate
        unique_articles = self._deduplicate(articles)

        # 3. Score articles
        for article in unique_articles:
            article['score'] = self.scoring_repo.get_score(article)

        # 4. Sort and return top N
        sorted_articles = sorted(unique_articles, key=lambda x: x.get('score', 0), reverse=True)
        return sorted_articles[:count]

    def _deduplicate(self, articles: List[Dict], similarity_threshold: int = 80) -> List[Dict]:
        deduplicated = []
        for article in articles:
            is_duplicate = False
            for existing_article in deduplicated:
                if fuzz.ratio(article['title'], existing_article['title']) > similarity_threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                deduplicated.append(article)
        return deduplicated