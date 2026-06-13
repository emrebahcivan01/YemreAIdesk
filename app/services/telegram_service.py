import os
import requests


def get_channels() -> dict[str, str]:
    """Yapılandırılmış Telegram kanallarını döndür. {isim: chat_id}"""
    channels: dict[str, str] = {}
    if cid := os.getenv("TELEGRAM_CHAT_ID", ""):
        channels["Varsayılan"] = cid
    if cid := os.getenv("TELEGRAM_VIP_CHAT_ID", ""):
        channels["VIP Kanal"] = cid
    if cid := os.getenv("TELEGRAM_PUBLIC_CHAT_ID", ""):
        channels["Public Kanal"] = cid
    return channels


def _token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "")


def send_message(text: str, chat_id: str | None = None) -> tuple[bool, str]:
    token = _token()
    cid = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")

    if not token or not cid:
        return False, "TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID eksik."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": cid, "text": text, "parse_mode": "HTML"}

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200 and resp.json().get("ok"):
            return True, "Mesaj gönderildi."
        return False, resp.json().get("description", "Bilinmeyen hata")
    except requests.RequestException as e:
        return False, str(e)


def send_photo(image_bytes: bytes, caption: str = "", chat_id: str | None = None) -> tuple[bool, str]:
    token = _token()
    cid = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")

    if not token or not cid:
        return False, "TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID eksik."

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        resp = requests.post(
            url,
            data={"chat_id": cid, "caption": caption, "parse_mode": "HTML"},
            files={"photo": ("chart.png", image_bytes, "image/png")},
            timeout=15,
        )
        if resp.status_code == 200 and resp.json().get("ok"):
            return True, "Fotoğraf gönderildi."
        return False, resp.json().get("description", "Bilinmeyen hata")
    except requests.RequestException as e:
        return False, str(e)


def has_any_channel() -> bool:
    return bool(_token() and get_channels())
