import unittest
from src.processor.financial_report_processor import FinancialReportProcessor

class TestFinancialReportProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = FinancialReportProcessor()

    def test_process_ticker_url_valid(self):
        # Test processing a valid ticker and URL
        ticker = "AAPL"
        url = "http://example.com/aapl_report.zip"
        result = self.processor.process_ticker_url(ticker, url)
        self.assertIsNone(result)  # Adjust based on expected behavior

    def test_process_ticker_url_invalid(self):
        # Test processing an invalid ticker and URL
        ticker = "INVALID"
        url = "http://example.com/invalid_report.zip"
        result = self.processor.process_ticker_url(ticker, url)
        self.assertIsNone(result)  # Adjust based on expected behavior

    def test_extract_ticker_from_url(self):
        # Test extracting ticker from a valid URL
        url = "http://example.com/reports/AAPL/2023_report.zip"
        ticker = self.processor._extract_ticker_from_url(url)
        self.assertEqual(ticker, "AAPL")

    def test_find_file_by_pattern(self):
        # Test finding a file by pattern
        files = ["instance.xbrl", "taxonomy.xsd"]
        found_file = self.processor._find_file_by_pattern(files, ["instance.xbrl"], [])
        self.assertEqual(found_file, "instance.xbrl")

if __name__ == '__main__':
    unittest.main()