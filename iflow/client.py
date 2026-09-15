from typing import Optional
from playwright.async_api import async_playwright
BLOCK_RESOURCES = "**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,woff2,mp4,ttf}"
async def get_page_content(
    url: str,
    *,
    headless: bool = False,
    wait_selector: str = "text=BUFF",
    timeout_goto: int = 60000,
    timeout_cf: int = 15000,
    timeout_selector: int = 5000,
    viewport: Optional[dict] = None,
) -> str:
    """每次调用独立启动/关闭浏览器，避免跨 event-loop 复用导致的 WebSocket 失效。"""
    viewport = viewport or {"width": 1280, "height": 800}
    pw = await async_playwright().start()
    browser = None
    page = None
    try:
        browser = await pw.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-extensions",
                "--disable-gpu",
            ],
        )
        context = await browser.new_context(viewport=viewport)
        await context.route(BLOCK_RESOURCES, lambda route: route.abort())
        page = await context.new_page()
        await page.goto(url, timeout=timeout_goto, wait_until="domcontentloaded")
        try:
            await page.wait_for_function(
                "document.title.indexOf('Just a moment') === -1",
                timeout=timeout_cf,
            )
        except Exception:
            pass
        try:
            await page.wait_for_selector(wait_selector, timeout=timeout_selector)
        except Exception:
            pass
        return await page.content()
    finally:
        if page:
            try:
                await page.close()
            except Exception:
                pass
        if browser:
            try:
                await browser.close()
            except Exception:
                pass
        try:
            await pw.stop()
        except Exception:
            pass
