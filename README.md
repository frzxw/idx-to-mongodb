# Financial Report Processor

This project is designed to process financial reports from the Indonesia Stock Exchange (IDX). It automates the downloading, extraction, and parsing of financial report data, storing the results in a MongoDB database.

## Project Structure

```
idx-to-mongodb
├── src
│   ├── main.py                # Entry point for the application
│   ├── processor              # Contains the financial report processing logic
│   │   └── financial_report_processor.py
│   ├── utils                  # Utility functions for downloading and extracting files
│   │   ├── download.py
│   │   ├── extract.py
│   │   └── xbrl_parser.py
│   └── models                 # Data models for representing financial report data
│       └── report.py
├── data                       # Directory for data files
│   └── reports.csv            # CSV file with ticker symbols and download URLs
├── temp                       # Temporary storage for downloads and extracted files
│   ├── downloads
│   └── extracted
├── tests                      # Unit tests for the application
│   ├── test_processor.py
│   └── test_parser.py
├── requirements.txt           # Project dependencies
└── setup.py                   # Packaging information
```

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd idx-to-mongodb
pip install -r requirements.txt
```

## Usage

To run the application, execute the following command:

```bash
python main.py
```

Make sure to have the necessary configurations in place, including MongoDB connection details and the CSV file with ticker symbols and URLs.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.