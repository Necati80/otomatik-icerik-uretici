import os
import json
import tempfile
import time
from app import get_latest_titles, filter_new_titles, generate_content_with_openai, post_to_wordpress

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        print('Ayar dosyası (settings.json) bulunamadı!')
        return None
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    data = load_settings()
    if not data:
        return
    rss_url = data.get('rss_url')
    post_count = int(data.get('post_count', 3))
    openai_key = data.get('openai_key')
    wp_url = data.get('wp_url')
    wp_user = data.get('wp_user')
    wp_pass = data.get('wp_pass')
    prompt_template = data.get('prompt_template') or '"{title}" için bana bir tanıtım yazısı yaz.'
    posted_titles_file = os.path.join(tempfile.gettempdir(), f"posted_titles_{wp_user}.txt")
    print('İşlem başlıyor...')
    time.sleep(1)
    print('RSS beslemesi okunuyor...')
    all_titles = get_latest_titles(rss_url)
    if not all_titles:
        print('Siteden başlık alınamadı. İşlem durduruluyor.')
        return
    print(f'{len(all_titles)} adet başlık RSS\'ten başarıyla çekildi.')
    time.sleep(1)
    new_titles = filter_new_titles(all_titles, posted_titles_file)
    if not new_titles:
        print('Yayınlanacak yeni başlık bulunamadı.')
        return
    print(f'{len(new_titles)} adet yeni başlık bulundu.')
    time.sleep(1)
    for title in new_titles[:post_count]:
        print(f'"{title}" için içerik oluşturuluyor...')
        content = generate_content_with_openai(title, openai_key, prompt_template)
        if content:
            print(f'"{title}" başlıklı yazı WordPress\'e gönderiliyor...')
            success = post_to_wordpress(title, content, wp_url, wp_user, wp_pass)
            if success:
                with open(posted_titles_file, 'a', encoding='utf-8') as f:
                    f.write(title + '\n')
                print('Yazı başarıyla yayınlandı!')
            else:
                print(f'"{title}" başlıklı yazı yayınlanamadı.')
        else:
            print(f'"{title}" için içerik oluşturulamadı.')
        time.sleep(1)
    print('Tüm işlemler tamamlandı.')

if __name__ == '__main__':
    main() 