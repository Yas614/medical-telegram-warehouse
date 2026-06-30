# Medical Telegram Data Warehouse

An end-to-end ELT data engineering pipeline that extracts medical-related Telegram data, transforms it into an analytical PostgreSQL warehouse using dbt, enriches image data with YOLOv8, exposes analytics through FastAPI, and orchestrates the workflow with Dagster.

---

# Project Overview

This project was developed as part of the **10 Academy Data Engineering Challenge**. The objective is to transform unstructured Telegram data into a clean, analytics-ready warehouse capable of answering business questions about Ethiopian medical businesses.

The pipeline consists of:

- Telegram data extraction using Telethon
- Raw data lake storage
- PostgreSQL data warehouse
- dbt transformations
- YOLO image enrichment
- FastAPI analytical API
- Dagster orchestration

---

# Architecture

```text
Telegram Channels
        │
        ▼
 Telethon Scraper
        │
        ▼
 Raw JSON Data Lake
        │
        ▼
 PostgreSQL
        │
        ▼
 dbt Transformations
        │
 ┌──────┴───────┐
 ▼              ▼
YOLOv8      FastAPI
        │
        ▼
     Dagster
```

---

# Project Structure

```text
medical-telegram-warehouse/
│
├── api/
├── data/
│   ├── raw/
│   └── images/
├── logs/
├── medical_warehouse/
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
├── src/
├── scripts/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Data Lake Design

Raw Telegram data is stored using a partitioned directory structure.

### Messages

```
data/raw/telegram_messages/YYYY-MM-DD/channel_name.json
```

### Images

```
data/raw/images/channel_name/message_id.jpg
```

This structure preserves the original Telegram API response while supporting incremental loading and historical tracking.

---

# Data Warehouse

The warehouse follows a dimensional **Star Schema**.

### Fact Table

- **fct_messages**
    - message_id
    - channel_key
    - date_key
    - message_text
    - message_length
    - views
    - forwards
    - has_image

### Dimension Tables

**dim_channels**

- channel_key
- channel_name
- channel_type
- first_post_date
- last_post_date

**dim_dates**

- date_key
- full_date
- day_name
- month
- quarter
- year

---

# Technology Stack

| Layer | Technology |
|---------|------------|
| Programming | Python |
| Scraping | Telethon |
| Database | PostgreSQL |
| Transformation | dbt |
| Computer Vision | YOLOv8 |
| API | FastAPI |
| Orchestration | Dagster |
| Containers | Docker |

---

# Running the Project

Install dependencies

```bash
pip install -r requirements.txt
```

Start PostgreSQL

```bash
docker compose up -d
```

Run scraper

```bash
python src/scraper.py
```

Load raw data

```bash
python src/load_to_postgres.py
```

Execute dbt models

```bash
dbt run
dbt test
```

Start FastAPI

```bash
uvicorn api.main:app --reload
```

Launch Dagster

```bash
dagster dev
```

---

# API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/reports/top-products` | Most frequently mentioned products |
| `/api/channels/{channel}/activity` | Channel activity statistics |
| `/api/search/messages` | Keyword search |
| `/api/reports/visual-content` | Image analytics |

---

# Data Quality

dbt validation includes:

- Unique constraints
- Not-null validation
- Foreign key relationship tests
- Custom business rule tests

---

# Future Improvements

- Incremental dbt models
- Cloud deployment
- CI/CD integration
- Fine-tuned medical object detection
- Interactive dashboard

---

# Author

**Yasmin Aminu Abdusemed**


GitHub: https://github.com/Yas614