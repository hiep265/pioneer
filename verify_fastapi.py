"""
services/expert_crawler/facebook_crawler_puppeteer.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sử dụng **Pyppeteer** thay cho Selenium để cào dữ liệu Facebook.
- Hoạt động bất đồng bộ (async/await), thường nhanh hơn Selenium.
- Tự động quản lý trình duyệt Chromium.
- Giữ nguyên toàn bộ logic đọc cookie, cuộn trang, và cấu trúc dữ liệu trả về.

YÊU CẦU HỆ THỐNG
----------------
Python ≥3.9
pip install pyppeteer==1.0.2 beautifulsoup4 python-dotenv

ENV:
- FB_PAGE_ID      : slug hoặc ID số của profile/page.
- FB_COOKIES      : fallback path tới file cookie nếu không có trong ./cookies.

Ví dụ chạy nhanh:
    python -m services.expert_crawler.facebook_crawler_puppeteer
"""
from __future__ import annotations
import os, json, logging, time, random, re, argparse, sys, asyncio
from datetime import datetime, timedelta
from typing import List, Dict

from bs4 import BeautifulSoup
from pyppeteer import launch
from pyppeteer.page import Page
from pyppeteer.browser import Browser
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("FbCrawlerPuppeteer")


class FacebookCrawler:
    """Thu thập bài viết bằng Pyppeteer, hoạt động bất đồng bộ (async)."""

    MOBILE_UA = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    )

    # Do __init__ không thể là async, ta dùng @classmethod để tạo instance
    @classmethod
    async def create(cls, *, desktop: bool = False, headless: bool = True):
        self = cls()
        self.headless = headless
        self.desktop = desktop

        # ---------- ENV & Cookie (giống hệt bản Selenium) -------------------
        self.page_id = os.getenv("FB_PAGE_ID")
        if not self.page_id:
            raise ValueError("⚠  FB_PAGE_ID phải khai báo trong .env")

        txt_path = "cookies/www.facebook.com_cookies.txt"
        json_path = "cookies/fb_cookie.json"
        self.cookie_path = (
            txt_path
            if os.path.isfile(txt_path)
            else json_path
            if os.path.isfile(json_path)
            else os.getenv("FB_COOKIES", json_path)
        )
        if not os.path.isfile(self.cookie_path):
            raise FileNotFoundError(f"Cookie file '{self.cookie_path}' không tồn tại")

        # ---------- Khởi tạo trình duyệt Pyppeteer -------------------------
        launch_options = {
            "headless": headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--lang=vi-VN",
            ],
            # Bỏ qua các lỗi HTTPS không an toàn (nếu có)
            "ignoreHTTPSErrors": True,
        }
        if not headless:
            log.info("[OPEN] Chrome UI visible – headless=False")
            launch_options["args"].append("--start-maximized")

        self.browser: Browser = await launch(**launch_options)
        self.page: Page = (await self.browser.pages())[0]

        # Thiết lập User-Agent và Viewport
        if self.desktop:
            await self.page.setUserAgent(self.MOBILE_UA.replace("iPhone; CPU iPhone OS 15_0 like Mac OS X", "Windows NT 10.0; Win64; x64"))
            await self.page.setViewport({'width': 1920, 'height': 1080})
        else:
            await self.page.setUserAgent(self.MOBILE_UA)
            await self.page.setViewport({'width': 800, 'height': 1200})

        await self._inject_cookies()
        return self

    # ------------------------------------------------------
    async def close(self):
        """Đóng trình duyệt."""
        if self.browser:
            await self.browser.close()

    async def fetch_posts(self, days: int = 10, limit: int = 50) -> List[Dict]:
        """Trả về list bài viết ≤ `limit` trong `days` ngày gần nhất."""
        log.info("Scraping %s (≤%s ngày, max %s bài)", self.page_id, days, limit)
        since = datetime.now() - timedelta(days=days)
        base = "www.facebook.com" if self.desktop else "m.facebook.com"
        url = f"https://{base}/{self.page_id}"
        await self.page.goto(url, {"waitUntil": "networkidle2"})

        # Đợi tối đa 15s cho tới khi ít nhất 1 bài xuất hiện
        try:
            await self.page.waitForSelector(
                "div[data-ft*='top_level_post_id']", {"timeout": 15000}
            )
        except Exception:
            log.warning("⏲  Hết giờ chờ bài viết – có thể slug sai hoặc cookie hết hạn")

        posts: List[Dict] = []
        last_height, same_cnt = 0, 0
        while len(posts) < limit and same_cnt < 4:
            html_content = await self.page.content()
            soup = BeautifulSoup(html_content, "lxml")
            articles = self._get_articles(soup)
            log.debug("Đang xét %d bài trên trang", len(articles))

            for art in articles:
                post = self._parse_article(art)
                if not post:
                    continue
                if datetime.fromisoformat(post["time"]) < since:
                    same_cnt = 4  # trigger break outer loop
                    break
                if post["post_id"] not in {p["post_id"] for p in posts}:
                    posts.append(post)
                    if len(posts) >= limit:
                        break
            
            # Cuộn nhẹ để tải thêm
            await self.page.evaluate("window.scrollBy(0, 1200)")
            await asyncio.sleep(random.uniform(1.5, 2.2))
            
            new_height = await self.page.evaluate("document.body.scrollHeight")
            same_cnt = same_cnt + 1 if new_height == last_height else 0
            last_height = new_height

        log.info("Hoàn thành – lấy được %d bài", len(posts))
        # Không tự động đóng trình duyệt, để có thể gọi fetch_posts nhiều lần
        return posts[:limit]

    # ------------------------------------------------------
    # Hai hàm _get_articles và _parse_article giữ nguyên vì dùng BeautifulSoup
    @staticmethod
    def _get_articles(soup: BeautifulSoup):
        return soup.select("div[data-ft*='top_level_post_id']")

    def _parse_article(self, art) -> Dict | None:
        link_tag = art.select_one("a[href*='story_fbid'], a[href*='/posts/']")
        if not link_tag:
            return None
        href = link_tag.get("href")
        full_url = href if href.startswith("http") else f"https://m.facebook.com{href}"
        m = re.search(r"story_fbid=(\d+)|/posts/(\d+)|pfbid0[a-zA-Z0-9]+", full_url)
        post_id = None
        if m:
            # Ưu tiên ID số, fallback về pfbid
            post_id = m.group(1) or m.group(2) or m.group(0)

        if not post_id:
            return None

        utime = art.select_one("abbr[data-utime]")
        ts_iso = datetime.now().isoformat()
        if utime and utime.has_attr("data-utime"):
            ts_iso = datetime.fromtimestamp(int(utime["data-utime"])).isoformat()
        
        cap_tag = art.select_one("div[data-ft] p, div[data-ft] span, div[dir='auto']")
        caption = cap_tag.get_text("\n", strip=True) if cap_tag else ""
        
        imgs = [img["src"] for img in art.select("img") if "https://" in img.get("src", "")]
        
        cmt_tags = art.select("div[dir='auto'][data-visualcompletion='ignore-dynamic']")[:2]
        comments = [c.get_text(" ", strip=True) for c in cmt_tags]
        
        return {
            "post_id": post_id,
            "text": caption,
            "time": ts_iso,
            "url": full_url,
            "images": imgs,
            "comments": comments,
        }

    # ------------------------------------------------------
    async def _inject_cookies(self):
        # Pyppeteer cần nạp cookie cho domain cụ thể
        # nên ta không cần truy cập trang trước như Selenium
        cookies_to_set = []
        if self.cookie_path.endswith(".json"):
            with open(self.cookie_path, encoding="utf-8") as fp:
                cookies = json.load(fp)
            for c in cookies:
                # Pyppeteer cần một số trường bắt buộc
                cookies_to_set.append({
                    "name": c.get("name"),
                    "value": c.get("value"),
                    "domain": c.get("domain", ".facebook.com"),
                    "path": c.get("path", "/"),
                    "expires": c.get("expirationDate", -1),
                    "httpOnly": c.get("httpOnly", False),
                    "secure": c.get("secure", False),
                })
        else: # .txt
            with open(self.cookie_path, encoding="utf-8") as fp:
                txt = fp.readlines()
            for line in txt:
                line = line.strip()
                if not line or not line.startswith(".facebook.com"):
                    continue
                parts = line.split("\t")
                if len(parts) == 7:
                    cookies_to_set.append({
                        "name": parts[5],
                        "value": parts[6],
                        "domain": parts[0],
                        "path": parts[2],
                        "expires": int(parts[4]),
                        "secure": parts[3] == "TRUE",
                    })

        await self.page.setCookie(*cookies_to_set)
        log.info("Đã nạp %d cookie vào trình duyệt", len(cookies_to_set))


# ---------------- CLI chạy thử nhanh ----------------------
async def main():
    parser = argparse.ArgumentParser(description="Facebook Crawler (Pyppeteer)")
    parser.add_argument("--show", action="store_true", help="Mở cửa sổ Chrome (headless=False)")
    parser.add_argument("--desktop", action="store_true", help="Dùng giao diện desktop")
    parser.add_argument("--days", type=int, default=10, help="Số ngày gần nhất")
    parser.add_argument("--limit", type=int, default=10, help="Số bài tối đa")
    args = parser.parse_args(sys.argv[1:])

    crawler = None
    try:
        crawler = await FacebookCrawler.create(desktop=args.desktop, headless=not args.show)
        data = await crawler.fetch_posts(days=args.days, limit=args.limit)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        log.error(f"Lỗi xảy ra: {e}", exc_info=True)
    finally:
        if crawler:
            await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())