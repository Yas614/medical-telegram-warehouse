import os
import json
import psycopg2
from dotenv import load_dotenv

# Load configurations from root directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, '.env'))

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=os.getenv('POSTGRES_PORT')
    )
    cursor = conn.cursor()

    # 1. Create a raw landing schema and table structure
    cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            message_id INT,
            channel_name VARCHAR(255),
            message_date TIMESTAMP,
            message_text TEXT,
            has_media BOOLEAN,
            image_path TEXT,
            views INT,
            forwards INT
        );
    """)
    # Clean old records if running multiple times
    cursor.execute("TRUNCATE TABLE raw.telegram_messages;")
    conn.commit()

    # 2. Iterate through data partitions and push to warehouse
    base_path = os.path.join(base_dir, "data", "raw", "telegram_messages")
    records_inserted = 0

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        cursor.execute("""
                            INSERT INTO raw.telegram_messages 
                            (message_id, channel_name, message_date, message_text, has_media, image_path, views, forwards)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            item['message_id'], item['channel_name'], item['message_date'], 
                            item['message_text'], item['has_media'], item['image_path'], 
                            item['views'], item['forwards']
                        ))
                        records_inserted += 1
                        
    conn.commit()
    print(f"🎉 Success! Loaded {records_inserted} raw records into Postgres raw.telegram_messages table.")

except Exception as e:
    print(f"❌ Database error: {str(e)}")
finally:
    if 'cursor' in locals(): cursor.close()
    if 'conn' in locals(): conn.close()