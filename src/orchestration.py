import os
import subprocess
from pathlib import Path
from dagster import asset, Definitions, OpExecutionContext

# Path configurations matching your directory layout
DBT_PROJECT_DIR = Path(__file__).joinpath("..", "..", "medical_warehouse").resolve()

@asset(compute_kind="python")
def telegram_raw_data_lake():
    """Asset 1: Scrapes and updates raw data layers using Telethon."""
    print("Executing Telethon extraction layer...")
    result = subprocess.run(["python", "src/load_raw.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Ingestion lifecycle failed: {result.stderr}")
    return "Data Lake updated"

@asset(deps=[telegram_raw_data_lake], compute_kind="python")
def yolo_ml_enrichment():
    """Asset 2: Performs object detection over scraped image folders post-ingestion."""
    print("Executing YOLOv8 inference loops...")
    result = subprocess.run(["python", "src/yolo_enrichment.py"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"YOLO ML enrichment stage failed: {result.stderr}")
    return "ML Metadata Generated"

@asset(deps=[yolo_ml_enrichment], compute_kind="dbt")
def medical_warehouse_dbt_assets(context: OpExecutionContext):
    """Asset 3: Executes multi-tiered SQL transformations using dbt via subprocess."""
    context.log.info(f"Launching dbt run in target directory: {DBT_PROJECT_DIR}")
    
    # Run the dbt transformation natively using your environment's installed dbt core/adapter
    result = subprocess.run(
        ["dbt", "run"],
        cwd=DBT_PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    # Output logs to Dagster UI terminal stream
    if result.stdout:
        context.log.info(result.stdout)
    if result.stderr:
        context.log.error(result.stderr)
        
    if result.returncode != 0:
        raise Exception(f"dbt transformations failed with exit code {result.returncode}")
        
    return "dbt Transformations Complete"

# Define global deployment configurations using your working Dagster 1.13 framework
defs = Definitions(
    assets=[telegram_raw_data_lake, yolo_ml_enrichment, medical_warehouse_dbt_assets],
)