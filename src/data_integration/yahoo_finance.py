"""Yahoo Finance Data Integration"""
import yfinance as yf
import pandas as pd
from typing import Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class YahooFinanceClient:
    """Client for fetching historical stock data from Yahoo Finance"""
    
    def __init__(self):
        self.cache = {}
    
    def get_historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical stock data
        
        Args:
            symbol: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            logger.info(f"Fetched {len(df)} records for {symbol}")
            return df
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_info(self, symbol: str) -> dict:
        """
        Get stock information and fundamentals
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Dictionary with stock information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            return {}
    
    def get_real_time_price(self, symbol: str) -> Optional[float]:
        """
        Get real-time price for a stock
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Current price or None
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"Error fetching real-time price for {symbol}: {e}")
            return None
    
    def get_multiple_symbols(self, symbols: List[str], period: str = "1y") -> dict:
        """
        Fetch data for multiple symbols
        
        Args:
            symbols: List of stock ticker symbols
            period: Data period
        
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        result = {}
        for symbol in symbols:
            df = self.get_historical_data(symbol, period)
            if df is not None:
                result[symbol] = df
        return result
