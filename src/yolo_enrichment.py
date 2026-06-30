import os
import glob
import psycopg2
from ultralytics import YOLO

# 1. Database Connection Configurations
DB_PARAMS = {
    "host": "localhost",
    "database": "medical_db",
    "user": "postgres",
    "password": "Strong!password123",  
    "port": "5432"
}

IMAGE_DIR = "data/raw/images"

def init_db():
    """Ensure the target table exists in the raw schema with defensive handling."""
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.enriched_images (
            image_id SERIAL PRIMARY KEY,
            channel_name VARCHAR(255),
            message_id VARCHAR(50),
            detected_object VARCHAR(255),
            confidence FLOAT,
            box_coordinates TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def process_images():
    """Scan local storage, run YOLO inference, and ingest results."""
    print("Initializing YOLOv8 Model...")
    # Using a standard pre-trained model; it auto-downloads on the first run safely
    model = YOLO("yolov8n.pt") 
    
    init_db()
    
    # Find all JPGs recursively inside your directory structure
    image_paths = glob.glob(os.path.join(IMAGE_DIR, "**", "*.jpg"), recursive=True)
    
    if not image_paths:
        print(f"No image assets found to enrich in path: {IMAGE_DIR}")
        return

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    print(f"Found {len(image_paths)} images. Starting ML inference pipeline...")
    
    for path in image_paths:
        try:
            # Clean path mechanics to find channel and message details
            # Expected pattern: data/raw/images/channel_name/message_id.jpg
            normalized_path = os.path.normpath(path)
            parts = normalized_path.split(os.sep)
            channel_name = parts[-2]
            message_id = os.path.splitext(parts[-1])[0]

            # Run Object Detection Inference
            results = model(path, verbose=False)[0]
            
            for box in results.boxes:
                obj_id = int(box.cls[0])
                obj_name = model.names[obj_id]  # Converts numerical ID to 'person', 'bottle', etc.
                confidence = float(box.conf[0])
                coords = str(box.xyxy[0].tolist()) # Bounding box arrays

                # Ingest bounding box evaluations defensively
                cur.execute("""
                    INSERT INTO raw.enriched_images (channel_name, message_id, detected_object, confidence, box_coordinates)
                    VALUES (%s, %s, %s, %s, %s);
                """, (channel_name, message_id, obj_name, confidence, coords))
                
            print(f"✔ Successfully processed image: {channel_name}/{message_id}")
            
        except Exception as e:
            print(f"⚠ Critical skip on file {path} due to error: {str(e)}")
            continue

    conn.commit()
    cur.close()
    conn.close()
    print("🎉 YOLO image enrichment pipeline execution complete!")

if __name__ == "__main__":
    process_images()