"""
Otomatik AI Pipeline
GATE sinyali → TradingView screenshot → Claude analiz → Journal kayıt
"""

import threading
from datetime import datetime

from app.services import ai_service, journal_service, tradingview_service, telegram_service

# alert_id → durum
_status: dict[int, dict] = {}
_lock = threading.Lock()


def get_status(alert_id: int) -> dict | None:
    return _status.get(alert_id)


def get_all_statuses() -> dict:
    return dict(_status)


def run_pipeline(
    alert_id: int,
    symbol: str,
    timeframe: str,
    message: str,
    send_telegram: bool = False,
) -> None:
    """Pipeline'ı arka planda çalıştır."""
    t = threading.Thread(
        target=_pipeline_worker,
        args=(alert_id, symbol, timeframe, message, send_telegram),
        daemon=True,
    )
    t.start()


def _pipeline_worker(alert_id, symbol, timeframe, message, send_telegram):
    with _lock:
        _status[alert_id] = {"state": "running", "started_at": datetime.now().isoformat()}

    try:
        # 1. TradingView screenshot
        _set(alert_id, state="screenshot")
        img_bytes = tradingview_service.capture_single(symbol, timeframe)

        # 2. Claude Vision analiz
        _set(alert_id, state="analyzing")
        note = f"Otomatik pipeline · GATE sinyali · {message[:120]}"
        result = ai_service.analyze_chart(img_bytes, symbol, timeframe, manual_note=note)

        # 3. Journal'a kaydet
        _set(alert_id, state="saving")
        analysis_id = journal_service.save_analysis(result, manual_note=note)

        # 4. Opsiyonel Telegram
        if send_telegram and result.telegram_message:
            channels = telegram_service.get_channels()
            chat_id  = channels.get("Varsayılan") or next(iter(channels.values()), None)
            if chat_id:
                telegram_service.send_message(result.telegram_message, chat_id=chat_id)
                journal_service.mark_telegram_sent(analysis_id)

        _set(alert_id,
             state="done",
             analysis_id=analysis_id,
             bias=result.bias,
             confidence=result.confidence,
             summary=(result.summary or "")[:200],
             finished_at=datetime.now().isoformat())

    except Exception as e:
        _set(alert_id, state="error", error=str(e), finished_at=datetime.now().isoformat())


def _set(alert_id, **kwargs):
    with _lock:
        _status.setdefault(alert_id, {}).update(kwargs)
