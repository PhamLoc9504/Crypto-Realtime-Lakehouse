# 🚀 Real-time Crypto Data Platform (Medallion Architecture)

Project này xây dựng một hệ thống xử lý dữ liệu thời gian thực cho giá Bitcoin, áp dụng kiến trúc Medallion (Lakehouse) với Docker.

## 🏗 Kiến trúc hệ thống

### **Producer**
- Lấy dữ liệu từ Binance API và đẩy vào Kafka
- Tự động fetch giá BTC/USDT mỗi 5 giây
- Format dữ liệu theo chuẩn JSON

### **Kafka & Zookeeper**
- Hệ thống Message Broker điều phối dữ liệu
- Kafka port nội bộ: `29092`, port external: `9092`
- Topic: `crypto_topic`
- Kafka UI available tại `localhost:8080`

### **Consumer**
- Hút dữ liệu từ Kafka và lưu vào tầng Bronze (PostgreSQL)
- Xử lý real-time streaming data
- Auto-reconnect khi mất kết nối

### **ELT Job**
- Xử lý và chuyển đổi dữ liệu qua các tầng:
  - **Bronze**: Dữ liệu thô từ Kafka
  - **Silver**: Dữ liệu đã làm sạch, xử lý trùng lặp và tính toán SMA
  - **Gold**: Dữ liệu tổng hợp theo giờ để báo cáo
- Chạy mỗi 60 giây để tổng hợp dữ liệu

### **Dashboard**
- Hiển thị trực quan bằng Streamlit (giờ Việt Nam GMT+7)
- Real-time metrics và charts
- SMA 10 lines cho phân tích kỹ thuật
- Responsive design với dark theme

## 🛠 Công nghệ sử dụng

- **Language**: Python (pandas, psycopg2, kafka-python, streamlit, plotly)
- **Database**: PostgreSQL 15
- **Infrastructure**: Docker & Docker Compose
- **Streaming**: Apache Kafka 7.4.0
- **API**: Binance REST API
- **Visualization**: Plotly Express + Streamlit

## ⚡ Cách chạy nhanh

```bash
# Clone repository
git clone <your-repo-link>
cd DE_CANG

# Khởi động toàn bộ hệ thống
docker compose up --build -d

# Kiểm tra status containers
docker compose ps

# Truy cập các services:
# Dashboard: http://localhost:8501
# Kafka UI: http://localhost:8080
# DBeaver: localhost:5432 (user: loc_admin, password: password123)
```

## 📊 Kiến trúc Medallion

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Binance API   │───▶│    Kafka     │───▶│   PostgreSQL    │
│                │    │              │    │                 │
│ - BTC/USDT     │    │ - crypto_topic│    │ - Bronze Layer  │
│ - Real-time     │    │ - Partitions │    │ - Silver Layer  │
└─────────────────┘    └──────────────┘    │ - Gold Layer    │
                                         └─────────────────┘
                                                │
                                                ▼
                                        ┌─────────────────┐
                                        │   Streamlit    │
                                        │   Dashboard    │
                                        │                │
                                        │ - Real-time     │
                                        │ - SMA 10       │
                                        │ - GMT+7        │
                                        └─────────────────┘
```

## 🗂 Database Schema

### Bronze Layer (`crypto_prices`)
```sql
CREATE TABLE crypto_prices (
    symbol VARCHAR(50),
    price NUMERIC,
    trade_time TIMESTAMP
);
```

### Silver Layer (`crypto_prices_cleaned`)
```sql
CREATE TABLE crypto_prices_cleaned (
    symbol VARCHAR(50),
    price NUMERIC,
    trade_time TIMESTAMP,
    PRIMARY KEY (symbol, trade_time)
);
```

### Gold Layer (`crypto_hourly_stats`)
```sql
CREATE TABLE crypto_hourly_stats (
    symbol VARCHAR(50),
    hour_timestamp TIMESTAMP,
    avg_price NUMERIC,
    max_price NUMERIC,
    min_price NUMERIC,
    total_records INTEGER,
    PRIMARY KEY (symbol, hour_timestamp)
);
```

## 🔧 Configuration

### Environment Variables
- `DB_HOST`: postgres (default)
- `KAFKA_BOOTSTRAP_SERVERS`: kafka:29092 (default)

### Ports
- **Streamlit Dashboard**: 8501
- **Kafka**: 9092
- **PostgreSQL**: 5432
- **Kafka UI**: 8080

## 📝 Features

### Dashboard Features
- ✅ Real-time price updates (2s refresh)
- ✅ SMA 10 technical indicator
- ✅ Vietnam timezone (GMT+7)
- ✅ Responsive dark theme
- ✅ Multi-layer data visualization
- ✅ Error handling and status messages

### Data Pipeline Features
- ✅ Auto-retry for API failures
- ✅ Duplicate data handling
- ✅ Real-time streaming
- ✅ Automated ELT processing
- ✅ Data quality checks

## 🐛 Troubleshooting

### Common Issues

1. **Kafka Connection Error**
   ```bash
   docker compose restart kafka producer consumer
   ```

2. **Dashboard Not Updating**
   ```bash
   # Check producer logs
   docker logs producer
   
   # Check consumer logs  
   docker logs consumer
   
   # Check ELT job logs
   docker logs elt_job
   ```

3. **Database Connection Issues**
   ```bash
   # Restart postgres
   docker compose restart postgres
   
   # Check if tables exist
   docker exec -it postgres psql -U loc_admin -d crypto_dw -c "\dt"
   ```

4. **Streamlit Duplicate Element ID**
   - Dashboard tự động restart với unique keys
   - Issue đã được fix trong version mới

## 📈 Monitoring

### Health Checks
```bash
# Check all containers
docker compose ps

# View real-time logs
docker compose logs -f producer consumer elt_job dashboard

# Check Kafka topics
docker exec kafka kafka-topics --bootstrap-server kafka:29092 --list
```

### Performance Metrics
- Producer: ~200 messages/minute
- Consumer: Real-time processing
- Dashboard: 2-second refresh rate
- ELT Job: 60-second intervals

## 🚀 Future Enhancements

- [ ] Add more crypto pairs (ETH, BNB, etc.)
- [ ] Implement alert system for price changes
- [ ] Add more technical indicators (RSI, MACD)
- [ ] Data retention policies
- [ ] Backup and recovery mechanisms
- [ ] Performance monitoring dashboard

## 📞 Contact

Project developed by Lộc - Real-time Data Engineering Pipeline
- Architecture: Medallion Lakehouse
- Technology: Docker + Kafka + PostgreSQL + Streamlit
- Features: Real-time processing + Technical Analysis

---

**⚡ Quick Start Command:**
```bash
docker compose up --build -d && echo "Dashboard ready at http://localhost:8501"
```
