"""
PII Detector Module
Detects personally identifiable information in text
"""

import re
from typing import List, Dict, Set, Optional
import pandas as pd
from loguru import logger


class PIIDetector:
    """Detects PII in text and DataFrames"""
    
    def __init__(self):
        """Initialize PII detection patterns"""
        self.patterns = {
            'israeli_id': re.compile(r'\b\d{9}\b'),  # 9 digits
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone_il': re.compile(r'\b0\d{1,2}-?\d{7}\b'),  # Israeli phone
            'phone_mobile': re.compile(r'\b05[0-9]-?\d{7}\b'),  # Israeli mobile
        }
    
    def detect_israeli_id(self, text: str) -> bool:
        """
        Detect Israeli ID (9 digits with Luhn check)
        
        Args:
            text: Text to search
            
        Returns:
            True if Israeli ID found
        """
        if not isinstance(text, str):
            text = str(text)
        
        matches = self.patterns['israeli_id'].findall(text)
        
        for match in matches:
            if self._validate_israeli_id(match):
                return True
        
        return False
    
    def _validate_israeli_id(self, id_number: str) -> bool:
        """
        Validate Israeli ID using Luhn algorithm
        
        Args:
            id_number: 9-digit ID number
            
        Returns:
            True if valid
        """
        if len(id_number) != 9:
            return False
        
        try:
            # Luhn algorithm for Israeli ID
            total = 0
            for i, digit in enumerate(id_number):
                num = int(digit)
                if i % 2 == 0:  # Odd positions (0-indexed)
                    num *= 1
                else:  # Even positions
                    num *= 2
                    if num > 9:
                        num = num // 10 + num % 10
                total += num
            
            return total % 10 == 0
        except ValueError:
            return False
    
    def detect_email(self, text: str) -> bool:
        """
        Detect email addresses
        
        Args:
            text: Text to search
            
        Returns:
            True if email found
        """
        if not isinstance(text, str):
            text = str(text)
        
        return bool(self.patterns['email'].search(text))
    
    def detect_phone(self, text: str) -> bool:
        """
        Detect Israeli phone numbers
        
        Args:
            text: Text to search
            
        Returns:
            True if phone found
        """
        if not isinstance(text, str):
            text = str(text)
        
        return bool(self.patterns['phone_il'].search(text) or 
                   self.patterns['phone_mobile'].search(text))
    
    def detect_in_column(self, series: pd.Series) -> Dict[str, int]:
        """
        Detect PII types in a pandas Series (column)
        
        Args:
            series: pandas Series to scan
            
        Returns:
            Dictionary with counts of each PII type found
        """
        results = {
            'israeli_id': 0,
            'email': 0,
            'phone': 0,
        }
        
        # Sample first 100 rows for performance
        sample_size = min(100, len(series))
        sample = series.head(sample_size)
        
        for value in sample:
            if pd.isna(value):
                continue
            
            text = str(value)
            
            if self.detect_israeli_id(text):
                results['israeli_id'] += 1
            if self.detect_email(text):
                results['email'] += 1
            if self.detect_phone(text):
                results['phone'] += 1
        
        return results
    
    def scan_dataframe(self, df: pd.DataFrame, threshold: float = 0.1) -> Dict[str, Dict]:
        """
        Scan entire DataFrame for PII
        
        Args:
            df: pandas DataFrame to scan
            threshold: Minimum ratio of PII to flag column (default 10%)
            
        Returns:
            Dictionary mapping column names to detected PII types
        """
        logger.info(f"Scanning DataFrame with {len(df.columns)} columns...")
        
        results = {}
        
        for col in df.columns:
            col_results = self.detect_in_column(df[col])
            
            # Calculate ratio of PII found
            sample_size = min(100, len(df[col]))
            ratios = {k: v / sample_size for k, v in col_results.items()}
            
            # Flag column if any PII type exceeds threshold
            flagged_types = [k for k, v in ratios.items() if v >= threshold]
            
            if flagged_types:
                results[col] = {
                    'types': flagged_types,
                    'counts': {k: col_results[k] for k in flagged_types},
                    'ratios': {k: ratios[k] for k in flagged_types}
                }
                
                logger.info(f"Column '{col}' flagged with: {', '.join(flagged_types)}")
        
        logger.success(f"Scan complete. {len(results)} columns flagged with PII.")
        
        return results
    
    def get_sample_values(self, series: pd.Series, n: int = 3) -> List[str]:
        """
        Get sample values from a series (for preview)
        
        Args:
            series: pandas Series
            n: Number of samples
            
        Returns:
            List of sample values as strings
        """
        samples = series.dropna().head(n).tolist()
        return [str(val) for val in samples]


# TODO: Future enhancements
# - Integrate Microsoft Presidio for advanced NLP-based detection
# - Add Hebrew name detection with spaCy
# - Add address detection
# - Add bank account number patterns
# - Improve phone number validation
