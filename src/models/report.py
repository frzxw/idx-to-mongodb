class FinancialReport:
    """Data model for representing a financial report."""
    
    def __init__(self, ticker: str, instance_filename: str, taxonomy_filename: Optional[str], facts: Dict):
        """
        Initialize a FinancialReport instance.
        
        Args:
            ticker: Ticker symbol of the financial report.
            instance_filename: Name of the XBRL instance file.
            taxonomy_filename: Name of the taxonomy file (optional).
            facts: Dictionary containing extracted facts from the XBRL file.
        """
        self.ticker = ticker
        self.instance_filename = instance_filename
        self.taxonomy_filename = taxonomy_filename
        self.facts = facts

    def to_dict(self) -> Dict:
        """Convert the financial report data to a dictionary."""
        return {
            'ticker': self.ticker,
            'instance_filename': self.instance_filename,
            'taxonomy_filename': self.taxonomy_filename,
            'facts': self.facts
        }