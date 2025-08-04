# Yandex Maps İşletme Verisi Çekme Aracı

Bu araç, Yandex Haritalar'dan Kadıköy, İstanbul bölgesindeki işletmelerin verilerini otomatik olarak çekmenizi sağlar.

## 🚀 Özellikler

- **Kapsamlı Veri Çekme**: İşletme adı, kategori, adres, telefon, değerlendirme, yorum sayısı ve çalışma saatleri
- **Çoklu Kategori Desteği**: 60+ farklı kategoride arama
- **Duplikat Temizleme**: Aynı işletmelerin tekrarını önler
- **Çoklu Format**: JSON ve CSV formatında dışa aktarma
- **Rate Limiting**: Yandex'in anti-bot sistemlerine karşı koruma
- **Detaylı Loglama**: İşlem takibi ve hata ayıklama

## 📦 Kurulum

Gerekli kütüphaneler zaten `requirements.txt` dosyasında mevcut:

```bash
pip install -r requirements.txt
```

## 🔧 Kullanım

### 1. Belirli Bir Kategori İçin Arama

```bash
# Restoran araması
python run_scraper.py --kategori "restoran"

# Kuaför araması
python run_scraper.py -k "kuaför"

# Eczane araması farklı konumda
python run_scraper.py -k "eczane" --konum "Üsküdar, İstanbul"
```

### 2. Tüm Kategorilerde Arama

```bash
# Tüm kategorilerde kapsamlı tarama
python run_scraper.py --hepsi
```

### 3. Doğrudan Python Scripti

```bash
# Ana scraper'ı direkt çalıştır
python yandex_business_scraper.py
```

### 4. Parametreler

- `--kategori, -k`: Belirli kategori araması (örn: "restoran", "kuaför")
- `--hepsi, -a`: Tüm kategorilerde arama yap
- `--konum, -l`: Arama konumu (varsayılan: "Kadıköy, İstanbul")
- `--headless`: Browser'ı gizli modda çalıştır (varsayılan: True)

## 📊 Çıktı Formatları

### JSON Dosyası Örneği
```json
[
  {
    "name": "Örnek Restoran",
    "category": "Restoran",
    "address": "Moda Cad. No:123, Kadıköy/İstanbul",
    "phone": "+90 216 XXX XX XX",
    "rating": "4.5",
    "review_count": "127 yorum",
    "working_hours": "09:00-23:00"
  }
]
```

### CSV Dosyası
Aynı veriler CSV formatında, Excel'de açılabilir formatta kaydedilir.

## 📋 Desteklenen Kategoriler

- **Yeme-İçme**: restoran, kafe, pastane, fırın, döner, pizza
- **Sağlık**: hastane, eczane, diş hekimi, veteriner
- **Güzellik**: kuaför, berber, güzellik salonu, masaj
- **Alışveriş**: market, mağaza, giyim, elektronik, kitap
- **Ulaşım**: otobüs durağı, metro, taksi, oto tamiri
- **Finans**: banka, ATM, muhasebe
- **Eğitim**: okul, kurs, dershane
- **Ve 40+ kategori daha...

## 🔍 Çıktı Dosyaları

Script çalıştığında aşağıdaki dosyalar oluşturulur:

- `kadiköy_[kategori]_işletmeler.json` - JSON formatında veriler
- `kadiköy_[kategori]_işletmeler.csv` - CSV formatında veriler  
- `yandex_scraper.log` - Detaylı işlem logları

## ⚠️ Önemli Notlar

### Yasal Uyarı
- Bu araç sadece halka açık bilgileri toplar
- Yandex'in hizmet şartlarına uygun kullanın
- Ticari kullanım öncesi yasal danışmanlık alın
- Rate limiting ile respectful scraping yapılır

### Teknik Detaylar
- Chrome WebDriver kullanır (otomatik indirilir)
- Headless modda çalışır (gizli browser)
- Anti-bot korumasına karşı rastgele gecikmeler
- Duplikat verileri otomatik temizler

### Performans
- Tek kategori: ~5-10 dakika
- Tüm kategoriler: ~2-4 saat
- Ortalama 1000-5000 işletme (kategoriye göre değişir)

## 🛠️ Sorun Giderme

### ChromeDriver Hatası
```bash
# Chrome browser kurulu değilse
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

### Timeout Hataları
- İnternet bağlantınızı kontrol edin
- VPN kullanıyorsanız kapatmayı deneyin
- Script'teki `wait_time` değerini artırın

### Boş Sonuçlar
- Kategori adını Türkçe karakterlerle yazın
- Konum parametresini kontrol edin
- Log dosyasından detaylı hata mesajlarını inceleyin

## 📈 İyileştirme Önerileri

1. **Proxy Kullanımı**: Büyük veri çekme işlemleri için proxy rotasyonu
2. **Veritabanı Entegrasyonu**: SQLite/PostgreSQL desteği
3. **GUI Arayüz**: Kullanıcı dostu grafik arayüz
4. **Zamanlama**: Cron job ile otomatik güncellemeler

## 🤝 Katkıda Bulunma

Bu araç açık kaynak ruhuyla geliştirilmiştir. İyileştirme önerileri:

- CSS selector güncellemeleri
- Yeni veri alanları ekleme
- Hata yönetimi iyileştirmeleri
- Performans optimizasyonları

## 📞 Destek

Sorunlar için:
1. Log dosyasını kontrol edin (`yandex_scraper.log`)
2. Console çıktısını inceleyin
3. GitHub issues kısmından bildirim yapın

---

**Not**: Bu araç eğitim ve araştırma amaçlıdır. Kullanımdan doğabilecek sorumluluk kullanıcıya aittir.