import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
import xml.etree.ElementTree as ET
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# --- AYARLAR ---

# 1. Veri Çekilecek Site Bilgileri (Artık RSS Beslemesi)
TARGET_URL = "site ismi giriniz"
# Örnek: "https://www.orneksite.com/kategori/haberler"

# 2. OpenAI API Bilgileri
OPENAI_API_KEY = "BURAYA_CALISAN_OPENAI_API_ANAHTARINIZI_YAPISTIRIN"
OPENAI_PROMPT_TEMPLATE = '"{title}" için bana bir tanıtım yazısı yaz.'

# 3. WordPress Site Bilgileri
WORDPRESS_URL = "https://necatialbayrak.wordpress.com/xmlrpc.php" 
WORDPRESS_USERNAME = "necatialbayrak"
WORDPRESS_PASSWORD = "1234Neco."

# 4. Daha Önce Paylaşılan Başlıkların Kayıt Dosyası
POSTED_TITLES_FILE = "posted_titles.txt"


def get_latest_titles(rss_url):
    """Selenium ile RSS beslemesinden başlıkları çeker."""
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(rss_url)
        page_source = driver.page_source
        driver.quit()
        # XML ayrıştırma
        root = ET.fromstring(page_source)
        titles = []
        for item in root.findall('.//channel/item'):
            title_element = item.find('title')
            if title_element is not None and title_element.text:
                titles.append(title_element.text.strip())
        return titles
    except Exception as e:
        print(f"Hata (get_latest_titles, selenium): {e}")
        return []

def filter_new_titles(titles):
    """Daha önce paylaşılmamış yeni başlıkları filtreler."""
    try:
        if not os.path.exists(POSTED_TITLES_FILE):
            posted_titles = set()
        else:
            with open(POSTED_TITLES_FILE, 'r', encoding='utf-8') as f:
                posted_titles = set(line.strip() for line in f)

        new_titles = [title for title in titles if title not in posted_titles]
        return new_titles
        
    except Exception as e:
        print(f"Hata: Geçmiş başlıklar dosyası okunurken hata oluştu: {e}")
        return []

def generate_content_with_openai(title):
    """Verilen başlık için OpenAI kullanarak içerik oluşturur."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = OPENAI_PROMPT_TEMPLATE.format(title=title)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes blog posts."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Yanıtın ve içeriğin varlığını kontrol et
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            print("Hata: OpenAI'den beklenen formatta bir yanıt alınamadı.")
            return None

    except Exception as e:
        print(f"Hata: OpenAI API'sine bağlanırken hata oluştu: {e}")
        return None

def post_to_wordpress(title, content):
    """Oluşturulan içeriği WordPress'te yayınlar."""
    try:
        client = Client(WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD)
        post = WordPressPost()
        post.title = title
        post.content = content
        post.post_status = 'publish'  # 'draft' olarak da ayarlayabilirsiniz.
        
        # Etiket ve kategori de ekleyebilirsin
        # post.terms_names = {
        #     'post_tag': ['api', 'python'],
        #     'category': ['Teknoloji', 'Yazılım']
        # }

        post_id = client.call(NewPost(post))
        return post_id is not None
    except Exception as e:
        print(f"Hata: WordPress'e gönderirken hata oluştu: {e}")
        return False

def main():
    """Ana program akışı"""
    print("İşlem başlıyor...")
    
    # Adım 1: Başlıkları çek
    all_titles = get_latest_titles(TARGET_URL)
    
    if not all_titles:
        print("Siteden başlık alınamadı. İşlem durduruluyor.")
        return

    # Adım 2: Yeni başlıkları filtrele
    new_titles = filter_new_titles(all_titles)
    
    if not new_titles:
        print("Yayınlanacak yeni başlık bulunamadı.")
        return
        
    print(f"{len(new_titles)} adet yeni başlık bulundu.")
    
    # Adım 3 & 4: Her yeni başlık için içerik oluştur ve yayınla
    for title in new_titles:
        print(f'"{title}" için içerik oluşturuluyor...')
        content = generate_content_with_openai(title)
        
        if content:
            print(f'"{title}" başlıklı yazı WordPress\'e gönderiliyor...')
            success = post_to_wordpress(title, content)
            
            if success:
                # Başarılı olursa, başlığı listeye ekle
                with open(POSTED_TITLES_FILE, 'a', encoding='utf-8') as f:
                    f.write(title + '\n')
                print("Yazı başarıyla yayınlandı!")
            else:
                print(f'"{title}" başlıklı yazı yayınlanamadı.')
        else:
            print(f'"{title}" için içerik oluşturulamadı.')
            
    print("Tüm işlemler tamamlandı.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        TARGET_URL = sys.argv[1]
    else:
        TARGET_URL = input("Lütfen RSS adresini girin: ").strip()
    main() 