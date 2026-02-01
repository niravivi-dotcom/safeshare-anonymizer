"""
File Handler Module
Handles reading and writing Excel files
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import openpyxl
from loguru import logger


class FileHandler:
    """Handles Excel file operations"""
    
    MAX_FILE_SIZE_MB = 10  # MVP limit
    
    @staticmethod
    def validate_file(file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not file_path.exists():
            return False, "קובץ לא נמצא / File not found"
        
        # Check file extension
        valid_extensions = ['.xlsx', '.xls']
        if file_path.suffix.lower() not in valid_extensions:
            return False, f"פורמט לא נתמך. השתמש ב: {', '.join(valid_extensions)}"
        
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > FileHandler.MAX_FILE_SIZE_MB:
            return False, f"הקובץ גדול מדי ({file_size_mb:.1f}MB). מקסימום: {FileHandler.MAX_FILE_SIZE_MB}MB"
        
        return True, None
    
    @staticmethod
    def load_excel(file_path: Path) -> pd.DataFrame:
        """
        Load Excel file into pandas DataFrame
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            pandas DataFrame
            
        Raises:
            ValueError: If file cannot be read
        """
        try:
            logger.info(f"Loading Excel file: {file_path}")
            
            # Try to read with openpyxl (for .xlsx)
            if file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                # Use xlrd for .xls
                df = pd.read_excel(file_path, engine='xlrd')
            
            logger.success(f"Successfully loaded {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load Excel file: {e}")
            raise ValueError(f"לא ניתן לקרוא את הקובץ: {str(e)}")
    
    @staticmethod
    def save_excel(df: pd.DataFrame, output_path: Path) -> None:
        """
        Save DataFrame to Excel file
        
        Args:
            df: pandas DataFrame
            output_path: Path to save the file
            
        Raises:
            ValueError: If file cannot be saved
        """
        try:
            logger.info(f"Saving Excel file: {output_path}")
            
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to Excel
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            logger.success(f"Successfully saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save Excel file: {e}")
            raise ValueError(f"לא ניתן לשמור את הקובץ: {str(e)}")
    
    @staticmethod
    def secure_delete(file_path: Path) -> None:
        """
        Securely delete a file (overwrite then delete)
        
        Args:
            file_path: Path to file to delete
        """
        try:
            if file_path.exists():
                # Overwrite with zeros (simple version)
                with open(file_path, 'wb') as f:
                    f.write(b'\x00' * file_path.stat().st_size)
                
                # Delete
                file_path.unlink()
                logger.info(f"Securely deleted: {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            raise ValueError(f"לא ניתן למחוק את הקובץ: {str(e)}")


def get_file_info(df: pd.DataFrame) -> dict:
    """
    Get basic information about the DataFrame
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Dictionary with file statistics
    """
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': df.columns.tolist(),
        'dtypes': df.dtypes.to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
    }
