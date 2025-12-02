"""Zerodha Kite API Client"""
import requests
import logging
from typing import Optional, Dict, List
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class ZerodhaClient:
    """Client for interacting with Zerodha Kite API"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key or os.getenv('ZERODHA_API_KEY')
        self.api_secret = api_secret or os.getenv('ZERODHA_API_SECRET')
        self.base_url = "https://api.kite.trade"
        self.access_token = None
        self.session = requests.Session()
    
    def set_access_token(self, access_token: str):
        """
        Set access token for API calls
        
        Args:
            access_token: Access token from Zerodha
        """
        self.access_token = access_token
        self.session.headers.update({
            'Authorization': f'token {self.api_key}:{self.access_token}',
            'X-Kite-Version': '3'
        })
    
    def get_quote(self, instruments: List[str]) -> Optional[Dict]:
        """
        Get real-time quotes for instruments
        
        Args:
            instruments: List of instrument identifiers (e.g., 'NSE:INFY')
        
        Returns:
            Dictionary with quote data
        """
        if not self.access_token:
            logger.error("Access token not set")
            return None
        
        try:
            url = f"{self.base_url}/quote"
            params = {'i': instruments}
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to fetch quotes: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching quotes: {e}")
            return None
    
    def get_historical_data(
        self,
        instrument_token: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = "day"
    ) -> Optional[List[Dict]]:
        """
        Get historical data for an instrument
        
        Args:
            instrument_token: Instrument token
            from_date: Start date
            to_date: End date
            interval: Data interval (minute, day, 3minute, 5minute, 10minute, 15minute, 30minute, 60minute)
        
        Returns:
            List of OHLC data
        """
        if not self.access_token:
            logger.error("Access token not set")
            return None
        
        try:
            url = f"{self.base_url}/instruments/historical/{instrument_token}/{interval}"
            params = {
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d')
            }
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('data', {}).get('candles', [])
            return None
        
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    def get_instruments(self, exchange: str = "NSE") -> Optional[List[Dict]]:
        """
        Get list of instruments
        
        Args:
            exchange: Exchange name (NSE, BSE, NFO, etc.)
        
        Returns:
            List of instruments
        """
        try:
            url = f"{self.base_url}/instruments/{exchange}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                # Response is CSV format
                return response.text
            return None
        
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            return None
