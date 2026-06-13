# CLAUDE.md — Yemre AI Trading Desk

Bu proje AI destekli hibrit trading karar destek sistemidir.

## Ana Amaç

Sistem otomatik para kazandıran bot değildir. Trader'a strateji kurallarına göre analiz, bias ve karar destek sağlar. Nihai karar her zaman kullanıcıdadır.

## Teknoloji Stack

- Python 3.11+
- Streamlit (MVP arayüz)
- Anthropic Claude API (Vision analiz)
- SQLite (Journal)
- Telegram Bot API (sinyal gönderimi)

## Proje Yapısı

```
streamlit_app.py          → Ana Streamlit arayüzü
app/
  services/
    ai_service.py         → Claude Vision analiz motoru
    telegram_service.py   → Telegram bot gönderimi
    journal_service.py    → SQLite journal işlemleri
  knowledge/
    strategy.md           → Trading strateji kuralları (CORE)
    risk_rules.md         → Risk yönetimi kuralları
    telegram_format.md    → Telegram mesaj şablonları
    no_trade_conditions.md → İşlem alınmayacak durumlar
data/
  journal.db              → SQLite veritabanı (gitignore'da)
  screenshots/            → Kaydedilen grafikler (gitignore'da)
```

## Kodlama Kuralları

- API key'ler asla koda yazılmayacak — sadece `.env`
- AI çıktıları JSON formatında alınacak
- Her servis ayrı dosyada, küçük fonksiyonlar
- Telegram gönderimi her zaman manuel onay gerektirir
- Otomatik işlem açma hiçbir zaman olmayacak
- AI çıktısı doğrudan işlem emri değildir
- Hatalı veya belirsiz analizlerde sistem NO_TRADE döndürür

## Güvenlik

- Otomatik emir gönderimi yok
- Telegram gönderimi kullanıcı onayı gerektirir
- Exchange API entegrasyonu bu versiyonda yok
- `.env` dosyası git'e commit edilmez

## Versiyon Planı

- v0.1: Screenshot + AI analiz + Telegram (şu an)
- v0.2: Journal + performans takibi
- v0.3: Risk hesaplayıcı
- v0.4: TradingView alert webhook
- v0.5: LTF sinyal motoru
