from flask import Flask, request, jsonify, render_template, redirect, url_for
import cloudscraper
import xml.etree.ElementTree as ET
from openai import OpenAI
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
import os

app = Flask(__name__)

# --- HEADER AYARLARI ---
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.google.com/"
}

# --- YARDIMCI FONKSİYONLAR ---
def get_titles_from_rss(rss_url, posted_titles_file):
    scraper = cloudscraper.create_scraper(
        browser={
            'custom': DEFAULT_HEADERS["User-Agent"]
        }
    )
    response = scraper.get(rss_url, headers=DEFAULT_HEADERS)
    response.encoding = "utf-8"
    titles = []
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        for item in root.findall(".//item"):
            title_element = item.find("title")
            if title_element is not None and title_element.text:
                titles.append(title_element.text)
    # Mükerrer başlıkları filtrele
    if os.path.exists(posted_titles_file):
        with open(posted_titles_file, "r", encoding="utf-8") as f:
            posted = set(line.strip() for line in f)
        titles = [t for t in titles if t not in posted]
    return titles

def generate_content_with_openai(title, api_key, prompt_template):
    client = OpenAI(api_key=api_key)
    prompt = prompt_template.format(title=title)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen blog yazılarını oluşturan yardımcı bir asistansın."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def post_to_wordpress(title, content, wp_url, wp_user, wp_pass):
    # xmlrpc.php ekle
    if not wp_url.endswith("xmlrpc.php"):
        if not wp_url.endswith("/"):
            wp_url += "/"
        wp_url += "xmlrpc.php"
    client = Client(wp_url, wp_user, wp_pass)
    post = WordPressPost()
    post.title = title
    post.content = content
    post.post_status = 'publish'
    post_id = client.call(NewPost(post))
    return post_id

# --- ARAYÜZ ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Formdan gelen verileri al
        rss_url = request.form.get("rss_url")
        openai_key = request.form.get("openai_key")
        post_count = request.form.get("post_count")
        wp_url = request.form.get("wp_url")
        wp_user = request.form.get("wp_user")
        wp_pass = request.form.get("wp_pass")
        prompt_template = request.form.get("prompt_template")
        # Sonuçları göstermek için /result sayfasına yönlendir
        return redirect(url_for("result",
            rss_url=rss_url,
            openai_key=openai_key,
            post_count=post_count,
            wp_url=wp_url,
            wp_user=wp_user,
            wp_pass=wp_pass,
            prompt_template=prompt_template
        ))
    return render_template("index.html")

@app.route("/result")
def result():
    # Parametreleri al
    rss_url = request.args.get("rss_url")
    openai_key = request.args.get("openai_key")
    post_count = int(request.args.get("post_count", 3))
    wp_url = request.args.get("wp_url")
    wp_user = request.args.get("wp_user")
    wp_pass = request.args.get("wp_pass")
    prompt_template = request.args.get("prompt_template", "{title} için bana bir tanıtım yazısı yaz.")
    posted_titles_file = "posted_titles.txt"

    if not all([rss_url, openai_key, wp_url, wp_user, wp_pass]):
        return render_template("result.html", results=[{"status": "error", "error": "Eksik parametre!"}])

    titles = get_titles_from_rss(rss_url, posted_titles_file)
    if not titles:
        return render_template("result.html", results=[{"status": "error", "error": "Yeni başlık bulunamadı!"}])

    results = []
    for title in titles[:post_count]:
        try:
            content = generate_content_with_openai(title, openai_key, prompt_template)
            post_id = post_to_wordpress(title, content, wp_url, wp_user, wp_pass)
            results.append({"title": title, "status": "ok", "post_id": post_id})
            # Başlığı kaydet
            with open(posted_titles_file, "a", encoding="utf-8") as f:
                f.write(title + "\n")
        except Exception as e:
            results.append({"title": title, "status": "error", "error": str(e)})

    return render_template("result.html", results=results)

# --- API (JSON) ---
@app.route("/auto-post", methods=["POST"])
def auto_post():
    data = request.json
    rss_url = data.get("rss_url")
    api_key = data.get("openai_key")
    post_count = int(data.get("post_count", 3))
    wp_url = data.get("wp_url")
    wp_user = data.get("wp_user")
    wp_pass = data.get("wp_pass")
    prompt_template = data.get("prompt_template", "{title} için bana bir tanıtım yazısı yaz.")
    posted_titles_file = "posted_titles.txt"

    if not all([rss_url, api_key, wp_url, wp_user, wp_pass]):
        return jsonify({"error": "Eksik parametre!"}), 400

    titles = get_titles_from_rss(rss_url, posted_titles_file)
    if not titles:
        return jsonify({"error": "Yeni başlık bulunamadı!"}), 400

    results = []
    for title in titles[:post_count]:
        try:
            content = generate_content_with_openai(title, api_key, prompt_template)
            post_id = post_to_wordpress(title, content, wp_url, wp_user, wp_pass)
            results.append({"title": title, "status": "ok", "post_id": post_id})
            # Başlığı kaydet
            with open(posted_titles_file, "a", encoding="utf-8") as f:
                f.write(title + "\n")
        except Exception as e:
            results.append({"title": title, "status": "error", "error": str(e)})

    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 