"""Prophet Time Series Model"""
import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict
from prophet import Prophet

logger = logging.getLogger(__name__)


class ProphetPredictor:
    """Time series forecasting using Prophet"""
    
    def __init__(
        self,
        changepoint_prior_scale: float = 0.05,
        seasonality_mode: str = 'multiplicative'
    ):
        self.changepoint_prior_scale = changepoint_prior_scale
        self.seasonality_mode = seasonality_mode
        self.model = None
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for Prophet (requires 'ds' and 'y' columns)
        
        Args:
            df: Input DataFrame with DatetimeIndex and 'Close' column
        
        Returns:
            DataFrame formatted for Prophet
        """
        data = df.reset_index()
        
        # Ensure we have the right columns
        if 'Date' in data.columns:
            data = data.rename(columns={'Date': 'ds', 'Close': 'y'})
        elif 'index' in data.columns:
            data = data.rename(columns={'index': 'ds', 'Close': 'y'})
        else:
            data['ds'] = data.index
            data = data.rename(columns={'Close': 'y'})
        
        return data[['ds', 'y']]
    
    def train(self, df: pd.DataFrame) -> bool:
        """
        Train Prophet model
        
        Args:
            df: Training data
        
        Returns:
            True if training successful
        """
        try:
            # Prepare data
            prophet_df = self.prepare_data(df)
            
            # Initialize and train model
            self.model = Prophet(
                changepoint_prior_scale=self.changepoint_prior_scale,
                seasonality_mode=self.seasonality_mode,
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=True
            )
            
            # Suppress Prophet logging
            self.model.fit(prophet_df)
            
            logger.info("Prophet model trained successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error training Prophet model: {e}")
            return False
    
    def predict(self, periods: int = 30) -> Optional[pd.DataFrame]:
        """
        Make predictions
        
        Args:
            periods: Number of periods to forecast
        
        Returns:
            DataFrame with predictions
        """
        if self.model is None:
            logger.error("Model not trained")
            return None
        
        try:
            # Create future dataframe
            future = self.model.make_future_dataframe(periods=periods)
            
            # Make predictions
            forecast = self.model.predict(future)
            
            # Select relevant columns
            result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            result = result.rename(columns={
                'ds': 'Date',
                'yhat': 'Predicted',
                'yhat_lower': 'Lower_Bound',
                'yhat_upper': 'Upper_Bound'
            })
            
            logger.info(f"Generated {periods} predictions")
            return result
        
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            return None
    
    def get_trend(self) -> Optional[str]:
        """
        Get overall trend direction
        
        Returns:
            'upward', 'downward', or 'stable'
        """
        if self.model is None:
            return None
        
        try:
            # Get future predictions
            forecast = self.predict(periods=7)
            
            if forecast is None or len(forecast) < 2:
                return None
            
            # Compare first and last prediction
            first_pred = forecast['Predicted'].iloc[0]
            last_pred = forecast['Predicted'].iloc[-1]
            
            change_pct = (last_pred - first_pred) / first_pred * 100
            
            if change_pct > 2:
                return 'upward'
            elif change_pct < -2:
                return 'downward'
            else:
                return 'stable'
        
        except Exception as e:
            logger.error(f"Error getting trend: {e}")
            return None
