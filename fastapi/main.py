from fastapi import FastAPI
from kafka import KafkaConsumer, KafkaProducer
import pickle
import numpy as np
import json
import threading

app = FastAPI(
    title="Titanic API",
    version="0.1",
    description="Kader belirleyen servis"
)

# Model yükleme
filename = 'titanic_model.sav'
model = pickle.load(open(filename, 'rb'))

# Kafka Consumer ve Producer yapılandırması
consumer = KafkaConsumer(
    'to_process',
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='earliest',
    group_id='fastapi-consumer-group',  # Benzersiz bir grup ID
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

sex_mapping = {"Erkek": 0, "Kadın": 1}
title_mapping = {"Bay": 1, "Hanım": 2, "Bayan": 3, "Usta": 4, "Doktor": 5, "Özgü": 6}
embarked_mapping = {"Southampton, İngiltere": 1, "Cherbourg, Fransa": 2, "Queesntown, İrlanda": 3}

def process_message(message):
    # Mesajı işleyip tahmin yapma
    try:
        features = [
            message['pclass'],
            sex_mapping[message['sex']],
            message['age'],
            message['sibsp'],
            message['parch'],
            embarked_mapping[message['embarked']],
            title_mapping[message['title']]
        ]

        prediction = model.predict([features])
        proba = model.predict_proba([features])

        result_text = "Survived" if prediction[0] == 1 else "Not Survived"
        probability = proba[0][1] * 100 if prediction[0] == 1 else proba[0][0] * 100

        processed_message = {
            'request_id': message['request_id'], 
            'prediction': result_text, 
            'probability': probability
        }

    except Exception as e:
        processed_message = {'request_id': message['request_id'], 'error': str(e)}

    return processed_message

def send_to_processed_topic(processed_data):
    producer.send('processed_topic', value=processed_data)

def kafka_listener():
    for message in consumer:
        data = message.value
        processed_data = process_message(data)
        send_to_processed_topic(processed_data)

# Kafka dinleyicisini arka planda başlatma
threading.Thread(target=kafka_listener, daemon=True).start()

@app.get("/health")
def health_check():
    return {"message": "Up and Running"}
