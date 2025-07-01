from __future__ import annotations
import os, json, logging, argparse, sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("FbCrawlerApify")


class FacebookCrawlerApify:
    """Thu thập bài viết qua Apify Actor API và trả về các trường rút gọn."""

    DEFAULT_POST_ACTOR = "apify/facebook-posts-scraper"

    def __init__(self) -> None:
        self.token: str | None = os.getenv("APIFY_TOKEN")
        if not self.token:
            raise ValueError("⚠  APIFY_TOKEN phải khai báo trong .env hoặc ENV")
        self.page_id: str | None = os.getenv("FB_PAGE_ID")
        if not self.page_id:
            raise ValueError("⚠  FB_PAGE_ID phải khai báo trong .env hoặc ENV")

        self.post_actor = os.getenv("APIFY_POST_ACTOR", self.DEFAULT_POST_ACTOR)
        self.client = ApifyClient(self.token)

    # --------------------------------------------------
    def fetch_posts(self, *, days: int = 10, limit: Optional[int] = None) -> List[Dict]:
        """Trả về **những bài viết** trong `days` ngày gần nhất.
        - `limit` = None → lấy tất cả.
        """
        since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        log.info("▶️  Call actor %s cho page %s", self.post_actor, self.page_id)

        results_limit = limit * 5 if limit else 10000  # đảm bảo không cắt sớm
        run_input = {
            "startUrls": [{"url": f"https://www.facebook.com/{self.page_id}"}],
            "resultsLimit": results_limit,
            "onlyPostsNewerThan": since,
            "proxyConfig": {"useApifyProxy": True},
        }
        run = self.client.actor(self.post_actor).call(run_input=run_input)
        raw_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
        log.info("📄  Nhận %d bài (chưa lọc)", len(raw_items))

        posts: List[Dict] = []
        for it in raw_items:
            # --------------- Ưu tiên lấy ảnh từ photo_image.uri -------------
            images: List[str] = []
            media = it.get("media")
            if isinstance(media, list):
                for m in media:
                    if not isinstance(m, dict):
                        continue
                    uri: Optional[str] = None
                    # ưu tiên trường photo_image.uri
                    if isinstance(m.get("photo_image"), dict):
                        uri = m["photo_image"].get("uri")
                    # fallback sang url nếu uri không có
                    if not uri:
                        uri = m.get("url")
                    if uri and uri.startswith("http"):
                        images.append(uri)
            # loại trùng
            images = list(dict.fromkeys(images))

            # --------------- Lấy số like, comment ---------------------------
            likes_cnt = (
                it.get("likes")
                or it.get("likesCount")
                or it.get("topReactionsCount")
                or it.get("reactions")
                or 0
            )
            comments_cnt = (
                it.get("comments")
                or it.get("commentsCount")
                or it.get("commentCount")
                or 0
            )

            post = {
                "text": it.get("text", ""),
                "images": images,
                "url": it.get("url") or it.get("topLevelUrl"),
                "likes": int(likes_cnt),
                "comments": int(comments_cnt),
            }
            posts.append(post)
            if limit and len(posts) >= limit:
                break

        log.info("✅  Hoàn tất – trả về %d bài", len(posts))
        return posts



# ---------------- CLI ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Crawler via Apify API (fields rút gọn)")
    parser.add_argument("--days", type=int, default=10, help="Số ngày gần nhất")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--limit", type=int, help="Số bài tối đa (mặc định: tất cả)")
    group.add_argument("--all", action="store_true", help="Lấy tất cả bài")
    args = parser.parse_args(sys.argv[1:])

    lim = None if args.all or args.limit is None else args.limit
    crawler = FacebookCrawlerApify()
    data = crawler.fetch_posts(days=args.days, limit=lim)
    print(json.dumps(data, ensure_ascii=False, indent=2))