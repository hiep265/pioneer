import feedparser
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class NewsRepository:
    RSS_FEEDS = {
        "reuters":      "http://localhost:1200/reuters/world",
        "the_guardian": "https://www.theguardian.com/world/rss",
        "ap_news":      "http://localhost:1200/apnews/topics/world-news",
    }

    # ---------- PUBLIC -------------------------------------------------------
    def fetch_all(
        self,
        max_per_source: int = 15,
        keywords: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Lấy tin từ 3 nguồn, bỏ trùng *toàn cục* và lọc theo từ-khóa (nếu có).
        Trả về list[dict] với các field: title, summary, link, source
        """
        seen: set[str] = set()        # chứa hash của bài đã thêm
        articles: List[Dict] = []

        for source, url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                fetched = 0

                for entry in feed.entries:
                    if fetched >= max_per_source:
                        break

                    # 1) Chuẩn hóa (title + link) để sinh "dấu vân tay"
                    title = entry.title.strip()
                    link  = entry.link.split("?")[0]  # bỏ query-string dư
                    fingerprint = self._fingerprint(title, link)

                    # 2) Bỏ bài trùng (đã gặp ở nguồn khác)
                    if fingerprint in seen:
                        continue

                    summary = self._clean(entry.get("summary", ""))

                    # 3) Lọc theo từ-khóa nếu có
                    if keywords and not self._has_keyword(title, summary, keywords):
                        continue

                    # 4) Lưu
                    articles.append(
                        {"title": title, "summary": summary, "link": link, "source": source}
                    )
                    fetched += 1
                    seen.add(fingerprint)

            except Exception as exc:
                print(f"[{source}] error: {exc}")

        return articles

    # ---------- PRIVATE ------------------------------------------------------
    @staticmethod
    def _clean(html: str) -> str:
        return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

    @staticmethod
    def _fingerprint(title: str, link: str) -> str:
        """Ghép & hạ thấp, bỏ ký tự không chữ – chống trùng tương đối."""
        def slugify(text: str) -> str:
            return re.sub(r"[^a-z0-9]+", "", text.lower())

        return f"{slugify(title)}-{slugify(link)}"

    @staticmethod
    def _has_keyword(title: str, summary: str, kws: List[str]) -> bool:
        target = f"{title} {summary}".lower()
        return any(kw.lower() in target for kw in kws)
