FROM python:3.8-slim

# Çalışma dizini oluştur
WORKDIR /app

# Gerekli Python paketlerini yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Consumer scriptini kopyala
COPY kafka_consumer.py .

# Consumer scriptini çalıştır
CMD ["python", "kafka_consumer.py"]