"""
Anonymizer Module
Handles consistent anonymization of PII data
"""

import hashlib
from typing import Dict, Any
import pandas as pd
from loguru import logger


class Anonymizer:
    """Consistent anonymization of PII values"""
    
    def __init__(self):
        """Initialize anonymizer with empty mappings"""
        self.mappings: Dict[str, Dict[Any, str]] = {}
        self.counters: Dict[str, int] = {}
    
    def _get_next_id(self, prefix: str) -> str:
        """
        Get next sequential anonymous ID
        
        Args:
            prefix: Prefix for the ID (e.g., 'ID', 'EMAIL')
            
        Returns:
            Anonymous ID string (e.g., 'ID-001')
        """
        if prefix not in self.counters:
            self.counters[prefix] = 0
        
        self.counters[prefix] += 1
        return f"{prefix}-{self.counters[prefix]:03d}"
    
    def _get_deterministic_id(self, value: Any, prefix: str) -> str:
        """
        Generate deterministic ID using hash (consistent across runs)
        
        Args:
            value: Original value
            prefix: Prefix for the ID
            
        Returns:
            Anonymous ID string
        """
        # Create hash of the value
        hash_obj = hashlib.sha256(str(value).encode('utf-8'))
        hash_hex = hash_obj.hexdigest()[:8]  # First 8 chars
        
        return f"{prefix}-{hash_hex}"
    
    def anonymize_value(self, value: Any, pii_type: str, 
                       deterministic: bool = False) -> str:
        """
        Anonymize a single value
        
        Args:
            value: Original value to anonymize
            pii_type: Type of PII ('israeli_id', 'email', 'phone', etc.)
            deterministic: Use hash-based IDs (same input = same output)
            
        Returns:
            Anonymized value
        """
        # Handle missing values
        if pd.isna(value):
            return value
        
        # Map PII type to prefix
        prefix_map = {
            'israeli_id': 'ID',
            'email': 'EMAIL',
            'phone': 'PHONE',
            'name': 'PERSON',
            'address': 'ADDRESS',
            'account': 'ACCOUNT'
        }
        
        prefix = prefix_map.get(pii_type, 'ANON')
        
        # Initialize mapping for this type if needed
        if pii_type not in self.mappings:
            self.mappings[pii_type] = {}
        
        # Check if we've seen this value before
        if value in self.mappings[pii_type]:
            return self.mappings[pii_type][value]
        
        # Generate new anonymous ID
        if deterministic:
            anon_value = self._get_deterministic_id(value, prefix)
        else:
            anon_value = self._get_next_id(prefix)
        
        # Store mapping
        self.mappings[pii_type][value] = anon_value
        
        return anon_value
    
    def anonymize_column(self, series: pd.Series, pii_type: str,
                        deterministic: bool = False) -> pd.Series:
        """
        Anonymize entire column
        
        Args:
            series: pandas Series to anonymize
            pii_type: Type of PII
            deterministic: Use hash-based IDs
            
        Returns:
            Anonymized Series
        """
        logger.info(f"Anonymizing column with {len(series)} values as {pii_type}...")
        
        result = series.apply(
            lambda x: self.anonymize_value(x, pii_type, deterministic)
        )
        
        unique_mappings = len(self.mappings.get(pii_type, {}))
        logger.success(f"Anonymized column: {unique_mappings} unique values mapped")
        
        return result
    
    def anonymize_dataframe(self, df: pd.DataFrame, 
                          column_types: Dict[str, str],
                          deterministic: bool = False) -> pd.DataFrame:
        """
        Anonymize multiple columns in a DataFrame
        
        Args:
            df: pandas DataFrame
            column_types: Mapping of column names to PII types
            deterministic: Use hash-based IDs
            
        Returns:
            Anonymized DataFrame
        """
        logger.info(f"Starting anonymization of {len(column_types)} columns...")
        
        # Create a copy to avoid modifying original
        df_anon = df.copy()
        
        for col, pii_type in column_types.items():
            if col in df_anon.columns:
                df_anon[col] = self.anonymize_column(
                    df_anon[col], 
                    pii_type, 
                    deterministic
                )
        
        logger.success("Anonymization complete!")
        return df_anon
    
    def get_mappings(self) -> Dict[str, Dict[Any, str]]:
        """
        Get all anonymization mappings
        
        Returns:
            Dictionary of all mappings by PII type
        """
        return self.mappings
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get anonymization statistics
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_pii_types': len(self.mappings),
            'total_values_mapped': sum(len(m) for m in self.mappings.values()),
            'by_type': {}
        }
        
        for pii_type, mapping in self.mappings.items():
            stats['by_type'][pii_type] = {
                'unique_values': len(mapping),
                'examples': list(mapping.values())[:3]  # First 3 examples
            }
        
        return stats


# TODO: Future enhancements
# - Add partial masking option (e.g., 050-12***67)
# - Add fake data generation option (using Faker)
# - Add reversible anonymization with encryption
# - Support for maintaining data characteristics (e.g., gender in names)
