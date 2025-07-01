"""
services/expert_crawler/facebook_crawler_selenium.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sử dụng **Selenium + Chrome headless** thay cho `facebook-scraper`.
- Đọc cookie (JSON hoặc TXT) giống bản cũ → nạp vào trình duyệt.
- Truy cập giao diện **m.facebook.com** (nhẹ, ít JS) để cuộn & lấy bài.
- Trả về list dict {post_id, text, time, url, images, comments} giống interface cũ → không phải sửa downstream code.

YÊU CẦU HỆ THỐNG
----------------
Python ≥3.9
pip install selenium==4.21.0 beautifulsoup4 python-dotenv
Chromium/Chrome + ChromeDriver cùng version (hoặc cài qua selenium-manager tự động).

ENV:
- FB_PAGE_ID      : slug hoặc ID số của profile/page.
- FB_COOKIES      : fallback path tới file cookie nếu không có trong ./cookies.

Ví dụ chạy nhanh:
    python -m services.expert_crawler.facebook_crawler_selenium
"""
from __future__ import annotations
import os, json, logging, time, random, re, argparse, sys
from datetime import datetime, timedelta
from typing import List, Dict

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("FbCrawlerSelenium")


class FacebookCrawler:
    """Thu thập bài viết công khai (hoặc bạn bè, nếu cookie có quyền) bằng Selenium."""

    MOBILE_UA = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    )

    def __init__(self, *, desktop: bool = False, headless: bool = True) -> None:
        """Args:
        desktop: True → dùng giao diện desktop (www.facebook.com) thay vì mobile.
        headless: False → hiển thị cửa sổ Chrome, xem trực tiếp Selenium làm gì.
        """
        self.headless = headless
        self.desktop = desktop

        # ---------- ENV & Cookie -----------------------------
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

        # ---------- Chrome driver -----------------------------
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            # các flag này chỉ cần khi chạy headless
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
        else:
            log.info("[OPEN] Chrome UI visible – headless=False")
            options.add_argument("--start-maximized")

        options.add_argument("--lang=vi-VN")
        if not desktop:
            mobile_emulation = {"userAgent": self.MOBILE_UA}
            options.add_experimental_option("mobileEmulation", mobile_emulation)

        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
        if headless:
            self.driver.set_window_size(800, 1200)

        self._inject_cookies()

    # ------------------------------------------------------
    def fetch_posts(self, days: int = 10, limit: int = 50) -> List[Dict]:
        """Trả về list bài viết ≤ `limit` trong `days` ngày gần nhất."""
        log.info("Scraping %s (≤%s ngày, max %s bài)", self.page_id, days, limit)
        since = datetime.now() - timedelta(days=days)
        base = "www.facebook.com" if self.desktop else "m.facebook.com"
        url = f"https://{base}/{self.page_id}"
        self.driver.get(url)

        # Đợi tối đa 15 s cho tới khi ít nhất 1 bài xuất hiện
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-ft*='top_level_post_id']")
                )
            )
        except Exception:
            log.warning("⏲  Hết giờ chờ bài viết – có thể slug sai hoặc cookie hết hạn")

        posts: List[Dict] = []
        last_height, same_cnt = 0, 0
        while len(posts) < limit and same_cnt < 4:
            soup = BeautifulSoup(self.driver.page_source, "lxml")
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
            self.driver.execute_script("window.scrollBy(0, 1200);")
            time.sleep(random.uniform(1.5, 2.2))
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            same_cnt = same_cnt + 1 if new_height == last_height else 0
            last_height = new_height

        log.info("Hoàn thành – lấy được %d bài", len(posts))
        if self.headless:
            self.driver.quit()
        return posts[:limit]

    # ------------------------------------------------------
    @staticmethod
    def _get_articles(soup: BeautifulSoup):
        return soup.select("div[data-ft*='top_level_post_id']")

    def _parse_article(self, art) -> Dict | None:
        link_tag = art.select_one("a[href*='story_fbid'], a[href*='/posts/']")
        if not link_tag:
            return None
        href = link_tag.get("href")
        full_url = href if href.startswith("http") else f"https://m.facebook.com{href}"
        m = re.search(r"story_fbid=(\d+)|/posts/(\d+)", full_url)
        post_id = m.group(1) or m.group(2) if m else None
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
    def _inject_cookies(self):
        self.driver.get("https://m.facebook.com")
        if self.cookie_path.endswith(".json"):
            with open(self.cookie_path, encoding="utf-8") as fp:
                cookies = json.load(fp)
            for c in cookies:
                self.driver.add_cookie(
                    {
                        "name": c["name"],
                        "value": c["value"],
                        "domain": ".facebook.com",
                        "path": "/",
                    }
                )
        else:
            with open(self.cookie_path, encoding="utf-8") as fp:
                txt = fp.readlines()
            for line in txt:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                n, v = [x.strip() for x in line.split("=", 1)]
                self.driver.add_cookie(
                    {"name": n, "value": v, "domain": ".facebook.com", "path": "/"}
                )
        log.info("Đã nạp %d cookie vào trình duyệt", len(self.driver.get_cookies()))


# ---------------- CLI chạy thử nhanh ----------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Crawler (Selenium)")
    parser.add_argument("--show", action="store_true", help="Mở cửa sổ Chrome (headless=False)")
    parser.add_argument("--desktop", action="store_true", help="Dùng giao diện desktop")
    parser.add_argument("--days", type=int, default=10, help="Số ngày gần nhất")
    parser.add_argument("--limit", type=int, default=10, help="Số bài tối đa")
    args = parser.parse_args(sys.argv[1:])

    crawler = FacebookCrawler(desktop=args.desktop, headless=not args.show)
    data = crawler.fetch_posts(days=args.days, limit=args.limit)
    print(json.dumps(data, ensure_ascii=False, indent=2))