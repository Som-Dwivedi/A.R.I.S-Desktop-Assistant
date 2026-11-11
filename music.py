from playwright.sync_api import sync_playwright
import time

_browser = None
_page = None
_playwright = None


def _get_browser():
    global _browser, _page, _playwright

    if _browser is None:
        _playwright = sync_playwright().start()

        _browser = _playwright.chromium.launch(
            headless=False
        )

        _page = _browser.new_page()

    return _page


def play_music(query):
    query = query.strip()

    if not query:
        return "Bhai kya play karna hai?"

    try:
        page = _get_browser()

        search_url = (
            "https://music.youtube.com/search?q="
            + query.replace(" ", "+")
        )

        page.goto(search_url, wait_until="domcontentloaded")

        time.sleep(3)

        # Click the first visible song result
        song = page.locator(
            "ytmusic-responsive-list-item-renderer"
        ).first

        song.click()

        time.sleep(2)

        return f"Playing {query}..."

    except Exception as e:
        return f"Music error: {str(e)}"