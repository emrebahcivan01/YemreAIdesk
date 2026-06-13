#!/bin/bash
# ─────────────────────────────────────────────────────────────────
#  Yemre AI Trading Desk — Webhook + Cloudflare Tunnel Başlatıcı
#  Kullanım: ./start_webhook.sh
# ─────────────────────────────────────────────────────────────────

cd "$(dirname "$0")"

CF_LOG="/tmp/yemre_cf_tunnel.log"
CF_URL_FILE=".cloudflare_url"

# ── cloudflared kurulu mu? ────────────────────────────────────────
if ! command -v cloudflared &>/dev/null; then
    echo ""
    echo "  cloudflared bulunamadı. Kurulum:"
    echo "    brew install cloudflared"
    echo ""
    exit 1
fi

# ── venv aktif et ─────────────────────────────────────────────────
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# ── eski URL dosyasını temizle ────────────────────────────────────
rm -f "$CF_URL_FILE"
> "$CF_LOG"

# ── Webhook sunucusunu başlat ─────────────────────────────────────
echo ""
echo "  Webhook sunucusu başlatılıyor (port 8080)..."
python webhook_server.py &
WEBHOOK_PID=$!
sleep 1

# sunucu ayağa kalktı mı?
if ! kill -0 $WEBHOOK_PID 2>/dev/null; then
    echo "  HATA: Webhook sunucusu başlatılamadı."
    echo "  Belki 8080 portu dolu — 'lsof -i :8080' ile kontrol et."
    exit 1
fi

# ── Cloudflare Tunnel başlat ──────────────────────────────────────
echo "  Cloudflare Tunnel açılıyor..."
cloudflared tunnel --url http://localhost:8080 --loglevel info 2>"$CF_LOG" &
CF_PID=$!

# ── URL'i bekle (max 30 sn) ───────────────────────────────────────
CF_URL=""
for i in $(seq 1 30); do
    CF_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$CF_LOG" 2>/dev/null | head -1)
    [ -n "$CF_URL" ] && break
    sleep 1
done

# URL'i dosyaya kaydet (Streamlit okur)
echo "$CF_URL" > "$CF_URL_FILE"

# ── Sonucu göster ─────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -n "$CF_URL" ]; then
    echo "  SISTEM HAZIR"
    echo ""
    echo "  TradingView Alert Webhook URL:"
    echo "  $CF_URL/webhook/tradingview"
    echo ""
    echo "  Bu URL'i TradingView Alert'e yapistir."
    echo "  Streamlit Alertler sayfasinda da gorunur."
else
    echo "  UYARI: Cloudflare URL alinamadi"
    echo "  Log: $CF_LOG"
    echo "  Webhook sunucusu calisiyor ama tunel yok."
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Durdurmak icin: Ctrl+C"
echo ""

# ── Çıkışta her şeyi kapat ───────────────────────────────────────
cleanup() {
    echo ""
    echo "  Kapatiliyor..."
    kill $WEBHOOK_PID $CF_PID 2>/dev/null
    rm -f "$CF_URL_FILE"
    exit 0
}
trap cleanup EXIT INT TERM

wait
