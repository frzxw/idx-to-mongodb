import os
import csv
import zipfile
import re
import logging
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from concurrent.futures import ThreadPoolExecutor

# Constants
# File system constants
DOWNLOAD_DIR = Path("downloads")
EXTRACTED_DIR = Path("extracted")
CHUNK_SIZE = 8192  # Download chunk size in bytes

# MongoDB constants
DEFAULT_MONGODB_URI = "mongodb://localhost:27017/"
DEFAULT_DB_NAME = "idx_financial_reports"
COLLECTION_NAME = "Q12024"

# CSV file constants
CSV_FILE_PATH = "example.csv"

# File type constants
INSTANCE_FILE_EXTENSIONS = ['.xbrl', '.xml']
INSTANCE_FILE_NAMES = ['instance.xbrl', 'instance.xml']
TAXONOMY_FILE_EXTENSIONS = ['.xsd']
TAXONOMY_FILE_NAMES = ['taxonomy.xsd']
ZIP_EXTENSION = '.zip'
DEFAULT_ZIP_FILENAME = "instance.zip"

# URL parsing constants
TICKER_PATTERN = r'/[^/]+/([A-Z0-9]+)/'
MAX_TICKER_LENGTH = 5

# Logging constants
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

# Selenium constants
WEBDRIVER_PATH = "msedgedriver.exe"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
)
DOWNLOAD_TIMEOUT = 2  # seconds
DOWNLOAD_CHECK_INTERVAL = 2  # seconds
PAGE_LOAD_TIMEOUT = 2  # seconds
DOWNLOAD_INIT_WAIT = 5  # seconds\
    
# Threading constants
MAX_WORKERS = 5

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)


class FinancialReportProcessor:
    """Process financial reports from IDX (Indonesia Stock Exchange)."""
    
    def __init__(self, mongodb_uri: str = DEFAULT_MONGODB_URI, 
                 db_name: str = DEFAULT_DB_NAME):
        """
        Initialize the processor with MongoDB connection details.
        
        Args:
            mongodb_uri: MongoDB connection URI
            db_name: Name of the database to use
        """
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        
        # Ensure directories exist
        DOWNLOAD_DIR.mkdir(exist_ok=True)
        EXTRACTED_DIR.mkdir(exist_ok=True)
        
    def process_csv_file(self, csv_filepath: str) -> None:
        """
        Process a CSV file containing ticker symbols and download URLs.
        
        Args:
            csv_filepath: Path to CSV file with ticker,url format
        """
        logger.info(f"Processing CSV file: {csv_filepath}")
        
        with open(csv_filepath, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    ticker, url = row[0].strip(), row[1].strip()
                    self.process_ticker_url(ticker, url)
                else:
                    logger.warning(f"Skipping invalid row: {row}")
    
    def process_ticker_url(self, ticker: str, url: str) -> None:
        """
        Process a single ticker and its corresponding download URL.
        
        Args:
            ticker: Stock ticker symbol
            url: URL to download the financial report ZIP file
        """
        logger.info(f"Processing ticker {ticker} with URL: {url}")
        
        try:
            # Extract ticker from URL as backup if provided ticker is empty
            if not ticker:
                ticker = self._extract_ticker_from_url(url)
            
            # Download and extract the ZIP file
            zip_path = self._download_file(url, ticker)
            if not zip_path:
                return
                
            extracted_files = self._extract_zip(zip_path, ticker)
            if not extracted_files:
                return
                
            # Process the extracted files
            self._process_extracted_files(ticker, extracted_files)
            
        except Exception as e:
            logger.error(f"Error processing {ticker}: {str(e)}")
    
    def _extract_ticker_from_url(self, url: str) -> str:
        """
        Extract ticker symbol from URL.
        
        Args:
            url: URL to extract ticker from
            
        Returns:
            Ticker symbol
        """
        # Try to find the pattern in the URL (like /TW1/ADMR/)
        matches = re.findall(TICKER_PATTERN, url)
        if matches:
            return matches[-1]  # Use the last match as it's likely the correct one
        
        # Fallback to the filename
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        
        # Extract filename without extension
        filename = os.path.splitext(os.path.basename(path))[0]
        
        # If filename is "instance", try to get the parent directory name
        if filename.lower() == "instance":
            parent_dir = os.path.basename(os.path.dirname(path))
            if parent_dir and len(parent_dir) <= MAX_TICKER_LENGTH and parent_dir.isupper():
                return parent_dir
        
        return filename
    
    def _download_file(self, url: str, ticker: str) -> Optional[Path]:
        """
        Download file from URL using Selenium with MS Edge.
        
        Args:
            url: URL to download from
            ticker: Ticker symbol for filename
            
        Returns:
            Path to downloaded file or None if download failed
        """
        try:
            logger.info(f"Downloading file for {ticker} from {url}")
            
            # Create a specific download directory for this ticker
            ticker_dir = DOWNLOAD_DIR / ticker
            ticker_dir.mkdir(exist_ok=True)
            
            # Determine filename
            filename = os.path.basename(urlparse(url).path)
            if not filename.endswith(ZIP_EXTENSION):
                filename = f"{ticker}_instance{ZIP_EXTENSION}"
            
            driver = self._setup_webdriver(ticker_dir)
            
            try:
                # Set page load timeout
                driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
                
                # Navigate to the URL
                driver.get(url)
                logger.info(f"Navigated to URL for {ticker}")
                
                # Wait for download to start
                time.sleep(DOWNLOAD_INIT_WAIT)
                
                downloaded_file = self._wait_for_download(ticker_dir)
                if not downloaded_file:
                    return None
                    
                # Rename the file if needed
                if downloaded_file.name != filename:
                    target_path = ticker_dir / filename
                    downloaded_file.rename(target_path)
                    downloaded_file = target_path
                    
                logger.info(f"Downloaded file to {downloaded_file}")
                return downloaded_file
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Error downloading file for {ticker}: {str(e)}")
            return None
    
    def _setup_webdriver(self, download_dir: Path) -> webdriver.Edge:
        """
        Configure and initialize the Edge webdriver.
        
        Args:
            download_dir: Directory where downloads should be saved
        
        Returns:
            Configured Edge webdriver
        """
        options = Options()
        prefs = {
            "download.default_directory": str(download_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument(f"user-agent={DEFAULT_USER_AGENT}")
        
        # Initialize Edge webdriver
        service = Service(WEBDRIVER_PATH)
        return webdriver.Edge(service=service, options=options)
    
    def _wait_for_download(self, download_dir: Path) -> Optional[Path]:
        """
        Wait for a file download to complete.
        
        Args:
            download_dir: Directory where files are being downloaded
            
        Returns:
            Path to downloaded file or None if download failed
        """
        waited = 0
        while waited < DOWNLOAD_TIMEOUT:
            # Check for any new files in the directory
            files = list(download_dir.glob("*"))
            # Filter out temporary download files
            valid_files = [f for f in files if not f.name.endswith('.crdownload') and not f.name.endswith('.tmp')]
            
            if valid_files:
                # Get the most recently modified file
                downloaded_file = max(valid_files, key=lambda x: x.stat().st_mtime)
                if downloaded_file.exists() and downloaded_file.stat().st_size > 0:
                    return downloaded_file
            
            time.sleep(DOWNLOAD_CHECK_INTERVAL)
            waited += DOWNLOAD_CHECK_INTERVAL
            logger.info(f"Waiting for download... ({waited}s)")
        
        logger.error("Download failed or timed out")
        return None
    
    def _extract_zip(self, zip_path: Path, ticker: str) -> List[Path]:
        """
        Extract ZIP file contents.
        
        Args:
            zip_path: Path to ZIP file
            ticker: Ticker symbol for extraction directory
            
        Returns:
            List of paths to extracted files
        """
        try:
            logger.info(f"Extracting {zip_path}")
            
            # Create extraction directory
            extract_dir = EXTRACTED_DIR / ticker
            extract_dir.mkdir(exist_ok=True)
            
            extracted_files = []
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    # Extract the file
                    file_info.filename = os.path.basename(file_info.filename)
                    zip_ref.extract(file_info, extract_dir)
                    extracted_files.append(extract_dir / file_info.filename)
            
            logger.info(f"Extracted {len(extracted_files)} files to {extract_dir}")
            return extracted_files
            
        except Exception as e:
            logger.error(f"Error extracting {zip_path}: {str(e)}")
            return []
    
    def _process_extracted_files(self, ticker: str, files: List[Path]) -> None:
        """
        Process extracted files and prepare for MongoDB.
        
        Args:
            ticker: Ticker symbol
            files: List of extracted file paths
        """
        logger.info(f"Processing {len(files)} files for {ticker}")
        
        # Look for instance.xbrl file
        instance_file = self._find_file_by_pattern(files, INSTANCE_FILE_NAMES, INSTANCE_FILE_EXTENSIONS)
        
        # Look for taxonomy file
        taxonomy_file = self._find_file_by_pattern(files, TAXONOMY_FILE_NAMES, TAXONOMY_FILE_EXTENSIONS)
        
        if not instance_file:
            logger.warning(f"No XBRL instance file found for {ticker}")
            return
            
        # Process the XBRL file
        report_data = self._parse_xbrl(instance_file, taxonomy_file)
        
        if report_data:
            # Add ticker information
            report_data['ticker'] = ticker
            report_data['processed_date'] = datetime.now()
            
            # Store in MongoDB
            self._store_in_mongodb(ticker, report_data)
    
    def _find_file_by_pattern(self, files: List[Path], 
                              filenames: List[str], 
                              extensions: List[str]) -> Optional[Path]:
        """
        Find a file by matching its name or extension.
        
        Args:
            files: List of file paths to search
            filenames: List of exact filenames to match
            extensions: List of file extensions to match
            
        Returns:
            Matching file path or None
        """
        # First try exact filename match
        for filename in filenames:
            found = next((f for f in files if f.name.lower() == filename.lower()), None)
            if found:
                return found
                
        # Then try extension match
        for ext in extensions:
            found = next((f for f in files if f.name.lower().endswith(ext.lower())), None)
            if found:
                return found
                
        return None
    
    def _parse_xbrl(self, instance_path: Path, taxonomy_path: Optional[Path]) -> Dict:
        """
        Parse XBRL instance file and taxonomy file.
        
        Args:
            instance_path: Path to XBRL instance file
            taxonomy_path: Path to taxonomy file (optional)
            
        Returns:
            Dictionary with parsed financial data
        """
        try:
            logger.info(f"Parsing XBRL file: {instance_path}")
            
            tree = ET.parse(instance_path)
            root = tree.getroot()
            
            # Extract namespaces
            namespaces = {k: v for k, v in root.attrib.items() 
                         if k.startswith('xmlns:')}
            
            # Extract facts (simplified approach)
            facts = self._extract_facts_from_xbrl(root)
            
            # Create structured report data
            report_data = {
                'facts': facts,
                'file_info': {
                    'instance_filename': instance_path.name,
                    'taxonomy_filename': taxonomy_path.name if taxonomy_path else None,
                    'file_size': instance_path.stat().st_size
                }
            }
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error parsing XBRL: {str(e)}")
            return {}
    
    def _extract_facts_from_xbrl(self, root: ET.Element) -> Dict:
        """
        Extract facts from XBRL document root element.
        
        Args:
            root: Root element of XBRL document
            
        Returns:
            Dictionary of extracted facts
        """
        facts = {}
        for elem in root.iter():
            if not elem.attrib:
                continue
                
            # Get context reference and value
            context_ref = elem.attrib.get('contextRef')
            if context_ref and elem.text and elem.text.strip():
                tag_name = elem.tag.split('}')[-1]
                facts[f"{tag_name}_{context_ref}"] = {
                    'value': elem.text.strip(),
                    'context': context_ref,
                    'name': tag_name
                }
        
        return facts
    
    def _store_in_mongodb(self, ticker: str, data: Dict) -> None:
        """
        Store financial report data in MongoDB.
        
        Args:
            ticker: Ticker symbol
            data: Financial report data to store
        """
        try:
            logger.info(f"Storing data for {ticker} in MongoDB")
            
            client = MongoClient(self.mongodb_uri)
            db = client[self.db_name]
            collection = db[COLLECTION_NAME]
            
            # Use ticker and reporting period as unique identifier
            filter_query = {
                'ticker': ticker,
                'file_info.instance_filename': data['file_info']['instance_filename']
            }
            
            # Upsert the document
            collection.update_one(
                filter_query,
                {'$set': data},
                upsert=True
            )
            
            logger.info(f"Successfully stored data for {ticker} in MongoDB")
            
        except Exception as e:
            logger.error(f"Error storing data in MongoDB: {str(e)}")


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