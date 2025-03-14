# filepath: idx-to-mongodb/idx-to-mongodb/src/main.py
from src.processor.financial_report_processor import FinancialReportProcessor
import csv
import logging
from concurrent.futures import ThreadPoolExecutor
from src.config import DEFAULT_MONGODB_URI, DEFAULT_DB_NAME, CSV_FILE_PATH, MAX_WORKERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application."""
    processor = FinancialReportProcessor(
        mongodb_uri=DEFAULT_MONGODB_URI,
        db_name=DEFAULT_DB_NAME
    )
    
    # Process from a CSV file
    with open(CSV_FILE_PATH, 'r') as csvfile:
        reader = csv.reader(csvfile)
        tasks = [(row[0].strip(), row[1].strip()) for row in reader if len(row) >= 2]
    
    with ThreadPoolExecutor(MAX_WORKERS) as executor:
        results = list(executor.map(lambda task: processor.process_ticker_url(*task), tasks))
    
    logger.info("All rows have been processed")

if __name__ == "__main__":
    main()