import psycopg2
import time
import os
from dotenv import load_dotenv

load_dotenv()

def run_full_elt():
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"), 
            database="crypto_dw",
            user="loc_admin",
            password="password123",
            port="5432"
        )
        cursor = conn.cursor()

        # 1. BRONZE -> SILVER (Làm sạch)
        query_bronze_to_silver = """
        INSERT INTO crypto_prices_cleaned (symbol, price, trade_time)
        SELECT symbol, price, trade_time 
        FROM crypto_prices
        WHERE price > 0 AND trade_time IS NOT NULL
        ON CONFLICT (symbol, trade_time) DO NOTHING;
        """

        # 2. SILVER -> GOLD (Tổng hợp số liệu)
        query_silver_to_gold = """
        INSERT INTO crypto_hourly_stats (symbol, hour_timestamp, avg_price, max_price, min_price, total_records)
        SELECT 
            symbol, 
            date_trunc('hour', trade_time) as hour_timestamp,
            AVG(price), MAX(price), MIN(price), COUNT(*)
        FROM crypto_prices_cleaned
        GROUP BY symbol, hour_timestamp
        ON CONFLICT (symbol, hour_timestamp) 
        DO UPDATE SET 
            avg_price = EXCLUDED.avg_price,
            max_price = EXCLUDED.max_price,
            min_price = EXCLUDED.min_price,
            total_records = EXCLUDED.total_records;
        """
        
        cursor.execute(query_bronze_to_silver)
        cursor.execute(query_silver_to_gold)
        conn.commit()
        print(f"✨ [ELT] Bronze -> Silver -> Gold thành công lúc {time.ctime()}")

    except Exception as e:
        print(f"🔥 Lỗi ELT: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    print("⚙️ ELT Job (Medallion Architecture) đang bắt đầu...")
    while True:
        run_full_elt()
        time.sleep(60) 