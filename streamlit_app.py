import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from app.services import ai_service, telegram_service, journal_service, tradingview_service

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
    .bias-bullish  { color: #00c853; font-size: 1.5rem; font-weight: bold; }
    .bias-bearish  { color: #ff1744; font-size: 1.5rem; font-weight: bold; }
    .bias-ranging  { color: #ff9100; font-size: 1.5rem; font-weight: bold; }
    .bias-notrade  { color: #9e9e9e; font-size: 1.5rem; font-weight: bold; }
    .confidence-bar { margin-top: 4px; }
    .section-header { font-size: 1.1rem; font-weight: 600; margin-top: 1rem; }

    .gate-card {
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 5px solid;
    }
    .gate-bull { background: rgba(0,200,83,0.08); border-color: #00c853; }
    .gate-bear { background: rgba(255,23,68,0.08);  border-color: #ff1744; }
    .gate-htf  { background: rgba(100,181,246,0.08); border-color: #64b5f6; }
    .gate-title { font-size: 1.15rem; font-weight: 700; margin-bottom: 6px; }
    .gate-row   { font-size: 0.92rem; font-family: monospace; margin: 2px 0; }
    .gate-time  { font-size: 0.78rem; color: #888; margin-top: 8px; }
    .stat-box   { text-align: center; padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.04); }
    .stat-num   { font-size: 1.6rem; font-weight: 700; }
    .stat-lbl   { font-size: 0.78rem; color: #888; }
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
    today_alerts = [a for a in alerts if a.get("created_at", "").startswith(today)]
    bull_today   = sum(1 for a in today_alerts if "BULL GATE" in a.get("message","").upper())
    bear_today   = sum(1 for a in today_alerts if "BEAR GATE" in a.get("message","").upper())
    last_gate    = next((a for a in alerts
                         if "BULL GATE" in a.get("message","").upper()
                         or "BEAR GATE" in a.get("message","").upper()), None)
    running_trades = [t for t in trades if t.get("result") == "RUNNING"]

    # ── Başlık ───────────────────────────────────────────────────
    h_col, ref_col = st.columns([5, 1])
    with h_col:
        st.title("Dashboard")
    with ref_col:
        st.markdown("<div style='padding-top:18px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Yenile", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── Sistem durumu ─────────────────────────────────────────────
    cf_url_file = Path(__file__).parent / ".cloudflare_url"
    cf_url = cf_url_file.read_text().strip() if cf_url_file.exists() else ""
    api_ok  = bool(os.getenv("ANTHROPIC_API_KEY"))
    tg_tok  = bool(os.getenv("TELEGRAM_BOT_TOKEN"))
    wh_ok   = bool(cf_url)

    st1, st2, st3, st4 = st.columns(4)
    with st1:
        st.markdown(f"{'🟢' if api_ok else '🔴'} **Claude API**")
        st.caption("Bağlı" if api_ok else "API key eksik")
    with st2:
        st.markdown(f"{'🟢' if tg_tok else '🔴'} **Telegram**")
        st.caption("Bağlı" if tg_tok else "Token eksik")
    with st3:
        st.markdown(f"{'🟢' if wh_ok else '🟡'} **Webhook**")
        st.caption("Aktif" if wh_ok else "start_webhook.sh çalıştır")
    with st4:
        if btc_price:
            sign   = "+" if (btc_pct or 0) >= 0 else ""
            color  = "#00c853" if (btc_pct or 0) >= 0 else "#ff1744"
            st.markdown(
                f"**BTC** &nbsp; <span style='font-size:1.2rem;font-weight:700'>"
                f"${btc_price:,.0f}</span> "
                f"<span style='color:{color};font-size:0.9rem'>{sign}{btc_pct:.2f}%</span>",
                unsafe_allow_html=True,
            )
            st.caption("Binance spot · 30s cache")
        else:
            st.markdown("**BTC** &nbsp; —")
            st.caption("Fiyat alınamadı")

    st.divider()

    # ── Bugün özeti ──────────────────────────────────────────────
    st.markdown("##### Bugün")
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("BULL GATE",    bull_today)
    d2.metric("BEAR GATE",    bear_today)
    d3.metric("Toplam Alert", len(today_alerts))
    d4.metric("Açık İşlem",  len(running_trades))
    pnl_color = "normal" if tstats["total_pnl"] >= 0 else "inverse"
    d5.metric("Toplam P&L",  f"${tstats['total_pnl']:+,.2f}", delta_color=pnl_color)

    st.divider()

    # ── Ana içerik: son sinyal + son analiz ──────────────────────
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.markdown("##### Son GATE Sinyali")
        if last_gate:
            msg    = last_gate.get("message", "")
            symbol = last_gate.get("symbol", "?")
            tf     = last_gate.get("timeframe", "?")
            ts     = last_gate.get("created_at", "")[:16].replace("T", " ")
            mu     = msg.upper()
            is_bull = "BULL GATE" in mu
            p       = _parse_gate(msg)
            cls     = "gate-bull" if is_bull else "gate-bear"
            icon    = "🟢" if is_bull else "🔴"
            title   = "BULL GATE ✓" if is_bull else "BEAR GATE ✓"

            rows = [f"📍 Entry : <b>{_fmt(p.get('entry','?'))}</b>"]
            if p.get("sl"):
                rows.append(f"🛑 SL &nbsp;&nbsp;&nbsp;: {_fmt(p['sl'])} "
                             f"<span style='color:#888'>({_pct(p.get('entry',0), p['sl'])})</span>")
            if p.get("tp"):
                rows.append(f"🎯 TP &nbsp;&nbsp;&nbsp;: {_fmt(p['tp'])} "
                             f"<span style='color:#888'>({_pct(p.get('entry',0), p['tp'])})</span>")
            if p.get("sl") and p.get("tp"):
                try:
                    rr = abs(float(p["tp"]) - float(p["entry"])) / abs(float(p["entry"]) - float(p["sl"]))
                    rows.append(f"📊 R/R &nbsp;&nbsp;: <b>1:{rr:.1f}</b>")
                except Exception:
                    pass
            if p.get("score"):
                rows.append(f"⚡ Score : {p['score']}/10")

            st.markdown(f"""
<div class="gate-card {cls}" style="font-size:1.05rem">
  <div class="gate-title" style="font-size:1.3rem">{icon} {title} &nbsp;·&nbsp; {symbol} &nbsp;·&nbsp; {tf}</div>
  {"<br>".join(f'<div class="gate-row">{r}</div>' for r in rows)}
  <div class="gate-time">⏰ {ts}</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.info("Henüz GATE sinyali yok.")

        # ── Açık işlemler ─────────────────────────────────────────
        if running_trades:
            st.markdown("##### Açık İşlemler")
            for tr in running_trades:
                dicon = "🟢" if tr["direction"] == "LONG" else "🔴"
                entry_v = tr.get("entry") or 0
                sl_v    = tr.get("sl") or 0
                tp_v    = tr.get("tp") or 0
                risk_v  = tr.get("risk_usd") or 0
                sl_pct  = _pct(entry_v, sl_v) if sl_v else ""
                tp_pct  = _pct(entry_v, tp_v) if tp_v else ""
                st.markdown(
                    f"{dicon} **{tr['symbol']}** {tr['direction']} &nbsp;|&nbsp; "
                    f"Entry: `{_fmt(entry_v)}` &nbsp;|&nbsp; "
                    f"SL: `{_fmt(sl_v)}` {sl_pct} &nbsp;|&nbsp; "
                    f"TP: `{_fmt(tp_v)}` {tp_pct} &nbsp;|&nbsp; "
                    f"Risk: ${risk_v:.0f}",
                    unsafe_allow_html=True,
                )

    with right_col:
        # ── Son 5 alert ───────────────────────────────────────────
        st.markdown("##### Son Sinyaller")
        if alerts:
            for a in alerts[:6]:
                mu  = a.get("message", "").upper()
                sym = a.get("symbol", "?")
                tf  = a.get("timeframe", "?")
                ts  = a.get("created_at", "")[:16].replace("T", " ")
                if "BULL GATE" in mu:
                    ico = "🟢"
                    lbl = "BULL GATE"
                elif "BEAR GATE" in mu:
                    ico = "🔴"
                    lbl = "BEAR GATE"
                elif any(k in mu for k in ("CHOCH","BOS","HTF","TRIGGER")):
                    ico = "📈" if any(k in mu for k in ("BULL","BULLISH")) else "📉"
                    lbl = "HTF"
                else:
                    ico = "⚡"
                    lbl = "Alert"
                st.markdown(
                    f"{ico} **{lbl}** &nbsp; {sym} · {tf}"
                    f"<br><span style='font-size:0.75rem;color:#888'>{ts}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown("<hr style='margin:4px 0;border-color:#333'>", unsafe_allow_html=True)
        else:
            st.caption("Henüz sinyal yok.")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── Son AI analizi ────────────────────────────────────────
        st.markdown("##### Son AI Analizi")
        if analyses:
            a = analyses[0]
            bias = a.get("bias", "—")
            bias_colors = {
                "BULLISH": "#00c853", "BEARISH": "#ff1744",
                "RANGING": "#ff9100", "NO_TRADE": "#9e9e9e",
            }
            color = bias_colors.get(bias, "#ffffff")
            st.markdown(
                f"<span style='color:{color};font-size:1.1rem;font-weight:700'>{bias}</span> "
                f"&nbsp; {a.get('symbol','?')} · {a.get('timeframe','?')}<br>"
                f"<span style='font-size:0.8rem;color:#888'>Güven: {a.get('confidence','?')}/10 &nbsp;·&nbsp; {a.get('created_at','')[:16]}</span>",
                unsafe_allow_html=True,
            )
            if a.get("summary"):
                st.caption(a["summary"][:180] + ("…" if len(a.get("summary","")) > 180 else ""))
        else:
            st.caption("Henüz analiz yok.")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── Equity özeti ──────────────────────────────────────────
        if tstats["closed"] > 0:
            st.markdown("##### İşlem Özeti")
            st.markdown(
                f"Win Rate: **{tstats['winrate']}%** &nbsp;|&nbsp; "
                f"Ort. R:R: **{tstats['avg_rr']}** &nbsp;|&nbsp; "
                f"{tstats['wins']}W / {tstats['losses']}L / {tstats['be']}BE"
            )

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
    from app.services import pipeline_service, tradingview_service as _tv_svc
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
