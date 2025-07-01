import os, json, logging, random, re, argparse, sys, asyncio, hashlib
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

    # ------------ khởi tạo ------------------------------------------------
    @classmethod
    async def create(cls, *, desktop: bool = False):
        self = cls()
        self.desktop = desktop

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
            # 👉 chỉnh đường Chrome phù hợp máy bạn
            "executablePath": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        }

        log.info("[OPEN] Mở Chrome giao diện thật …")
        self.browser: Browser = await launch(**launch_options)
        self.page: Page = (await self.browser.pages())[0]

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

    # ------------ utils ---------------------------------------------------
    async def _expand_see_more(self):
        """Bấm tất cả nút/nhãn 'Xem thêm' hiện trong viewport."""
        js = """
        () => {
          const btns = Array.from(document.querySelectorAll('span, a, div'));
          btns.filter(el => {
             const t = (el.innerText || '').trim();
             return t === 'Xem thêm' || t === 'See more';
          }).forEach(el => el.click());
        }
        """
        try:
            await self.page.evaluate(js)
            await asyncio.sleep(0.8)
        except Exception as e:
            log.debug(f"Không click được See more: {e}")

    # ------------ crawl ---------------------------------------------------
    async def fetch_posts(
    self,
    days: int = 10,
    limit: int = 10,
    max_scroll: int = 120,      # du di nếu feed dài
    idle_retry: int = 4         # số vòng cuộn “trơ” liên tiếp thì dừng
) -> List[Dict]:
        log.info("Scraping %s (≤%s ngày, cần %s bài)", self.page_id, days, limit)

        base = "www.facebook.com" if self.desktop else "m.facebook.com"
        await self.page.goto(f"https://{base}/{self.page_id}", {"waitUntil": "networkidle2"})
        await asyncio.sleep(300)

        posts, seen_ids = [], set()
        scrolls, idle_cnt = 0, 0
        last_height, last_art_cnt = 0, 0

        while scrolls < max_scroll and len(posts) < limit:
            # 1️⃣ mở caption dài trong viewport
            await self._expand_see_more()

            # 2️⃣ lấy danh sách article
            html  = await self.page.content()
            soup  = BeautifulSoup(html, "lxml")
            arts  = self._get_articles(soup)
            log.info("💬 Xét %d article (đã có %d hợp lệ)", len(arts), len(posts))

            added = 0
            for art in arts:
                if len(posts) >= limit:
                    break
                post = self._parse_article(art)
                if not post:
                    continue
                pid = str(post["post_id"]).strip()
                if pid in seen_ids or post["text"].strip().lower() == "ho quoc tuan":
                    continue
                posts.append(post)
                seen_ids.add(pid)
                added += 1

            # 3️⃣ kiểm tra có tiến triển?
            curr_height   = await self.page.evaluate("document.body.scrollHeight")
            curr_art_cnt  = len(arts)
            progressed    = (added > 0) or (curr_height > last_height) or (curr_art_cnt > last_art_cnt)

            if progressed:
                idle_cnt = 0
            else:
                idle_cnt += 1
                if idle_cnt >= idle_retry:
                    log.info("😕 Cuộn %s lần liền không nạp bài mới – dừng.", idle_retry)
                    break

            last_height, last_art_cnt = curr_height, curr_art_cnt

            # 4️⃣ cuộn sát đáy để FB auto-load
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(random.uniform(1.2, 2.0))
            scrolls += 1

        log.info("✅ Thu được %d/%d bài hợp lệ sau %d lần cuộn", len(posts), limit, scrolls)
        return posts[:limit]

    # ------------ helpers -------------------------------------------------
    def _get_articles(self, soup: BeautifulSoup) -> List[BeautifulSoup]:
        # chỉ các container feed có data-tracking-duration-id
        arts = soup.select(
            "div.m.bg-s2[data-mcomponent='MContainer'][data-type='container'][data-tracking-duration-id]"
        )

        good = []
        for art in arts:
            cap_tag = art.select_one("div.native-text.rslh")
            has_caption = bool(cap_tag)
            has_media = art.select_one("img[data-type='image'], video") is not None

            # bỏ nếu không có caption & media
            if not (has_caption or has_media):
                continue

            # caption ngắn hoặc chứa từ khoá giao diện => bỏ
            if has_caption:
                txt = cap_tag.get_text(strip=True)
                bad_kw = ("người theo dõi", "Bài viết", "Giới thiệu", "Chi tiết")
                if len(txt) <= 10 or any(k.lower() in txt.lower() for k in bad_kw):
                    continue

            good.append(art)

        return good


    def _fallback_post_id(self, art, caption: str) -> str:
        """Nếu không tìm thấy id qua link → lấy `data-image-id` → hash caption."""
        img_tag = art.select_one("img[data-image-id]")
        if img_tag and img_tag.get("data-image-id"):
            return img_tag["data-image-id"]
        # hash caption (ổn định cho cùng caption)
        return hashlib.md5(caption.encode("utf-8")).hexdigest()

    def _parse_article(self, art) -> Dict | None:
        # 1. caption
        cap_tag = art.select_one("div.native-text.rslh")
        caption = cap_tag.get_text(" ", strip=True) if cap_tag else ""

        # 2. ảnh
        img_tags = art.select("img[data-type='image']")
        imgs = [img["src"] for img in img_tags if "https://" in img.get("src", "")]

        # 3. nếu không có nội dung gì thì bỏ qua
        if not caption and not imgs:
            return None

        # 4. lọc block vớ vẩn (header/avatar)
        bad_kw = ("người theo dõi", "Bài viết", "Giới thiệu", "Chi tiết")
        if any(k.lower() in caption.lower() for k in bad_kw):
            return None

        # 5. lấy post_id
        post_id = None
        for tag in img_tags:
            pid = tag.get("data-image-id")
            if pid:
                post_id = pid
                break
        if not post_id:
            post_id = self._fallback_post_id(art, caption)

        if caption.strip().lower() == "ho quoc tuan":
            return None

        # 6. comment (tuỳ chọn)
        cmt_tags = art.select("div[dir='auto'][data-visualcompletion='ignore-dynamic']")[:2]
        comments = [c.get_text(" ", strip=True) for c in cmt_tags]

        return {
            "post_id": post_id,
            "text": caption,
            "url": None,
            "images": imgs,
            "comments": comments,
        }


    # ------------ cookies -------------------------------------------------
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
                for line in fp:
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
