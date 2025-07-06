FROM python:3.10-slim

# Sistem bağımlılıklarını yükle
RUN apt-get update && \
    apt-get install -y wget unzip \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# Python bağımlılıklarını yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Port ayarla
ENV PORT=10000
EXPOSE 10000

# Uygulamayı başlat
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"] 