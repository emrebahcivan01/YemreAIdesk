# TradingView → Webhook Kurulum Kılavuzu

## Adım 1 — cloudflared Kur (bir kere)

```bash
brew install cloudflared
```

Ücretsiz, hesap gerektirmez, ngrok'tan daha stabil.

---

## Adım 2 — Her Şeyi Tek Komutla Başlat

```bash
cd ~/Desktop/PROJELER/YemreAIdesk
./start_webhook.sh
```

Script şunları yapar:
1. Webhook sunucusunu (port 8080) başlatır
2. Cloudflare Tunnel açar
3. URL'i ekranda gösterir ve `.cloudflare_url` dosyasına kaydeder
4. Streamlit Alertler sayfasında URL otomatik görünür

Çıktı örneği:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SISTEM HAZIR

  TradingView Alert Webhook URL:
  https://abc-xyz-123.trycloudflare.com/webhook/tradingview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Adım 3 — İndikatörleri TradingView'e Ekle

### Pine Editor'da Aç:
1. TradingView → Pine Editor (altta)
2. `yemre_htf_bias.pine` içeriğini kopyala → yapıştır → **Add to chart** (4H grafik)
3. Tekrar et: `yemre_5m_entry.pine` → 5M grafik üzerine ekle

---

## Adım 4 — Alert Kur (Webhook ile)

### HTF BIAS alertleri (4H grafik):
1. Grafik üzerinde sağ tık → **Add Alert**
2. **Condition:** `YEMRE HTF BIAS` → açılır menüden istediğin koşulu seç:
   - `YEMRE HTF: Bullish Trigger` (önerilen — KZ aktif + score ≥ 6)
   - `YEMRE HTF: 4H BOS BULL`
   - `YEMRE HTF: 4H CHoCH BULL`
3. **Webhook URL:** `https://abc-xyz.trycloudflare.com/webhook/tradingview`
4. **Message** (aşağıdaki JSON'u kopyala):

```json
{"symbol":"{{ticker}}","interval":"{{interval}}","close":"{{close}}","message":"HTF BIAS: BULLISH | Score: {{plot_0}}/9 | KZ aktif"}
```

### 5M ENTRY alertleri (2 ayrı alert kur):

**BULL GATE:**
1. **Condition:** `YEMRE 5M ENTRY` → `YEMRE 5M: BULL GATE ✓`
2. **Webhook URL:** aynı URL
3. **Message:**
```json
{"symbol":"{{ticker}}","interval":"{{interval}}","close":"{{close}}","sl":"{{plot_2}}","tp":"{{plot_3}}","message":"BULL GATE ✓ | Score:{{plot_0}}/10 | Entry:{{close}} | SL:{{plot_2}} | TP:{{plot_3}}"}
```

**BEAR GATE:**
1. **Condition:** `YEMRE 5M ENTRY` → `YEMRE 5M: BEAR GATE ✓`
2. **Webhook URL:** aynı URL
3. **Message:**
```json
{"symbol":"{{ticker}}","interval":"{{interval}}","close":"{{close}}","sl":"{{plot_2}}","tp":"{{plot_3}}","message":"BEAR GATE ✓ | Score:{{plot_0}}/10 | Entry:{{close}} | SL:{{plot_2}} | TP:{{plot_3}}"}
```

> `{{plot_0}}` = skor, `{{plot_2}}` = SL seviyesi, `{{plot_3}}` = TP seviyesi

---

## Adım 5 — Streamlit'te Kontrol Et

Streamlit → **Alertler** sayfası:
- Cloudflare URL otomatik görünür (yeşil kutu)
- Gelen alertler listede çıkar
- `./start_webhook.sh` kapalıysa sarı uyarı çıkar

---

## Opsiyonel: Otomatik Telegram Bildirimi

`.env` dosyasına ekle:
```
WEBHOOK_AUTO_TELEGRAM=true
```

Alert geldiğinde otomatik olarak yapılandırılmış Telegram kanalına mesaj gönderir.

---

## Alert Message Referansı

| Değişken | Açıklama |
|----------|----------|
| `{{ticker}}` | Sembol adı (ör: BTCUSDT) |
| `{{interval}}` | Zaman dilimi (ör: 5, 240) |
| `{{close}}` | Kapanış fiyatı |
| `{{plot_0}}` | İndikatör plot_0 değeri (bias score) |
| `{{time}}` | Alert zamanı |

---

## İndikatör Özeti

### YEMRE HTF BIAS (4H Grafik)
| Satır | Açıklama |
|-------|----------|
| AMD | Günlük aralıkta fiyat pozisyonu (Accum/Manip/Dist) |
| PD Zone | Haftalık Premium / Equilibrium / Discount |
| OTE | Fibonacci 61.8-78.6% optimal giriş bölgesi |
| BTC Corr | BTC ile yön uyumu |
| USDT.D | Tether dominance yönü |
| SMT | Smart Money divergence tespiti |
| 4H Struct | BOS BULL/BEAR veya CHoCH ↑/↓ (pivot tabanlı) |
| VWAP | Günlük VWAP seviyesi |
| Kill Zone | Aktif seans (London/NY/Asia) |
| Bias Score | 0-9 arası puanlama |
| Trigger | Kill Zone + Score ≥ 6 ise aktif |
| Bias | BULLISH / BEARISH / RANGING |

### YEMRE 5M ENTRY (5M/3M/1M Grafik)
| Satır | Açıklama |
|-------|----------|
| FVG / OB | Fair Value Gap veya Order Block var mı |
| IFVG CE | Inverse FVG'nin 50% seviyesine dönüş |
| 4H Align | 4H bias ile uyum (BULL OK / BEAR OK / CONFLICT) |
| KZ | Kill Zone aktif mi |
| CISD / MSB | Change in State of Delivery / Market Structure Break |
| Sweep | Likidite süpürme tespiti |
| DOL | Günlük aralıkta pozisyon (AT HIGH / MID / AT LOW) |
| Corr | Korelasyon sembolü ile uyum |
| Score | 0-10 arası giriş skoru |
| Gate | BULL GATE ✓ / BEAR GATE ✓ / GATE ✗ |

**GATE ✓ koşulları:** HTF align + Kill Zone aktif + MSB teyidi + Score ≥ 6
