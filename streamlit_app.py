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
    background-color: #070a0f !important;
    font-family: 'Inter', sans-serif;
}
html {
    background-image:
        radial-gradient(circle, rgba(79,195,247,0.032) 1px, transparent 1px),
        radial-gradient(ellipse at 78% 8%, rgba(15,40,110,0.45) 0%, transparent 52%) !important;
    background-size: 44px 44px, 100% 100% !important;
    background-attachment: fixed !important;
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

/* ── Market Sessions Bar ── */
.sess-bar {
    display:flex; align-items:stretch; margin-bottom:14px;
    background:rgba(255,255,255,0.02);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:10px; overflow:hidden;
}
.sess-item {
    display:flex; align-items:center; gap:9px; padding:10px 20px;
    border-right:1px solid rgba(255,255,255,0.05); flex:1;
}
.sess-item:last-child { border-right:none; }
.sess-dot  { width:6px;height:6px;border-radius:50%;display:inline-block;flex-shrink:0; }
.sess-on   { background:#00ff88;box-shadow:0 0 7px #00ff88; }
.sess-off  { background:#1e2a38; }
.sess-city { font-size:0.62rem;color:#3d4a58;text-transform:uppercase;
    letter-spacing:0.1em;font-family:'JetBrains Mono',monospace; }
.sess-time { font-size:0.9rem;font-weight:600;color:#8a9bb0;
    font-family:'JetBrains Mono',monospace;margin-left:auto; }
.sess-utc  { font-size:0.7rem;color:#2a3440;font-family:'JetBrains Mono',monospace;
    margin-left:auto; }
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

    # ── Market Sessions Bar ───────────────────────────────────────
    st.markdown("""
<div class="sess-bar">
  <div class="sess-item">
    <span class="sess-dot sess-off" id="dot-london"></span>
    <span class="sess-city">LONDON</span>
    <span class="sess-time" id="sess-london">--:--</span>
  </div>
  <div class="sess-item">
    <span class="sess-dot sess-off" id="dot-newyork"></span>
    <span class="sess-city">NEW YORK</span>
    <span class="sess-time" id="sess-newyork">--:--</span>
  </div>
  <div class="sess-item">
    <span class="sess-dot sess-off" id="dot-dubai"></span>
    <span class="sess-city">DUBAI</span>
    <span class="sess-time" id="sess-dubai">--:--</span>
  </div>
  <div class="sess-item">
    <span class="sess-dot sess-off" id="dot-tokyo"></span>
    <span class="sess-city">TOKYO</span>
    <span class="sess-time" id="sess-tokyo">--:--</span>
  </div>
  <div class="sess-item" style="border-right:none;justify-content:flex-end;flex:0 0 auto;padding-right:22px">
    <span class="sess-utc" id="sess-utc-clock"></span>
  </div>
</div>
<script>
(function(){
  function _p(n){return String(n).padStart(2,'0');}
  var zones=[
    {t:'sess-london', d:'dot-london', off:1, o:8, c:17},
    {t:'sess-newyork', d:'dot-newyork', off:-4, o:9, c:17},
    {t:'sess-dubai', d:'dot-dubai', off:4, o:8, c:17},
    {t:'sess-tokyo', d:'dot-tokyo', off:9, o:9, c:18}
  ];
  function _run(){
    var now=new Date();
    var utcMs=now.getTime()+now.getTimezoneOffset()*60000;
    zones.forEach(function(z){
      var ct=new Date(utcMs+z.off*3600000);
      var h=ct.getHours(),m=ct.getMinutes();
      var te=document.getElementById(z.t);
      if(te) te.textContent=_p(h)+':'+_p(m);
      var de=document.getElementById(z.d);
      if(de) de.className='sess-dot '+(h>=z.o&&h<z.c?'sess-on':'sess-off');
    });
    var uc=document.getElementById('sess-utc-clock');
    if(uc) uc.textContent='UTC '+_p(now.getUTCHours())+':'+_p(now.getUTCMinutes())+':'+_p(now.getUTCSeconds());
  }
  _run();
  setInterval(_run,1000);
})();
</script>
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
    st.markdown("<div class='sec-lbl' style='font-size:0.8rem;margin-bottom:16px'>⬡ Chart AI Analizi</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.6])

    with col_left:
        st.markdown("<div class='sec-lbl'>Grafik Yükle</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "TradingView Screenshot",
            type=["png", "jpg", "jpeg", "webp"],
            label_visibility="collapsed",
        )
        if uploaded:
            st.image(uploaded, use_container_width=True)

        symbol = st.text_input("Sembol", value="BTCUSDT", placeholder="BTCUSDT, XAUUSD, ETHUSDT...")
        timeframe_options = ["1M", "3M", "5M", "15M", "30M", "1H", "2H", "4H", "1D", "1W"]
        timeframe = st.selectbox("Timeframe", timeframe_options, index=5)
        manual_note = st.text_area(
            "Manuel Not",
            placeholder="Haber, özel durum, likidite bölgesi...",
            height=80,
        )
        analyze_btn = st.button("⬡ Analiz Et", type="primary", use_container_width=True, disabled=not uploaded)
        if not uploaded:
            st.markdown("<div style='font-size:0.72rem;color:#3d4a58;margin-top:4px'>Screenshot yükleyince aktif olur</div>", unsafe_allow_html=True)

    with col_right:
        if "last_analysis" not in st.session_state:
            st.session_state.last_analysis = None
            st.session_state.last_analysis_id = None
            st.session_state.last_image_bytes = None

        if analyze_btn and uploaded:
            if not api_ok:
                st.error("ANTHROPIC_API_KEY eksik.")
            else:
                image_bytes = uploaded.read()
                ext = uploaded.name.rsplit(".", 1)[-1].lower()
                media_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
                media_type = media_map.get(ext, "image/png")
                with st.spinner("Claude grafiği analiz ediyor…"):
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
            bias_colors = {"BULLISH": "#00ff88", "BEARISH": "#ff3366", "RANGING": "#ffd32a"}
            bias_labels = {"BULLISH": "▲ BULLISH", "BEARISH": "▼ BEARISH", "RANGING": "◆ RANGING"}
            b_color = bias_colors.get(result.bias, "#5a6878")
            b_label = bias_labels.get(result.bias, result.bias)
            conf_pct = result.confidence / 10 * 100

            st.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);
border-left:3px solid {b_color};border-radius:12px;padding:16px 20px;margin-bottom:14px">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <span style="color:{b_color};font-size:1.4rem;font-weight:700;font-family:'JetBrains Mono',monospace">{b_label}</span>
    <span style="color:#5a6878;font-size:0.78rem;font-family:'JetBrains Mono',monospace">{result.symbol} · {result.timeframe}</span>
  </div>
  <div style="margin-top:10px;height:3px;background:rgba(255,255,255,0.07);border-radius:2px">
    <div style="height:100%;width:{conf_pct}%;background:{b_color};border-radius:2px"></div>
  </div>
  <div style="font-size:0.68rem;color:#3d4a58;margin-top:5px;font-family:'JetBrains Mono',monospace">GÜVEN: {result.confidence}/10</div>
</div>
""", unsafe_allow_html=True)

            tab_summary, tab_scenarios, tab_levels, tab_telegram = st.tabs(
                ["Özet", "Senaryolar", "Seviyeler", "Telegram"]
            )

            with tab_summary:
                st.markdown(f"<div style='color:#c0cad6;line-height:1.7;font-size:0.9rem'>{result.summary}</div>", unsafe_allow_html=True)
                if result.market_structure:
                    st.markdown(f"""
<div style="margin-top:12px;padding:12px 16px;background:rgba(79,195,247,0.05);
border:1px solid rgba(79,195,247,0.12);border-radius:10px;font-size:0.85rem;color:#8ab4cc">
<span style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:#4fc3f7">Piyasa Yapısı</span><br><br>
{result.market_structure}</div>""", unsafe_allow_html=True)
                if result.risk_notes:
                    st.markdown(f"""
<div style="margin-top:10px;padding:12px 16px;background:rgba(255,211,42,0.05);
border:1px solid rgba(255,211,42,0.15);border-radius:10px;font-size:0.85rem;color:#c8a800">
⚠ {result.risk_notes}</div>""", unsafe_allow_html=True)
                if result.no_trade_conditions:
                    items = "".join(f"<div style='padding:3px 0;color:#7f8c9a'>· {c}</div>" for c in result.no_trade_conditions)
                    st.markdown(f"""
<div style="margin-top:10px;padding:12px 16px;background:rgba(255,51,102,0.05);
border:1px solid rgba(255,51,102,0.12);border-radius:10px;font-size:0.83rem">
<div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:#ff3366;margin-bottom:8px">İşlem Alınmaz</div>
{items}</div>""", unsafe_allow_html=True)

            with tab_scenarios:
                col_l, col_s = st.columns(2)
                with col_l:
                    st.markdown(f"""
<div style="padding:14px;background:rgba(0,255,136,0.04);border:1px solid rgba(0,255,136,0.15);
border-radius:10px;font-size:0.84rem;color:#8abba0;line-height:1.6">
<div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:#00ff88;margin-bottom:8px">▲ Long Senaryo</div>
{result.long_scenario}</div>""", unsafe_allow_html=True)
                with col_s:
                    st.markdown(f"""
<div style="padding:14px;background:rgba(255,51,102,0.04);border:1px solid rgba(255,51,102,0.15);
border-radius:10px;font-size:0.84rem;color:#bb8a90;line-height:1.6">
<div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:#ff3366;margin-bottom:8px">▼ Short Senaryo</div>
{result.short_scenario}</div>""", unsafe_allow_html=True)

            with tab_levels:
                kl = result.key_levels
                resistances = kl.get("resistance", [])
                supports    = kl.get("support", [])
                col_r, col_s = st.columns(2)
                with col_r:
                    r_items = "".join(f"<div style='padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-family:\"JetBrains Mono\",monospace;font-size:0.85rem;color:#e0e6ed'>{lvl}</div>" for lvl in resistances)
                    st.markdown(f"""
<div style="padding:12px 16px;background:rgba(255,51,102,0.04);border:1px solid rgba(255,51,102,0.12);border-radius:10px">
<div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:#ff3366;margin-bottom:8px">▼ Direnç</div>
{r_items or '<div style="color:#3d4a58;font-size:0.8rem">—</div>'}</div>""", unsafe_allow_html=True)
                with col_s:
                    s_items = "".join(f"<div style='padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-family:\"JetBrains Mono\",monospace;font-size:0.85rem;color:#e0e6ed'>{lvl}</div>" for lvl in supports)
                    st.markdown(f"""
<div style="padding:12px 16px;background:rgba(0,255,136,0.04);border:1px solid rgba(0,255,136,0.12);border-radius:10px">
<div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:#00ff88;margin-bottom:8px">▲ Destek</div>
{s_items or '<div style="color:#3d4a58;font-size:0.8rem">—</div>'}</div>""", unsafe_allow_html=True)

            with tab_telegram:
                channels = telegram_service.get_channels()
                has_tg = bool(channels and os.getenv("TELEGRAM_BOT_TOKEN"))
                if channels:
                    selected_channel_name = st.selectbox("Kanal", list(channels.keys()), key="tg_channel")
                    selected_chat_id = channels[selected_channel_name]
                else:
                    selected_chat_id = None
                    st.markdown("<div style='font-size:0.8rem;color:#5a6878'>Telegram kanalı .env'de yapılandırılmamış</div>", unsafe_allow_html=True)

                sym_upper = result.symbol.upper()
                if any(x in sym_upper for x in ("XAU", "GOLD")):
                    sig_num = journal_service.get_daily_signal_number(result.symbol)
                    st.markdown(f"<div style='font-size:0.8rem;color:#ffd32a;margin-bottom:8px'>⚡ XAU Sinyal #{sig_num} (bugün)</div>", unsafe_allow_html=True)

                tg_text = st.text_area("Mesaj", value=result.telegram_message, height=200, key="tg_edit")

                col_send, col_photo, col_save = st.columns(3)
                with col_send:
                    if st.button("✈ Mesaj Gönder", use_container_width=True, disabled=not has_tg):
                        ok, msg = telegram_service.send_message(tg_text, chat_id=selected_chat_id)
                        if ok:
                            st.success(msg)
                            if st.session_state.last_analysis_id:
                                journal_service.mark_telegram_sent(st.session_state.last_analysis_id)
                        else:
                            st.error(f"Gönderilemedi: {msg}")
                with col_photo:
                    has_img = st.session_state.last_image_bytes is not None
                    if st.button("🖼 Fotoğraf + Mesaj", use_container_width=True, disabled=not (has_tg and has_img)):
                        ok, msg = telegram_service.send_photo(
                            st.session_state.last_image_bytes, caption=tg_text[:1024], chat_id=selected_chat_id,
                        )
                        if ok:
                            st.success(msg)
                            if st.session_state.last_analysis_id:
                                journal_service.mark_telegram_sent(st.session_state.last_analysis_id)
                        else:
                            st.error(f"Gönderilemedi: {msg}")
                with col_save:
                    if st.button("◎ Journal'a Kaydet", use_container_width=True):
                        if st.session_state.last_analysis_id is None:
                            aid = journal_service.save_analysis(result, manual_note=manual_note)
                            st.session_state.last_analysis_id = aid
                            st.success(f"Kaydedildi #{aid}")
                        else:
                            st.info(f"Zaten kaydedildi #{st.session_state.last_analysis_id}")
        else:
            st.markdown("""
<div style="height:200px;display:flex;align-items:center;justify-content:center;
border:1px dashed rgba(255,255,255,0.07);border-radius:12px;color:#3d4a58;font-size:0.85rem">
Grafik yükle ve Analiz Et'e bas
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SAYFA: OTOMATİK TARAMA
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Otomatik Tarama":
    st.markdown("<div class='sec-lbl' style='font-size:0.8rem;margin-bottom:16px'>⬡ Otomatik Çok Timeframe Analizi</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.8rem;color:#5a6878;margin-bottom:18px'>Tek tuşla 5M → 1D arası 7 timeframe'i TradingView'dan çeker ve analiz eder.</div>", unsafe_allow_html=True)

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
        st.markdown("<div class='sec-lbl'>Timeframe'ler</div>", unsafe_allow_html=True)
        tf_list_html = "".join(
            f"<div style='padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.04);"
            f"font-family:\"JetBrains Mono\",monospace;font-size:0.8rem;color:#7f8c9a'>{tf}</div>"
            for tf, _ in tradingview_service.TIMEFRAMES
        )
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);"
            f"border-radius:10px;padding:10px 14px;margin-bottom:12px'>{tf_list_html}</div>",
            unsafe_allow_html=True,
        )

        if tradingview_service.has_session():
            st.markdown(
                "<div style='padding:8px 12px;background:rgba(0,255,136,0.07);border:1px solid rgba(0,255,136,0.2);"
                "border-radius:8px;font-size:0.8rem;color:#00ff88;margin-bottom:8px'>"
                "<span class=\"dot-on\" style=\"display:inline-block;margin-right:6px\"></span> TradingView oturumu mevcut</div>",
                unsafe_allow_html=True,
            )
            if st.button("Oturumu Sıfırla", type="secondary"):
                tradingview_service.clear_session()
                st.rerun()
        else:
            st.markdown(
                "<div style='padding:8px 12px;background:rgba(255,211,42,0.07);border:1px solid rgba(255,211,42,0.2);"
                "border-radius:8px;font-size:0.8rem;color:#ffd32a;margin-bottom:8px'>"
                "<span class=\"dot-warn\" style=\"display:inline-block;margin-right:6px\"></span> Oturum yok — giriş gerekli</div>",
                unsafe_allow_html=True,
            )
            if st.button("TradingView Girişi Yap", type="primary", use_container_width=True):
                with st.spinner("Tarayıcı açılıyor — giriş yapınca otomatik kaydedilir..."):
                    try:
                        tradingview_service.do_login_and_save()
                        st.success("Giriş başarılı! Session kaydedildi.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Giriş kaydedilemedi: {e}")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    scan_btn = st.button("⬡ Tüm Timeframe'leri Tara ve Analiz Et", type="primary", use_container_width=True)

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
        st.markdown("<div class='sec-lbl' style='margin-top:8px'>Analiz Sonuçları</div>", unsafe_allow_html=True)

        # Bias özet kartlar
        _bc_map = {"BULLISH": "#00ff88", "BEARISH": "#ff3366", "RANGING": "#ffd32a", "NO_TRADE": "#5a6878", "INSUFFICIENT_DATA": "#3d4a58"}
        _bl_map = {"BULLISH": "▲ BULL", "BEARISH": "▼ BEAR", "RANGING": "◆ RANGING", "NO_TRADE": "— N/T", "INSUFFICIENT_DATA": "— —"}
        bias_html = ""
        for tf_name, data in mtf.items():
            if "result" in data:
                r = data["result"]
                clr = _bc_map.get(r.bias, "#5a6878")
                lbl = _bl_map.get(r.bias, r.bias)
                cp  = r.confidence / 10 * 100
                bias_html += (
                    f"<div style='flex:1;min-width:90px;background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);"
                    f"border-top:2px solid {clr};border-radius:10px;padding:10px 12px;text-align:center'>"
                    f"<div style='font-size:0.6rem;color:#3d4a58;text-transform:uppercase;letter-spacing:0.1em;"
                    f"font-family:\"JetBrains Mono\",monospace'>{tf_name}</div>"
                    f"<div style='font-size:0.85rem;font-weight:700;color:{clr};margin:5px 0 4px;"
                    f"font-family:\"JetBrains Mono\",monospace'>{lbl}</div>"
                    f"<div style='height:2px;background:rgba(255,255,255,0.06);border-radius:1px'>"
                    f"<div style='height:100%;width:{cp:.0f}%;background:{clr};opacity:0.6;border-radius:1px'></div></div>"
                    f"<div style='font-size:0.62rem;color:#3d4a58;margin-top:4px'>{r.confidence}/10</div>"
                    f"</div>"
                )
            else:
                bias_html += (
                    f"<div style='flex:1;min-width:90px;background:rgba(255,255,255,0.025);border:1px solid rgba(255,51,102,0.15);"
                    f"border-radius:10px;padding:10px 12px;text-align:center'>"
                    f"<div style='font-size:0.6rem;color:#3d4a58;text-transform:uppercase;letter-spacing:0.1em;"
                    f"font-family:\"JetBrains Mono\",monospace'>{tf_name}</div>"
                    f"<div style='font-size:0.85rem;font-weight:700;color:#ff3366;margin:5px 0'>HATA</div>"
                    f"</div>"
                )
        st.markdown(f"<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px'>{bias_html}</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

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
                    _bc = {"BULLISH": "#00ff88", "BEARISH": "#ff3366", "RANGING": "#ffd32a"}.get(result.bias, "#5a6878")
                    _bl = {"BULLISH": "▲ BULLISH", "BEARISH": "▼ BEARISH", "RANGING": "◆ RANGING"}.get(result.bias, result.bias)
                    _cp = result.confidence / 10 * 100
                    st.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);border-left:3px solid {_bc};
border-radius:10px;padding:12px 16px;margin-bottom:10px">
  <span style="color:{_bc};font-size:1.1rem;font-weight:700;font-family:'JetBrains Mono',monospace">{_bl}</span>
  <div style="margin-top:8px;height:2px;background:rgba(255,255,255,0.07);border-radius:1px">
    <div style="height:100%;width:{_cp:.0f}%;background:{_bc};border-radius:1px"></div>
  </div>
  <div style="font-size:0.65rem;color:#3d4a58;margin-top:4px;font-family:'JetBrains Mono',monospace">GÜVEN {result.confidence}/10</div>
</div>""", unsafe_allow_html=True)

                    if result.summary:
                        st.markdown(f"<div style='font-size:0.82rem;color:#8a9bb0;line-height:1.65;margin-bottom:8px'>{result.summary}</div>", unsafe_allow_html=True)
                    if result.market_structure:
                        st.markdown(
                            f"<div style='font-size:0.8rem;padding:8px 12px;background:rgba(79,195,247,0.05);"
                            f"border:1px solid rgba(79,195,247,0.12);border-radius:8px;color:#8ab4cc;margin-bottom:6px'>"
                            f"<span style=\"font-size:0.62rem;text-transform:uppercase;color:#4fc3f7\">Piyasa Yapısı</span>"
                            f"<br>{result.market_structure}</div>",
                            unsafe_allow_html=True,
                        )
                    if result.risk_notes:
                        st.markdown(
                            f"<div style='font-size:0.8rem;padding:8px 12px;background:rgba(255,211,42,0.05);"
                            f"border:1px solid rgba(255,211,42,0.15);border-radius:8px;color:#c8a800;margin-bottom:6px'>⚠ {result.risk_notes}</div>",
                            unsafe_allow_html=True,
                        )
                    if result.no_trade_conditions:
                        ntc = "".join(f"<div style='padding:2px 0;color:#7f8c9a;font-size:0.78rem'>· {c}</div>" for c in result.no_trade_conditions)
                        st.markdown(
                            f"<div style='padding:8px 12px;background:rgba(255,51,102,0.05);"
                            f"border:1px solid rgba(255,51,102,0.12);border-radius:8px;margin-bottom:6px'>"
                            f"<div style=\"font-size:0.62rem;text-transform:uppercase;color:#ff3366;margin-bottom:4px\">İşlem Alınmaz</div>{ntc}</div>",
                            unsafe_allow_html=True,
                        )

                    kl = result.key_levels
                    lvl_r = kl.get("resistance", [])
                    lvl_s = kl.get("support", [])
                    if lvl_r or lvl_s:
                        lc1, lc2 = st.columns(2)
                        with lc1:
                            r_items = "".join(
                                f"<div style='padding:3px 0;font-family:\"JetBrains Mono\",monospace;font-size:0.8rem;"
                                f"color:#e0e6ed;border-bottom:1px solid rgba(255,255,255,0.04)'>{lvl}</div>"
                                for lvl in lvl_r
                            )
                            st.markdown(
                                f"<div style='padding:8px 12px;background:rgba(255,51,102,0.04);"
                                f"border:1px solid rgba(255,51,102,0.12);border-radius:8px'>"
                                f"<div style=\"font-size:0.62rem;text-transform:uppercase;color:#ff3366;margin-bottom:6px\">▼ Direnç</div>"
                                f"{r_items or '<span style=\"color:#3d4a58\">—</span>'}</div>",
                                unsafe_allow_html=True,
                            )
                        with lc2:
                            s_items = "".join(
                                f"<div style='padding:3px 0;font-family:\"JetBrains Mono\",monospace;font-size:0.8rem;"
                                f"color:#e0e6ed;border-bottom:1px solid rgba(255,255,255,0.04)'>{lvl}</div>"
                                for lvl in lvl_s
                            )
                            st.markdown(
                                f"<div style='padding:8px 12px;background:rgba(0,255,136,0.04);"
                                f"border:1px solid rgba(0,255,136,0.12);border-radius:8px'>"
                                f"<div style=\"font-size:0.62rem;text-transform:uppercase;color:#00ff88;margin-bottom:6px\">▲ Destek</div>"
                                f"{s_items or '<span style=\"color:#3d4a58\">—</span>'}</div>",
                                unsafe_allow_html=True,
                            )

# ─────────────────────────────────────────────────────────────────────────────
# SAYFA: JOURNAL
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Journal":
    st.markdown("<div class='sec-lbl' style='font-size:0.8rem;margin-bottom:16px'>⬡ Trading Journal</div>", unsafe_allow_html=True)

    records = journal_service.get_recent_analyses(limit=200)
    stats   = journal_service.get_stats()
    trades  = journal_service.get_trades(limit=200)
    tstats  = journal_service.get_trade_stats()

    tab_trade, tab_perf, tab_log = st.tabs(["İşlemler", "Performans", "Analiz Geçmişi"])

    # ─────────────────────────────────────────────────────────────
    with tab_trade:

        # ── Üst istatistikler ─────────────────────────────────────
        _pnl = tstats["total_pnl"]
        _pnl_cls = "sn-pos" if _pnl >= 0 else "sn-neg"
        _wr = tstats["winrate"]
        _wr_cls = "sn-green" if _wr >= 50 else "sn-red"
        st.markdown(f"""
<div class="stats-row">
  <div class="stat-card">
    <div class="stat-num sn-white">{tstats['total']}</div>
    <div class="stat-lbl">Toplam İşlem</div>
  </div>
  <div class="stat-card">
    <div class="stat-num {_wr_cls}">{_wr}%</div>
    <div class="stat-lbl">Win Rate · <span style="color:#00ff88">{tstats['wins']}W</span> / <span style="color:#ff3366">{tstats['losses']}L</span> / <span style="color:#5a6878">{tstats['be']}BE</span></div>
  </div>
  <div class="stat-card">
    <div class="stat-num sn-blue">{tstats['avg_rr']}</div>
    <div class="stat-lbl">Ort. R:R</div>
  </div>
  <div class="stat-card">
    <div class="stat-num {_pnl_cls}">${_pnl:+,.0f}</div>
    <div class="stat-lbl">Toplam P&L</div>
  </div>
  <div class="stat-card">
    <div class="stat-num sn-blue">{tstats['running']}</div>
    <div class="stat-lbl">Açık İşlem</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Equity curve ──────────────────────────────────────────
        if tstats["equity_curve"]:
            st.markdown("<div class='sec-lbl' style='margin-top:16px'>Equity Curve</div>", unsafe_allow_html=True)
            eq_data = {e["date"]: e["pnl"] for e in tstats["equity_curve"]}
            st.line_chart(eq_data, use_container_width=True, height=200)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── Yeni işlem formu ──────────────────────────────────────
        pf = st.session_state.prefill_trade or {}
        form_open = bool(pf) or tstats["total"] == 0

        if pf:
            st.markdown(
                f"<div style='padding:8px 14px;background:rgba(79,195,247,0.07);border:1px solid rgba(79,195,247,0.2);"
                f"border-radius:8px;font-size:0.82rem;color:#4fc3f7;margin-bottom:8px'>"
                f"Alert'ten aktarıldı: <b>{pf.get('symbol')}</b> {pf.get('direction')} — {pf.get('notes','')}</div>",
                unsafe_allow_html=True,
            )

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
            rc = stats["result_counts"]
            _awr = stats["winrate"]
            _awr_cls = "sn-green" if _awr >= 50 else "sn-red"
            st.markdown(f"""
<div class="stats-row">
  <div class="stat-card">
    <div class="stat-num sn-white">{stats['total']}</div>
    <div class="stat-lbl">Toplam Analiz</div>
  </div>
  <div class="stat-card">
    <div class="stat-num {_awr_cls}">{_awr}%</div>
    <div class="stat-lbl">Win Rate</div>
  </div>
  <div class="stat-card">
    <div class="stat-num sn-blue">{stats['decided_count']}</div>
    <div class="stat-lbl">Karar Verilen</div>
  </div>
  <div class="stat-card">
    <div class="stat-num sn-white">{stats['avg_confidence']}/10</div>
    <div class="stat-lbl">Ort. Güven</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" style="font-size:1.2rem"><span style="color:#00ff88">{rc.get('TP',0)}</span> / <span style="color:#ff3366">{rc.get('SL',0)}</span> / <span style="color:#5a6878">{rc.get('BE',0)}</span></div>
    <div class="stat-lbl">TP / SL / BE</div>
  </div>
</div>
""", unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            col_bias, col_result = st.columns(2)

            with col_bias:
                st.markdown("<div class='sec-lbl'>Bias Dağılımı</div>", unsafe_allow_html=True)
                bc = stats["bias_counts"]
                if bc:
                    bias_order = ["BULLISH", "BEARISH", "RANGING", "NO_TRADE", "INSUFFICIENT_DATA"]
                    bias_data = {k: bc.get(k, 0) for k in bias_order if bc.get(k, 0) > 0}
                    st.bar_chart(bias_data, use_container_width=True, height=200)

            with col_result:
                st.markdown("<div class='sec-lbl'>Sonuç Dağılımı</div>", unsafe_allow_html=True)
                rc_clean = {k: v for k, v in stats["result_counts"].items() if v > 0}
                if rc_clean:
                    st.bar_chart(rc_clean, use_container_width=True, height=200)
                else:
                    st.caption("Henüz sonuç işaretlenmedi.")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # ── Güven skoru analizi ─────────────────────────────────────────
            st.markdown("<div class='sec-lbl'>Güven Skoru vs Win Rate</div>", unsafe_allow_html=True)
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

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # ── Sembol bazlı ────────────────────────────────────────────────
            col_sym, col_trend = st.columns(2)

            with col_sym:
                st.markdown("<div class='sec-lbl'>Sembol Bazlı Analiz</div>", unsafe_allow_html=True)
                sym_data = {k: v["count"] for k, v in stats["symbol_stats"].items()}
                if sym_data:
                    st.bar_chart(sym_data, use_container_width=True, height=180)

            with col_trend:
                st.markdown("<div class='sec-lbl'>Son 30 Gün Trend</div>", unsafe_allow_html=True)
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
    st.markdown("<div class='sec-lbl' style='font-size:0.8rem;margin-bottom:16px'>⬡ Sinyal Akışı</div>", unsafe_allow_html=True)

    cf_url_file  = Path(__file__).parent / ".cloudflare_url"
    webhook_port = os.getenv("WEBHOOK_PORT", "8080")
    cf_url = cf_url_file.read_text().strip() if cf_url_file.exists() else ""

    _wh_dot = "dot-on" if cf_url else "dot-warn"
    _wh_lbl = "Webhook Aktif" if cf_url else "Cloudflare Kapalı"
    _wh_clr = "#00ff88" if cf_url else "#ffd32a"
    _wh_bg  = "rgba(0,255,136,0.05)" if cf_url else "rgba(255,211,42,0.05)"
    _wh_br  = "rgba(0,255,136,0.18)" if cf_url else "rgba(255,211,42,0.18)"
    _url_html = (
        f"<code style='background:rgba(255,255,255,0.05);padding:2px 8px;border-radius:4px;"
        f"font-size:0.78rem;color:#c0cad6'>{cf_url}/webhook/tradingview</code>"
        if cf_url else
        "<span style='color:#3d4a58;font-size:0.8rem'>Başlat: <code style=\"color:#5a6878\">./start_webhook.sh</code></span>"
    )
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:14px;padding:10px 18px;background:{_wh_bg};
border:1px solid {_wh_br};border-radius:10px;margin-bottom:14px">
  <span class="{_wh_dot}" style="display:inline-block;flex-shrink:0"></span>
  <span style="font-size:0.75rem;color:{_wh_clr};font-family:'JetBrains Mono',monospace;
  text-transform:uppercase;letter-spacing:0.08em;white-space:nowrap">{_wh_lbl}</span>
  <span style="color:rgba(255,255,255,0.08)">|</span>
  {_url_html}
</div>
""", unsafe_allow_html=True)

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

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

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
    st.markdown("<div class='sec-lbl' style='font-size:0.8rem;margin-bottom:20px'>⬡ Sistem Hakkında</div>", unsafe_allow_html=True)

    _api_h = bool(os.getenv("ANTHROPIC_API_KEY"))
    _tg_h  = bool(os.getenv("TELEGRAM_BOT_TOKEN"))
    _tv_h  = tradingview_service.has_session()
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(79,195,247,0.06),rgba(79,195,247,0.02));
border:1px solid rgba(79,195,247,0.15);border-radius:16px;padding:28px 32px;margin-bottom:20px">
  <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.2em;color:#4fc3f7;margin-bottom:12px">
    AI Destekli Trading Karar Destek Sistemi
  </div>
  <div style="font-size:1.8rem;font-weight:700;color:#e0e6ed;font-family:'JetBrains Mono',monospace;letter-spacing:0.04em">
    YEMRE AI TRADING DESK
  </div>
  <div style="font-size:0.78rem;color:#5a6878;margin-top:8px;font-family:'JetBrains Mono',monospace">
    v0.6 — LTF Sinyal Motoru Aktif
  </div>
  <div style="display:flex;gap:20px;margin-top:18px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06)">
    <div style="display:flex;align-items:center;gap:7px;font-size:0.72rem;font-family:'JetBrains Mono',monospace">
      <span class="{'dot-on' if _api_h else 'dot-off'}" style="display:inline-block"></span>
      <span style="color:#5a6878;text-transform:uppercase;letter-spacing:0.08em">Claude API</span>
    </div>
    <div style="display:flex;align-items:center;gap:7px;font-size:0.72rem;font-family:'JetBrains Mono',monospace">
      <span class="{'dot-on' if _tg_h else 'dot-off'}" style="display:inline-block"></span>
      <span style="color:#5a6878;text-transform:uppercase;letter-spacing:0.08em">Telegram</span>
    </div>
    <div style="display:flex;align-items:center;gap:7px;font-size:0.72rem;font-family:'JetBrains Mono',monospace">
      <span class="{'dot-on' if _tv_h else 'dot-warn'}" style="display:inline-block"></span>
      <span style="color:#5a6878;text-transform:uppercase;letter-spacing:0.08em">TradingView</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    _modules = [
        ("#00ff88", "▲", "Chart AI Analyzer",
         "Claude Vision ile grafik analizi. Bias, seviyeler, senaryo ve Telegram mesajı üretir."),
        ("#00ff88", "▲", "Otomatik MTF Tarama",
         "5M → 1D arası 7 timeframe'i TradingView'dan çekip analiz eder. Playwright otomasyonu."),
        ("#4fc3f7", "◆", "Trading Journal",
         "SQLite tabanlı işlem ve analiz geçmişi. Equity curve, win rate, P&L ve R:R takibi."),
        ("#4fc3f7", "◆", "Telegram Multi-Kanal",
         "VIP / Public / Varsayılan kanallara metin veya fotoğraflı analiz gönderimi."),
        ("#ffd32a", "⬡", "TradingView Webhook",
         "Pine Script alert → FastAPI + Cloudflare Tunnel → canlı sinyal akışı. Port 8080."),
        ("#ffd32a", "⬡", "LTF Sinyal Motoru",
         "HTF bias takibi + 5M GATE alignment doğrulaması. SQLite ile kalıcı durum."),
    ]

    _mod_cols = st.columns(2)
    for i, (color, icon, title, desc) in enumerate(_modules):
        with _mod_cols[i % 2]:
            st.markdown(f"""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);
border-left:3px solid {color};border-radius:10px;padding:14px 18px;margin-bottom:10px">
  <div style="font-size:0.72rem;font-weight:700;color:{color};font-family:'JetBrains Mono',monospace;
  letter-spacing:0.06em;margin-bottom:6px">{icon} {title.upper()}</div>
  <div style="font-size:0.8rem;color:#5a6878;line-height:1.55">{desc}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="margin-top:16px;padding:16px 20px;background:rgba(255,51,102,0.04);
border:1px solid rgba(255,51,102,0.12);border-radius:10px">
  <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.14em;color:#ff3366;margin-bottom:10px">
    Güvenlik Kuralları
  </div>
  <div style="display:flex;flex-direction:column;gap:5px;font-size:0.8rem;color:#7f8c9a">
    <div>· Otomatik emir gönderimi kesinlikle yok</div>
    <div>· Telegram gönderimi kullanıcı onayı gerektirir</div>
    <div>· API key'ler sadece .env dosyasında — koda yazılmaz</div>
    <div>· Exchange API entegrasyonu bu versiyonda yok</div>
  </div>
</div>
<div style="margin-top:12px;text-align:center;font-size:0.68rem;color:#2a3440;
font-family:'JetBrains Mono',monospace;padding:8px">
  Bu uygulama yatırım tavsiyesi vermez. Tüm kararlar kullanıcıya aittir.
</div>
""", unsafe_allow_html=True)
