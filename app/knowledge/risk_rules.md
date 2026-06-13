# Risk Yönetimi Kuralları

## Temel Risk Parametreleri

- **Maksimum risk/işlem**: Hesabın %1-2'si
- **Günlük maksimum kayıp**: Hesabın %3'ü (bu noktada işlem durur)
- **Haftalık maksimum kayıp**: Hesabın %6'sı
- **Minimum R/R**: 1:2 (TP en az SL'nin 2 katı mesafede)
- **İdeal R/R**: 1:3 veya üzeri

## Pozisyon Büyüklüğü Hesaplama

```
Lot = (Hesap * Risk%) / (Stop Mesafesi * Pip Değeri)
```

### XAUUSD (Altın)
- Pip değeri: 1 pip = $10 (standart lot)
- Minimum FVG: 3 dolar
- Maksimum stop: 15-20 dolar

### BTCUSDT
- Risk mesafesi: fiyat bazlı
- Minimum stop: %0.5

### Forex Majörler
- Pip değeri çiftlere göre değişir
- EUR/USD: 1 pip = $10 (standart lot)

## Pozisyon Yönetimi

- **TP1** kırıldıktan sonra: Stop loss başa alınır (BE)
- **TP2** kırıldıktan sonra: Pozisyonun %50'si kapatılır
- **TP3**: Kalan pozisyonun kapatılması veya trailing stop

## Açık Pozisyon Yönetimi

- Aynı anda maksimum 3 açık pozisyon
- Korelasyonlu varlıklarda (BTC + altcoin) aynı yönde pozisyon riski ikiye katlar
- Haberden önce açık pozisyon varsa stop sıkıştırılabilir veya pozisyon azaltılabilir

## Günlük Limitlere Ulaşınca

- %3 günlük kayıptan sonra o gün işlem yapılmaz
- Sisteme log kaydedilir
- Telegram'a "günlük limit, işlem durdu" notu gönderilir
