"""Tests for Data Integration Module"""
import pytest
from src.data_integration import YahooFinanceClient


class TestYahooFinanceClient:
    """Test Yahoo Finance Client"""
    
    def test_initialization(self):
        """Test client initialization"""
        client = YahooFinanceClient()
        assert client is not None
        assert isinstance(client.cache, dict)
    
    def test_get_historical_data(self):
        """Test historical data fetching"""
        client = YahooFinanceClient()
        df = client.get_historical_data('AAPL', period='5d')
        
        if df is not None:
            assert not df.empty
            assert 'Close' in df.columns
            assert 'Volume' in df.columns
    
    def test_get_info(self):
        """Test stock info fetching"""
        client = YahooFinanceClient()
        info = client.get_info('AAPL')
        
        assert isinstance(info, dict)
    
    def test_invalid_symbol(self):
        """Test handling of invalid symbol"""
        client = YahooFinanceClient()
        df = client.get_historical_data('INVALID_SYMBOL_XYZ', period='1d')
        
        assert df is None or df.empty
