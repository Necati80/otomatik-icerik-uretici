#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yandex İşletme Verisi Çekme Aracı - Basit Kullanım Scripti
"""

import argparse
import sys
from yandex_business_scraper import YandexBusinessScraper

def main():
    parser = argparse.ArgumentParser(description='Kadıköy İşletme Verisi Çekme Aracı')
    parser.add_argument('--kategori', '-k', type=str, 
                       help='Belirli bir kategori ara (örn: "restoran", "kuaför")')
    parser.add_argument('--hepsi', '-a', action='store_true',
                       help='Tüm kategorilerde ara')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Browser\'ı gizli modda çalıştır')
    parser.add_argument('--konum', '-l', type=str, default="Kadıköy, İstanbul",
                       help='Arama konumu (varsayılan: Kadıköy, İstanbul)')
    
    args = parser.parse_args()
    
    if not args.kategori and not args.hepsi:
        print("Hata: --kategori veya --hepsi seçeneklerinden birini belirtmelisiniz")
        parser.print_help()
        sys.exit(1)
    
    # Scraper'ı başlat
    scraper = YandexBusinessScraper(headless=args.headless)
    
    try:
        scraper.setup_driver()
        
        if args.hepsi:
            print("Tüm kategorilerde işletme taraması başlıyor...")
            businesses = scraper.scrape_all_categories()
        else:
            print(f"'{args.kategori}' kategorisinde arama yapılıyor...")
            businesses = scraper.search_businesses(args.kategori, args.konum)
        
        if businesses:
            # Dosya adlarını oluştur
            if args.kategori:
                base_name = f"kadiköy_{args.kategori.replace(' ', '_')}_işletmeler"
            else:
                base_name = "kadiköy_tüm_işletmeler"
            
            json_file = f"{base_name}.json"
            csv_file = f"{base_name}.csv"
            
            # Verileri kaydet
            scraper.save_to_json(businesses, json_file)
            scraper.save_to_csv(businesses, csv_file)
            
            print(f"\n✅ Tarama tamamlandı!")
            print(f"📊 Toplam {len(businesses)} işletme bulundu")
            print(f"💾 Veriler kaydedildi:")
            print(f"   📄 JSON: {json_file}")
            print(f"   📊 CSV: {csv_file}")
            
            # İlk 5 işletmeyi göster
            print(f"\n📋 İlk 5 işletme:")
            for i, business in enumerate(businesses[:5], 1):
                print(f"{i}. {business.get('name', 'N/A')} - {business.get('category', 'N/A')}")
                print(f"   📍 {business.get('address', 'Adres yok')}")
                if business.get('phone'):
                    print(f"   📞 {business.get('phone')}")
                print()
                
        else:
            print("❌ Hiç işletme bulunamadı")
    
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    main()