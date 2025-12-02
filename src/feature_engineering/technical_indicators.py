"""Technical Indicators Calculator"""
import pandas as pd
import numpy as np
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate various technical indicators"""
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, periods: list = [20, 50, 200]) -> pd.DataFrame:
        """Calculate Simple Moving Averages"""
        result = df.copy()
        for period in periods:
            result[f'SMA_{period}'] = result['Close'].rolling(window=period).mean()
        return result
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, periods: list = [12, 26]) -> pd.DataFrame:
        """Calculate Exponential Moving Averages"""
        result = df.copy()
        for period in periods:
            result[f'EMA_{period}'] = result['Close'].ewm(span=period, adjust=False).mean()
        return result
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        result = df.copy()
        
        delta = result['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        result['RSI'] = 100 - (100 / (1 + rs))
        
        return result
    
    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> pd.DataFrame:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        result = df.copy()
        
        exp1 = result['Close'].ewm(span=fast, adjust=False).mean()
        exp2 = result['Close'].ewm(span=slow, adjust=False).mean()
        
        result['MACD'] = exp1 - exp2
        result['MACD_signal'] = result['MACD'].ewm(span=signal, adjust=False).mean()
        result['MACD_hist'] = result['MACD'] - result['MACD_signal']
        
        return result
    
    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std_dev: int = 2
    ) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        result = df.copy()
        
        sma = result['Close'].rolling(window=period).mean()
        std = result['Close'].rolling(window=period).std()
        
        result['BB_upper'] = sma + (std * std_dev)
        result['BB_middle'] = sma
        result['BB_lower'] = sma - (std * std_dev)
        result['BB_width'] = result['BB_upper'] - result['BB_lower']
        
        return result
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average True Range"""
        result = df.copy()
        
        high_low = result['High'] - result['Low']
        high_close = np.abs(result['High'] - result['Close'].shift())
        low_close = np.abs(result['Low'] - result['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        result['ATR'] = true_range.rolling(window=period).mean()
        
        return result
    
    @staticmethod
    def calculate_stochastic(
        df: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3
    ) -> pd.DataFrame:
        """Calculate Stochastic Oscillator"""
        result = df.copy()
        
        low_min = result['Low'].rolling(window=k_period).min()
        high_max = result['High'].rolling(window=k_period).max()
        
        result['Stoch_K'] = 100 * (result['Close'] - low_min) / (high_max - low_min)
        result['Stoch_D'] = result['Stoch_K'].rolling(window=d_period).mean()
        
        return result
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate On-Balance Volume"""
        result = df.copy()
        
        obv = [0]
        for i in range(1, len(result)):
            if result['Close'].iloc[i] > result['Close'].iloc[i-1]:
                obv.append(obv[-1] + result['Volume'].iloc[i])
            elif result['Close'].iloc[i] < result['Close'].iloc[i-1]:
                obv.append(obv[-1] - result['Volume'].iloc[i])
            else:
                obv.append(obv[-1])
        
        result['OBV'] = obv
        
        return result
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        result = df.copy()
        
        result = TechnicalIndicators.calculate_sma(result)
        result = TechnicalIndicators.calculate_ema(result)
        result = TechnicalIndicators.calculate_rsi(result)
        result = TechnicalIndicators.calculate_macd(result)
        result = TechnicalIndicators.calculate_bollinger_bands(result)
        result = TechnicalIndicators.calculate_atr(result)
        result = TechnicalIndicators.calculate_stochastic(result)
        result = TechnicalIndicators.calculate_obv(result)
        
        logger.info("Calculated all technical indicators")
        return result
