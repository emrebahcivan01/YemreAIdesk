"""
LTF Sinyal Motoru
HTF bias durumunu SQLite'a kaydeder.
Gelen 5M GATE sinyalini HTF bias ile karşılaştırır.
"""

import re
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "journal.db"


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _init() -> None:
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS htf_bias (
                symbol      TEXT PRIMARY KEY,
                bias        TEXT NOT NULL,
                score       TEXT,
                raw_message TEXT,
                updated_at  TEXT NOT NULL
            )
        """)
        c.commit()


# ── HTF Bias Güncelleme ────────────────────────────────────────────

def update_htf_bias(symbol: str, bias: str, score: str = "", raw_message: str = "") -> None:
    """HTF alertinden gelen bias'ı kaydet / güncelle (UPSERT)."""
    _init()
    with _conn() as c:
        c.execute("""
            INSERT INTO htf_bias (symbol, bias, score, raw_message, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                bias        = excluded.bias,
                score       = excluded.score,
                raw_message = excluded.raw_message,
                updated_at  = excluded.updated_at
        """, (symbol.upper(), bias.upper(), score, raw_message, datetime.now().isoformat()))
        c.commit()


def get_htf_bias(symbol: str) -> dict | None:
    """Sembol için son HTF bias kaydını döndür."""
    _init()
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM htf_bias WHERE symbol = ?", (symbol.upper(),)
        ).fetchone()
    return dict(row) if row else None


def get_all_htf_biases() -> list[dict]:
    """Tüm takip edilen sembollerin bias durumunu döndür."""
    _init()
    with _conn() as c:
        rows = c.execute("SELECT * FROM htf_bias ORDER BY updated_at DESC").fetchall()
    return [dict(r) for r in rows]


# ── Mesaj Parsing ─────────────────────────────────────────────────

def parse_htf_bias_from_message(message: str) -> tuple[str, str]:
    """
    Webhook mesajından HTF bias yönünü ve score'u çıkar.
    Desteklenen formatlar:
      'HTF BIAS BULLISH | Score: 7/9'
      '4H CHoCH BULLISH'
      '4H BOS BULL'
      'BULLISH TRIGGER'
    Döner: (bias, score)  — bias: 'BULLISH' | 'BEARISH' | ''
    """
    msg_up = message.upper()

    bias = ""
    if any(k in msg_up for k in ("BULLISH", "BULL", "BOS BULL", "CHOCH BULL")):
        bias = "BULLISH"
    if any(k in msg_up for k in ("BEARISH", "BEAR", "BOS BEAR", "CHOCH BEAR")):
        bias = "BEARISH"

    # Daha spesifik olanlar kazanır
    if "BEARISH" in msg_up or "BOS BEAR" in msg_up or "CHOCH BEAR" in msg_up:
        bias = "BEARISH"
    elif "BULLISH" in msg_up or "BOS BULL" in msg_up or "CHOCH BULL" in msg_up:
        bias = "BULLISH"

    score = ""
    m = re.search(r"(\d+/\d+)", message)
    if m:
        score = m.group(1)

    return bias, score


# ── GATE Alignment Kontrolü ───────────────────────────────────────

def validate_gate(symbol: str, direction: str) -> dict:
    """
    5M GATE sinyali mevcut HTF bias ile uyumlu mu?
    direction: 'BULL' veya 'BEAR'
    Döner: {'aligned': bool, 'htf_bias': str | None, 'reason': str}
    """
    htf = get_htf_bias(symbol)

    if not htf:
        return {
            "aligned": None,
            "htf_bias": None,
            "reason": "HTF bias kaydı yok — ilk HTF alertini bekle",
        }

    bias = htf["bias"]
    is_bull_gate = "BULL" in direction.upper()

    if bias == "BULLISH" and is_bull_gate:
        return {"aligned": True,  "htf_bias": bias, "reason": "HTF BULLISH + BULL GATE ✓"}
    if bias == "BEARISH" and not is_bull_gate:
        return {"aligned": True,  "htf_bias": bias, "reason": "HTF BEARISH + BEAR GATE ✓"}
    if bias == "RANGING":
        return {"aligned": False, "htf_bias": bias, "reason": "HTF RANGING — sinyal filtrendi"}

    gate_txt = "BULL" if is_bull_gate else "BEAR"
    return {
        "aligned": False,
        "htf_bias": bias,
        "reason": f"HTF {bias} ↔ {gate_txt} GATE uyumsuz",
    }
