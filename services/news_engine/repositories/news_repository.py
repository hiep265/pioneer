import feedparser
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class NewsRepository:
    RSS_FEEDS = {
        "reuters": "http://feeds.reuters.com/reuters/worldNews",
        "the_guardian": "https://www.theguardian.com/world/rss",
    }

    def fetch_all(self, max_per_source: int = 15, keywords: Optional[List[str]] = None) -> List[Dict]:
        articles = []
        for source, url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                fetched_count = 0
                for entry in feed.entries:
                    if fetched_count >= max_per_source:
                        break
                    
                    summary = self._clean_summary(entry.get("summary", ""))
                    article_data = {
                        "title": entry.title,
                        "summary": summary,
                        "link": entry.link,
                        "source": source,
                    }

                    # Filter by keywords if provided
                    if keywords:
                        if not self._contains_keywords(article_data, keywords):
                            continue # Skip this article if it doesn't match keywords

                    articles.append(article_data)
                    fetched_count += 1
            except Exception as e:
                print(f"Could not fetch or parse feed from {source}: {e}")
        return articles

    def _clean_summary(self, summary: str) -> str:
        if '<' in summary and '>' in summary:
            return BeautifulSoup(summary, "html.parser").get_text()
        return summary

    def _contains_keywords(self, article: Dict, keywords: List[str]) -> bool:
        text_to_search = (article.get("title", "") + " " + article.get("summary", "")).lower()
        for keyword in keywords:
            if keyword.lower() in text_to_search:
                return True
        return False