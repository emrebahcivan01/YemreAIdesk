# Yemre AI Trading Desk

AI destekli hibrit trading karar destek sistemi. Otomatik işlem açmaz — trader'a strateji kurallarına göre grafik analizi, bias ve sinyal desteği sağlar.

## Özellikler

- **Chart AI Analizi** — TradingView screenshotu yükle, Claude Vision strateji kurallarına göre analiz etsin
- **Otomatik Çok Timeframe Tarama** — 5M → 1D arası 7 timeframe'i TradingView'dan otomatik çekip analiz eder
- **TradingView Webhook** — Pine Script alert → FastAPI + Cloudflare Tunnel → Streamlit'te canlı sinyal akışı
- **Otomatik AI Pipeline** — GATE sinyali gelince arka planda screenshot + Claude analiz + journal kaydı
- **Trading Journal** — İşlem kayıt, P&L hesaplama, equity curve, win rate istatistikleri
- **Telegram Multi-Kanal** — VIP / Public / Varsayılan kanallara mesaj veya fotoğraflı analiz gönderimi
- **Pine Script İndikatörler** — 5M entry ve HTF bias indikatörleri

## Kurulum

```bash
git clone https://github.com/emrebahcivan01/YemreAIdesk.git
cd YemreAIdesk

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### `.env` Dosyası

```bash
cp .env.example .env
```

`.env` dosyasını düzenle:

```env
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=-100...
```

## Kullanım

### Streamlit Arayüzü

```bash
source venv/bin/activate
streamlit run streamlit_app.py
```

### TradingView Webhook (ayrı terminal)

```bash
./start_webhook.sh
```

Çıktıdaki Cloudflare URL'ini TradingView alert'ine yapıştır:
```
https://xxxx.trycloudflare.com/webhook/tradingview
```

## TradingView Alert Formatı

Alert mesajı JSON olarak gönderilmeli:

```json
{
  "symbol": "BTCUSDT",
  "interval": "5",
  "close": "{{close}}",
  "message": "BULL GATE ✓ | FVG MSB | Entry: {{close}} | SL: 103000 | TP: 107000 | Score: 8/10"
}
```

## Proje Yapısı

```
streamlit_app.py          → Ana Streamlit arayüzü
webhook_server.py         → FastAPI webhook sunucusu
start_webhook.sh          → Webhook + Cloudflare Tunnel başlatıcı
app/
  services/
    ai_service.py         → Claude Vision analiz motoru
    telegram_service.py   → Telegram gönderimi
    journal_service.py    → SQLite journal
    pipeline_service.py   → Otomatik AI pipeline
    tradingview_service.py→ Playwright ile TradingView screenshot
  knowledge/
    strategy.md           → Trading strateji kuralları
    risk_rules.md         → Risk yönetimi kuralları
indicators/
  yemre_5m_entry.pine     → 5M entry sinyali (Pine Script)
  yemre_htf_bias.pine     → HTF bias indikatörü (Pine Script)
```

## Güvenlik

- API key'ler sadece `.env` dosyasında — asla koda yazılmaz
- Otomatik emir gönderimi yok
- Telegram gönderimi her zaman manuel onay gerektirir
- Exchange API entegrasyonu yok

## Lisans

Bu proje kişisel kullanım içindir. Yatırım tavsiyesi vermez.
