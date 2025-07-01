# app/logic/expert_service.py
from typing import List, Dict, Optional
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from dotenv import load_dotenv

from ..repositories.fb_scraper import FacebookCrawlerApify
from .keyword_matcher import KeywordMatcher

load_dotenv()

# Khởi tạo OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

openai_client = OpenAI(api_key=api_key)

# Khởi tạo Vietnamese Embedding model
VIETNAMESE_MODEL_NAME = "AITeamVN/Vietnamese_Embedding"
try:
    vietnamese_model = SentenceTransformer(VIETNAMESE_MODEL_NAME)
    vietnamese_model.max_seq_length = 256
except Exception as e:
    print(f"Không thể tải model {VIETNAMESE_MODEL_NAME}: {e}")
    print("Sử dụng model dự phòng...")
    vietnamese_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    vietnamese_model.max_seq_length = 256

class ExpertService:
    """
    Lớp logic nghiệp vụ để xử lý các hoạt động liên quan đến chuyên gia.
    """
    def __init__(self):
        """
        Khởi tạo các repository và service cần thiết.
        """
        self.fb_crawler = FacebookCrawlerApify()
        self.kw_matcher = KeywordMatcher()
        self.vietnamese_model = vietnamese_model
        self.openai_client = openai_client

    def translate_to_vietnamese(self, text: str) -> str:
        """
        Dịch văn bản từ tiếng Anh sang tiếng Việt sử dụng ChatGPT.
        
        Args:
            text: Văn bản cần dịch.
            
        Returns:
            Văn bản đã được dịch sang tiếng Việt.
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Bạn là một trợ lý dịch thuật. Hãy dịch văn bản sau từ tiếng Anh sang tiếng Việt. Chỉ trả về văn bản đã dịch, không thêm bất kỳ giải thích nào."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Lỗi khi dịch văn bản: {e}")
            return text  # Trả về văn bản gốc nếu có lỗi
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Lấy vector embedding cho văn bản sử dụng Vietnamese Embedding model.
        
        Args:
            text: Văn bản cần lấy embedding.
            
        Returns:
            Vector embedding của văn bản.
        """
        return self.vietnamese_model.encode(text, normalize_embeddings=True)
    
    def get_relevant_expert_posts(
        self,
        keywords: Optional[List[str]],
        days: int,
        limit: int,
        content: Optional[str] = None
    ) -> List[Dict]:
        """
        Lấy các bài đăng chuyên gia có nội dung phù hợp với bài báo đầu vào (nếu có).
        Nếu không có bài nào đủ độ tương đồng, trả về danh sách rỗng.
        Nếu không có content, lọc theo từ khóa.

        Args:
            keywords: Danh sách từ khóa để lọc.
            days: Số ngày gần nhất để lấy bài.
            limit: Số lượng tối đa bài đăng cần lấy ban đầu từ nguồn.
            content: Nội dung bài báo tiếng Anh (sẽ được dịch sang tiếng Việt).

        Returns:
            Danh sách các bài đăng phù hợp với độ tương đồng cao, hoặc theo từ khóa.
        """
        SIMILARITY_THRESHOLD = 0.4  # Ngưỡng tương đồng để coi là "giống"

        # 1. Lấy bài đăng từ Facebook trong X ngày gần nhất
        all_posts = self.fb_crawler.fetch_posts(days=days, limit=limit)

        # 2. Nếu có nội dung cần so sánh:
        if content:
            vietnamese_content = self.translate_to_vietnamese(content)
            content_embedding = self.get_embedding(vietnamese_content)

            matched_posts = []
            for post in all_posts:
                post_text = post.get("text", "")
                if not post_text.strip():
                    continue

                post_embedding = self.get_embedding(post_text)
                similarity = float(np.dot(content_embedding, post_embedding))  # Dot product

                if similarity >= SIMILARITY_THRESHOLD:
                    post["similarity"] = similarity
                    post["translated_content"] = vietnamese_content
                    matched_posts.append(post)

            # Trả về tất cả bài có độ tương đồng vượt ngưỡng, sắp xếp giảm dần
            return sorted(matched_posts, key=lambda x: x["similarity"], reverse=True)

        # 3. Nếu không có nội dung, lọc theo từ khóa (logic cũ)
        else:
            scored_posts = []
            for post in all_posts:
                post_text = post.get("text", "")
                comments_text = " ".join([c.get("text", "") for c in post.get("comments", [])])
                full_text = f"{post_text} {comments_text}"
                
                score, reason = self.kw_matcher.match_and_score(full_text, keywords or [])

                if score > 0:
                    post["score"] = score
                    post["reason"] = reason
                    scored_posts.append(post)

            return sorted(scored_posts, key=lambda x: x["score"], reverse=True)
