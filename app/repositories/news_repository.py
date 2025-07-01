import feedparser, sys, re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ── CONFIG ───────────────────────────────────────────
MODEL_NAME   = "sentence-transformers/all-mpnet-base-v2"
SIM_DUP_TH   = 0.83         # duplicate threshold
SIM_COS_SHORT = 0.30        # min cosine cho keyword ≤ 2 token
SIM_COS_LONG  = 0.50        # min cosine cho keyword ≥ 3 token

MODEL = SentenceTransformer(MODEL_NAME)
MODEL.max_seq_length = 256

_EMB_DUP_BUF: List[np.ndarray] = []
_EMB_KW_BUF: Dict[str, np.ndarray] = {}

# ── UTILS ────────────────────────────────────────────
def _embed(text: str) -> np.ndarray:
    return MODEL.encode(text, normalize_embeddings=True)

def _is_duplicate(text: str) -> bool:
    vec = _embed(text)
    if _EMB_DUP_BUF and cosine_similarity([vec], _EMB_DUP_BUF).max() >= SIM_DUP_TH:
        return True
    _EMB_DUP_BUF.append(vec)
    return False

def _keyword_relevant(text: str, kws: List[str]) -> bool:
    if not kws:
        return True
    lowered = text.lower()
    vec = None  # delay encode tới khi cần
    for kw in kws:
        kw_norm = kw.lower().strip()
        tokens = kw_norm.split()
        # Nếu từ/cụm xuất hiện exact → true luôn
        if kw_norm in lowered:
            return True
        # chưa trong câu → so cosine
        if kw not in _EMB_KW_BUF:
            _EMB_KW_BUF[kw] = _embed(kw)
        if vec is None:
            vec = _embed(text)
        sim = cosine_similarity([vec], [_EMB_KW_BUF[kw]])[0, 0]
        # log để bạn quan sát
        print(f"[RELEVANT CHECK] '{kw}' vs sentence  →  {sim:.3f}")
        thresh = SIM_COS_SHORT if len(tokens) <= 2 else SIM_COS_LONG
        if sim >= thresh:
            return True
    return False

def _clean_html(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

# ── MAIN CLASS ───────────────────────────────────────
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

                    # 1) keyword filter
                    if not _keyword_relevant(text, keywords or []):
                        continue
                    # 2) duplicate filter
                    if _is_duplicate(text):
                        print(f"[DUP] {source:12} | {title}")
                        continue

                    articles.append(
                        {"title": title, "summary": summary, "link": link, "source": source}
                    )
                    taken += 1

            except Exception as e:
                print(f"[{source}] ERROR: {e}", file=sys.stderr)

        return articles
