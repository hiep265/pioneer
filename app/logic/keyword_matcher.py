import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple

# ── CONFIG ───────────────────────────────────────────
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
SIM_COS_THRESHOLD = 0.50  # min cosine for relevance

MODEL = SentenceTransformer(MODEL_NAME)
MODEL.max_seq_length = 256

_EMB_KW_BUF: Dict[str, np.ndarray] = {}

# ── UTILS ────────────────────────────────────────────
def _embed(text: str) -> np.ndarray:
    return MODEL.encode(text, normalize_embeddings=True)

class KeywordMatcher:
    def __init__(self):
        pass

    def match_and_score(self, text: str, keywords: List[str]) -> Tuple[float, str]:
        if not keywords:
            return 0.0, "No keywords provided."

        text_lower = text.lower()
        text_embedding = _embed(text)
        
        max_sim = 0.0
        matched_keyword = ""
        
        for kw in keywords:
            kw_norm = kw.lower().strip()
            
            # Exact match check
            if kw_norm in text_lower:
                return 1.0, f"Exact match for keyword: '{kw}'"
            
            # Semantic similarity check
            if kw not in _EMB_KW_BUF:
                _EMB_KW_BUF[kw] = _embed(kw)
            
            sim = cosine_similarity([text_embedding], [_EMB_KW_BUF[kw]])[0, 0]
            
            if sim > max_sim:
                max_sim = sim
                matched_keyword = kw
        
        if max_sim >= SIM_COS_THRESHOLD:
            return max_sim, f"Semantic match for keyword: '{matched_keyword}' (score: {max_sim:.2f})"
        else:
            return 0.0, "No relevant keywords found."

if __name__ == '__main__':
    matcher = KeywordMatcher()
    
    # Test cases
    article_text_1 = "President Biden discusses new economic policies and trade agreements."
    keywords_1 = ["Biden", "economy", "trade"]
    score_1, reason_1 = matcher.match_and_score(article_text_1, keywords_1)
    print(f"Text 1: '{article_text_1}'\nKeywords: {keywords_1}\nScore: {score_1:.2f}, Reason: {reason_1}\n")

    article_text_2 = "Local news about a cat stuck in a tree."
    keywords_2 = ["politics", "global affairs"]
    score_2, reason_2 = matcher.match_and_score(article_text_2, keywords_2)
    print(f"Text 2: '{article_text_2}'\nKeywords: {keywords_2}\nScore: {score_2:.2f}, Reason: {reason_2}\n")

    article_text_3 = "The stock market experienced a significant downturn today."
    keywords_3 = ["stock market crash"]
    score_3, reason_3 = matcher.match_and_score(article_text_3, keywords_3)
    print(f"Text 3: '{article_text_3}'\nKeywords: {keywords_3}\nScore: {score_3:.2f}, Reason: {reason_3}\n")
