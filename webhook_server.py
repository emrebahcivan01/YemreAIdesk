"""
TradingView → Yemre AI Trading Desk Webhook Sunucusu

Başlatma:
    source venv/bin/activate
    python webhook_server.py        # port 8080

.env ayarları:
    WEBHOOK_AUTO_TELEGRAM=true      # otomatik Telegram gönderimi
    WEBHOOK_GATE_CHANNEL=VIP        # 5M gate sinyalleri için kanal adı
    WEBHOOK_BIAS_CHANNEL=Public     # 4H HTF sinyalleri için kanal adı
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    print("FastAPI kurulu değil. Çalıştır: pip install fastapi uvicorn")
    sys.exit(1)

from app.services import journal_service, telegram_service, pipeline_service

app = FastAPI(
    title="Yemre AI Trading Desk – Webhook",
    description="TradingView alert alıcısı",
    version="0.2",
)

TF_MAP = {
    "1": "1M", "3": "3M", "5": "5M", "15": "15M", "30": "30M",
    "60": "1H", "120": "2H", "240": "4H", "480": "8H",
    "D": "1D", "1D": "1D", "W": "1W",
}


def _fmt_price(val) -> str:
    try:
        f = float(val)
        return f"{f:,.2f}" if f < 10_000 else f"{f:,.1f}"
    except Exception:
        return str(val)


def _pct(entry, level) -> str:
    try:
        e, l = float(entry), float(level)
        diff = (l - e) / e * 100
        sign = "+" if diff >= 0 else ""
        return f"{sign}{diff:.2f}%"
    except Exception:
        return ""


def _build_telegram_message(symbol, timeframe, message, close, sl=None, tp=None) -> str:
    """Alert türüne göre Telegram mesajı oluştur."""
    now = datetime.now(timezone.utc).strftime("%H:%M UTC")
    msg_up = message.upper()

    # ── 5M GATE sinyali ──────────────────────────────────────────
    if "BULL GATE" in msg_up or "BEAR GATE" in msg_up:
        is_bull = "BULL GATE" in msg_up
        icon    = "🟢" if is_bull else "🔴"
        dir_txt = "BULL GATE ✓" if is_bull else "BEAR GATE ✓"

        # Setup nedenini çıkar (FVG MSB NY KZ gibi kısımlar)
        setup = ""
        parts = message.split("|")
        for p in parts:
            p = p.strip()
            if any(k in p.upper() for k in ("FVG","OB","MSB","CISD","SWEEP","IFVG","KZ","LONDON","NY")):
                setup = p
                break

        # Skor
        score = ""
        for p in parts:
            if "/" in p and "Score" not in p and "SL" not in p and "TP" not in p and "Entry" not in p:
                score = p.strip()
                break
            if "Score" in p or ("/" in p and "10" in p):
                score = p.replace("Score:", "").strip().split()[0]
                break

        lines = [f"{icon} <b>{dir_txt}</b>  {symbol} · {timeframe}\n"]
        if setup:
            lines.append(f"📋 <i>{setup}</i>")
        lines.append("")
        lines.append(f"📍 Entry : <code>{_fmt_price(close)}</code>")

        if sl:
            pct = _pct(close, sl)
            lines.append(f"🛑 SL    : <code>{_fmt_price(sl)}</code>  ({pct})")
        if tp:
            pct = _pct(close, tp)
            lines.append(f"🎯 TP    : <code>{_fmt_price(tp)}</code>  ({pct})")
        if sl and tp:
            try:
                risk   = abs(float(close) - float(sl))
                reward = abs(float(tp)    - float(close))
                rr = reward / risk if risk else 0
                lines.append(f"📊 R/R   : 1:{rr:.1f}")
            except Exception:
                pass
        if score:
            lines.append(f"⚡ Score  : {score}/10")
        lines.append(f"\n⏰ {now}")
        return "\n".join(lines)

    # ── 4H HTF sinyali (CHoCH / BOS / Trigger) ───────────────────
    if any(k in msg_up for k in ("CHOCH", "BOS", "HTF", "TRIGGER", "BULLISH", "BEARISH")):
        is_bull = any(k in msg_up for k in ("BULL", "BULLISH"))
        icon    = "📈" if is_bull else "📉"
        # Score varsa çıkar
        score_txt = ""
        if "Score" in message or "/9" in message:
            for p in message.split("|"):
                if "/9" in p:
                    score_txt = "  " + p.strip()
                    break
        lines = [
            f"{icon} <b>HTF Sinyal</b>  {symbol} · {timeframe}",
            f"📝 {message}{score_txt}",
            f"⏰ {now}",
        ]
        return "\n".join(lines)

    # ── Genel alert ───────────────────────────────────────────────
    return (
        f"⚡ <b>Alert</b>  {symbol} · {timeframe}\n"
        f"💰 {_fmt_price(close)}\n"
        f"📝 {message}\n"
        f"⏰ {now}"
    )


def _pick_channel(message: str) -> str | None:
    """Sinyal türüne göre Telegram kanalını seç."""
    channels = telegram_service.get_channels()
    if not channels:
        return None

    msg_up = message.upper()
    is_gate = "BULL GATE" in msg_up or "BEAR GATE" in msg_up
    is_htf  = any(k in msg_up for k in ("CHOCH", "BOS", "HTF", "TRIGGER"))

    if is_gate:
        gate_ch = os.getenv("WEBHOOK_GATE_CHANNEL", "VIP")
        return channels.get(gate_ch) or channels.get("Varsayılan") or next(iter(channels.values()))

    if is_htf:
        bias_ch = os.getenv("WEBHOOK_BIAS_CHANNEL", "Public")
        return channels.get(bias_ch) or channels.get("Varsayılan") or next(iter(channels.values()))

    return channels.get("Varsayılan") or next(iter(channels.values()))


# ── Endpointler ───────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.post("/webhook/tradingview")
async def tradingview_alert(request: Request):
    """TradingView'dan gelen alert'i kaydet ve Telegram'a gönder."""
    try:
        body = await request.body()
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {"message": body.decode("utf-8", errors="replace")}

        symbol    = str(data.get("symbol",   "UNKNOWN")).upper()
        interval  = str(data.get("interval", ""))
        close     = str(data.get("close",    ""))
        message   = str(data.get("message",  ""))
        sl        = data.get("sl")
        tp        = data.get("tp")

        timeframe = TF_MAP.get(interval, interval or "?")

        alert_id = journal_service.save_alert(
            symbol=symbol,
            timeframe=timeframe,
            message=message or f"Alert | Fiyat: {close}",
            source="tradingview",
        )

        # Otomatik Telegram
        auto_notify = os.getenv("WEBHOOK_AUTO_TELEGRAM", "false").lower() == "true"
        tg_sent = False
        if auto_notify and telegram_service.has_any_channel():
            chat_id = _pick_channel(message)
            if chat_id:
                tg_text = _build_telegram_message(symbol, timeframe, message, close, sl, tp)
                ok, _ = telegram_service.send_message(tg_text, chat_id=chat_id)
                tg_sent = ok

        # Otomatik AI pipeline (sadece GATE sinyallerinde)
        auto_pipeline = os.getenv("PIPELINE_AUTO", "false").lower() == "true"
        is_gate = "BULL GATE" in message.upper() or "BEAR GATE" in message.upper()
        pipeline_started = False
        if auto_pipeline and is_gate:
            pipeline_service.run_pipeline(
                alert_id=alert_id,
                symbol=symbol,
                timeframe=timeframe,
                message=message,
                send_telegram=False,
            )
            pipeline_started = True

        return JSONResponse({
            "ok": True,
            "alert_id": alert_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "telegram_sent": tg_sent,
            "pipeline_started": pipeline_started,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts")
async def list_alerts(limit: int = 50):
    alerts = journal_service.get_recent_alerts(limit=limit)
    return {"alerts": alerts, "count": len(alerts)}


if __name__ == "__main__":
    port = int(os.getenv("WEBHOOK_PORT", "8080"))
    auto = os.getenv("WEBHOOK_AUTO_TELEGRAM", "false")
    pipeline = os.getenv("PIPELINE_AUTO", "false")
    print(f"\n  Webhook sunucusu: http://0.0.0.0:{port}")
    print(f"  Otomatik Telegram: {auto}")
    print(f"  Otomatik AI Pipeline: {pipeline}")
    print(f"  Gate kanalı:  {os.getenv('WEBHOOK_GATE_CHANNEL','VIP')}")
    print(f"  Bias kanalı:  {os.getenv('WEBHOOK_BIAS_CHANNEL','Public')}\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
