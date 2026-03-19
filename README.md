# 🚀 Real-time Crypto Data Platform (Medallion Architecture)

Project này xây dựng một hệ thống xử lý dữ liệu thời gian thực cho giá Bitcoin, áp dụng kiến trúc **Medallion (Lakehouse)** với Docker.

## 🏗 Kiến trúc hệ thống

Đây là sơ đồ kiến trúc luồng dữ liệu của hệ thống:

![Sơ đồ kiến trúc luồng dữ liệu](image\data_processing_pipeline.png)

*(Sơ đồ mô tả luồng dữ liệu từ Binance API -> Kafka -> Consumer -> Postgres (3 tầng Bronze, Silver, Gold) -> Streamlit Dashboard)*

---

## 📊 Kết quả kiểm tra dữ liệu

### 1. Dữ liệu thô (Bronze Layer)

Đây là ví dụ về dữ liệu thô được lưu trữ trong bảng `crypto_prices` (PostgreSQL) thông qua DBeaver:

![Ảnh chụp màn hình dữ liệu thô trong DBeaver](image\dbeaver_screenshot.png)

Dữ liệu bao gồm thông tin chi tiết về từng giao dịch như ký hiệu, giá, thời gian giao dịch (`trade_time`) và thời gian ghi vào hệ thống (`ingested_at`).

### 2. Dữ liệu đã làm sạch (Silver Layer)

Bảng `crypto_prices_cleaned` chứa dữ liệu đã qua xử lý:
- **Loại bỏ duplicates**: Dữ liệu trùng lặp được loại bỏ dựa trên `symbol` và `trade_time`
- **Data validation**: Các bản ghi với `price <= 0` hoặc `trade_time` null bị loại bỏ
- **Primary key constraints**: Đảm bảo tính duy nhất của dữ liệu

```sql
-- Ví dụ truy vấn Silver Layer
SELECT symbol, price, trade_time 
FROM crypto_prices_cleaned 
WHERE trade_time >= NOW() - INTERVAL '1 hour'
ORDER BY trade_time DESC 
LIMIT 10;
```

### 3. Dữ liệu tổng hợp (Gold Layer)

Bảng `crypto_hourly_stats` chứa dữ liệu tổng hợp theo giờ:
- **Aggregated metrics**: AVG, MAX, MIN price mỗi giờ
- **Business intelligence**: Served layer cho dashboard và reports
- **Performance optimized**: Truy vấn nhanh cho analytics

```sql
-- Ví dụ dữ liệu Gold Layer
| symbol | hour_timestamp     | avg_price | max_price | min_price | total_records |
|--------|-------------------|-----------|-----------|-----------|---------------|
| BTC/USDT | 2024-01-15 14:00 | 43250.25  | 43300.00  | 43200.00  | 120           |
| BTC/USDT | 2024-01-15 13:00 | 43180.50  | 43250.00  | 43100.00  | 115           |
```

---

## 🎯 Features & Capabilities

### Real-time Processing
- **Producer**: Fetch data từ Binance API mỗi 5 giây
- **Kafka Streaming**: Message broker với partitioning và replication
- **Consumer**: Real-time ingestion vào PostgreSQL
- **ELT Pipeline**: Tự động xử lý mỗi 60 giây

### Data Quality
- **Schema validation**: Kiểm tra định dạng dữ liệu đầu vào
- **Duplicate handling**: Loại bỏ dữ liệu trùng lặp
- **Data cleansing**: Filter invalid records
- **Audit trail**: Tracking thời gian ingestion

### Analytics & Visualization
- **Technical indicators**: SMA 10 cho phân tích kỹ thuật
- **Real-time dashboard**: Streamlit với 2-second refresh
- **Multi-layer views**: Bronze, Silver, Gold data visualization
- **Timezone support**: GMT+7 (Vietnam timezone)

---

## � Dashboard Features

### Overview
Dashboard **CryptoLens Analytics** là giao diện chính để theo dõi dữ liệu crypto real-time với thiết kế chuyên nghiệp và hiện đại.

### Dashboard Screenshot

#### Main Dashboard View
![Dashboard chính với metrics và charts](image\Dashboard.png)

*Giao diện chính hiển thị:*
- **KPI Metrics**: Bitcoin price real-time với delta percentages
- **Live Status**: Indicator với animation cho system status  
- **Pipeline Info**: Architecture flow visualization
- **Price Chart**: Real-time price movement với SMA 10
- **Gold Layer**: Hourly aggregations với bar charts
- **Summary Table**: Serving layer data với formatted values

### Technical Features

#### Design System
- **Professional Theme**: Light theme với DM Sans font
- **Responsive Layout**: Adaptive cho different screen sizes
- **Color Palette**: Blue/Teal/Green color scheme
- **Micro-interactions**: Hover effects và transitions

#### Performance
- **2-second Refresh**: Real-time data updates
- **Efficient Queries**: Optimized SQL cho fast loading
- **Error Handling**: Graceful degradation khi data unavailable
- **Memory Management**: Efficient data processing

#### Data Visualization
```python
# Chart configuration example
CHART_LAYOUT = dict(
    font=dict(family="DM Sans, sans-serif", size=12, color="#0F172A"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=36, b=10),
    # ... additional styling
)
```

### User Interface Components

#### Header Section
- **Logo Badge**: CryptoLens branding
- **Live Indicator**: Real-time status với animation
- **Architecture Info**: Pipeline visualization

#### Metrics Cards
- **Price Card**: Current BTC price với delta
- **Time Card**: Last update timestamp
- **Records Card**: Data count information
- **Pipeline Card**: System architecture flow

#### Chart Sections
- **Silver Layer Chart**: Price movement với SMA
- **Gold Layer Chart**: Hourly aggregations
- **Data Tables**: Formatted summary data

### Access Information
- **URL**: `http://localhost:8501`
- **Refresh Rate**: 2 seconds
- **Timezone**: GMT+7 (Vietnam)
- **Data Sources**: PostgreSQL Silver & Gold layers

### Troubleshooting Dashboard

#### Common Issues
1. **No Data Display**
   ```bash
   # Check ELT job status
   docker logs elt_job
   
   # Verify Silver layer has data
   docker exec postgres psql -U loc_admin -d crypto_dw -c "SELECT COUNT(*) FROM crypto_prices_cleaned;"
   ```

2. **Chart Not Updating**
   ```bash
   # Restart dashboard
   docker compose restart dashboard
   
   # Check browser console for errors
   ```

3. **Timezone Issues**
   ```bash
   # Verify timezone conversion in code
   df['trade_time'] = pd.to_datetime(df['trade_time']) + pd.Timedelta(hours=7)
   ```

#### Performance Optimization
- **Data Limiting**: Query only latest 100 records
- **Index Optimization**: Proper indexes on timestamp columns
- **Connection Pooling**: Efficient database connections
- **Caching Strategy**: Browser caching for static assets

---

## �🔧 Technical Implementation

### Kafka Configuration
```yaml
# Docker Compose Kafka setup
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092
KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT
KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

### Database Schema Design
```sql
-- Bronze Layer (Raw data)
CREATE TABLE crypto_prices (
    symbol VARCHAR(50),
    price NUMERIC,
    trade_time TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT NOW()
);

-- Silver Layer (Cleaned data)
CREATE TABLE crypto_prices_cleaned (
    symbol VARCHAR(50),
    price NUMERIC CHECK (price > 0),
    trade_time TIMESTAMP,
    PRIMARY KEY (symbol, trade_time)
);

-- Gold Layer (Aggregated data)
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

### ELT Logic
```sql
-- Bronze -> Silver
INSERT INTO crypto_prices_cleaned (symbol, price, trade_time)
SELECT symbol, price, trade_time 
FROM crypto_prices
WHERE price > 0 AND trade_time IS NOT NULL
ON CONFLICT (symbol, trade_time) DO NOTHING;

-- Silver -> Gold
INSERT INTO crypto_hourly_stats (symbol, hour_timestamp, avg_price, max_price, min_price, total_records)
SELECT 
    symbol, 
    date_trunc('hour', trade_time) as hour_timestamp,
    AVG(price), MAX(price), MIN(price), COUNT(*)
FROM crypto_prices_cleaned
GROUP BY symbol, hour_timestamp
ON CONFLICT (symbol, hour_timestamp) DO UPDATE SET
    avg_price = EXCLUDED.avg_price,
    max_price = EXCLUDED.max_price,
    min_price = EXCLUDED.min_price,
    total_records = EXCLUDED.total_records;
```

---

## 📈 Performance Metrics

### Throughput & Latency
- **Data ingestion**: ~200 records/minute
- **End-to-end latency**: < 10 seconds
- **Dashboard refresh**: 2 seconds
- **ELT processing**: 60 seconds intervals

### Storage Optimization
- **Compression**: PostgreSQL table compression
- **Partitioning**: Potential hourly partitioning for Gold layer
- **Retention**: Configurable data retention policies

### Monitoring & Alerting
```bash
# Health check commands
docker compose ps                    # Container status
docker logs producer                 # Producer logs
docker logs consumer                 # Consumer logs
docker logs elt_job                  # ELT job logs

# Kafka monitoring
docker exec kafka kafka-topics --bootstrap-server kafka:29092 --list
docker exec kafka kafka-consumer-groups --bootstrap-server kafka:29092 --list
```

---

## 🚀 Deployment & Operations

### Environment Setup
```bash
# Production environment variables
DB_HOST=postgres
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
POSTGRES_USER=loc_admin
POSTGRES_PASSWORD=password123
POSTGRES_DB=crypto_dw
```

### Scaling Considerations
- **Kafka partitions**: Increase for higher throughput
- **PostgreSQL**: Connection pooling, read replicas
- **Dashboard**: Multiple instances with load balancer
- **Monitoring**: Prometheus + Grafana integration

### Backup & Recovery
```bash
# Database backup
docker exec postgres pg_dump -U loc_admin crypto_dw > backup_$(date +%Y%m%d).sql

# Volume backup
docker run --rm -v de_cang_db_data_final:/data -v $(pwd):/backup alpine tar czf /backup/db_backup_$(date +%Y%m%d).tar.gz -C /data .
```

---

## � Development & Testing

### Local Development
```bash
# Start development environment
docker compose up --build

# Run tests
python -m pytest tests/

# Code formatting
black *.py
flake8 *.py
```

### Testing Strategy
- **Unit tests**: Python function testing
- **Integration tests**: Kafka + PostgreSQL integration
- **End-to-end tests**: Full pipeline testing
- **Performance tests**: Load testing for scalability

---

## 📚 Learning Outcomes

### Data Engineering Concepts
- **Medallion Architecture**: Bronze → Silver → Gold layers
- **Real-time streaming**: Kafka for message queuing
- **ELT vs ETL**: Extract, Load, Transform patterns
- **Data quality**: Validation and cleansing strategies

### Technical Skills
- **Docker orchestration**: Multi-container applications
- **Streaming data**: Real-time data processing
- **Database design**: Schema evolution and optimization
- **Visualization**: Real-time dashboard development

---

## � Future Enhancements

### Technical Improvements
- [ ] **Apache Spark**: For large-scale data processing
- [ ] **Apache Airflow**: Workflow orchestration
- [ ] **Redis**: Caching layer for performance
- [ ] **Monitoring**: Prometheus + Grafana stack

### Business Features
- [ ] **Multiple symbols**: ETH, BNB, ADA, etc.
- [ ] **Advanced indicators**: RSI, MACD, Bollinger Bands
- [ ] **Alert system**: Price movement notifications
- [ ] **API endpoints**: RESTful API for external access

### Data Science
- [ ] **Machine learning**: Price prediction models
- [ ] **Anomaly detection**: Unusual pattern recognition
- [ ] **Sentiment analysis**: Social media integration
- [ ] **Portfolio analytics**: Multi-asset tracking

---

## 📞 Support & Contributing

### Getting Help
- **Documentation**: Check this README and code comments
- **Issues**: Report bugs via GitHub Issues
- **Community**: Join discussions for feature requests

### Contributing Guidelines
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Submit Pull Request

---

**⚡ Quick Start Command:**
```bash
git clone <repository-url> && cd DE_CANG
docker compose up --build -d
echo "🚀 CryptoLens Analytics ready at http://localhost:8501"
```

*Built with ❤️ using Docker, Kafka, PostgreSQL, and Streamlit*
