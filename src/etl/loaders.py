"""Data Loading Module"""
import pandas as pd
import logging
from typing import Optional, Dict
import os
import json

logger = logging.getLogger(__name__)


class DataLoader:
    """Load data to storage"""
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """
        Save DataFrame to CSV
        
        Args:
            df: DataFrame to save
            filename: Output filename
        
        Returns:
            True if successful
        """
        try:
            filepath = os.path.join(self.output_dir, filename)
            df.to_csv(filepath, index=False)
            logger.info(f"Saved data to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return False
    
    def save_to_parquet(self, df: pd.DataFrame, filename: str) -> bool:
        """
        Save DataFrame to Parquet
        
        Args:
            df: DataFrame to save
            filename: Output filename
        
        Returns:
            True if successful
        """
        try:
            filepath = os.path.join(self.output_dir, filename)
            df.to_parquet(filepath, index=False, engine='pyarrow')
            logger.info(f"Saved data to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving to Parquet: {e}")
            return False
    
    def save_multiple(
        self,
        data: Dict[str, pd.DataFrame],
        format: str = 'csv'
    ) -> bool:
        """
        Save multiple DataFrames
        
        Args:
            data: Dictionary mapping names to DataFrames
            format: Output format (csv, parquet)
        
        Returns:
            True if all successful
        """
        success = True
        
        for name, df in data.items():
            filename = f"{name}.{format}"
            if format == 'csv':
                if not self.save_to_csv(df, filename):
                    success = False
            elif format == 'parquet':
                if not self.save_to_parquet(df, filename):
                    success = False
        
        return success
    
    def save_metadata(self, metadata: dict, filename: str) -> bool:
        """
        Save metadata as JSON
        
        Args:
            metadata: Metadata dictionary
            filename: Output filename
        
        Returns:
            True if successful
        """
        try:
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Saved metadata to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            return False
