import streamlit as st
from kafka import KafkaProducer
import json
import uuid
import os
import time
import pandas as pd

# Kafka Producer yapılandırması
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Paylaşılan veri hacmi içindeki dosya yolu
PROCESSED_DATA_PATH = '/data/processed_messages.jsonl'

st.title("Titanic Survival Prediction")
pclass = st.selectbox("Class", [1, 2, 3])
sex = st.selectbox("Sex", ["Erkek", "Kadın"])
title = st.selectbox("Title", ["Bay", "Hanım", "Bayan", "Usta", "Doktor", "Özgü"])
age = st.number_input("Age", min_value=1, max_value=100, value=30)
sibsp = st.number_input("Siblings/Spouses Aboard", min_value=0, max_value=10, value=0)
parch = st.number_input("Parents/Children Aboard", min_value=0, max_value=10, value=0)
embarked = st.selectbox("Embarked", ["Southampton, İngiltere", "Cherbourg, Fransa", "Queesntown, İrlanda"])

# Predict butonu
if st.button('Predict'):
    unique_id = str(uuid.uuid4())

    data = {
        "pclass": pclass,
        "sex": sex,
        "title":title,
        "age": age,
        "sibsp": sibsp,
        "parch": parch,
        "embarked": embarked,
        "request_id": unique_id
    }
    
    producer.send('to_process', value=data)
    st.write(f"Request ID: {unique_id}")

    # JSONL dosyasından işlenmiş veriyi al
    processed_data = None
    start_time = time.time()
    timeout = 60  # 60 saniye timeout süresi
    
    while (time.time() - start_time) < timeout and processed_data is None:
        if os.path.exists(PROCESSED_DATA_PATH):
            data = pd.read_json(PROCESSED_DATA_PATH, lines=True)
            if len(data[data.request_id==unique_id]) > 0:
                break
        time.sleep(1)  # Bir sonraki deneme arasında kısa bir mola ver.

    processed_data = {
        "request_id": data[data.request_id==unique_id].request_id.values[0],
        "prediction": data[data.request_id==unique_id].prediction.values[0],
        "probability": data[data.request_id==unique_id].probability.values[0]
        }

    if processed_data:
        st.write("Processed Data:", processed_data)
    else:
        st.write("No response in time, please try again.")