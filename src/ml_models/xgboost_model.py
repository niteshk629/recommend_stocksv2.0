"""XGBoost Prediction Model"""
import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, Tuple
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

logger = logging.getLogger(__name__)


class XGBoostPredictor:
    """Stock price prediction using XGBoost"""
    
    def __init__(
        self,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        n_estimators: int = 100,
        objective: str = 'reg:squarederror'
    ):
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators
        self.objective = objective
        self.model = None
        self.feature_names = []
    
    def create_features(self, df: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
        """
        Create features for training
        
        Args:
            df: Input DataFrame
            lookback: Number of historical days to use
        
        Returns:
            DataFrame with features
        """
        features = df.copy()
        
        # Lag features
        for i in range(1, lookback + 1):
            features[f'Close_lag_{i}'] = features['Close'].shift(i)
            features[f'Volume_lag_{i}'] = features['Volume'].shift(i)
        
        # Rolling statistics
        for window in [5, 10, 20]:
            features[f'Close_rolling_mean_{window}'] = features['Close'].rolling(window).mean()
            features[f'Close_rolling_std_{window}'] = features['Close'].rolling(window).std()
            features[f'Volume_rolling_mean_{window}'] = features['Volume'].rolling(window).mean()
        
        # Price changes
        features['price_change'] = features['Close'].pct_change()
        features['price_change_1d'] = features['Close'].pct_change(1)
        features['price_change_5d'] = features['Close'].pct_change(5)
        
        # Target: Next day's closing price
        features['target'] = features['Close'].shift(-1)
        
        # Drop rows with NaN
        features = features.dropna()
        
        return features
    
    def prepare_train_data(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare training and testing data
        
        Args:
            df: Input DataFrame with features
            test_size: Proportion of data for testing
        
        Returns:
            X_train, X_test, y_train, y_test
        """
        # Create features
        features = self.create_features(df)
        
        # Separate features and target
        feature_cols = [col for col in features.columns if col not in ['target', 'Date']]
        self.feature_names = feature_cols
        
        X = features[feature_cols].values
        y = features['target'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        return X_train, X_test, y_train, y_test
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2) -> Dict[str, float]:
        """
        Train XGBoost model
        
        Args:
            df: Training data
            test_size: Proportion for testing
        
        Returns:
            Dictionary with training metrics
        """
        try:
            # Prepare data
            X_train, X_test, y_train, y_test = self.prepare_train_data(df, test_size)
            
            # Initialize and train model
            self.model = xgb.XGBRegressor(
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                n_estimators=self.n_estimators,
                objective=self.objective,
                random_state=42
            )
            
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                verbose=False
            )
            
            # Calculate metrics
            y_pred = self.model.predict(X_test)
            
            metrics = {
                'mse': mean_squared_error(y_test, y_pred),
                'mae': mean_absolute_error(y_test, y_pred),
                'r2': r2_score(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
            }
            
            logger.info(f"XGBoost model trained - R2: {metrics['r2']:.4f}, RMSE: {metrics['rmse']:.4f}")
            return metrics
        
        except Exception as e:
            logger.error(f"Error training XGBoost model: {e}")
            return {}
    
    def predict(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Make predictions
        
        Args:
            df: Input data
        
        Returns:
            Array of predictions
        """
        if self.model is None:
            logger.error("Model not trained")
            return None
        
        try:
            # Create features
            features = self.create_features(df)
            X = features[self.feature_names].values
            
            # Make predictions
            predictions = self.model.predict(X)
            
            logger.info(f"Generated {len(predictions)} predictions")
            return predictions
        
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            return None
    
    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Get feature importance
        
        Returns:
            DataFrame with feature importances
        """
        if self.model is None:
            return None
        
        try:
            importance = self.model.feature_importances_
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importance
            })
            feature_importance = feature_importance.sort_values('importance', ascending=False)
            
            return feature_importance
        
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return None
