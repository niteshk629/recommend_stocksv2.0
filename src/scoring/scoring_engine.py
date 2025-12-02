"""Composite Scoring Engine"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from ..feature_engineering import TechnicalIndicators, SentimentAnalyzer
from ..ml_models import ProphetPredictor, XGBoostPredictor, FinBERTAnalyzer

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Composite scoring engine for stock recommendations"""
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, float]] = None
    ):
        # Default weights
        self.weights = weights or {
            'technical': 0.3,
            'fundamental': 0.2,
            'sentiment': 0.2,
            'ml_prediction': 0.3
        }
        
        # Default thresholds
        self.thresholds = thresholds or {
            'strong_buy': 80,
            'buy': 60,
            'hold': 40,
            'sell': 20
        }
        
        # Initialize components
        self.technical_indicators = TechnicalIndicators()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def calculate_technical_score(self, df: pd.DataFrame) -> float:
        """
        Calculate technical analysis score (0-100)
        
        Args:
            df: DataFrame with technical indicators
        
        Returns:
            Technical score
        """
        score = 50.0  # Base score
        
        try:
            if df.empty:
                return score
            
            latest = df.iloc[-1]
            
            # RSI Score (30-70 is normal)
            if 'RSI' in df.columns:
                rsi = latest['RSI']
                if rsi < 30:
                    score += 15  # Oversold - good buying opportunity
                elif rsi > 70:
                    score -= 15  # Overbought - caution
            
            # MACD Score
            if 'MACD' in df.columns and 'MACD_signal' in df.columns:
                if latest['MACD'] > latest['MACD_signal']:
                    score += 10  # Bullish signal
                else:
                    score -= 10  # Bearish signal
            
            # Moving Average Score
            if 'Close' in df.columns and 'SMA_50' in df.columns and 'SMA_200' in df.columns:
                price = latest['Close']
                sma_50 = latest['SMA_50']
                sma_200 = latest['SMA_200']
                
                if price > sma_50 > sma_200:
                    score += 15  # Strong uptrend
                elif price > sma_50:
                    score += 10  # Uptrend
                elif price < sma_50:
                    score -= 10  # Downtrend
            
            # Bollinger Bands Score
            if 'Close' in df.columns and 'BB_lower' in df.columns and 'BB_upper' in df.columns:
                price = latest['Close']
                bb_lower = latest['BB_lower']
                bb_upper = latest['BB_upper']
                
                if price < bb_lower:
                    score += 10  # Near lower band - potential buy
                elif price > bb_upper:
                    score -= 10  # Near upper band - potential sell
            
            # Volume trend
            if 'Volume' in df.columns and len(df) > 20:
                recent_volume = df['Volume'].tail(5).mean()
                avg_volume = df['Volume'].tail(20).mean()
                
                if recent_volume > avg_volume * 1.5:
                    score += 5  # High volume - strong interest
            
            # Ensure score is within bounds
            score = max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculating technical score: {e}")
        
        return score
    
    def calculate_fundamental_score(self, info: Dict) -> float:
        """
        Calculate fundamental analysis score (0-100)
        
        Args:
            info: Stock information dictionary
        
        Returns:
            Fundamental score
        """
        score = 50.0  # Base score
        
        try:
            # P/E Ratio (lower is generally better, but depends on sector)
            if 'forwardPE' in info and info['forwardPE']:
                pe = info['forwardPE']
                if pe < 15:
                    score += 15
                elif pe < 25:
                    score += 5
                elif pe > 40:
                    score -= 10
            
            # PEG Ratio (< 1 is good value)
            if 'pegRatio' in info and info['pegRatio']:
                peg = info['pegRatio']
                if peg < 1:
                    score += 10
                elif peg > 2:
                    score -= 5
            
            # Debt to Equity (lower is better)
            if 'debtToEquity' in info and info['debtToEquity']:
                de = info['debtToEquity']
                if de < 50:
                    score += 10
                elif de > 100:
                    score -= 10
            
            # ROE (higher is better)
            if 'returnOnEquity' in info and info['returnOnEquity']:
                roe = info['returnOnEquity']
                if roe > 0.15:
                    score += 10
                elif roe > 0.10:
                    score += 5
            
            # Profit Margin
            if 'profitMargins' in info and info['profitMargins']:
                margin = info['profitMargins']
                if margin > 0.20:
                    score += 10
                elif margin > 0.10:
                    score += 5
            
            # Revenue Growth
            if 'revenueGrowth' in info and info['revenueGrowth']:
                growth = info['revenueGrowth']
                if growth > 0.20:
                    score += 10
                elif growth > 0.10:
                    score += 5
                elif growth < 0:
                    score -= 10
            
            # Ensure score is within bounds
            score = max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculating fundamental score: {e}")
        
        return score
    
    def calculate_sentiment_score(self, symbol: str) -> float:
        """
        Calculate sentiment analysis score (0-100)
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Sentiment score
        """
        try:
            score = self.sentiment_analyzer.get_sentiment_score(symbol)
            return score
        except Exception as e:
            logger.error(f"Error calculating sentiment score: {e}")
            return 50.0
    
    def calculate_ml_score(
        self,
        df: pd.DataFrame,
        prophet_predictor: Optional[ProphetPredictor] = None,
        xgboost_predictor: Optional[XGBoostPredictor] = None
    ) -> float:
        """
        Calculate ML prediction score (0-100)
        
        Args:
            df: Historical data
            prophet_predictor: Prophet model
            xgboost_predictor: XGBoost model
        
        Returns:
            ML prediction score
        """
        score = 50.0
        
        try:
            current_price = df['Close'].iloc[-1]
            
            # Prophet prediction
            if prophet_predictor and prophet_predictor.model:
                trend = prophet_predictor.get_trend()
                if trend == 'upward':
                    score += 15
                elif trend == 'downward':
                    score -= 15
            
            # XGBoost prediction
            if xgboost_predictor and xgboost_predictor.model:
                predictions = xgboost_predictor.predict(df)
                if predictions is not None and len(predictions) > 0:
                    predicted_price = predictions[-1]
                    price_change = (predicted_price - current_price) / current_price * 100
                    
                    if price_change > 5:
                        score += 15
                    elif price_change > 2:
                        score += 10
                    elif price_change < -5:
                        score -= 15
                    elif price_change < -2:
                        score -= 10
            
            # Ensure score is within bounds
            score = max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculating ML score: {e}")
        
        return score
    
    def calculate_composite_score(
        self,
        symbol: str,
        df: pd.DataFrame,
        info: Dict,
        prophet_predictor: Optional[ProphetPredictor] = None,
        xgboost_predictor: Optional[XGBoostPredictor] = None
    ) -> Dict[str, float]:
        """
        Calculate composite score combining all factors
        
        Args:
            symbol: Stock symbol
            df: Historical data with technical indicators
            info: Fundamental information
            prophet_predictor: Prophet model
            xgboost_predictor: XGBoost model
        
        Returns:
            Dictionary with scores and recommendation
        """
        # Calculate individual scores
        technical_score = self.calculate_technical_score(df)
        fundamental_score = self.calculate_fundamental_score(info)
        sentiment_score = self.calculate_sentiment_score(symbol)
        ml_score = self.calculate_ml_score(df, prophet_predictor, xgboost_predictor)
        
        # Calculate weighted composite score
        composite_score = (
            technical_score * self.weights['technical'] +
            fundamental_score * self.weights['fundamental'] +
            sentiment_score * self.weights['sentiment'] +
            ml_score * self.weights['ml_prediction']
        )
        
        # Determine recommendation
        if composite_score >= self.thresholds['strong_buy']:
            recommendation = 'STRONG BUY'
        elif composite_score >= self.thresholds['buy']:
            recommendation = 'BUY'
        elif composite_score >= self.thresholds['hold']:
            recommendation = 'HOLD'
        else:
            recommendation = 'SELL'
        
        return {
            'symbol': symbol,
            'composite_score': round(composite_score, 2),
            'technical_score': round(technical_score, 2),
            'fundamental_score': round(fundamental_score, 2),
            'sentiment_score': round(sentiment_score, 2),
            'ml_score': round(ml_score, 2),
            'recommendation': recommendation
        }
