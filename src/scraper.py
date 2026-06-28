import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
CHANNELS = ['@CheMed1', '@LobeliaCosmetics', '@TikvahPharma'] # Use exact channel handles

client = TelegramClient('kara_scraper_session', API_ID, API_HASH)

async def scrape_channel(channel_handle):
    logging.info(f"Starting scrape for channel: {channel_handle}")
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # Define Data Lake Paths
    json_dir = f"data/raw/telegram_messages/{today_str}"
    img_dir = f"data/raw/images/{channel_handle.strip('@')}"
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    messages_data = []

    try:
        # Fetching last 100 messages for the interim scope
        async for message in client.iter_messages(channel_handle, limit=100):
            image_path = None
            has_media = message.photo is not None

            if has_media:
                filename = f"{message.id}.jpg"
                path = os.path.join(img_dir, filename)
                await message.download_media(file=path)
                image_path = path

            msg_info = {
                "message_id": message.id,
                "channel_name": channel_handle,
                "message_date": message.date.isoformat() if message.date else None,
                "message_text": message.text,
                "has_media": has_media,
                "image_path": image_path,
                "views": message.views if message.views else 0,
                "forwards": message.forwards if message.forwards else 0
            }
            messages_data.append(msg_info)

        # Save to Data Lake
        output_file = os.path.join(json_dir, f"{channel_handle.strip('@')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=4)
        
        logging.info(f"Successfully saved {len(messages_data)} messages for {channel_handle}")

    except Exception as e:
        logging.error(f"Error scraping {channel_handle}: {str(e)}")

async def main():
    for channel in CHANNELS:
        await scrape_channel(channel)

with client:
    client.loop.run_until_complete(main())