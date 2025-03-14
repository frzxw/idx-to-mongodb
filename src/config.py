# Configuration constants and settings used throughout the application.

# File system constants
DOWNLOAD_DIR = "temp/downloads"
EXTRACTED_DIR = "temp/extracted"

# MongoDB constants
DEFAULT_MONGODB_URI = "mongodb://localhost:27017/"
DEFAULT_DB_NAME = "financial_reports"
COLLECTION_NAME = "reports"

# CSV file constants
CSV_FILE_PATH = "data/reports.csv"

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

# Selenium constants
WEBDRIVER_PATH = "msedgedriver.exe"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
)

# Download settings
DOWNLOAD_TIMEOUT = 2  # seconds
DOWNLOAD_CHECK_INTERVAL = 2  # seconds
PAGE_LOAD_TIMEOUT = 2  # seconds
DOWNLOAD_INIT_WAIT = 5  # seconds

# Threading constants
MAX_WORKERS = 5