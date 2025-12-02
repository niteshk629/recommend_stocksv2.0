"""ETL Pipeline Orchestration"""
import logging
from typing import List, Dict
import pandas as pd
from .extractors import DataExtractor
from .transformers import DataTransformer
from .loaders import DataLoader

logger = logging.getLogger(__name__)


class ETLPipeline:
    """Main ETL Pipeline"""
    
    def __init__(self, max_workers: int = 4, output_dir: str = "data"):
        self.extractor = DataExtractor(max_workers=max_workers)
        self.transformer = DataTransformer()
        self.loader = DataLoader(output_dir=output_dir)
    
    def run(
        self,
        symbols: List[str],
        period: str = "1y",
        save_format: str = 'csv'
    ) -> Dict[str, pd.DataFrame]:
        """
        Run complete ETL pipeline
        
        Args:
            symbols: List of stock symbols
            period: Data period
            save_format: Output format (csv, parquet)
        
        Returns:
            Dictionary of processed DataFrames
        """
        logger.info(f"Starting ETL pipeline for {len(symbols)} symbols")
        
        # Extract
        logger.info("Extracting historical data...")
        historical_data = self.extractor.extract_historical_data(symbols, period)
        
        logger.info("Extracting fundamentals...")
        fundamentals = self.extractor.extract_fundamentals(symbols)
        
        # Transform
        logger.info("Transforming data...")
        transformed_data = {}
        
        for symbol, df in historical_data.items():
            # Clean data
            df_clean = self.transformer.clean_data(df)
            
            # Add returns
            df_clean = self.transformer.add_returns(df_clean)
            
            # Handle outliers
            df_clean = self.transformer.handle_outliers(
                df_clean,
                ['Open', 'High', 'Low', 'Close', 'Volume']
            )
            
            transformed_data[symbol] = df_clean
        
        # Load
        logger.info("Loading data...")
        self.loader.save_multiple(transformed_data, format=save_format)
        
        # Save fundamentals metadata
        if fundamentals:
            self.loader.save_metadata(fundamentals, 'fundamentals.json')
        
        logger.info("ETL pipeline completed successfully")
        return transformed_data
