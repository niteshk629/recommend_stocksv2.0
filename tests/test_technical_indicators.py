"""Tests for Technical Indicators"""
import pytest
import pandas as pd
import numpy as np
from src.feature_engineering import TechnicalIndicators


class TestTechnicalIndicators:
    """Test Technical Indicators calculations"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data"""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        df = pd.DataFrame({
            'Open': np.random.uniform(100, 150, 100),
            'High': np.random.uniform(150, 200, 100),
            'Low': np.random.uniform(50, 100, 100),
            'Close': np.random.uniform(100, 150, 100),
            'Volume': np.random.uniform(1000000, 5000000, 100)
        }, index=dates)
        
        return df
    
    def test_calculate_sma(self, sample_data):
        """Test SMA calculation"""
        result = TechnicalIndicators.calculate_sma(sample_data, [20])
        
        assert 'SMA_20' in result.columns
        assert not result['SMA_20'].isna().all()
    
    def test_calculate_rsi(self, sample_data):
        """Test RSI calculation"""
        result = TechnicalIndicators.calculate_rsi(sample_data)
        
        assert 'RSI' in result.columns
        # RSI should be between 0 and 100
        valid_rsi = result['RSI'].dropna()
        if len(valid_rsi) > 0:
            assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()
    
    def test_calculate_macd(self, sample_data):
        """Test MACD calculation"""
        result = TechnicalIndicators.calculate_macd(sample_data)
        
        assert 'MACD' in result.columns
        assert 'MACD_signal' in result.columns
        assert 'MACD_hist' in result.columns
    
    def test_calculate_bollinger_bands(self, sample_data):
        """Test Bollinger Bands calculation"""
        result = TechnicalIndicators.calculate_bollinger_bands(sample_data)
        
        assert 'BB_upper' in result.columns
        assert 'BB_middle' in result.columns
        assert 'BB_lower' in result.columns
    
    def test_calculate_all_indicators(self, sample_data):
        """Test calculating all indicators"""
        result = TechnicalIndicators.calculate_all_indicators(sample_data)
        
        # Check that multiple indicators are present
        expected_indicators = ['SMA_20', 'RSI', 'MACD', 'BB_upper']
        for indicator in expected_indicators:
            assert indicator in result.columns
