# İşlem Alınmayacak Durumlar

Bu kurallardan herhangi biri geçerliyse sistem NO_TRADE döndürmeli.

## Kesin NO_TRADE Durumları

1. **Bias Belirsizliği**: HTF (4H/Günlük) bias net değilse, BOS/CHoCH teyidi yoksa
2. **Haber Riski**: FOMC, CPI, NFP, Fed konuşması, kripto düzenleyici haberler öncesi/sırası
3. **Çelişkili Sinyaller**: BTC, USDT.D ve Total3 birbiriyle çelişiyorsa
4. **Düşük Confidence**: AI güven skoru 5 ve altındaysa
5. **Risk/Ödül**: R/R 1:2'nin altındaysa
6. **Yapı Ortası**: Fiyat ana destek ve direnç arasının tam ortasındaysa
7. **Geniş Stop**: Stop mesafesi hesap riskinin %2'sinden fazlasını gerektiriyorsa
8. **Mitigate OB**: Hedeflenen OB daha önce tamamen test edilmişse
9. **Doldurulmuş FVG**: Hedeflenen FVG tamamen doldurulmuşsa
10. **Ters HTF**: LTF setup HTF bias'a karşı yönde oluşuyorsa

## Dikkatli Olunacak Durumlar (LOW_CONFIDENCE)

- Fiyat likidite havuzuna çok yakınsa (hunt riski)
- Haftalık veya aylık önemli seviye yakındaysa
- Piyasa saati düşük likidite dönemindeyse (Asya seansı başlangıcı)
- Son 24 saatte çok hızlı hareket varsa (aşırı alım/satım)
- Birden fazla timeframe çelişkili bilgi veriyorsa

## Sistem Yanıt Değerleri

```
NO_TRADE       → İşlem kesinlikle alınmamalı
LOW_CONFIDENCE → Dikkatli ol, setup oluşmasını bekle
BULLISH        → Long setup ara
BEARISH        → Short setup ara
RANGING        → Her iki yöne hazır ol, düşük pozisyon
```
