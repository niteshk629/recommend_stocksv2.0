"""Tests for Scoring Engine"""
import pytest
import pandas as pd
import numpy as np
from src.scoring import ScoringEngine
from src.feature_engineering import TechnicalIndicators


class TestScoringEngine:
    """Test Scoring Engine"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data with indicators"""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        df = pd.DataFrame({
            'Open': np.random.uniform(100, 150, 100),
            'High': np.random.uniform(150, 200, 100),
            'Low': np.random.uniform(50, 100, 100),
            'Close': np.random.uniform(100, 150, 100),
            'Volume': np.random.uniform(1000000, 5000000, 100)
        }, index=dates)
        
        # Add technical indicators
        df = TechnicalIndicators.calculate_all_indicators(df)
        
        return df
    
    @pytest.fixture
    def sample_info(self):
        """Create sample stock info"""
        return {
            'forwardPE': 25.5,
            'pegRatio': 1.2,
            'debtToEquity': 45.3,
            'returnOnEquity': 0.18,
            'profitMargins': 0.22,
            'revenueGrowth': 0.15
        }
    
    def test_initialization(self):
        """Test engine initialization"""
        engine = ScoringEngine()
        
        assert engine is not None
        assert 'technical' in engine.weights
        assert 'strong_buy' in engine.thresholds
    
    def test_calculate_technical_score(self, sample_data):
        """Test technical score calculation"""
        engine = ScoringEngine()
        score = engine.calculate_technical_score(sample_data)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_calculate_fundamental_score(self, sample_info):
        """Test fundamental score calculation"""
        engine = ScoringEngine()
        score = engine.calculate_fundamental_score(sample_info)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_calculate_composite_score(self, sample_data, sample_info):
        """Test composite score calculation"""
        engine = ScoringEngine()
        result = engine.calculate_composite_score('TEST', sample_data, sample_info)
        
        assert 'composite_score' in result
        assert 'recommendation' in result
        assert 'technical_score' in result
        assert 'fundamental_score' in result
        assert 'sentiment_score' in result
        assert 'ml_score' in result
        
        assert 0 <= result['composite_score'] <= 100
        assert result['recommendation'] in ['STRONG BUY', 'BUY', 'HOLD', 'SELL']
