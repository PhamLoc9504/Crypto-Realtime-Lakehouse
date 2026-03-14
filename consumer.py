import json
import psycopg2
import os
from kafka import KafkaConsumer

# 1. Cấu hình kết nối Postgres
db_host = os.environ.get('DB_HOST', 'postgres')
conn = psycopg2.connect(
    host=db_host,
    database="crypto_dw",
    user="loc_admin",
    password="password123",
    port="5432"
)
cursor = conn.cursor()

kafka_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
consumer = KafkaConsumer(
    'crypto_topic',
    bootstrap_servers=[kafka_servers],
    auto_offset_reset='earliest',
    api_version=(0, 10),  
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)
print("🚀 Consumer đang đợi dữ liệu từ Kafka để đẩy vào Postgres...")

try:
    for message in consumer:
        data = message.value
        
       
        insert_query = """
        INSERT INTO crypto_prices (symbol, price, trade_time)
        VALUES (%s, %s, %s)
        """
        
        cursor.execute(insert_query, (data['symbol'], data['price'], data['timestamp']))
        conn.commit() 
        
        print(f"✅ Đã lưu vào Postgres: {data['symbol']} - {data['price']} - {data['timestamp']}")

except Exception as e:
    print(f"🔥 Lỗi rồi Lộc ơi: {e}")
finally:
    cursor.close()
    conn.close()