from flask import Flask, render_template, Response, request, stream_with_context
import os
import requests
from openai import OpenAI
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
import xml.etree.ElementTree as ET
import time
import tempfile
from apscheduler.schedulers.background import BackgroundScheduler
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import logging

# Flask uygulamasını başlat
app = Flask(__name__)

# --- PARAMETRELİ İŞ MANTIĞI FONKSİYONLARI ---

def get_latest_titles(rss_url):
    """Selenium ile RSS beslemesinden başlıkları çeker."""
    try:
        chromedriver_autoinstaller.install()
        options = Options()
        options.binary_location = "/usr/bin/google-chrome"
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--single-process")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=tr")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(rss_url)
        page_source = driver.page_source
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.quit()
        logging.info("Sayfa kaynağı ilk 1000 karakter: %s", page_source[:1000])
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

def filter_new_titles(titles, posted_titles_file):
    """Daha önce paylaşılmamış yeni başlıkları filtreler."""
    try:
        if not os.path.exists(posted_titles_file):
            return titles
        with open(posted_titles_file, 'r', encoding='utf-8') as f:
            posted_titles = set(line.strip() for line in f)
        new_titles = [title for title in titles if title not in posted_titles]
        return new_titles
    except Exception as e:
        print(f"Hata (filter_new_titles): {e}")
        return []

def generate_content_with_openai(title, openai_key, prompt_template):
    """Verilen başlık için OpenAI kullanarak içerik oluşturur."""
    try:
        prompt = prompt_template.format(title=title)
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen blog yazılarını oluşturan yardımcı bir asistansın."},
                {"role": "user", "content": prompt}
            ]
        )
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        return None
    except Exception as e:
        print(f"Hata (generate_content_with_openai): {e}")
        return None

def get_wordpress_xmlrpc_url(site_url):
    site_url = site_url.rstrip('/')
    if not site_url.endswith('xmlrpc.php'):
        return site_url + '/xmlrpc.php'
    return site_url

def post_to_wordpress(title, content, wp_url, wp_user, wp_pass):
    """Oluşturulan içeriği WordPress'te yayınlar."""
    try:
        wp_url = get_wordpress_xmlrpc_url(wp_url)
        client = Client(wp_url, wp_user, wp_pass)
        post = WordPressPost()
        post.title = title  # type: ignore
        post.content = content  # type: ignore
        post.post_status = 'publish'  # type: ignore
        post_id = client.call(NewPost(post))
        return post_id is not None
    except Exception as e:
        print(f"Hata (post_to_wordpress): {e}")
        return False

def get_page_source(rss_url):
    chromedriver_autoinstaller.install()  # Otomatik chromedriver kurulumu
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=tr")
    options.add_argument("--single-process")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(rss_url)
    page_source = driver.page_source

    # Render loglarında incelemek için kaydet
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(page_source)

    driver.quit()
    logging.info("Sayfa kaynağı ilk 1000 karakter: %s", page_source[:1000])
    return page_source

def test_access(url):
    try:
        response = requests.get(url, timeout=10)
        print("Status code:", response.status_code)
        print("Content (ilk 200 karakter):", response.text[:200])
    except Exception as e:
        print("Hata:", e)

# --- WEB ARAYÜZÜ İÇİN YENİ FONKSİYONLAR ---

@app.route('/')
def index():
    """Ana sayfayı (index.html) render eder."""
    return render_template('index.html')

def save_settings(data):
    wp_user = data.get('wp_user')
    if not wp_user:
        return
    settings_file = os.path.join(os.path.dirname(__file__), f'settings_{wp_user}.json')
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_settings(wp_user):
    settings_file = os.path.join(os.path.dirname(__file__), f'settings_{wp_user}.json')
    if not os.path.exists(settings_file):
        return None
    with open(settings_file, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/run', methods=['POST'])
def run_script():
    data = request.get_json()
    # Bilgileri kullanıcıya özel dosyaya kaydet
    save_settings(data)
    return run_script_with_data(data)

def run_script_with_data(data):
    rss_url = data.get('rss_url')
    post_count = int(data.get('post_count', 3))
    openai_key = data.get('openai_key')
    wp_url = data.get('wp_url')
    wp_user = data.get('wp_user')
    wp_pass = data.get('wp_pass')
    prompt_template = data.get('prompt_template') or '"{title}" için bana bir tanıtım yazısı yaz.'
    posted_titles_file = os.path.join(tempfile.gettempdir(), f"posted_titles_{wp_user}.txt")
    def generate_logs():
        yield "İşlem başlıyor...\n"
        time.sleep(1)
        yield "RSS beslemesi okunuyor...\n"
        all_titles = get_latest_titles(rss_url)
        if not all_titles:
            yield "Siteden başlık alınamadı. İşlem durduruluyor.\n"
            return
        yield f"{len(all_titles)} adet başlık RSS'ten başarıyla çekildi.\n"
        time.sleep(1)
        new_titles = filter_new_titles(all_titles, posted_titles_file)
        if not new_titles:
            yield "Yayınlanacak yeni başlık bulunamadı.\n"
            return
        yield f"{len(new_titles)} adet yeni başlık bulundu.\n"
        time.sleep(1)
        for title in new_titles[:post_count]:
            yield f'"{title}" için içerik oluşturuluyor...\n'
            content = generate_content_with_openai(title, openai_key, prompt_template)
            if content:
                yield f'"{title}" başlıklı yazı WordPress\'e gönderiliyor...\n'
                success = post_to_wordpress(title, content, wp_url, wp_user, wp_pass)
                if success:
                    with open(posted_titles_file, 'a', encoding='utf-8') as f:
                        f.write(title + '\n')
                    yield "Yazı başarıyla yayınlandı!\n"
                else:
                    yield f'"{title}" başlıklı yazı yayınlanamadı.\n'
            else:
                yield f'"{title}" için içerik oluşturulamadı.\n'
            time.sleep(1)
        yield "Tüm işlemler tamamlandı.\n"
    return Response(stream_with_context(generate_logs()), mimetype='text/plain')

# Otomatik görev fonksiyonu

def scheduled_job():
    data = load_settings(None)
    if data:
        print("[APScheduler] Otomatik görev başlatıldı.")
        # Otomatik görevde loglar terminale yazılır
        for log in run_script_with_data(data).response:
            print(log.decode('utf-8') if isinstance(log, bytes) else log, end='')
    else:
        print("[APScheduler] Ayar dosyası bulunamadı, otomatik görev çalışmadı.")

# Scheduler başlat
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, 'interval', hours=24, id='auto_post_job', replace_existing=True)
scheduler.start()

@app.route("/test-access")
def test_access_route():
    results = []
    for url in [
        "https://www.google.com",
        "https://www.bbc.com",
        "https://jsonplaceholder.typicode.com/posts/1"
    ]:
        try:
            response = requests.get(url, timeout=10)
            results.append(f"{url} - Status code: {response.status_code}")
        except Exception as e:
            results.append(f"{url} - Hata: {e}")
    return "<br>".join(results)

if __name__ == "__main__":
    test_access("https://www.google.com")
    test_access("https://www.bbc.com")
    test_access("https://jsonplaceholder.typicode.com/posts/1")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port) 