import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from app.services import ai_service, telegram_service, journal_service, tradingview_service, ltf_service

# ─── Sayfa yapılandırması ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Yemre AI Trading Desk",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Stil ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #070a0f !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #090c13 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebar"] * { color: #8a9bb0 !important; }
[data-testid="stSidebar"] .stRadio label { color: #c0cad6 !important; }
[data-testid="block-container"] { padding-top: 1.2rem !important; }
h1,h2,h3,h4,h5 { color: #e0e6ed !important; }
.stButton>button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #c0cad6 !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton>button:hover {
    background: rgba(255,255,255,0.09) !important;
    border-color: rgba(255,255,255,0.2) !important;
}

/* ── Topbar ── */
.yai-topbar {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 12px 22px; margin-bottom: 18px;
}
.yai-topbar-title {
    font-size: 1rem; font-weight: 700; letter-spacing: 0.18em;
    color: #e0e6ed; text-transform: uppercase;
    background: linear-gradient(90deg,#e0e6ed,#7f8c9a);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.yai-status-group { display: flex; gap: 18px; align-items: center; }
.yai-status-item  { display: flex; align-items: center; gap: 6px;
    font-size: 0.73rem; color: #7f8c9a; font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase; letter-spacing: 0.06em; }
.dot-on  { width:7px;height:7px;border-radius:50%;background:#00ff88;box-shadow:0 0 8px #00ff88;display:inline-block; }
.dot-off { width:7px;height:7px;border-radius:50%;background:#ff3366;box-shadow:0 0 8px #ff3366;display:inline-block; }
.dot-warn{ width:7px;height:7px;border-radius:50%;background:#ffd32a;box-shadow:0 0 6px #ffd32a;display:inline-block; }
.yai-btc-block { display:flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace; }
.yai-btc-lbl { font-size:0.7rem;color:#5a6878;text-transform:uppercase;letter-spacing:0.1em; }
.yai-btc-price { font-size:1.15rem;font-weight:700;color:#e0e6ed; }
.yai-btc-up   { font-size:0.8rem;color:#00ff88;font-weight:600; }
.yai-btc-down { font-size:0.8rem;color:#ff3366;font-weight:600; }

/* ── HTF Bias ── */
.htf-grid { display:flex;gap:10px;margin-bottom:16px; }
.htf-card {
    flex:1; padding:14px 18px; border-radius:12px;
    border:1px solid; position:relative; overflow:hidden;
}
.htf-bull { border-color:rgba(0,255,136,0.25);background:rgba(0,255,136,0.04);box-shadow:0 0 24px rgba(0,255,136,0.06); }
.htf-bear { border-color:rgba(255,51,102,0.25);background:rgba(255,51,102,0.04);box-shadow:0 0 24px rgba(255,51,102,0.06); }
.htf-ranging { border-color:rgba(255,211,42,0.25);background:rgba(255,211,42,0.04);box-shadow:0 0 24px rgba(255,211,42,0.06); }
.htf-sym  { font-size:0.68rem;color:#5a6878;letter-spacing:0.1em;text-transform:uppercase;font-family:'JetBrains Mono',monospace; }
.htf-val  { font-size:1.05rem;font-weight:700;letter-spacing:0.04em;margin:5px 0 3px; }
.htf-bull .htf-val  { color:#00ff88; }
.htf-bear .htf-val  { color:#ff3366; }
.htf-ranging .htf-val { color:#ffd32a; }
.htf-meta { font-size:0.68rem;color:#3d4a58;font-family:'JetBrains Mono',monospace; }

/* ── Stats Row ── */
.stats-row { display:flex;gap:10px;margin-bottom:18px; }
.stat-card {
    flex:1; background:rgba(255,255,255,0.025);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:12px; padding:16px 14px; text-align:center;
}
.stat-num { font-size:2rem;font-weight:700;font-family:'JetBrains Mono',monospace;line-height:1; }
.sn-green { color:#00ff88; text-shadow:0 0 20px rgba(0,255,136,0.4); }
.sn-red   { color:#ff3366; text-shadow:0 0 20px rgba(255,51,102,0.4); }
.sn-blue  { color:#4fc3f7; }
.sn-white { color:#e0e6ed; }
.sn-pos   { color:#00ff88; }
.sn-neg   { color:#ff3366; }
.stat-lbl { font-size:0.64rem;color:#3d4a58;text-transform:uppercase;letter-spacing:0.12em;margin-top:5px; }

/* ── Gate Signal ── */
.gate-main { border-radius:14px;overflow:hidden;margin-bottom:12px; }
.gate-main-hdr {
    padding:13px 20px; font-size:0.82rem; font-weight:700;
    letter-spacing:0.06em; display:flex; justify-content:space-between; align-items:center;
}
.gate-bull-hdr {
    background:linear-gradient(135deg,rgba(0,255,136,0.13),rgba(0,255,136,0.04));
    border-left:3px solid #00ff88; color:#00ff88;
}
.gate-bear-hdr {
    background:linear-gradient(135deg,rgba(255,51,102,0.13),rgba(255,51,102,0.04));
    border-left:3px solid #ff3366; color:#ff3366;
}
.gate-body {
    padding:16px 20px; background:rgba(255,255,255,0.02);
    border:1px solid rgba(255,255,255,0.06); border-top:none; border-radius:0 0 14px 14px;
}
.gate-item {
    display:flex; justify-content:space-between; align-items:center;
    padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.04);
    font-family:'JetBrains Mono',monospace;
}
.gate-item:last-child { border-bottom:none; }
.gi-lbl { font-size:0.68rem;color:#3d4a58;text-transform:uppercase;letter-spacing:0.1em; }
.gi-val { font-size:0.92rem;font-weight:600;color:#e0e6ed; }
.gi-val.g { color:#00ff88; }
.gi-val.r { color:#ff3366; }
.gi-val.b { color:#4fc3f7;font-size:1.1rem;font-weight:700; }
.gi-sub { font-size:0.72rem;color:#3d4a58;margin-left:8px; }
.gate-score-bar { height:3px;background:rgba(255,255,255,0.08);border-radius:2px;margin-top:12px;overflow:hidden; }
.gsb-fill-bull { height:100%;background:linear-gradient(90deg,#00c853,#00ff88);border-radius:2px; }
.gsb-fill-bear { height:100%;background:linear-gradient(90deg,#ff1744,#ff3366);border-radius:2px; }
.gate-ts { font-size:0.68rem;color:#3d4a58;margin-top:8px;font-family:'JetBrains Mono',monospace; }

/* ── Signal Feed ── */
.sf-wrap { background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;overflow:hidden; }
.sf-hdr { padding:9px 16px;font-size:0.64rem;text-transform:uppercase;letter-spacing:0.14em;color:#3d4a58;
    border-bottom:1px solid rgba(255,255,255,0.05);background:rgba(255,255,255,0.02); }
.sf-item { display:flex;align-items:center;gap:10px;padding:9px 16px;border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.8rem; }
.sf-item:last-child { border-bottom:none; }
.sf-ico { font-size:0.65rem;font-family:'JetBrains Mono',monospace;font-weight:700;padding:2px 5px;border-radius:4px; }
.sf-ico-bull { color:#00ff88;background:rgba(0,255,136,0.1); }
.sf-ico-bear { color:#ff3366;background:rgba(255,51,102,0.1); }
.sf-ico-htf  { color:#4fc3f7;background:rgba(79,195,247,0.1); }
.sf-ico-gen  { color:#7f8c9a;background:rgba(255,255,255,0.07); }
.sf-pair { color:#c0cad6;font-weight:600; }
.sf-tf   { color:#5a6878;font-size:0.72rem;margin-left:3px; }
.sf-time { font-size:0.68rem;color:#3d4a58;margin-left:auto;font-family:'JetBrains Mono',monospace; }

/* ── AI Card ── */
.ai-card {
    background:rgba(79,195,247,0.04);border:1px solid rgba(79,195,247,0.12);
    border-radius:12px;padding:14px 18px;margin-top:10px;
}
.ai-top { display:flex;align-items:center;justify-content:space-between;margin-bottom:6px; }
.ai-bias-lbl { font-size:1rem;font-weight:700;letter-spacing:0.04em; }
.ai-bull { color:#00ff88; } .ai-bear { color:#ff3366; } .ai-ranging { color:#ffd32a; } .ai-neutral { color:#7f8c9a; }
.ai-meta { font-size:0.68rem;color:#3d4a58;font-family:'JetBrains Mono',monospace; }
.ai-summary { font-size:0.78rem;color:#7f8c9a;margin-top:8px;line-height:1.6;border-top:1px solid rgba(255,255,255,0.05);padding-top:8px; }

/* ── Trade Card ── */
.trade-card {
    background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
    border-radius:10px;padding:12px 16px;margin-bottom:8px;
}
.trade-hdr { display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.82rem; }
.trade-long  { color:#00ff88;font-weight:700;font-family:'JetBrains Mono',monospace; }
.trade-short { color:#ff3366;font-weight:700;font-family:'JetBrains Mono',monospace; }
.trade-sym { color:#e0e6ed;font-weight:600; }
.trade-risk { font-size:0.72rem;color:#5a6878;font-family:'JetBrains Mono',monospace; }
.trade-levels { display:flex;gap:18px;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#5a6878; }
.tl-val { color:#c0cad6;margin-left:4px; }

/* ── Section Label ── */
.sec-lbl {
    font-size:0.64rem;text-transform:uppercase;letter-spacing:0.16em;
    color:#3d4a58;margin-bottom:10px;margin-top:4px;
    display:flex;align-items:center;gap:8px;
}
.sec-lbl::after { content:'';flex:1;height:1px;background:rgba(255,255,255,0.05); }

/* ── Misc ── */
.bias-bullish { color:#00ff88;font-size:1.4rem;font-weight:700; }
.bias-bearish { color:#ff3366;font-size:1.4rem;font-weight:700; }
.bias-ranging { color:#ffd32a;font-size:1.4rem;font-weight:700; }
.bias-notrade { color:#5a6878;font-size:1.4rem;font-weight:700; }
.gate-card { border-radius:12px;padding:16px 20px;margin-bottom:12px;border-left:5px solid; }
.gate-bull { background:rgba(0,255,136,0.06);border-color:#00ff88; }
.gate-bear { background:rgba(255,51,102,0.06);border-color:#ff3366; }
.gate-htf  { background:rgba(79,195,247,0.06);border-color:#4fc3f7; }
.gate-title { font-size:1.1rem;font-weight:700;margin-bottom:6px; }
.gate-row   { font-size:0.88rem;font-family:'JetBrains Mono',monospace;margin:3px 0; }
.gate-time  { font-size:0.72rem;color:#3d4a58;margin-top:8px; }
.stat-box   { text-align:center;padding:10px;border-radius:8px;background:rgba(255,255,255,0.03); }
.stat-num   { font-size:1.6rem;font-weight:700; }
.stat-lbl   { font-size:0.72rem;color:#5a6878; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "prefill_trade" not in st.session_state:
    st.session_state.prefill_trade = None

with st.sidebar:
    st.title("Yemre AI Trading Desk")
    st.caption("AI Destekli Hibrit Karar Destek Sistemi")
    st.divider()
    pages = ["Dashboard", "Analiz", "Otomatik Tarama", "Journal", "Alertler", "Hakkında"]
    page = st.radio(
        "Sayfa", pages,
        index=pages.index(st.session_state.page),
        label_visibility="collapsed",
        key="page",
    )
    st.divider()
    st.caption(f"Model: {os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-6')}")
    api_ok = bool(os.getenv("ANTHROPIC_API_KEY"))
    tg_channels = telegram_service.get_channels()
    tg_ok = bool(os.getenv("TELEGRAM_BOT_TOKEN") and tg_channels)
    st.markdown(f"API: {'🟢 Bağlı' if api_ok else '🔴 Eksik'}")
    tg_label = f"🟢 {len(tg_channels)} kanal" if tg_ok else "🟡 Yapılandırılmamış"
    st.markdown(f"Telegram: {tg_label}")
    tv_session = tradingview_service.has_session()
    st.markdown(f"TradingView: {'🟢 Oturum var' if tv_session else '🟡 Giriş gerekli'}")

# ─────────────────────────────────────────────────────────────────────────────
# SAYFA: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "Dashboard":
    import re
    import requests as _req
    from datetime import datetime, timezone

    @st.cache_data(ttl=30)
    def _btc_price():
        try:
            r = _req.get(
                "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT",
                timeout=5,
            ).json()
            return float(r["lastPrice"]), float(r["priceChangePercent"])
        except Exception:
            return None, None

    def _parse_gate(msg):
        out = {}
        for key, pat in [("entry", r"Entry[:\s]*([\d,.]+)"),
                         ("sl",    r"SL[:\s]*([\d,.]+)"),
                         ("tp",    r"TP[:\s]*([\d,.]+)"),
                         ("score", r"Score[:\s]*(\d+)/10")]:
            m = re.search(pat, msg, re.IGNORECASE)
            if m:
                out[key] = m.group(1).replace(",", "")
        return out

    def _fmt(v):
        try:
            f = float(v)
            return f"{f:,.2f}" if f < 10_000 else f"{f:,.1f}"
        except Exception:
            return str(v)

    def _pct(e, l):
        try:
            d = (float(l) - float(e)) / float(e) * 100
            return f"{'+'if d>=0 else ''}{d:.2f}%"
        except Exception:
            return ""

    # ── Veri çek ─────────────────────────────────────────────────
    alerts      = journal_service.get_recent_alerts(limit=200)
    trades      = journal_service.get_trades(limit=200)
    tstats      = journal_service.get_trade_stats()
    analyses    = journal_service.get_recent_analyses(limit=5)
    btc_price, btc_pct = _btc_price()

    today = datetime.now(timezone.utc).date().isoformat()
    now_utc = datetime.now(timezone.utc).strftime("%H:%M UTC")
    today_alerts = [a for a in alerts if a.get("created_at", "").startswith(today)]
    bull_today   = sum(1 for a in today_alerts if "BULL GATE" in a.get("message","").upper())
    bear_today   = sum(1 for a in today_alerts if "BEAR GATE" in a.get("message","").upper())
    last_gate    = next((a for a in alerts
                         if "BULL GATE" in a.get("message","").upper()
                         or "BEAR GATE" in a.get("message","").upper()), None)
    running_trades = [t for t in trades if t.get("result") == "RUNNING"]

    cf_url_file = Path(__file__).parent / ".cloudflare_url"
    cf_url  = cf_url_file.read_text().strip() if cf_url_file.exists() else ""
    api_ok  = bool(os.getenv("ANTHROPIC_API_KEY"))
    tg_ok   = bool(os.getenv("TELEGRAM_BOT_TOKEN"))
    wh_ok   = bool(cf_url)

    # ── Top Bar ───────────────────────────────────────────────────
    btc_block = ""
    if btc_price:
        sign = "+" if (btc_pct or 0) >= 0 else ""
        chg_cls = "yai-btc-up" if (btc_pct or 0) >= 0 else "yai-btc-down"
        btc_block = (
            f"<div class='yai-btc-block'>"
            f"<span class='yai-btc-lbl'>BTC</span>"
            f"<span class='yai-btc-price'>${btc_price:,.0f}</span>"
            f"<span class='{chg_cls}'>{sign}{btc_pct:.2f}%</span>"
            f"</div>"
        )
    else:
        btc_block = "<div class='yai-btc-block'><span class='yai-btc-lbl'>BTC</span><span class='yai-btc-price' style='color:#3d4a58'>—</span></div>"

    st.markdown(f"""
<div class="yai-topbar">
  <div class="yai-status-group">
    <div class="yai-status-item"><span class="{'dot-on' if api_ok else 'dot-off'}"></span> CLAUDE</div>
    <div class="yai-status-item"><span class="{'dot-on' if tg_ok else 'dot-off'}"></span> TELEGRAM</div>
    <div class="yai-status-item"><span class="{'dot-on' if wh_ok else 'dot-warn'}"></span> WEBHOOK</div>
  </div>
  <div class="yai-topbar-title">⬡ YEMRE AI TRADING DESK</div>
  <div style="display:flex;align-items:center;gap:20px">
    {btc_block}
    <span style="font-size:0.72rem;color:#3d4a58;font-family:'JetBrains Mono',monospace">{now_utc}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    _, ref_col = st.columns([8, 1])
    with ref_col:
        if st.button("↺ Yenile", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── HTF Bias ──────────────────────────────────────────────────
    htf_biases = ltf_service.get_all_htf_biases()
    if htf_biases:
        cards_html = ""
        for hb in htf_biases[:4]:
            bias  = hb["bias"]
            cls   = {"BULLISH": "htf-bull", "BEARISH": "htf-bear"}.get(bias, "htf-ranging")
            val   = {"BULLISH": "▲ BULLISH", "BEARISH": "▼ BEARISH", "RANGING": "◆ RANGING"}.get(bias, bias)
            score = hb.get("score") or "—"
            ts    = hb.get("updated_at", "")[:16].replace("T", " ")
            cards_html += (
                f"<div class='htf-card {cls}'>"
                f"<div class='htf-sym'>{hb['symbol']} · 4H</div>"
                f"<div class='htf-val'>{val}</div>"
                f"<div class='htf-meta'>{score} &nbsp;·&nbsp; {ts}</div>"
                f"</div>"
            )
        st.markdown(f"<div class='htf-grid'>{cards_html}</div>", unsafe_allow_html=True)

    # ── Stats Row ─────────────────────────────────────────────────
    pnl = tstats["total_pnl"]
    pnl_cls = "sn-pos" if pnl >= 0 else "sn-neg"
    pnl_str = f"${pnl:+,.0f}"
    st.markdown(f"""
<div class="stats-row">
  <div class="stat-card">
    <div class="stat-num sn-green">{bull_today}</div>
    <div class="stat-lbl">Bull Gate · Bugün</div>
  </div>
  <div class="stat-card">
    <div class="stat-num sn-red">{bear_today}</div>
    <div class="stat-lbl">Bear Gate · Bugün</div>
  </div>
  <div class="stat-card">
    <div class="stat-num sn-white">{len(today_alerts)}</div>
    <div class="stat-lbl">Toplam Alert</div>
  </div>
  <div class="stat-card">
    <div class="stat-num sn-blue">{len(running_trades)}</div>
    <div class="stat-lbl">Açık İşlem</div>
  </div>
  <div class="stat-card">
    <div class="stat-num {pnl_cls}">{pnl_str}</div>
    <div class="stat-lbl">Toplam P&L</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Ana İçerik ────────────────────────────────────────────────
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.markdown("<div class='sec-lbl'>Son Gate Sinyali</div>", unsafe_allow_html=True)

        if last_gate:
            msg     = last_gate.get("message", "")
            symbol  = last_gate.get("symbol", "?")
            tf      = last_gate.get("timeframe", "?")
            ts      = last_gate.get("created_at", "")[:16].replace("T", " ")
            mu      = msg.upper()
            is_bull = "BULL GATE" in mu
            p       = _parse_gate(msg)
            hdr_cls = "gate-bull-hdr" if is_bull else "gate-bear-hdr"
            lbl     = "BULL GATE ✓" if is_bull else "BEAR GATE ✓"

            entry_v = p.get("entry", "")
            sl_v    = p.get("sl", "")
            tp_v    = p.get("tp", "")
            score_v = p.get("score", "")

            sl_sub = f"<span class='gi-sub'>({_pct(entry_v, sl_v)})</span>" if sl_v else ""
            tp_sub = f"<span class='gi-sub'>({_pct(entry_v, tp_v)})</span>" if tp_v else ""

            rr_html = ""
            if sl_v and tp_v and entry_v:
                try:
                    rr = abs(float(tp_v) - float(entry_v)) / abs(float(entry_v) - float(sl_v))
                    rr_html = f"<div class='gate-item'><span class='gi-lbl'>R / R</span><span class='gi-val b'>1 : {rr:.1f}</span></div>"
                except Exception:
                    pass

            score_bar_html = ""
            if score_v:
                pct = int(score_v) / 10 * 100
                fill_cls = "gsb-fill-bull" if is_bull else "gsb-fill-bear"
                score_bar_html = (
                    f"<div class='gate-score-bar'>"
                    f"<div class='{fill_cls}' style='width:{pct}%'></div>"
                    f"</div>"
                )

            st.markdown(f"""
<div class="gate-main">
  <div class="gate-main-hdr {hdr_cls}">
    <span>{lbl}</span>
    <span style="font-size:0.72rem;opacity:0.7">{symbol} &nbsp;·&nbsp; {tf}</span>
  </div>
  <div class="gate-body">
    <div class="gate-item">
      <span class="gi-lbl">Entry</span>
      <span class="gi-val" style="font-size:1.05rem;font-weight:700">{_fmt(entry_v) if entry_v else '—'}</span>
    </div>
    <div class="gate-item">
      <span class="gi-lbl">Stop Loss</span>
      <span class="gi-val r">{_fmt(sl_v) if sl_v else '—'} {sl_sub}</span>
    </div>
    <div class="gate-item">
      <span class="gi-lbl">Take Profit</span>
      <span class="gi-val g">{_fmt(tp_v) if tp_v else '—'} {tp_sub}</span>
    </div>
    {rr_html}
    <div class="gate-item">
      <span class="gi-lbl">Score</span>
      <span class="gi-val">{score_v}/10</span>
    </div>
    {score_bar_html}
    <div class="gate-ts">⏰ &nbsp;{ts}</div>
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='padding:24px;text-align:center;color:#3d4a58;"
                "border:1px dashed rgba(255,255,255,0.07);border-radius:12px;"
                "font-size:0.85rem'>Henüz GATE sinyali yok</div>",
                unsafe_allow_html=True,
            )

        # ── Açık İşlemler ─────────────────────────────────────────
        if running_trades:
            st.markdown("<div class='sec-lbl' style='margin-top:18px'>Açık İşlemler</div>", unsafe_allow_html=True)
            for tr in running_trades:
                is_long = tr["direction"] == "LONG"
                dir_cls = "trade-long" if is_long else "trade-short"
                dir_lbl = "▲ LONG" if is_long else "▼ SHORT"
                entry_v = tr.get("entry") or 0
                sl_v    = tr.get("sl") or 0
                tp_v    = tr.get("tp") or 0
                risk_v  = tr.get("risk_usd") or 0
                st.markdown(f"""
<div class="trade-card">
  <div class="trade-hdr">
    <span><span class="trade-sym">{tr['symbol']}</span> &nbsp; <span class="{dir_cls}">{dir_lbl}</span></span>
    <span class="trade-risk">Risk: ${risk_v:.0f}</span>
  </div>
  <div class="trade-levels">
    <span>Entry<span class="tl-val">{_fmt(entry_v)}</span></span>
    <span>SL<span class="tl-val" style="color:#ff3366">{_fmt(sl_v)}</span><span style="color:#3d4a58;font-size:0.68rem"> {_pct(entry_v,sl_v)}</span></span>
    <span>TP<span class="tl-val" style="color:#00ff88">{_fmt(tp_v)}</span><span style="color:#3d4a58;font-size:0.68rem"> {_pct(entry_v,tp_v)}</span></span>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── İşlem Özeti ───────────────────────────────────────────
        if tstats["closed"] > 0:
            wr = tstats["winrate"]
            wr_color = "#00ff88" if wr >= 50 else "#ff3366"
            st.markdown(f"""
<div style="display:flex;gap:16px;margin-top:12px;padding:12px 16px;
background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
border-radius:10px;font-family:'JetBrains Mono',monospace;font-size:0.8rem">
  <span style="color:#3d4a58">WIN RATE <span style="color:{wr_color};font-weight:700">{wr}%</span></span>
  <span style="color:#3d4a58">AVG R:R <span style="color:#4fc3f7;font-weight:700">{tstats['avg_rr']}</span></span>
  <span style="color:#3d4a58"><span style="color:#00ff88">{tstats['wins']}W</span> / <span style="color:#ff3366">{tstats['losses']}L</span> / <span style="color:#7f8c9a">{tstats['be']}BE</span></span>
</div>
""", unsafe_allow_html=True)

    with right_col:
        # ── Sinyal Feed ───────────────────────────────────────────
        st.markdown("<div class='sec-lbl'>Sinyal Akışı</div>", unsafe_allow_html=True)
        if alerts:
            items_html = ""
            for a in alerts[:7]:
                mu  = a.get("message", "").upper()
                sym = a.get("symbol", "?")
                tf  = a.get("timeframe", "?")
                ts  = a.get("created_at", "")[:16].replace("T", " ")
                if "BULL GATE" in mu:
                    ico_cls, lbl = "sf-ico-bull", "BG ▲"
                elif "BEAR GATE" in mu:
                    ico_cls, lbl = "sf-ico-bear", "BG ▼"
                elif any(k in mu for k in ("CHOCH","BOS","HTF","TRIGGER")):
                    ico_cls = "sf-ico-htf"
                    lbl = "HTF ▲" if any(k in mu for k in ("BULL","BULLISH")) else "HTF ▼"
                else:
                    ico_cls, lbl = "sf-ico-gen", "ALT"
                items_html += (
                    f"<div class='sf-item'>"
                    f"<span class='sf-ico {ico_cls}'>{lbl}</span>"
                    f"<span class='sf-pair'>{sym}</span>"
                    f"<span class='sf-tf'>· {tf}</span>"
                    f"<span class='sf-time'>{ts[11:]}</span>"
                    f"</div>"
                )
            st.markdown(f"""
<div class="sf-wrap">
  <div class="sf-hdr">Canlı Feed</div>
  {items_html}
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='padding:20px;text-align:center;color:#3d4a58;"
                "border:1px dashed rgba(255,255,255,0.07);border-radius:12px;"
                "font-size:0.82rem'>Sinyal bekleniyor…</div>",
                unsafe_allow_html=True,
            )

        # ── Son AI Analizi ────────────────────────────────────────
        if analyses:
            a = analyses[0]
            bias = a.get("bias", "—")
            bias_cls = {"BULLISH":"ai-bull","BEARISH":"ai-bear","RANGING":"ai-ranging"}.get(bias,"ai-neutral")
            bias_lbl = {"BULLISH":"▲ BULLISH","BEARISH":"▼ BEARISH","RANGING":"◆ RANGING"}.get(bias, bias)
            conf  = a.get("confidence","?")
            sym   = a.get("symbol","?")
            tf    = a.get("timeframe","?")
            ats   = a.get("created_at","")[:16].replace("T"," ")
            summ  = (a.get("summary","") or "")[:160]
            summ_html = f"<div class='ai-summary'>{summ}{'…' if len(a.get('summary',''))>160 else ''}</div>" if summ else ""
            st.markdown(f"""
<div class="ai-card" style="margin-top:14px">
  <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.14em;color:#3d4a58;margin-bottom:8px">Son AI Analizi</div>
  <div class="ai-top">
    <span class="ai-bias-lbl {bias_cls}">{bias_lbl}</span>
    <span class="ai-meta">{conf}/10</span>
  </div>
  <div class="ai-meta">{sym} · {tf} &nbsp;·&nbsp; {ats}</div>
  {summ_html}
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SAYFA: ANALİZ
# ─────────────────────────────────────────────────────────────────────────────
if page == "Analiz":
    st.header("Chart Analizi")

    col_left, col_right = st.columns([1, 1.6])

    with col_left:
        st.subheader("Giriş")

        uploaded = st.file_uploader(
            "TradingView Screenshot",
            type=["png", "jpg", "jpeg", "webp"],
            help="TradingView ekran görüntüsünü buraya yükle",
        )

        if uploaded:
            st.image(uploaded, use_container_width=True)

        symbol = st.text_input("Sembol", value="BTCUSDT", placeholder="BTCUSDT, XAUUSD, ETHUSDT...")
        timeframe_options = ["1M", "3M", "5M", "15M", "30M", "1H", "2H", "4H", "1D", "1W"]
        timeframe = st.selectbox("Timeframe", timeframe_options, index=5)
        manual_note = st.text_area(
            "Manuel Not (isteğe bağlı)",
            placeholder="Dikkat ettiğin özel bir durum, haber, likidite bölgesi vb.",
            height=100,
        )

        analyze_btn = st.button("Analiz Et", type="primary", use_container_width=True, disabled=not uploaded)
        if not uploaded:
            st.caption("Screenshot yükleyince analiz butonu aktif olur.")

    with col_right:
        st.subheader("Analiz Sonucu")

        if "last_analysis" not in st.session_state:
            st.session_state.last_analysis = None
            st.session_state.last_analysis_id = None
            st.session_state.last_image_bytes = None

        if analyze_btn and uploaded:
            if not api_ok:
                st.error("ANTHROPIC_API_KEY eksik. .env dosyasını kontrol et.")
            else:
                image_bytes = uploaded.read()
                ext = uploaded.name.rsplit(".", 1)[-1].lower()
                media_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
                media_type = media_map.get(ext, "image/png")

                with st.spinner("AI grafiği analiz ediyor..."):
                    try:
                        result = ai_service.analyze_chart(
                            image_bytes=image_bytes,
                            symbol=symbol.upper(),
                            timeframe=timeframe,
                            manual_note=manual_note,
                            media_type=media_type,
                        )
                        st.session_state.last_analysis = result
                        st.session_state.last_image_bytes = image_bytes
                        st.session_state.last_analysis_id = None
                        st.success("Analiz tamamlandı.")
                    except Exception as e:
                        st.error(f"Hata: {e}")

        result = st.session_state.last_analysis
        if result:
            # Bias rengi
            bias_class = {
                "BULLISH": "bias-bullish",
                "BEARISH": "bias-bearish",
                "RANGING": "bias-ranging",
            }.get(result.bias, "bias-notrade")
            bias_icon = {"BULLISH": "YUKARI", "BEARISH": "ASAGI", "RANGING": "YATAY"}.get(result.bias, result.bias)

            st.markdown(f'<div class="{bias_class}">{bias_icon} {result.bias}</div>', unsafe_allow_html=True)
            st.progress(result.confidence / 10, text=f"Güven: {result.confidence}/10")

            tab_summary, tab_scenarios, tab_levels, tab_telegram = st.tabs(
                ["Özet", "Senaryolar", "Seviyeler", "Telegram"]
            )

            with tab_summary:
                st.write(result.summary)
                if result.market_structure:
                    st.markdown("**Piyasa Yapısı**")
                    st.write(result.market_structure)
                if result.risk_notes:
                    st.warning(result.risk_notes)
                if result.no_trade_conditions:
                    st.markdown("**İşlem Alınmamalı Çünkü:**")
                    for c in result.no_trade_conditions:
                        st.markdown(f"- {c}")

            with tab_scenarios:
                col_l, col_s = st.columns(2)
                with col_l:
                    st.markdown("**Long Senaryo**")
                    st.info(result.long_scenario)
                with col_s:
                    st.markdown("**Short Senaryo**")
                    st.error(result.short_scenario)

            with tab_levels:
                kl = result.key_levels
                resistances = kl.get("resistance", [])
                supports = kl.get("support", [])
                col_r, col_s = st.columns(2)
                with col_r:
                    st.markdown("**Direnç Seviyeleri**")
                    for lvl in resistances:
                        st.markdown(f"- 🔴 {lvl}")
                with col_s:
                    st.markdown("**Destek Seviyeleri**")
                    for lvl in supports:
                        st.markdown(f"- 🟢 {lvl}")

            with tab_telegram:
                # Kanal seçici
                channels = telegram_service.get_channels()
                has_tg = bool(channels and os.getenv("TELEGRAM_BOT_TOKEN"))

                if channels:
                    selected_channel_name = st.selectbox(
                        "Kanal Seç",
                        list(channels.keys()),
                        key="tg_channel",
                    )
                    selected_chat_id = channels[selected_channel_name]
                else:
                    selected_chat_id = None
                    st.caption("Telegram kanalı yapılandırılmamış (.env)")

                # XAU sinyal numarası
                sym_upper = result.symbol.upper()
                if any(x in sym_upper for x in ("XAU", "GOLD")):
                    sig_num = journal_service.get_daily_signal_number(result.symbol)
                    st.info(f"XAU Sinyal #{sig_num} (bugün)")

                tg_text = st.text_area(
                    "Telegram Mesajı (düzenleyebilirsin)",
                    value=result.telegram_message,
                    height=200,
                    key="tg_edit",
                )

                col_send, col_photo, col_save = st.columns(3)

                with col_send:
                    if st.button("Mesaj Gönder", use_container_width=True, disabled=not has_tg):
                        ok, msg = telegram_service.send_message(tg_text, chat_id=selected_chat_id)
                        if ok:
                            st.success(msg)
                            if st.session_state.last_analysis_id:
                                journal_service.mark_telegram_sent(st.session_state.last_analysis_id)
                        else:
                            st.error(f"Gönderilemedi: {msg}")
                    if not has_tg:
                        st.caption("Telegram yapılandırılmamış")

                with col_photo:
                    has_img = st.session_state.last_image_bytes is not None
                    if st.button(
                        "Fotoğraf + Mesaj",
                        use_container_width=True,
                        disabled=not (has_tg and has_img),
                        help="Screenshot + mesajı birlikte gönderir",
                    ):
                        ok, msg = telegram_service.send_photo(
                            st.session_state.last_image_bytes,
                            caption=tg_text[:1024],
                            chat_id=selected_chat_id,
                        )
                        if ok:
                            st.success(msg)
                            if st.session_state.last_analysis_id:
                                journal_service.mark_telegram_sent(st.session_state.last_analysis_id)
                        else:
                            st.error(f"Gönderilemedi: {msg}")
                    if not has_img:
                        st.caption("Görsel için screenshot yükle")

                with col_save:
                    if st.button("Journal'a Kaydet", use_container_width=True):
                        if st.session_state.last_analysis_id is None:
                            aid = journal_service.save_analysis(
                                result,
                                manual_note=manual_note,
                            )
                            st.session_state.last_analysis_id = aid
                            st.success(f"Kaydedildi (ID: {aid})")
                        else:
                            st.info(f"Zaten kaydedildi (ID: {st.session_state.last_analysis_id})")

# ─────────────────────────────────────────────────────────────────────────────
# SAYFA: OTOMATİK TARAMA
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Otomatik Tarama":
    st.header("Otomatik Çok Timeframe Analizi")
    st.caption("Tek tuşla 5M → 1D arası 7 timeframe'i TradingView'dan çeker ve analiz eder.")

    col_cfg, col_status = st.columns([2, 1])

    with col_cfg:
        tv_symbol = st.text_input(
            "TradingView Sembol",
            value=os.getenv("TV_SYMBOL", "BINANCE:BTCUSDT.P"),
            help="Örnek: BINANCE:BTCUSDT.P, BINANCE:ETHUSDT, OANDA:XAUUSD",
        )
        tv_chart_id = st.text_input(
            "Chart ID (isteğe bağlı)",
            value=os.getenv("TV_CHART_ID", ""),
            help="TradingView URL'indeki chart kodu. Boş bırakırsan yeni chart açılır.",
            placeholder="örn: xKtFHLdP",
        )
        manual_note_auto = st.text_area(
            "Manuel Not (isteğe bağlı)",
            placeholder="Haber, özel durum, likidite bölgesi...",
            height=80,
        )

    with col_status:
        st.markdown("**Taranacak Timeframe'ler**")
        for tf, _ in tradingview_service.TIMEFRAMES:
            st.markdown(f"- {tf}")

        if tradingview_service.has_session():
            st.success("TradingView oturumu mevcut")
            if st.button("Oturumu Sıfırla", type="secondary"):
                tradingview_service.clear_session()
                st.rerun()
        else:
            st.warning("Oturum yok. Aşağıdaki butona bas, tarayıcıda giriş yap.")
            if st.button("TradingView Girişi Yap", type="primary", use_container_width=True):
                with st.spinner("Tarayıcı açılıyor — giriş yapınca otomatik kaydedilir..."):
                    try:
                        tradingview_service.do_login_and_save()
                        st.success("Giriş başarılı! Session kaydedildi.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Giriş kaydedilemedi: {e}")

    st.divider()

    scan_btn = st.button("Tüm Timeframe'leri Tara ve Analiz Et", type="primary", use_container_width=True)

    if scan_btn:
        if not api_ok:
            st.error("ANTHROPIC_API_KEY eksik.")
        else:
            status_box = st.empty()
            progress_bar = st.progress(0)
            tf_names = [tf for tf, _ in tradingview_service.TIMEFRAMES]
            total_steps = len(tf_names)
            current_step = {"n": 0}

            def on_progress(tf_name: str):
                current_step["n"] += 1
                status_box.info(f"Screenshot alınıyor: {tf_name} ({current_step['n']}/{total_steps})")
                progress_bar.progress(current_step["n"] / (total_steps * 2))

            try:
                with st.spinner("TradingView'dan screenshot'lar alınıyor..."):
                    screenshots = tradingview_service.capture_all_timeframes(
                        symbol=tv_symbol,
                        chart_id=tv_chart_id.strip(),
                        progress_callback=on_progress,
                    )

                status_box.info("AI analiz ediliyor...")
                mtf_results = {}

                for i, (tf_name, screenshot_bytes) in enumerate(screenshots.items()):
                    progress_bar.progress((total_steps + i + 1) / (total_steps * 2))
                    status_box.info(f"AI analiz ediyor: {tf_name} ({i+1}/{total_steps})")
                    try:
                        result = ai_service.analyze_chart(
                            image_bytes=screenshot_bytes,
                            symbol=tv_symbol,
                            timeframe=tf_name,
                            manual_note=manual_note_auto,
                            media_type="image/png",
                        )
                        mtf_results[tf_name] = {"result": result, "screenshot": screenshot_bytes}
                    except Exception as e:
                        mtf_results[tf_name] = {"error": str(e), "screenshot": screenshot_bytes}

                st.session_state["mtf_results"] = mtf_results
                progress_bar.progress(1.0)
                status_box.success("Tüm timeframe'ler analiz edildi!")

            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Hata: {e}")
                st.info("Sorun devam ederse 'Oturumu Sıfırla' butonuna bas ve tekrar giriş yap.")

    # Sonuçları göster
    if "mtf_results" in st.session_state and st.session_state["mtf_results"]:
        mtf = st.session_state["mtf_results"]
        st.subheader("Sonuçlar")

        # Bias özet tablosu
        bias_cols = st.columns(len(mtf))
        bias_colors = {"BULLISH": "🟢", "BEARISH": "🔴", "RANGING": "🟡", "NO_TRADE": "⚫", "INSUFFICIENT_DATA": "⚪"}
        for col, (tf_name, data) in zip(bias_cols, mtf.items()):
            with col:
                if "result" in data:
                    r = data["result"]
                    icon = bias_colors.get(r.bias, "⚪")
                    col.metric(tf_name, f"{icon} {r.bias}", f"{r.confidence}/10")
                else:
                    col.metric(tf_name, "HATA", "")

        st.divider()

        # Detaylı tab'lar
        tab_list = list(mtf.keys())
        tabs = st.tabs(tab_list)

        for tab, tf_name in zip(tabs, tab_list):
            data = mtf[tf_name]
            with tab:
                if "error" in data:
                    st.error(f"Analiz hatası: {data['error']}")
                    st.image(data["screenshot"], caption=f"{tf_name} screenshot")
                    continue

                result = data["result"]
                col_img, col_analysis = st.columns([1, 1])

                with col_img:
                    st.image(data["screenshot"], caption=f"{tf_name} — {tv_symbol}", use_container_width=True)

                with col_analysis:
                    bias_class = {
                        "BULLISH": "bias-bullish",
                        "BEARISH": "bias-bearish",
                        "RANGING": "bias-ranging",
                    }.get(result.bias, "bias-notrade")
                    bias_icon = {"BULLISH": "YUKARI", "BEARISH": "ASAGI", "RANGING": "YATAY"}.get(result.bias, result.bias)
                    st.markdown(f'<div class="{bias_class}">{bias_icon} {result.bias}</div>', unsafe_allow_html=True)
                    st.progress(result.confidence / 10, text=f"Güven: {result.confidence}/10")

                    if result.summary:
                        st.write(result.summary)
                    if result.market_structure:
                        st.markdown(f"**Yapı:** {result.market_structure}")
                    if result.risk_notes:
                        st.warning(result.risk_notes)
                    if result.no_trade_conditions:
                        for c in result.no_trade_conditions:
                            st.markdown(f"- {c}")

                    kl = result.key_levels
                    lvl_r = kl.get("resistance", [])
                    lvl_s = kl.get("support", [])
                    if lvl_r or lvl_s:
                        lc1, lc2 = st.columns(2)
                        with lc1:
                            st.markdown("**Direnç**")
                            for lvl in lvl_r:
                                st.markdown(f"🔴 {lvl}")
                        with lc2:
                            st.markdown("**Destek**")
                            for lvl in lvl_s:
                                st.markdown(f"🟢 {lvl}")

# ─────────────────────────────────────────────────────────────────────────────
# SAYFA: JOURNAL
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Journal":
    st.header("Trading Journal")

    records = journal_service.get_recent_analyses(limit=200)
    stats   = journal_service.get_stats()
    trades  = journal_service.get_trades(limit=200)
    tstats  = journal_service.get_trade_stats()

    tab_trade, tab_perf, tab_log = st.tabs(["İşlemler", "Performans", "Analiz Geçmişi"])

    # ─────────────────────────────────────────────────────────────
    with tab_trade:

        # ── Üst istatistikler ─────────────────────────────────────
        m1, m2, m3, m4, m5 = st.columns(5)
        pnl_delta = f"${tstats['total_pnl']:+,.2f}"
        pnl_color = "normal" if tstats["total_pnl"] >= 0 else "inverse"
        m1.metric("Toplam İşlem",  tstats["total"])
        m2.metric("Win Rate",      f"{tstats['winrate']}%",
                  f"{tstats['wins']}W / {tstats['losses']}L / {tstats['be']}BE")
        m3.metric("Ort. R:R",      tstats["avg_rr"])
        m4.metric("Toplam P&L",    pnl_delta, delta_color=pnl_color)
        m5.metric("Açık İşlem",    tstats["running"])

        # ── Equity curve ──────────────────────────────────────────
        if tstats["equity_curve"]:
            st.divider()
            st.markdown("**Equity Curve**")
            eq_data = {e["date"]: e["pnl"] for e in tstats["equity_curve"]}
            st.line_chart(eq_data, use_container_width=True, height=200)

        st.divider()

        # ── Yeni işlem formu ──────────────────────────────────────
        pf = st.session_state.prefill_trade or {}
        form_open = bool(pf) or tstats["total"] == 0

        if pf:
            st.info(f"📋 Alert'ten aktarıldı: **{pf.get('symbol')}** {pf.get('direction')} — {pf.get('notes','')}")

        with st.expander("➕ Yeni İşlem Ekle", expanded=form_open):
            fc1, fc2 = st.columns(2)
            with fc1:
                t_symbol    = st.text_input("Sembol",
                                            value=pf.get("symbol", "BTCUSDT"), key="t_sym")
                dir_opts    = ["LONG", "SHORT"]
                dir_default = dir_opts.index(pf["direction"]) if pf.get("direction") in dir_opts else 0
                t_direction = st.radio("Yön", dir_opts, index=dir_default,
                                       horizontal=True, key="t_dir")
                t_entry     = st.number_input("Entry", min_value=0.0,
                                              value=pf.get("entry", 0.0),
                                              format="%.4f", key="t_entry")
                t_sl        = st.number_input("Stop Loss", min_value=0.0,
                                              value=pf.get("sl", 0.0),
                                              format="%.4f", key="t_sl")
            with fc2:
                t_tp        = st.number_input("Take Profit", min_value=0.0,
                                              value=pf.get("tp", 0.0),
                                              format="%.4f", key="t_tp")
                t_risk      = st.number_input("Risk (USD)", min_value=0.0, value=10.0,
                                              format="%.2f", key="t_risk")
                t_notes     = st.text_area("Notlar", value=pf.get("notes", ""),
                                           height=80, key="t_notes")

                if t_entry > 0 and t_sl > 0 and t_tp > 0:
                    risk_pts   = abs(t_entry - t_sl)
                    reward_pts = abs(t_tp - t_entry)
                    rr_preview = reward_pts / risk_pts if risk_pts else 0
                    sl_pct     = abs(t_entry - t_sl) / t_entry * 100
                    tp_pct     = abs(t_tp - t_entry) / t_entry * 100
                    st.caption(f"R:R → 1:{rr_preview:.2f}  |  SL %{sl_pct:.2f}  |  TP %{tp_pct:.2f}")

            if st.button("İşlemi Kaydet", type="primary", key="t_save"):
                if t_entry > 0 and t_sl > 0:
                    journal_service.save_trade(
                        symbol=t_symbol, direction=t_direction,
                        entry=t_entry, sl=t_sl, tp=t_tp,
                        risk_usd=t_risk, notes=t_notes,
                        alert_id=pf.get("alert_id"),
                    )
                    st.session_state.prefill_trade = None
                    st.success("İşlem kaydedildi.")
                    st.rerun()
                else:
                    st.error("Entry ve SL zorunlu.")

        # ── İşlem listesi ─────────────────────────────────────────
        if not trades:
            st.info("Henüz işlem kaydedilmedi.")
        else:
            result_icons = {"TP": "✅", "SL": "❌", "BE": "➡️", "RUNNING": "🔄"}
            dir_icons    = {"LONG": "🟢", "SHORT": "🔴"}

            for tr in trades:
                rid   = tr.get("result") or "RUNNING"
                icon  = result_icons.get(rid, "")
                dicon = dir_icons.get(tr.get("direction", ""), "")
                pnl_str = f"  ${tr['pnl_usd']:+,.2f}" if tr.get("pnl_usd") is not None and rid != "RUNNING" else ""
                rr_str  = f"  1:{tr['rr_achieved']:.2f}R" if tr.get("rr_achieved") else ""

                with st.expander(
                    f"{icon} {dicon} {tr['symbol']} · {tr['direction']}  —  "
                    f"{tr['created_at'][:16]}{pnl_str}{rr_str}"
                ):
                    cl1, cl2, cl3 = st.columns(3)
                    with cl1:
                        st.markdown(f"**Entry:** {tr['entry']}")
                        st.markdown(f"**SL:** {tr['sl']}")
                        st.markdown(f"**TP:** {tr['tp']}")
                    with cl2:
                        st.markdown(f"**Risk:** ${tr['risk_usd']:.2f}")
                        if tr.get("exit_price"):
                            st.markdown(f"**Çıkış:** {tr['exit_price']}")
                        if tr.get("notes"):
                            st.caption(tr["notes"])

                    with cl3:
                        if rid == "RUNNING":
                            exit_price = st.number_input(
                                "Çıkış fiyatı", min_value=0.0, value=0.0,
                                format="%.4f", key=f"ep_{tr['id']}"
                            )
                            new_result = st.selectbox(
                                "Sonuç",
                                ["TP", "SL", "BE"],
                                key=f"tr_res_{tr['id']}",
                            )
                            if st.button("Kapat", key=f"tr_close_{tr['id']}"):
                                if exit_price > 0:
                                    journal_service.close_trade(tr["id"], new_result, exit_price)
                                    st.rerun()
                                else:
                                    st.error("Çıkış fiyatı gir.")
                        else:
                            st.markdown(f"**Sonuç:** {icon} {rid}")
                            if tr.get("pnl_usd") is not None:
                                color = "green" if tr["pnl_usd"] >= 0 else "red"
                                st.markdown(
                                    f"**P&L:** <span style='color:{color}'>${tr['pnl_usd']:+,.2f}</span>",
                                    unsafe_allow_html=True
                                )

    # ─────────────────────────────────────────────────────────────
    with tab_perf:
        if stats["total"] == 0:
            st.info("Henüz kayıtlı analiz yok. Analiz yapıp 'Journal'a Kaydet' butonuna bas.")
        else:
            # ── Üst metrikler ──────────────────────────────────────────────
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Toplam Analiz", stats["total"])
            c2.metric("Win Rate", f"{stats['winrate']}%", help="Sonucu işaretlenmiş analizlerde TP oranı")
            c3.metric("Karar Verilen", stats["decided_count"], help="TP + SL + BE toplamı")
            c4.metric("Ort. Güven", f"{stats['avg_confidence']}/10")
            rc = stats["result_counts"]
            c5.metric("TP / SL / BE", f"{rc.get('TP',0)} / {rc.get('SL',0)} / {rc.get('BE',0)}")

            st.divider()

            col_bias, col_result = st.columns(2)

            with col_bias:
                st.markdown("**Bias Dağılımı**")
                bc = stats["bias_counts"]
                if bc:
                    bias_order = ["BULLISH", "BEARISH", "RANGING", "NO_TRADE", "INSUFFICIENT_DATA"]
                    bias_data = {k: bc.get(k, 0) for k in bias_order if bc.get(k, 0) > 0}
                    st.bar_chart(bias_data, use_container_width=True, height=200)

            with col_result:
                st.markdown("**Sonuç Dağılımı**")
                rc_clean = {k: v for k, v in stats["result_counts"].items() if v > 0}
                if rc_clean:
                    st.bar_chart(rc_clean, use_container_width=True, height=200)
                else:
                    st.caption("Henüz sonuç işaretlenmedi.")

            st.divider()

            # ── Güven skoru analizi ─────────────────────────────────────────
            st.markdown("**Güven Skoru vs Win Rate**")
            conf_cols = st.columns(4)
            for i, cs in enumerate(stats["confidence_stats"]):
                with conf_cols[i]:
                    wr = cs["win_rate"]
                    color = "normal" if wr >= 50 else "inverse"
                    conf_cols[i].metric(
                        cs["label"],
                        f"{wr}%" if cs["total"] > 0 else "—",
                        f"{cs['total']} analiz",
                        delta_color=color,
                    )

            st.divider()

            # ── Sembol bazlı ────────────────────────────────────────────────
            col_sym, col_trend = st.columns(2)

            with col_sym:
                st.markdown("**Sembol Bazlı Analiz Sayısı**")
                sym_data = {k: v["count"] for k, v in stats["symbol_stats"].items()}
                if sym_data:
                    st.bar_chart(sym_data, use_container_width=True, height=180)

            with col_trend:
                st.markdown("**Son 30 Gün Günlük Analiz**")
                if stats["daily_trend"]:
                    st.bar_chart(stats["daily_trend"], use_container_width=True, height=180)
                else:
                    st.caption("Son 30 günde analiz yok.")

    with tab_log:
        if not records:
            st.info("Henüz kayıtlı analiz yok.")
        else:
            for rec in records:
                bias_emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "RANGING": "🟡", "NO_TRADE": "⚫"}.get(rec["bias"], "⚪")
                result_emoji = {"TP": "✅", "SL": "❌", "BE": "➡️", "NO_TRADE": "⏭️", "RUNNING": "🔄"}.get(rec.get("result"), "")
                tg_emoji = "📤" if rec.get("telegram_sent") else ""

                with st.expander(
                    f"{bias_emoji} {rec['symbol']} {rec['timeframe']} — {rec['created_at'][:16]}  {result_emoji} {tg_emoji}"
                ):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"**Bias:** {rec['bias']}")
                        st.markdown(f"**Güven:** {rec['confidence']}/10")
                        st.markdown(f"**Sembol:** {rec['symbol']}")
                        st.markdown(f"**Timeframe:** {rec['timeframe']}")

                        new_result = st.selectbox(
                            "Sonucu işaretle",
                            ["", "TP", "SL", "BE", "NO_TRADE", "RUNNING"],
                            index=["", "TP", "SL", "BE", "NO_TRADE", "RUNNING"].index(rec.get("result") or ""),
                            key=f"result_{rec['id']}",
                        )
                        if new_result and new_result != rec.get("result"):
                            if st.button("Kaydet", key=f"save_result_{rec['id']}"):
                                journal_service.update_result(rec["id"], new_result)
                                st.rerun()

                    with col2:
                        if rec.get("summary"):
                            st.write(rec["summary"])
                        if rec.get("manual_note"):
                            st.caption(f"Not: {rec['manual_note']}")

# ─────────────────────────────────────────────────────────────────────────────
# SAYFA: ALERTLER
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Alertler":
    import re
    from datetime import datetime, timezone, timedelta
    from app.services import pipeline_service, tradingview_service as _tv_svc, ltf_service
    tradingview_service = _tv_svc

    # ── Yardımcı fonksiyonlar ────────────────────────────────────
    def _parse_gate(msg: str) -> dict:
        """GATE mesajından Entry/SL/TP/Score çıkar."""
        out = {}
        for key, pat in [("entry", r"Entry[:\s]*([\d,.]+)"),
                         ("sl",    r"SL[:\s]*([\d,.]+)"),
                         ("tp",    r"TP[:\s]*([\d,.]+)"),
                         ("score", r"Score[:\s]*([\d]+)/10")]:
            m = re.search(pat, msg, re.IGNORECASE)
            if m:
                out[key] = m.group(1).replace(",", "")
        return out

    def _fmt(v) -> str:
        try:
            f = float(v)
            return f"{f:,.2f}" if f < 10_000 else f"{f:,.1f}"
        except Exception:
            return str(v)

    def _pct(entry, level) -> str:
        try:
            d = (float(level) - float(entry)) / float(entry) * 100
            return f"{'+'if d>=0 else ''}{d:.2f}%"
        except Exception:
            return ""

    def _rr(entry, sl, tp) -> str:
        try:
            risk   = abs(float(entry) - float(sl))
            reward = abs(float(tp)    - float(entry))
            return f"1:{reward/risk:.1f}" if risk else ""
        except Exception:
            return ""

    def _render_card(alert: dict):
        msg    = alert.get("message", "")
        symbol = alert.get("symbol", "?")
        tf     = alert.get("timeframe", "?")
        ts     = alert.get("created_at", "")[:16].replace("T", " ")
        aid    = alert.get("id", 0)
        mu     = msg.upper()

        is_bull_gate = "BULL GATE" in mu
        is_bear_gate = "BEAR GATE" in mu
        is_htf       = any(k in mu for k in ("CHOCH", "BOS", "HTF", "TRIGGER", "BULLISH", "BEARISH"))

        if is_bull_gate or is_bear_gate:
            p      = _parse_gate(msg)
            cls    = "gate-bull" if is_bull_gate else "gate-bear"
            icon   = "🟢" if is_bull_gate else "🔴"
            title  = "BULL GATE ✓" if is_bull_gate else "BEAR GATE ✓"

            rows = [f"📍 Entry : <b>{_fmt(p.get('entry','?'))}</b>"]
            if p.get("sl"):
                rows.append(f"🛑 SL &nbsp;&nbsp;&nbsp;: {_fmt(p['sl'])} <span style='color:#888'>({_pct(p.get('entry',0), p['sl'])})</span>")
            if p.get("tp"):
                rows.append(f"🎯 TP &nbsp;&nbsp;&nbsp;: {_fmt(p['tp'])} <span style='color:#888'>({_pct(p.get('entry',0), p['tp'])})</span>")
            if p.get("sl") and p.get("tp"):
                rr = _rr(p.get("entry", 0), p["sl"], p["tp"])
                if rr:
                    rows.append(f"📊 R/R &nbsp;&nbsp;: <b>{rr}</b>")
            if p.get("score"):
                rows.append(f"⚡ Score : {p['score']}/10")

            card_col, btn_col = st.columns([5, 1])
            with card_col:
                st.markdown(f"""
<div class="gate-card {cls}">
  <div class="gate-title">{icon} {title} &nbsp;·&nbsp; {symbol} &nbsp;·&nbsp; {tf}</div>
  {"<br>".join(f'<div class="gate-row">{r}</div>' for r in rows)}
  <div class="gate-time">⏰ {ts}</div>
</div>
""", unsafe_allow_html=True)

                        # LTF alignment durumu
                direction = "BULL" if is_bull_gate else "BEAR"
                al = ltf_service.validate_gate(symbol=symbol, direction=direction)
                if al["htf_bias"] is not None:
                    if al["aligned"] is True:
                        st.success(f"✓ {al['reason']}")
                    elif al["aligned"] is False:
                        st.warning(f"⚠ {al['reason']}")
                else:
                    st.caption(al["reason"])

                # Pipeline durumu
                ps = pipeline_service.get_status(aid)
                if ps:
                    state = ps.get("state", "")
                    if state == "done":
                        bias = ps.get("bias", "?")
                        conf = ps.get("confidence", "?")
                        summ = ps.get("summary", "")
                        bias_ico = {"BULLISH": "🟢", "BEARISH": "🔴", "RANGING": "🟡",
                                    "NO_TRADE": "⚫"}.get(bias, "⚪")
                        st.success(
                            f"{bias_ico} **AI:** {bias} · Güven: {conf}/10"
                            + (f"\n\n{summ}" if summ else "")
                        )
                    elif state == "error":
                        st.error(f"Pipeline hata: {ps.get('error','?')}")
                    else:
                        state_labels = {
                            "running": "Başlatılıyor…",
                            "screenshot": "📸 Screenshot alınıyor…",
                            "analyzing": "🤖 Claude analiz ediyor…",
                            "saving": "💾 Kaydediliyor…",
                        }
                        st.info(state_labels.get(state, state))

            with btn_col:
                st.markdown("<div style='padding-top:18px'></div>", unsafe_allow_html=True)
                if st.button("📋 İşlem\nAç", key=f"open_trade_{aid}", use_container_width=True):
                    direction = "LONG" if is_bull_gate else "SHORT"
                    st.session_state.prefill_trade = {
                        "symbol":    symbol,
                        "direction": direction,
                        "entry":     float(p.get("entry", 0) or 0),
                        "sl":        float(p.get("sl",    0) or 0),
                        "tp":        float(p.get("tp",    0) or 0),
                        "notes":     f"Alert #{aid} · {ts}",
                        "alert_id":  aid,
                    }
                    st.session_state.page = "Journal"
                    st.rerun()

                tv_ok = tradingview_service.has_session()
                ps    = pipeline_service.get_status(aid)
                ps_state = ps.get("state") if ps else None
                running = ps_state in ("running", "screenshot", "analyzing", "saving")

                if tv_ok and not running:
                    if st.button("🔬 AI\nAnaliz", key=f"pipeline_{aid}", use_container_width=True):
                        pipeline_service.run_pipeline(
                            alert_id=aid,
                            symbol=symbol,
                            timeframe=tf,
                            message=msg,
                        )
                        st.rerun()
                elif running:
                    st.button("⏳ Çalışıyor", disabled=True,
                              key=f"pipeline_dis_{aid}", use_container_width=True)
                else:
                    st.caption("TV oturumu yok")

        elif is_htf:
            is_bull = any(k in mu for k in ("BULL", "BULLISH"))
            icon    = "📈" if is_bull else "📉"
            st.markdown(f"""
<div class="gate-card gate-htf">
  <div class="gate-title">{icon} HTF Sinyal &nbsp;·&nbsp; {symbol} &nbsp;·&nbsp; {tf}</div>
  <div class="gate-row">{msg}</div>
  <div class="gate-time">⏰ {ts}</div>
</div>
""", unsafe_allow_html=True)

        else:
            st.markdown(f"""
<div class="gate-card gate-htf">
  <div class="gate-title">⚡ Alert &nbsp;·&nbsp; {symbol} &nbsp;·&nbsp; {tf}</div>
  <div class="gate-row">{msg}</div>
  <div class="gate-time">⏰ {ts}</div>
</div>
""", unsafe_allow_html=True)

    # ── Başlık & durum ────────────────────────────────────────────
    st.header("Sinyal Akışı")

    cf_url_file  = Path(__file__).parent / ".cloudflare_url"
    webhook_port = os.getenv("WEBHOOK_PORT", "8080")
    cf_url = cf_url_file.read_text().strip() if cf_url_file.exists() else ""

    status_col, url_col = st.columns([1, 3])
    with status_col:
        if cf_url:
            st.success("🟢 Webhook aktif")
        else:
            st.warning("🟡 Cloudflare kapalı")
    with url_col:
        if cf_url:
            st.code(f"{cf_url}/webhook/tradingview", language="text")
        else:
            st.caption("Başlat: `./start_webhook.sh`")

    # ── Kontroller ────────────────────────────────────────────────
    ctrl1, ctrl2, ctrl3 = st.columns([1, 1, 4])
    with ctrl1:
        if st.button("🔄 Yenile", use_container_width=True):
            st.rerun()
    with ctrl2:
        auto_refresh = st.toggle("Otomatik", value=False)

    # ── Alertleri çek ─────────────────────────────────────────────
    alerts = journal_service.get_recent_alerts(limit=200)

    # ── İstatistikler ─────────────────────────────────────────────
    if alerts:
        today = datetime.now(timezone.utc).date().isoformat()
        today_alerts = [a for a in alerts if a.get("created_at", "").startswith(today)]
        bull_today   = sum(1 for a in today_alerts if "BULL GATE" in a.get("message","").upper())
        bear_today   = sum(1 for a in today_alerts if "BEAR GATE" in a.get("message","").upper())
        htf_today    = sum(1 for a in today_alerts
                          if any(k in a.get("message","").upper()
                                 for k in ("CHOCH","BOS","HTF","TRIGGER")))

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{len(alerts)}</div><div class="stat-lbl">Toplam Alert</div></div>', unsafe_allow_html=True)
        with s2:
            st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#00c853">{bull_today}</div><div class="stat-lbl">BULL GATE bugün</div></div>', unsafe_allow_html=True)
        with s3:
            st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#ff1744">{bear_today}</div><div class="stat-lbl">BEAR GATE bugün</div></div>', unsafe_allow_html=True)
        with s4:
            st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#64b5f6">{htf_today}</div><div class="stat-lbl">HTF sinyal bugün</div></div>', unsafe_allow_html=True)

    st.divider()

    # ── Filtre ────────────────────────────────────────────────────
    if alerts:
        f1, f2 = st.columns([2, 1])
        with f1:
            filter_type = st.selectbox(
                "Filtre",
                ["Tümü", "BULL GATE", "BEAR GATE", "HTF Sinyal"],
                label_visibility="collapsed",
            )
        with f2:
            show_count = st.selectbox("Göster", [20, 50, 100, 200],
                                      label_visibility="collapsed")

        def _matches(a):
            mu = a.get("message", "").upper()
            if filter_type == "BULL GATE":  return "BULL GATE" in mu
            if filter_type == "BEAR GATE":  return "BEAR GATE" in mu
            if filter_type == "HTF Sinyal": return any(k in mu for k in ("CHOCH","BOS","HTF","TRIGGER"))
            return True

        filtered = [a for a in alerts if _matches(a)][:show_count]

        st.caption(f"{len(filtered)} sinyal gösteriliyor")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        for alert in filtered:
            _render_card(alert)
    else:
        st.info("Henüz alert alınmadı. TradingView alertleri geldiğinde burada görünecek.")

    # ── Otomatik yenileme ─────────────────────────────────────────
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# SAYFA: HAKKINDA
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Hakkında":
    st.header("Yemre AI Trading Desk")
    st.markdown("""
**Versiyon:** 0.5

**Bu sistem nedir?**
AI destekli hibrit trading karar destek sistemi. Otomatik işlem açmaz.
Trader'ın kendi strateji kurallarına göre grafik analizi yapar ve Telegram için mesaj üretir.

**Mevcut Modüller:**
- Chart AI Analyzer (Claude Vision)
- Otomatik Çok Timeframe Tarama (TradingView + Playwright)
- Trading Journal (SQLite) + Performans Dashboard
- Risk & Pozisyon Hesaplayıcı
- Telegram: Multi-kanal (VIP / Public / Varsayılan) + Fotoğraflı gönderim
- TradingView Alert Webhook (`python webhook_server.py` ile ayrı çalışır)

**Yakında (v0.6+):**
- LTF Sinyal Motoru
- Haftalık Performans Özeti (otomatik Telegram)
- Webhook → otomatik screenshot + AI analiz pipeline

---
*Bu uygulama yatırım tavsiyesi vermez. Tüm kararlar kullanıcıya aittir.*
""")
