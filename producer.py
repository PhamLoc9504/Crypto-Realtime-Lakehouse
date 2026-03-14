import json
import time
import requests
import os
from kafka import KafkaProducer

# Cấu hình Kafka - lấy từ environment variable hoặc dùng default
kafka_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
producer = KafkaProducer(
    bootstrap_servers=[kafka_servers],
    api_version=(0, 10), 
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def get_binance_price(symbol="BTCUSDT"):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return {
        "symbol": data['symbol'],
        "price": float(data['price']),
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }

print("--- Đang bắt đầu bơm dữ liệu từ Binance vào Kafka ---")
try:
    while True:
        message = get_binance_price("BTCUSDT")
        producer.send('crypto_topic', value=message)
        print(f"Đã gửi lên Kafka: {message}")
        time.sleep(2) # Nghỉ 2 giây rồi lấy tiếp
except KeyboardInterrupt:
    print("Đã dừng bơm dữ liệu.")