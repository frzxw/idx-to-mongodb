import unittest
from src.utils.xbrl_parser import parse_xbrl  # Adjust the import based on your actual function name and parameters

class TestXBRLParser(unittest.TestCase):
    
    def test_parse_valid_xbrl(self):
        # Test parsing a valid XBRL file
        result = parse_xbrl('path/to/valid_instance.xbrl', 'path/to/taxonomy.xsd')
        self.assertIsInstance(result, dict)  # Check if the result is a dictionary
        self.assertIn('facts', result)  # Check if 'facts' key is in the result

    def test_parse_invalid_xbrl(self):
        # Test parsing an invalid XBRL file
        result = parse_xbrl('path/to/invalid_instance.xbrl', 'path/to/taxonomy.xsd')
        self.assertEqual(result, {})  # Expect an empty dictionary for invalid input

    def test_parse_xbrl_without_taxonomy(self):
        # Test parsing an XBRL file without a taxonomy
        result = parse_xbrl('path/to/valid_instance.xbrl', None)
        self.assertIsInstance(result, dict)  # Check if the result is still a dictionary

if __name__ == '__main__':
    unittest.main()