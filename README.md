# Interim Status Report — Kara Solutions Data Platform

## 1. Data Lake Directory Architecture
Raw data scraped from public Telegram channels via Telethon is organized using a chronologically partitioned layout to ensure linear data tracking and recovery states:
- **Messages JSON Store:** `data/raw/telegram_messages/YYYY-MM-DD/channel_name.json`
- **Images Asset Store:** `data/raw/images/channel_name/message_id.jpg`

## 2. Warehouse Analytical Dimensional Model (Star Schema)
To optimize operational query velocities and simplify aggregations, the transformed layer is separated into explicit context dimensions and quantitative facts:

- **fct_messages (Fact Table):** Tracks discrete operational metrics (views, forwards, lengths) mapped across contextual relational keys.
- **dim_channels (Dimension):** Captures descriptive structural variables of the channel profiles including custom classifications.
- **dim_dates (Dimension):** Provides deep temporal contextual mapping (weekdays, weekends, quarters, years).

### Schema Flow Architecture
```text
          +-----------------------+
          |      dim_dates        |
          +-----------------------+
          | PK | date_key         |
          +-----------------------+
                     |
                     | 1:N
                     v
+------------------+   N:1   +-----------------------+
|   dim_channels   | ------> |     fct_messages      |
+------------------+         +-----------------------+
| PK | channel_key |         | PK | message_id       |
+------------------+         | FK | channel_key      |
                             | FK | date_key         |
                             |    | view_count       |
                             |    | forward_count    |
                             +-----------------------+