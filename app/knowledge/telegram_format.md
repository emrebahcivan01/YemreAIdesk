# Telegram Mesaj Formatları

## Public Analiz Formatı

```
📊 {SEMBOL} Analizi

📈 Bias: {BIAS}
🎯 Güven: {CONFIDENCE}/10

{ÖZET}

🔑 Kritik Seviyeler:
• Direnç: {DIRENÇ}
• Destek: {DESTEK}

📋 Plan:
{AKSIYON_PLANI}

⚠️ Bu analiz yatırım tavsiyesi değildir. Kendi analizinizi yapınız.
```

## VIP Sinyal Formatı

```
🚨 {SEMBOL} Sinyal #{SINYAL_NO}

Yön: {LONG/SHORT}
Bias: {BIAS} ({CONFIDENCE}/10)

📍 Giriş Bölgesi: {GIRIS}
🛑 Stop Loss: {SL}
🎯 TP1: {TP1}
🎯 TP2: {TP2}
🎯 TP3: {TP3} (varsa)

R/R: {RR}

📝 Not:
{EKSTRA_NOT}

⚠️ Yatırım tavsiyesi değildir. Risk yönetiminizi kendiniz yapınız.
```

## Haftalık Özet Formatı

```
📅 Haftalık Performans Özeti

📊 Toplam Analiz: {TOPLAM}
✅ Başarılı (TP): {TP_SAYI}
❌ Başarısız (SL): {SL_SAYI}
➡️ Başabaş (BE): {BE_SAYI}
⏭️ İşlem Alınmadı: {NO_TRADE_SAYI}

🏆 Başarı Oranı: {BASARI_ORANI}%
📈 En İyi Sembol: {EN_IYI}
📉 En Kötü Sembol: {EN_KOTU}

⚠️ Geçmiş performans gelecek sonuçları garanti etmez.
```

## Uyarı Notları

- Tüm analizlere "yatırım tavsiyesi değildir" notu eklenecek
- VIP sinyallerde her zaman stop loss belirtilecek
- R/R minimum 1:2 altındaki sinyaller gönderilmeyecek
- Yüksek volatilite dönemlerinde (FOMC, CPI vb.) özel uyarı eklenecek
