"""Data Extraction Module"""
import pandas as pd
import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..data_integration import YahooFinanceClient, GrowwClient, ZerodhaClient

logger = logging.getLogger(__name__)


class DataExtractor:
    """Extract data from multiple sources"""
    
    def __init__(self, max_workers: int = 4):
        self.yf_client = YahooFinanceClient()
        self.groww_client = GrowwClient()
        self.zerodha_client = ZerodhaClient()
        self.max_workers = max_workers
    
    def extract_historical_data(
        self,
        symbols: List[str],
        period: str = "1y"
    ) -> Dict[str, pd.DataFrame]:
        """
        Extract historical data for multiple symbols in parallel
        
        Args:
            symbols: List of stock symbols
            period: Data period
        
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(
                    self.yf_client.get_historical_data,
                    symbol,
                    period
                ): symbol for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data is not None:
                        results[symbol] = data
                        logger.info(f"Extracted data for {symbol}")
                except Exception as e:
                    logger.error(f"Error extracting data for {symbol}: {e}")
        
        return results
    
    def extract_fundamentals(self, symbols: List[str]) -> Dict[str, dict]:
        """
        Extract fundamental data for symbols
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary mapping symbols to fundamental data
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.yf_client.get_info, symbol): symbol
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    info = future.result()
                    if info:
                        results[symbol] = info
                except Exception as e:
                    logger.error(f"Error extracting fundamentals for {symbol}: {e}")
        
        return results
    
    def extract_real_time_data(self, symbols: List[str]) -> Dict[str, float]:
        """
        Extract real-time prices
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary mapping symbols to current prices
        """
        results = {}
        
        for symbol in symbols:
            try:
                price = self.yf_client.get_real_time_price(symbol)
                if price is not None:
                    results[symbol] = price
            except Exception as e:
                logger.error(f"Error extracting real-time data for {symbol}: {e}")
        
        return results
