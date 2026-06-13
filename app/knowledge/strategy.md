# Trading Stratejisi – Yemre AI Trading Desk

## 1. Genel Amaç

Bu sistemin amacı otomatik işlem açmak değil, trader'a strateji kurallarına göre karar destek sağlamaktır. Nihai karar her zaman kullanıcıdadır.

## 2. HTF Bias Kuralları

### Bullish Bias Şartları
- 4H swing high kırılmışsa (BOS - Break of Structure)
- 1H yapısı higher high / higher low üretiyorsa
- BTC pozitif seyrediyorsa, USDT.D düşüyorsa, Total3 yükseliyorsa
- Fiyat demand zone veya bullish Order Block üstünde tutunuyorsa
- 4H/1H kapanışlar demand bölgesinin üstündeyse

### Bearish Bias Şartları
- 4H swing low kırılmışsa (BOS - Break of Structure)
- 1H yapısı lower high / lower low üretiyorsa
- BTC negatif seyrediyorsa, USDT.D yükseliyorsa, Total3 düşüyorsa
- Fiyat supply zone veya bearish Order Block altında kalıyorsa
- 4H/1H kapanışlar supply bölgesinin altındaysa

### Ranging Piyasa
- 4H ve 1H net yön vermiyorsa
- Swing high ve swing low'lar net değilse
- Likidite her iki tarafta da yakın mesafedeyse
- Fiyat ana destek ve ana direnç arasında sıkışmışsa
- BTC, USDT.D ve Total3 birbiriyle çelişiyorsa

## 3. Order Block (OB) Kuralları

### Bullish Order Block
- Swing low'dan önce gelen son kırmızı (bearish) mum
- Bu mumun ardından güçlü, impulsif bir yükseliş hareketi gelmiş olmalı
- OB daha önce tamamen mitigate edilmemiş olmalı
- OB'nin yüksek-hacimli bir bölgede olması kaliteyi artırır

### Bearish Order Block
- Swing high'dan önce gelen son yeşil (bullish) mum
- Bu mumun ardından güçlü, impulsif bir düşüş hareketi gelmiş olmalı
- OB daha önce tamamen mitigate edilmemiş olmalı
- OB'nin yüksek-hacimli bir bölgede olması kaliteyi artırır

## 4. Fair Value Gap (FVG) Kuralları

- Üç mumlu imbalance bölgesi aranır (mum 1 high ile mum 3 low arasında boşluk)
- XAUUSD için minimum 3 dolar boşluk
- BTC için minimum %0.3 boşluk
- Altcoinler için minimum %0.5 boşluk
- Doldurulmamış FVG daha değerlidir
- FVG + OB kombinasyonu en güçlü setup'tır

## 5. Piyasa Yapısı (Market Structure)

### CHoCH (Change of Character)
- Mevcut trendin ilk kez kırıldığının işareti
- Zayıf/erken dönüş sinyali olarak değerlendirilir

### BOS (Break of Structure)
- Trend devamının güçlü teyidi
- CHoCH'tan daha güvenilir yapı kırılması

### MSB (Market Structure Break)
- LTF'de HTF bias yönünde oluşan yapı kırılması
- Giriş için tetikleyici sinyal

## 6. Makro Bağlam Kuralları

### BTC Dominance (BTC.D)
- BTC.D yükseliyorsa: altcoinler genelde negatif etkilenir
- BTC.D düşüyorsa: altcoinler genelde pozitif seyredebilir
- BTC.D ranging: alım seçici yapılmalı

### USDT.D (Tether Dominance)
- USDT.D yükseliyorsa: piyasadan para çıkıyor, bearish baskı
- USDT.D düşüyorsa: piyasaya para giriyor, bullish baskı

### Total3 (Altcoin Market Cap)
- Total3 yükseliyorsa: altcoin sezonu potansiyeli
- Total3 düşüyorsa: altcoinlerden kaçınılmalı

## 7. Likidite Analizi

- Önceki swing high'ların üzerindeki likidite (buy side liquidity)
- Önceki swing low'ların altındaki likidite (sell side liquidity)
- Fiyat genellikle likiditeyi topladıktan sonra ters yönde hareket eder
- Equal highs/lows = güçlü likidite havuzu

## 8. İşlem Alınmayacak Durumlar

- HTF bias net değilse (RANGING veya belirsiz)
- Haber öncesi/sonrası yüksek volatilite dönemlerinde (FOMC, CPI, NFP vb.)
- Fiyat ana destek ve direncin tam ortasındaysa
- Stop mesafesi çok genişse (risk/ödül 1:2'nin altındaysa)
- BTC, USDT.D ve Total3 birbirini desteklemiyorsa
- Confidence skoru 6'nın altındaysa
- OB veya FVG teyidi yoksa
- Günlük veya haftalık seviyeler çok yakınsa

## 9. Sinyal Kalitesi ve Confidence Skoru

```
8-10: Güçlü bias, setup net, VIP sinyal adayı
6-7: Orta güven, takipte tut, giriş gelmeden bekleme
4-5: Zayıf bias, kenar izle, işlem alma
1-3: Bias yok veya çelişkili, kesinlikle işlem alma
```

## 10. Timeframe Hiyerarşisi

```
HTF (High Time Frame): Haftalık, Günlük, 4H → Bias belirleme
MTF (Mid Time Frame): 1H, 30M → Yapı takibi
LTF (Low Time Frame): 15M, 5M, 3M, 1M → Giriş tetikleme
```

Kural: HTF bias'a karşı LTF'de işlem alınmaz.
