"""Data Transformation Module"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transform and clean data"""
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess data
        
        Args:
            df: Input DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # Reset index
        df = df.reset_index()
        
        # Ensure proper data types
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def normalize_data(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Normalize specified columns
        
        Args:
            df: Input DataFrame
            columns: Columns to normalize
        
        Returns:
            DataFrame with normalized columns
        """
        result = df.copy()
        
        for col in columns:
            if col in df.columns:
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val - min_val != 0:
                    result[f'{col}_normalized'] = (df[col] - min_val) / (max_val - min_val)
        
        return result
    
    def add_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate returns
        
        Args:
            df: Input DataFrame with Close prices
        
        Returns:
            DataFrame with returns columns
        """
        result = df.copy()
        
        if 'Close' in df.columns:
            # Daily returns
            result['returns'] = df['Close'].pct_change()
            
            # Cumulative returns
            result['cumulative_returns'] = (1 + result['returns']).cumprod() - 1
            
            # Log returns
            result['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        return result
    
    def aggregate_data(
        self,
        data: Dict[str, pd.DataFrame],
        operation: str = 'mean'
    ) -> pd.DataFrame:
        """
        Aggregate data from multiple sources
        
        Args:
            data: Dictionary of DataFrames
            operation: Aggregation operation (mean, median, sum)
        
        Returns:
            Aggregated DataFrame
        """
        if not data:
            return pd.DataFrame()
        
        # Combine all dataframes
        combined = pd.concat(data.values(), keys=data.keys())
        
        # Perform aggregation
        if operation == 'mean':
            result = combined.groupby(level=1).mean()
        elif operation == 'median':
            result = combined.groupby(level=1).median()
        elif operation == 'sum':
            result = combined.groupby(level=1).sum()
        else:
            result = combined.groupby(level=1).mean()
        
        return result
    
    def handle_outliers(
        self,
        df: pd.DataFrame,
        columns: List[str],
        method: str = 'iqr'
    ) -> pd.DataFrame:
        """
        Handle outliers in data
        
        Args:
            df: Input DataFrame
            columns: Columns to check for outliers
            method: Method to use (iqr, zscore)
        
        Returns:
            DataFrame with outliers handled
        """
        result = df.copy()
        
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                result[col] = df[col].clip(lower_bound, upper_bound)
            
            elif method == 'zscore':
                mean = df[col].mean()
                std = df[col].std()
                result[col] = df[col].clip(mean - 3*std, mean + 3*std)
        
        return result
