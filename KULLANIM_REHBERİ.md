# 📖 Kadıköy İşletme Verisi Çekme Rehberi

## 🎯 Hızlı Başlangıç

### 1️⃣ Tek Kategori Araması
En basit kullanım - belirli bir iş türünü aramak:

```bash
# Restoran arama
python3 run_scraper.py --kategori "restoran"

# Kuaför arama  
python3 run_scraper.py --kategori "kuaför"

# Market arama
python3 run_scraper.py --kategori "market"
```

### 2️⃣ Tüm İşletmeleri Çekme
Kadıköy'deki TÜM işletmeleri çekmek için:

```bash
python3 run_scraper.py --hepsi
```

⚠️ **Uyarı**: Bu işlem 2-4 saat sürebilir ve binlerce işletme bulabilir.

### 3️⃣ Demo Çalıştırma
Önce küçük bir test yapmak için:

```bash
python3 örnek_kullanım.py
```

## 📊 Çıktı Dosyaları

Her çalıştırmadan sonra şu dosyalar oluşur:

### JSON Dosyası
```
kadiköy_restoran_işletmeler.json
```
- Programatik kullanım için
- API entegrasyonları için ideal
- Tam veri yapısı korunur

### CSV Dosyası  
```
kadiköy_restoran_işletmeler.csv
```
- Excel'de açılabilir
- Analiz için uygun
- Filtreleme ve sıralama kolay

### Log Dosyası
```
yandex_scraper.log
```
- İşlem detayları
- Hata mesajları
- Performans bilgileri

## 🔧 Gelişmiş Kullanım

### Farklı Konumlar
```bash
# Üsküdar'daki restoranlar
python3 run_scraper.py -k "restoran" --konum "Üsküdar, İstanbul"

# Beşiktaş'taki kafeler
python3 run_scraper.py -k "kafe" --konum "Beşiktaş, İstanbul"
```

### Browser Görünür Modda
Debug için browser'ı görmek istiyorsanız:
```bash
python3 run_scraper.py -k "restoran" --no-headless
```

## 📋 Popüler Kategoriler

### Yeme-İçme
- `restoran` - Restoranlar
- `kafe` - Kafeler
- `pastane` - Pastaneler
- `döner` - Dönerci
- `pizza` - Pizzacı
- `hamburger` - Hamburgerci

### Hizmetler  
- `kuaför` - Kuaförler
- `berber` - Berberler
- `masaj` - Masaj salonları
- `temizlik` - Temizlik hizmetleri

### Alışveriş
- `market` - Marketler
- `eczane` - Eczaneler
- `giyim` - Giyim mağazaları
- `elektronik` - Elektronik mağazaları

### Sağlık
- `hastane` - Hastaneler
- `diş hekimi` - Diş hekimleri
- `veteriner` - Veterinerler

## ⚡ İpuçları

### Performans
- İlk çalıştırmada ChromeDriver indirilir (1-2 dakika)
- Tek kategori araması: 5-10 dakika
- İnternet hızınıza bağlı olarak değişir

### Daha İyi Sonuçlar
- Kategori adlarını Türkçe yazın
- Spesifik kategoriler daha hızlı sonuç verir
- Genel kategoriler ("işletme") çok fazla sonuç döndürür

### Veri Kalitesi
- Duplikatlar otomatik temizlenir
- Boş veriler filtrelenir
- Telefon numaraları her zaman mevcut olmayabilir

## 🚨 Sorun Giderme

### "command not found" Hatası
```bash
# Python3 yüklü mü kontrol edin
python3 --version

# Yüklü değilse:
sudo apt-get install python3
```

### ChromeDriver Hatası
```bash
# Chrome browser kurun
sudo apt-get install google-chrome-stable
```

### Boş Sonuçlar
1. İnternet bağlantısını kontrol edin
2. Kategori adını Türkçe yazın
3. Konum doğru mu kontrol edin
4. Log dosyasını inceleyin

### Çok Yavaş Çalışıyor
1. İnternet hızınızı kontrol edin
2. VPN kapatın
3. Headless modu kullanın (varsayılan)

## 📊 Örnek Sonuç Analizi

### JSON Verisi Okuma (Python)
```python
import json

# Verileri oku
with open('kadiköy_restoran_işletmeler.json', 'r', encoding='utf-8') as f:
    restoranlar = json.load(f)

# İstatistikler
print(f"Toplam restoran: {len(restoranlar)}")

# En yüksek puanlı 5 restoran
sorted_restaurants = sorted(restoranlar, 
                           key=lambda x: float(x.get('rating', 0) or 0), 
                           reverse=True)
print("En yüksek puanlı 5 restoran:")
for i, r in enumerate(sorted_restaurants[:5], 1):
    print(f"{i}. {r['name']} - {r['rating']} ⭐")
```

### Excel'de Analiz
1. CSV dosyasını Excel'de açın
2. "Veri" → "Filtre" ile filtreleme yapın
3. Puanlara göre sıralayın
4. Grafik oluşturun

## 🔒 Güvenlik ve Etik

### Yasal Kullanım
- ✅ Halka açık veriler çekilir
- ✅ Rate limiting uygulanır
- ✅ Respectful scraping yapılır
- ❌ Kişisel verileri toplamaz
- ❌ Yandex serverlarına zarar vermez

### Önerilen Kullanım
- Araştırma amaçlı
- Pazar analizi
- Akademik çalışmalar
- Kişisel projeler

### Önerilmeyen Kullanım
- Spam amaçlı
- Rekabetçi istihbarat
- Kitlesel pazarlama
- Telif hakkı ihlali

## 🎯 Sonuç

Bu araç sayesinde Kadıköy'deki işletmeler hakkında kapsamlı veri toplayabilirsiniz. Etik kurallara uyarak kullanın ve toplanan verileri sorumlu bir şekilde değerlendirin.

---

**📞 Destek**: Sorunlar için log dosyasını kontrol edin ve hata mesajlarını inceleyin.