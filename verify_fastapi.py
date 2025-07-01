import os, json, logging, random, re, argparse, sys, asyncio
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
    MOBILE_UA = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    )

    # ---------- Khởi tạo --------------------------------------------------
    @classmethod
    async def create(cls, *, desktop: bool = False):
        self = cls()
        self.desktop = desktop

        self.page_id = os.getenv("FB_PAGE_ID")
        if not self.page_id:
            raise ValueError("⚠  FB_PAGE_ID phải khai báo trong .env")

        # ---- cookie path
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

        launch_options = {
            "headless": False,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--lang=vi-VN",
                "--start-maximized",
            ],
            "ignoreHTTPSErrors": True,
            "executablePath": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        }

        log.info("[OPEN] Mở Chrome giao diện thật …")
        self.browser: Browser = await launch(**launch_options)
        self.page: Page = (await self.browser.pages())[0]

        # UA & viewport
        if self.desktop:
            await self.page.setUserAgent(
                self.MOBILE_UA.replace(
                    "iPhone; CPU iPhone OS 15_0 like Mac OS X",
                    "Windows NT 10.0; Win64; x64",
                )
            )
            await self.page.setViewport({"width": 1920, "height": 1080})
        else:
            await self.page.setUserAgent(self.MOBILE_UA)
            await self.page.setViewport({"width": 800, "height": 1200})

        await self._inject_cookies()
        return self

    async def close(self):
        if self.browser:
            await self.browser.close()

    # ---------- Hàm tiện ích ---------------------------------------------
    async def _expand_see_more(self):
        """Nhấn mọi nút 'Xem thêm' / 'See more' hiện trong viewport."""
        js = """
        () => {
            Array.from(document.querySelectorAll('div[role=button], span[role=button], a[role=button]'))
              .filter(el => {
                 const t = (el.innerText||'').trim();
                 return t === 'Xem thêm' || t === 'See more';
              })
              .forEach(el => el.click());
        }
        """
        try:
            await self.page.evaluate(js)
            await asyncio.sleep(0.8)
        except Exception as e:
            log.debug(f"Không click được See more: {e}")

    # ---------- Phần scrape chính ----------------------------------------
    async def fetch_posts(self, days: int = 10, limit: int = 50) -> List[Dict]:
        log.info("Scraping %s (≤%s ngày, max %s bài)", self.page_id, days, limit)
        since = datetime.now() - timedelta(days=days)
        base = "www.facebook.com" if self.desktop else "m.facebook.com"
        url = f"https://{base}/{self.page_id}"
        await self.page.goto(url, {"waitUntil": "networkidle2"})

        # chờ 1 bài viết đầu
        try:
            await self.page.waitForSelector(
                "div[data-mcomponent='MContainer'][data-type='container'].m.bg-s2",
                {"timeout": 15000},
            )
        except Exception:
            log.warning("⏲  Hết giờ chờ bài viết – slug sai hoặc cookie hết hạn")

        posts: List[Dict] = []
        last_height, same_cnt = 0, 0
        while len(posts) < limit and same_cnt < 4:
            # mở caption dài
            await self._expand_see_more()

            # lấy HTML
            html_content = await self.page.content()
            soup = BeautifulSoup(html_content, "lxml")
            articles = self._get_articles(soup)
            log.info("💬 Đang xét %d bài (đã thu %d)", len(articles), len(posts))

            for art in articles:
                post = self._parse_article(art)
                if not post:
                    continue
                if datetime.fromisoformat(post["time"]) < since:
                    same_cnt = 4
                    break
                if post["post_id"] not in {p["post_id"] for p in posts}:
                    posts.append(post)
                    if len(posts) >= limit:
                        break

            # cuộn
            await self.page.evaluate("window.scrollBy(0, 1200)")
            await asyncio.sleep(random.uniform(1.2, 1.8))
            new_height = await self.page.evaluate("document.body.scrollHeight")
            same_cnt = same_cnt + 1 if new_height == last_height else 0
            last_height = new_height

        log.info("✅ Hoàn thành – lấy %d bài", len(posts))
        return posts[:limit]

    # ---------- Helper parse ---------------------------------------------
    def _get_articles(self, soup: BeautifulSoup):
        anchors = soup.select('a[href*="/posts/"], a[href*="story_fbid="]')
        articles = []
        for a in anchors:
            art = a.find_parent("div")
            while art and len(art.find_all("a")) < 3:  # loại bỏ comment hoặc gợi ý
                art = art.find_parent("div")
            if art and art not in articles:
                articles.append(art)
        return articles

    def _parse_article(self, art) -> Dict | None:
        link_tag = art.select_one('a[href*="/posts/"], a[href*="story_fbid="]')
        if not link_tag:
            return None
        href = link_tag.get("href")
        full_url = href if href.startswith("http") else f"https://m.facebook.com{href}"
        m = re.search(r"story_fbid=(\d+)|/posts/(\d+)|pfbid0[a-zA-Z0-9]+", full_url)
        post_id = m.group(1) or m.group(2) or m.group(0) if m else None
        if not post_id:
            return None

        cap_tag = art.select_one("div[dir='auto'], span[dir='auto']")
        caption = cap_tag.get_text("\n", strip=True) if cap_tag else ""

        imgs = [img["src"] for img in art.select("img") if "https://" in img.get("src", "")]
        cmt_tags = art.select("div[dir='auto'][data-visualcompletion='ignore-dynamic']")[:2]
        comments = [c.get_text(" ", strip=True) for c in cmt_tags]

        return {
            "post_id": post_id,
            "text": caption,
            "url": full_url,
            "images": imgs,
            "comments": comments,
        }

    # ---------- Cookie ----------------------------------------------------
    async def _inject_cookies(self):
        cookies_to_set = []
        if self.cookie_path.endswith(".json"):
            with open(self.cookie_path, encoding="utf-8") as fp:
                cookies = json.load(fp)
            for c in cookies:
                cookies_to_set.append(
                    {
                        "name": c.get("name"),
                        "value": c.get("value"),
                        "domain": c.get("domain", ".facebook.com"),
                        "path": c.get("path", "/"),
                        "expires": c.get("expirationDate", -1),
                        "httpOnly": c.get("httpOnly", False),
                        "secure": c.get("secure", False),
                    }
                )
        else:
            with open(self.cookie_path, encoding="utf-8") as fp:
                txt = fp.readlines()
            for line in txt:
                if not line.startswith(".facebook.com"):
                    continue
                parts = line.strip().split("\t")
                if len(parts) == 7:
                    cookies_to_set.append(
                        {
                            "name": parts[5],
                            "value": parts[6],
                            "domain": parts[0],
                            "path": parts[2],
                            "expires": int(parts[4]),
                            "secure": parts[3] == "TRUE",
                        }
                    )

        await self.page.setCookie(*cookies_to_set)
        log.info("Đã nạp %d cookie", len(cookies_to_set))


# ---------------- CLI -----------------------------------------------------
async def main():
    parser = argparse.ArgumentParser(description="Facebook Crawler (Pyppeteer)")
    parser.add_argument("--desktop", action="store_true", help="Dùng giao diện desktop")
    parser.add_argument("--days", type=int, default=10, help="Số ngày gần nhất")
    parser.add_argument("--limit", type=int, default=10, help="Số bài tối đa")
    args = parser.parse_args(sys.argv[1:])

    crawler = None
    try:
        crawler = await FacebookCrawler.create(desktop=args.desktop)
        data = await crawler.fetch_posts(days=args.days, limit=args.limit)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        log.error(f"Lỗi: {e}", exc_info=True)
    finally:
        if crawler:
            await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
