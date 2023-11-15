from kafka import KafkaConsumer
import json
import os

def kafka_consumer_job():
    consumer = KafkaConsumer(
        'processed_topic',
        bootstrap_servers=['kafka:9092'],
        auto_offset_reset='latest',
        group_id='streamlit-consumer-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    # Veri dosyasının yazılacağı klasörü oluştur
    os.makedirs('/data', exist_ok=True)

    for message in consumer:
        with open('/data/processed_messages.jsonl', 'a') as file:
            file.write(json.dumps(message.value) + '\n')

if __name__ == "__main__":
    kafka_consumer_job()