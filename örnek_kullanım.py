#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Örnek Kullanım - Yandex İşletme Verisi Çekme
Bu script basit bir örnek kullanımı gösterir
"""

from yandex_business_scraper import YandexBusinessScraper
import time

def demo_scraper():
    """Scraper demo fonksiyonu"""
    print("🚀 Yandex İşletme Verisi Çekme Demo")
    print("=" * 50)
    
    # Scraper'ı başlat (headless=False ile browser'ı görebilirsiniz)
    scraper = YandexBusinessScraper(headless=True)
    
    try:
        print("📱 WebDriver başlatılıyor...")
        scraper.setup_driver()
        
        # Örnek arama: Kadıköy'deki kafeler
        print("☕ Kadıköy'deki kafeleri arıyorum...")
        cafes = scraper.search_businesses("kafe", "Kadıköy, İstanbul")
        
        if cafes:
            print(f"✅ {len(cafes)} kafe bulundu!")
            
            # İlk 3 kafeyi göster
            print("\n📋 Bulunan kafeler (ilk 3):")
            for i, cafe in enumerate(cafes[:3], 1):
                print(f"\n{i}. {cafe.get('name', 'İsim yok')}")
                print(f"   📍 {cafe.get('address', 'Adres yok')}")
                print(f"   📞 {cafe.get('phone', 'Telefon yok')}")
                print(f"   ⭐ {cafe.get('rating', 'Değerlendirme yok')}")
                
            # Verileri kaydet
            scraper.save_to_json(cafes, "demo_kafeler.json")
            scraper.save_to_csv(cafes, "demo_kafeler.csv")
            print(f"\n💾 Veriler kaydedildi:")
            print(f"   📄 demo_kafeler.json")
            print(f"   📊 demo_kafeler.csv")
            
        else:
            print("❌ Hiç kafe bulunamadı")
            
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        
    finally:
        print("\n🔒 Browser kapatılıyor...")
        scraper.close()
        print("✅ Demo tamamlandı!")

if __name__ == "__main__":
    demo_scraper()