#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yandex Maps Business Scraper for Kadıköy, Istanbul
Bu script Kadıköy bölgesindeki tüm işletmelerin verilerini Yandex Haritalar'dan çeker.
"""

import time
import json
import csv
import logging
import random
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests
from urllib.parse import quote, urlencode

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('yandex_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class YandexBusinessScraper:
    def __init__(self, headless: bool = True):
        """
        Yandex Maps işletme verisi çekme sınıfı
        
        Args:
            headless: Browser'ın görünür olup olmayacağı
        """
        self.headless = headless
        self.driver = None
        self.wait_time = 10
        self.businesses = []
        
    def setup_driver(self):
        """Chrome WebDriver'ı yapılandır"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_time)
            logger.info("WebDriver başarıyla başlatıldı")
            
        except Exception as e:
            logger.error(f"WebDriver başlatılırken hata: {e}")
            raise

    def search_businesses(self, query: str, location: str = "Kadıköy, İstanbul"):
        """
        Belirli bir sorgu için işletmeleri ara
        
        Args:
            query: Arama sorgusu (örn: "restoran", "kuaför", "market")
            location: Konum (varsayılan: Kadıköy, İstanbul)
        """
        try:
            # Yandex Maps arama URL'si oluştur
            search_url = f"https://yandex.com.tr/harita/11508/istanbul/?text={quote(query + ' ' + location)}"
            logger.info(f"Arama yapılıyor: {query} - {location}")
            
            self.driver.get(search_url)
            time.sleep(3)
            
            # Arama sonuçlarının yüklenmesini bekle
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='search-list-item']")))
            except TimeoutException:
                logger.warning(f"Arama sonuçları bulunamadı: {query}")
                return []
            
            businesses = []
            page_count = 0
            max_pages = 10  # Maksimum sayfa sayısı
            
            while page_count < max_pages:
                # Mevcut sayfadaki işletmeleri çek
                page_businesses = self.extract_businesses_from_page()
                if not page_businesses:
                    logger.info("Daha fazla işletme bulunamadı")
                    break
                    
                businesses.extend(page_businesses)
                logger.info(f"Sayfa {page_count + 1}: {len(page_businesses)} işletme bulundu")
                
                # Sonraki sayfaya geç
                if not self.go_to_next_page():
                    logger.info("Son sayfaya ulaşıldı")
                    break
                    
                page_count += 1
                time.sleep(random.uniform(2, 4))  # Rate limiting
            
            logger.info(f"Toplam {len(businesses)} işletme bulundu: {query}")
            return businesses
            
        except Exception as e:
            logger.error(f"İşletme arama hatası: {e}")
            return []

    def extract_businesses_from_page(self) -> List[Dict]:
        """Mevcut sayfadaki işletme verilerini çıkar"""
        businesses = []
        
        try:
            # İşletme kartlarını bul
            business_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='search-list-item']")
            
            for element in business_elements:
                try:
                    business_data = self.extract_business_data(element)
                    if business_data:
                        businesses.append(business_data)
                except Exception as e:
                    logger.warning(f"İşletme verisi çıkarılırken hata: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Sayfa verisi çıkarılırken hata: {e}")
            
        return businesses

    def extract_business_data(self, element) -> Optional[Dict]:
        """Tek bir işletmenin verilerini çıkar"""
        try:
            business = {}
            
            # İşletme adı
            try:
                name_element = element.find_element(By.CSS_SELECTOR, "[class*='search-business-snippet-view__title']")
                business['name'] = name_element.text.strip()
            except NoSuchElementException:
                business['name'] = "Bilinmiyor"
            
            # Kategori
            try:
                category_element = element.find_element(By.CSS_SELECTOR, "[class*='search-business-snippet-view__category']")
                business['category'] = category_element.text.strip()
            except NoSuchElementException:
                business['category'] = "Belirtilmemiş"
            
            # Adres
            try:
                address_element = element.find_element(By.CSS_SELECTOR, "[class*='search-business-snippet-view__address']")
                business['address'] = address_element.text.strip()
            except NoSuchElementException:
                business['address'] = "Adres bulunamadı"
            
            # Telefon
            try:
                phone_element = element.find_element(By.CSS_SELECTOR, "[class*='search-business-snippet-view__phones']")
                business['phone'] = phone_element.text.strip()
            except NoSuchElementException:
                business['phone'] = ""
            
            # Değerlendirme
            try:
                rating_element = element.find_element(By.CSS_SELECTOR, "[class*='business-rating-badge-view__rating']")
                business['rating'] = rating_element.text.strip()
            except NoSuchElementException:
                business['rating'] = ""
            
            # Yorum sayısı
            try:
                reviews_element = element.find_element(By.CSS_SELECTOR, "[class*='business-rating-badge-view__count']")
                business['review_count'] = reviews_element.text.strip()
            except NoSuchElementException:
                business['review_count'] = ""
            
            # Çalışma saatleri
            try:
                hours_element = element.find_element(By.CSS_SELECTOR, "[class*='search-business-snippet-view__working-hours']")
                business['working_hours'] = hours_element.text.strip()
            except NoSuchElementException:
                business['working_hours'] = ""
            
            return business if business.get('name') and business['name'] != "Bilinmiyor" else None
            
        except Exception as e:
            logger.warning(f"İşletme verisi çıkarma hatası: {e}")
            return None

    def go_to_next_page(self) -> bool:
        """Sonraki sayfaya geç"""
        try:
            # Sonraki sayfa butonunu bul ve tıkla
            next_button = self.driver.find_element(By.CSS_SELECTOR, "[class*='pager__button_type_next']")
            if next_button.is_enabled():
                next_button.click()
                time.sleep(3)
                return True
            return False
        except NoSuchElementException:
            return False

    def scrape_all_categories(self):
        """Tüm kategorilerde işletmeleri tara"""
        categories = [
            "restoran", "kafe", "market", "eczane", "kuaför", "berber",
            "hastane", "diş hekimi", "veteriner", "bakkal", "manav",
            "kasap", "otobüs durağı", "metro", "banka", "ATM",
            "spor salonu", "güzellik salonu", "masaj", "otel",
            "apart otel", "pansiyon", "alışveriş merkezi", "mağaza",
            "giyim", "ayakkabı", "elektronik", "telefon", "bilgisayar",
            "kitap", "kırtasiye", "oyuncak", "çiçek", "pastane",
            "fırın", "döner", "pizza", "hamburger", "çorba",
            "lahmacun", "kebap", "balık", "deniz ürünleri",
            "temizlik", "kuru temizleme", "çilingir", "elektrikçi",
            "tesisatçı", "tamirci", "oto tamiri", "oto yıkama",
            "benzin istasyonu", "oto galeri", "kiralık araç",
            "taksi", "nakliye", "kargo", "hukuk", "avukat",
            "muhasebe", "emlak", "eğitim", "kurs", "okul",
            "kreş", "anaokulu", "dershane", "müzik", "dans",
            "sanat", "fotoğraf", "video", "düğün", "organizasyon"
        ]
        
        all_businesses = []
        
        for category in categories:
            logger.info(f"Kategori taranıyor: {category}")
            businesses = self.search_businesses(category)
            all_businesses.extend(businesses)
            
            # Rate limiting - kategoriler arası bekleme
            time.sleep(random.uniform(3, 6))
        
        # Duplikatları temizle
        unique_businesses = self.remove_duplicates(all_businesses)
        logger.info(f"Toplam {len(unique_businesses)} benzersiz işletme bulundu")
        
        return unique_businesses

    def remove_duplicates(self, businesses: List[Dict]) -> List[Dict]:
        """Duplikat işletmeleri kaldır"""
        seen = set()
        unique_businesses = []
        
        for business in businesses:
            # İsim ve adres kombinasyonunu anahtar olarak kullan
            key = f"{business.get('name', '')}_{business.get('address', '')}"
            if key not in seen:
                seen.add(key)
                unique_businesses.append(business)
        
        return unique_businesses

    def save_to_json(self, businesses: List[Dict], filename: str = "kadiköy_işletmeler.json"):
        """Verileri JSON formatında kaydet"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(businesses, f, ensure_ascii=False, indent=2)
            logger.info(f"Veriler JSON olarak kaydedildi: {filename}")
        except Exception as e:
            logger.error(f"JSON kaydetme hatası: {e}")

    def save_to_csv(self, businesses: List[Dict], filename: str = "kadiköy_işletmeler.csv"):
        """Verileri CSV formatında kaydet"""
        try:
            if not businesses:
                logger.warning("Kaydedilecek veri bulunamadı")
                return
            
            fieldnames = ['name', 'category', 'address', 'phone', 'rating', 'review_count', 'working_hours']
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(businesses)
            
            logger.info(f"Veriler CSV olarak kaydedildi: {filename}")
        except Exception as e:
            logger.error(f"CSV kaydetme hatası: {e}")

    def close(self):
        """WebDriver'ı kapat"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver kapatıldı")


def main():
    """Ana fonksiyon"""
    scraper = YandexBusinessScraper(headless=True)
    
    try:
        # WebDriver'ı başlat
        scraper.setup_driver()
        
        # Tüm kategorilerde işletmeleri tara
        logger.info("Kadıköy işletme taraması başlıyor...")
        businesses = scraper.scrape_all_categories()
        
        if businesses:
            # Verileri kaydet
            scraper.save_to_json(businesses)
            scraper.save_to_csv(businesses)
            
            # Özet bilgi
            logger.info(f"Tarama tamamlandı. Toplam {len(businesses)} işletme bulundu.")
            
            # Kategori bazında dağılım
            categories = {}
            for business in businesses:
                cat = business.get('category', 'Belirtilmemiş')
                categories[cat] = categories.get(cat, 0) + 1
            
            logger.info("Kategori dağılımı:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
                logger.info(f"  {cat}: {count} işletme")
        else:
            logger.warning("Hiç işletme bulunamadı")
    
    except Exception as e:
        logger.error(f"Ana program hatası: {e}")
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()