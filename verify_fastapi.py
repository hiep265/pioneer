# news_repository.py
# ────────────────────────────────────────────────
import feedparser, sys
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ─── 1. CẤU HÌNH MODEL & NGƯỠNG ─────────────────
MODEL_NAME   = "sentence-transformers/all-mpnet-base-v2"
SIM_DUP_TH   = 0.83          # trùng nếu cosine ≥ 0.83
SIM_REL_TH   = 0.50          # liên quan keyword nếu cosine ≥ 0.50

MODEL = SentenceTransformer(MODEL_NAME)
MODEL.max_seq_length = 256   # tiêu đề + summary ngắn

_EMB_DUP_BUF: List[np.ndarray]        = []  # cache bài đã giữ
_EMB_KW_BUF: Dict[str, np.ndarray]    = {}  # cache keyword

# ─── 2. HÀM TIỆN ÍCH ────────────────────────────
def _embed(text: str) -> np.ndarray:
    return MODEL.encode(text, normalize_embeddings=True)

def _is_duplicate(text: str) -> bool:
    vec = _embed(text)
    if _EMB_DUP_BUF and cosine_similarity([vec], _EMB_DUP_BUF).max() >= SIM_DUP_TH:
        return True
    _EMB_DUP_BUF.append(vec)
    return False

def _is_relevant(text: str, keywords: List[str]) -> bool:
    if not keywords:
        return True
    vec = _embed(text)
    for kw in keywords:
        if kw not in _EMB_KW_BUF:
            _EMB_KW_BUF[kw] = _embed(kw)
        if cosine_similarity([vec], [_EMB_KW_BUF[kw]])[0, 0] >= SIM_REL_TH:
            return True
    return False

def _clean_html(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

# ─── 3. LỚP REPOSITORY ──────────────────────────
class NewsRepository:
    RSS_FEEDS = {
        "reuters":      "http://localhost:1200/reuters/world",
        "the_guardian": "https://www.theguardian.com/world/rss",
        "ap_news":      "http://localhost:1200/apnews/topics/world-news",
    }

    def fetch_all(
        self,
        max_per_source: int = 15,
        keywords: Optional[List[str]] = None,
    ) -> List[Dict]:
        articles: List[Dict] = []

        for source, url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                taken = 0

                for entry in feed.entries:
                    if taken >= max_per_source:
                        break

                    title   = entry.title.strip()
                    summary = _clean_html(entry.get("summary", ""))
                    link    = entry.link.split("?")[0]
                    text    = f"{title} {summary}"

                    # 1. Lọc keyword (semantic)
                    if not _is_relevant(text, keywords or []):
                        continue

                    # 2. Bỏ trùng (semantic)
                    if _is_duplicate(text):
                        print(f"[DUP] {source:12} | {title} | {link}")
                        continue

                    # 3. Giữ bài
                    articles.append(
                        {"title": title, "summary": summary,
                         "link": link, "source": source}
                    )
                    taken += 1

            except Exception as err:
                print(f"[{source}] ERROR: {err}", file=sys.stderr)

        return articles
