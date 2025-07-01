import asyncio
from pyppeteer import launch

async def main():
    browser = await launch(
        headless=False,  # Đặt True nếu muốn chạy nền (không hiển thị giao diện)
        executablePath=r"C:\Program Files\Google\Chrome\Application\chrome.exe",  # ✅ Đường dẫn đến Chrome thật
        args=["--no-sandbox", "--disable-setuid-sandbox"]
    )
    page = await browser.newPage()
    await page.goto('https://www.google.com')
    print("✅ Đã mở Google trong trình duyệt Chrome!")
    await asyncio.sleep(10)  # Giữ trình duyệt mở 10 giây
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
