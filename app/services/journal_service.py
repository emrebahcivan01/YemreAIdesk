import sqlite3
import json
from datetime import datetime
from pathlib import Path
from dataclasses import asdict

DB_PATH = Path(__file__).parent.parent.parent / "data" / "journal.db"


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                bias TEXT,
                confidence INTEGER,
                market_structure TEXT,
                key_levels TEXT,
                summary TEXT,
                long_scenario TEXT,
                short_scenario TEXT,
                no_trade_conditions TEXT,
                risk_notes TEXT,
                telegram_message TEXT,
                manual_note TEXT,
                screenshot_path TEXT,
                telegram_sent INTEGER DEFAULT 0,
                result TEXT DEFAULT NULL
            )
        """)
        conn.commit()


def save_analysis(analysis, manual_note: str = "", screenshot_path: str = "") -> int:
    init_db()
    with _get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO analyses (
                created_at, symbol, timeframe, bias, confidence,
                market_structure, key_levels, summary, long_scenario,
                short_scenario, no_trade_conditions, risk_notes,
                telegram_message, manual_note, screenshot_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            analysis.symbol,
            analysis.timeframe,
            analysis.bias,
            analysis.confidence,
            analysis.market_structure,
            json.dumps(analysis.key_levels, ensure_ascii=False),
            analysis.summary,
            analysis.long_scenario,
            analysis.short_scenario,
            json.dumps(analysis.no_trade_conditions, ensure_ascii=False),
            analysis.risk_notes,
            analysis.telegram_message,
            manual_note,
            screenshot_path,
        ))
        conn.commit()
        return cur.lastrowid


def get_recent_analyses(limit: int = 50) -> list[dict]:
    init_db()
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["key_levels"] = json.loads(d.get("key_levels") or "{}")
        d["no_trade_conditions"] = json.loads(d.get("no_trade_conditions") or "[]")
        result.append(d)
    return result


def mark_telegram_sent(analysis_id: int) -> None:
    init_db()
    with _get_conn() as conn:
        conn.execute(
            "UPDATE analyses SET telegram_sent = 1 WHERE id = ?", (analysis_id,)
        )
        conn.commit()


def update_result(analysis_id: int, result: str) -> None:
    """result: TP | SL | BE | NO_TRADE | RUNNING"""
    init_db()
    with _get_conn() as conn:
        conn.execute(
            "UPDATE analyses SET result = ? WHERE id = ?", (result, analysis_id)
        )
        conn.commit()


def get_daily_signal_number(symbol: str) -> int:
    """Bugün bu sembol için kaçıncı Telegram sinyali olacak (1'den başlar)."""
    init_db()
    today = datetime.now().strftime("%Y-%m-%d")
    prefix = symbol.upper()[:3]
    with _get_conn() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM analyses "
            "WHERE UPPER(symbol) LIKE ? AND DATE(created_at) = ? AND telegram_sent = 1",
            (f"%{prefix}%", today),
        ).fetchone()[0]
    return count + 1


def save_alert(symbol: str, timeframe: str, message: str, source: str = "tradingview") -> int:
    """TradingView webhook alertlerini kaydet."""
    init_db()
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                symbol TEXT,
                timeframe TEXT,
                message TEXT,
                source TEXT,
                processed INTEGER DEFAULT 0
            )
        """)
        cur = conn.execute(
            "INSERT INTO alerts (created_at, symbol, timeframe, message, source) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(), symbol, timeframe, message, source),
        )
        conn.commit()
        return cur.lastrowid


def get_recent_alerts(limit: int = 50) -> list[dict]:
    init_db()
    try:
        with _get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def save_trade(
    symbol: str,
    direction: str,
    entry: float,
    sl: float,
    tp: float,
    risk_usd: float,
    notes: str = "",
    alert_id: int | None = None,
) -> int:
    """Yeni işlem kaydı oluştur."""
    init_db()
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at  TEXT NOT NULL,
                closed_at   TEXT,
                symbol      TEXT NOT NULL,
                direction   TEXT NOT NULL,
                entry       REAL,
                sl          REAL,
                tp          REAL,
                exit_price  REAL,
                risk_usd    REAL,
                result      TEXT DEFAULT 'RUNNING',
                pnl_usd     REAL,
                rr_achieved REAL,
                notes       TEXT,
                alert_id    INTEGER
            )
        """)
        cur = conn.execute(
            """INSERT INTO trades
               (created_at, symbol, direction, entry, sl, tp, risk_usd, notes, alert_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (datetime.now().isoformat(), symbol.upper(), direction.upper(),
             entry, sl, tp, risk_usd, notes, alert_id),
        )
        conn.commit()
        return cur.lastrowid


def close_trade(trade_id: int, result: str, exit_price: float) -> None:
    """İşlemi kapat, P&L ve R:R hesapla."""
    init_db()
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()
        if not row:
            return
        entry     = row["entry"]
        sl        = row["sl"]
        risk_usd  = row["risk_usd"] or 0
        direction = row["direction"]

        risk_pts  = abs(entry - sl) if sl else 0
        if result == "BE":
            pnl_usd = 0.0
            rr = 0.0
        elif risk_pts and risk_usd:
            pts_diff = (exit_price - entry) if direction == "LONG" else (entry - exit_price)
            rr       = pts_diff / risk_pts
            pnl_usd  = rr * risk_usd
        else:
            pnl_usd = 0.0
            rr = 0.0

        conn.execute(
            """UPDATE trades SET result=?, exit_price=?, pnl_usd=?, rr_achieved=?,
               closed_at=? WHERE id=?""",
            (result, exit_price, round(pnl_usd, 2), round(rr, 2),
             datetime.now().isoformat(), trade_id),
        )
        conn.commit()


def get_trades(limit: int = 200) -> list[dict]:
    init_db()
    try:
        with _get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL, closed_at TEXT,
                    symbol TEXT NOT NULL, direction TEXT NOT NULL,
                    entry REAL, sl REAL, tp REAL, exit_price REAL,
                    risk_usd REAL, result TEXT DEFAULT 'RUNNING',
                    pnl_usd REAL, rr_achieved REAL, notes TEXT, alert_id INTEGER
                )
            """)
            rows = conn.execute(
                "SELECT * FROM trades ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def get_trade_stats() -> dict:
    init_db()
    try:
        with _get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL, closed_at TEXT,
                    symbol TEXT NOT NULL, direction TEXT NOT NULL,
                    entry REAL, sl REAL, tp REAL, exit_price REAL,
                    risk_usd REAL, result TEXT DEFAULT 'RUNNING',
                    pnl_usd REAL, rr_achieved REAL, notes TEXT, alert_id INTEGER
                )
            """)
            rows = conn.execute("SELECT * FROM trades ORDER BY created_at ASC").fetchall()
    except Exception:
        return {"total": 0, "closed": 0, "running": 0, "winrate": 0.0,
                "total_pnl": 0.0, "avg_rr": 0.0, "wins": 0, "losses": 0,
                "be": 0, "equity_curve": [], "result_counts": {}}

    trades = [dict(r) for r in rows]
    closed = [t for t in trades if t["result"] in ("TP", "SL", "BE")]
    wins   = [t for t in closed if t["result"] == "TP"]
    losses = [t for t in closed if t["result"] == "SL"]

    total_pnl = sum(t["pnl_usd"] or 0 for t in closed)
    rr_vals   = [t["rr_achieved"] for t in closed if t["rr_achieved"] is not None]
    avg_rr    = round(sum(rr_vals) / len(rr_vals), 2) if rr_vals else 0.0
    winrate   = round(len(wins) / len(closed) * 100, 1) if closed else 0.0

    equity_curve = []
    cumulative = 0.0
    for t in sorted(closed, key=lambda x: x["closed_at"] or ""):
        cumulative += t["pnl_usd"] or 0
        equity_curve.append({
            "date": (t["closed_at"] or "")[:10],
            "pnl":  round(cumulative, 2),
        })

    result_counts = {}
    for t in trades:
        r = t["result"] or "RUNNING"
        result_counts[r] = result_counts.get(r, 0) + 1

    return {
        "total":         len(trades),
        "closed":        len(closed),
        "running":       len(trades) - len(closed),
        "winrate":       winrate,
        "total_pnl":     round(total_pnl, 2),
        "avg_rr":        avg_rr,
        "wins":          len(wins),
        "losses":        len(losses),
        "be":            len([t for t in closed if t["result"] == "BE"]),
        "equity_curve":  equity_curve,
        "result_counts": result_counts,
    }


def get_stats() -> dict:
    """Performans istatistiklerini döndür."""
    init_db()
    with _get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]

        result_rows = conn.execute(
            "SELECT result, COUNT(*) as cnt FROM analyses WHERE result IS NOT NULL GROUP BY result"
        ).fetchall()
        result_counts = {r["result"]: r["cnt"] for r in result_rows}

        bias_rows = conn.execute(
            "SELECT bias, COUNT(*) as cnt FROM analyses GROUP BY bias ORDER BY cnt DESC"
        ).fetchall()
        bias_counts = {r["bias"]: r["cnt"] for r in bias_rows}

        tp = result_counts.get("TP", 0)
        sl = result_counts.get("SL", 0)
        be = result_counts.get("BE", 0)
        decided = tp + sl + be
        winrate = round(tp / decided * 100, 1) if decided > 0 else 0.0

        avg_conf_row = conn.execute("SELECT AVG(confidence) FROM analyses").fetchone()[0]
        avg_conf = round(avg_conf_row or 0, 1)

        conf_bands = [
            (8, 10, "8-10"),
            (6, 7, "6-7"),
            (4, 5, "4-5"),
            (1, 3, "1-3"),
        ]
        conf_stats = []
        for lo, hi, label in conf_bands:
            rows = conn.execute(
                "SELECT result FROM analyses WHERE confidence BETWEEN ? AND ? AND result IN ('TP','SL','BE')",
                (lo, hi),
            ).fetchall()
            total_c = len(rows)
            tp_c = sum(1 for r in rows if r["result"] == "TP")
            conf_stats.append({
                "label": label,
                "total": total_c,
                "win_rate": round(tp_c / total_c * 100, 1) if total_c > 0 else 0.0,
            })

        sym_rows = conn.execute(
            "SELECT symbol, COUNT(*) as cnt, AVG(confidence) as avg_c "
            "FROM analyses GROUP BY symbol ORDER BY cnt DESC LIMIT 10"
        ).fetchall()
        symbol_stats = {
            r["symbol"]: {"count": r["cnt"], "avg_confidence": round(r["avg_c"] or 0, 1)}
            for r in sym_rows
        }

        daily_rows = conn.execute(
            "SELECT DATE(created_at) as day, COUNT(*) as cnt "
            "FROM analyses WHERE created_at >= DATE('now', '-30 days') "
            "GROUP BY day ORDER BY day"
        ).fetchall()
        daily_trend = {r["day"]: r["cnt"] for r in daily_rows}

    return {
        "total": total,
        "result_counts": result_counts,
        "bias_counts": bias_counts,
        "winrate": winrate,
        "decided_count": decided,
        "avg_confidence": avg_conf,
        "confidence_stats": conf_stats,
        "symbol_stats": symbol_stats,
        "daily_trend": daily_trend,
    }
