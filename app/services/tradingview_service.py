import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

STORAGE_FILE = Path(__file__).parent.parent.parent / "data" / "tv_storage.json"
SESSION_FILE = Path(__file__).parent.parent.parent / "data" / "tv_session.json"

TIMEFRAMES = [
    ("5M",  "5"),
    ("15M", "15"),
    ("45M", "45"),
    ("1H",  "60"),
    ("4H",  "240"),
    ("8H",  "480"),
    ("1D",  "1D"),
]

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _chart_url(symbol: str, interval: str, chart_id: str = "") -> str:
    base = f"https://www.tradingview.com/chart/{chart_id}/" if chart_id else "https://www.tradingview.com/chart/"
    return f"{base}?symbol={symbol}&interval={interval}"


def _dismiss_popups(page):
    try:
        page.keyboard.press("Escape")
        time.sleep(0.4)
    except Exception:
        pass
    for sel in [
        'button[aria-label="Close"]',
        '[data-name="close"]',
        '[class*="closeButton"]',
        '[class*="close-button"]',
        '.tv-dialog__close',
    ]:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click()
                time.sleep(0.3)
        except Exception:
            pass


def _hide_watchlist(page):
    page.evaluate("""
        () => {
            const sels = ['.widgetbar-wrap', '.layout__area--right',
                          '[class*="widgetbar"]', '[data-name="widgetbar"]'];
            for (const s of sels) {
                const el = document.querySelector(s);
                if (el) el.style.cssText = 'display:none !important; width:0 !important;';
            }
        }
    """)


def _wait_for_chart(page):
    try:
        page.wait_for_selector("canvas", timeout=10000)
    except PWTimeout:
        pass
    time.sleep(5)


def do_login_and_save() -> bool:
    """
    Tarayıcıyı aç, kullanıcı TradingView'a giriş yapsın.
    Giriş tamamlanınca storage_state'i kaydet. True döner.
    Streamlit dışında, standalone çağrılmak üzere tasarlandı.
    """
    STORAGE_FILE.parent.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=_USER_AGENT,
        )
        page = context.new_page()
        page.goto("https://www.tradingview.com/accounts/signin/", wait_until="domcontentloaded")

        print("TradingView signin sayfası açıldı. Giriş yapın...")

        # URL signin'den çıkana kadar bekle — 5 dakika
        page.wait_for_url(
            lambda url: "tradingview.com" in url and "signin" not in url and "accounts" not in url,
            timeout=300000,
        )
        time.sleep(3)

        context.storage_state(path=str(STORAGE_FILE))
        print(f"Session kaydedildi: {STORAGE_FILE}")

        browser.close()
    return True


def capture_all_timeframes(
    symbol: str,
    chart_id: str = "",
    progress_callback=None,
) -> dict[str, bytes]:
    storage_path = _ensure_storage_file()
    screenshots: dict[str, bytes] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
        )
        context = browser.new_context(
            storage_state=storage_path,
            viewport={"width": 1920, "height": 1080},
            user_agent=_USER_AGENT,
        )
        page = context.new_page()

        for tf_name, interval in TIMEFRAMES:
            if progress_callback:
                progress_callback(tf_name)

            url = _chart_url(symbol, interval, chart_id)
            try:
                page.goto(url, wait_until="load", timeout=30000)
            except PWTimeout:
                pass

            _dismiss_popups(page)
            _wait_for_chart(page)
            _hide_watchlist(page)
            time.sleep(0.5)

            screenshots[tf_name] = page.screenshot(type="png")

        browser.close()

    return screenshots


def _ensure_storage_file() -> str:
    """Return path to a valid Playwright storage_state file, converting tv_session.json if needed."""
    if STORAGE_FILE.exists():
        return str(STORAGE_FILE)
    if SESSION_FILE.exists():
        cookies = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
        storage_state = {"cookies": cookies, "origins": []}
        STORAGE_FILE.write_text(json.dumps(storage_state), encoding="utf-8")
        return str(STORAGE_FILE)
    raise RuntimeError("TradingView oturumu bulunamadı. Önce 'TradingView Girişi Yap' butonuna bas.")


_TF_LABEL_TO_INTERVAL = {
    "1M": "1", "3M": "3", "5M": "5", "15M": "15", "30M": "30",
    "1H": "60", "2H": "120", "4H": "240", "8H": "480",
    "1D": "D", "1W": "W",
}


def capture_single(symbol: str, timeframe: str, chart_id: str = "") -> bytes:
    """Tek timeframe için headless screenshot. timeframe: '5M', '4H', '1D' vb."""
    storage_path = _ensure_storage_file()
    interval = _TF_LABEL_TO_INTERVAL.get(timeframe.upper(), timeframe)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=storage_path,
            viewport={"width": 1920, "height": 1080},
            user_agent=_USER_AGENT,
        )
        page = context.new_page()
        url = _chart_url(symbol, interval, chart_id)
        try:
            page.goto(url, wait_until="load", timeout=30000)
        except PWTimeout:
            pass
        _dismiss_popups(page)
        _wait_for_chart(page)
        _hide_watchlist(page)
        time.sleep(1)
        img = page.screenshot(type="png")
        browser.close()

    return img


def clear_session():
    for f in (STORAGE_FILE, SESSION_FILE):
        if f.exists():
            f.unlink()


def has_session() -> bool:
    return STORAGE_FILE.exists() or SESSION_FILE.exists()
