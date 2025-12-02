#!/usr/bin/env python3
"""
Example usage of the Stock Recommendation System
"""
import logging
from src.data_integration import YahooFinanceClient
from src.feature_engineering import TechnicalIndicators, SentimentAnalyzer
from src.ml_models import ProphetPredictor, XGBoostPredictor
from src.scoring import ScoringEngine
from src.etl import ETLPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_analysis():
    """Example: Basic stock analysis"""
    print("\n" + "="*60)
    print("Example 1: Basic Stock Analysis")
    print("="*60 + "\n")
    
    # Initialize client
    client = YahooFinanceClient()
    
    # Fetch data
    symbol = 'AAPL'
    print(f"Fetching data for {symbol}...")
    df = client.get_historical_data(symbol, period='1y')
    info = client.get_info(symbol)
    
    if df is not None:
        print(f"Fetched {len(df)} days of data")
        print(f"\nCurrent Price: ${df['Close'].iloc[-1]:.2f}")
        print(f"52W High: ${df['High'].max():.2f}")
        print(f"52W Low: ${df['Low'].min():.2f}")
        
        if info:
            print(f"\nCompany: {info.get('longName', 'N/A')}")
            print(f"Sector: {info.get('sector', 'N/A')}")
            print(f"Market Cap: ${info.get('marketCap', 0) / 1e9:.2f}B")
    else:
        print("Failed to fetch data")


def example_technical_analysis():
    """Example: Technical analysis with indicators"""
    print("\n" + "="*60)
    print("Example 2: Technical Analysis")
    print("="*60 + "\n")
    
    # Fetch data
    client = YahooFinanceClient()
    symbol = 'GOOGL'
    print(f"Analyzing {symbol}...")
    df = client.get_historical_data(symbol, period='6mo')
    
    if df is not None:
        # Calculate indicators
        print("Calculating technical indicators...")
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Display latest indicators
        latest = df_with_indicators.iloc[-1]
        print(f"\nTechnical Indicators for {symbol}:")
        print(f"RSI: {latest['RSI']:.2f}")
        print(f"MACD: {latest['MACD']:.4f}")
        print(f"MACD Signal: {latest['MACD_signal']:.4f}")
        print(f"SMA 20: ${latest['SMA_20']:.2f}")
        print(f"SMA 50: ${latest['SMA_50']:.2f}")
        print(f"Bollinger Upper: ${latest['BB_upper']:.2f}")
        print(f"Bollinger Lower: ${latest['BB_lower']:.2f}")


def example_sentiment_analysis():
    """Example: Sentiment analysis"""
    print("\n" + "="*60)
    print("Example 3: Sentiment Analysis")
    print("="*60 + "\n")
    
    analyzer = SentimentAnalyzer()
    symbol = 'TSLA'
    
    print(f"Analyzing sentiment for {symbol}...")
    print("(Note: Requires NEWS_API_KEY in .env file)")
    
    # Get sentiment score
    score = analyzer.get_sentiment_score(symbol)
    print(f"\nSentiment Score: {score:.2f}/100")
    
    if score > 60:
        print("Overall Sentiment: Positive")
    elif score > 40:
        print("Overall Sentiment: Neutral")
    else:
        print("Overall Sentiment: Negative")


def example_ml_predictions():
    """Example: ML predictions with Prophet and XGBoost"""
    print("\n" + "="*60)
    print("Example 4: ML Predictions")
    print("="*60 + "\n")
    
    # Fetch data
    client = YahooFinanceClient()
    symbol = 'MSFT'
    print(f"Making predictions for {symbol}...")
    df = client.get_historical_data(symbol, period='1y')
    
    if df is not None:
        # Prophet predictions
        print("\nTraining Prophet model...")
        prophet = ProphetPredictor()
        prophet.train(df)
        predictions = prophet.predict(periods=30)
        
        if predictions is not None:
            print(f"Next 7 days predictions:")
            for i in range(min(7, len(predictions))):
                row = predictions.iloc[i]
                print(f"  {row['Date'].strftime('%Y-%m-%d')}: ${row['Predicted']:.2f}")
        
        # XGBoost predictions
        print("\nTraining XGBoost model...")
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        xgboost = XGBoostPredictor()
        metrics = xgboost.train(df_with_indicators)
        
        if metrics:
            print(f"\nModel Performance:")
            print(f"  R² Score: {metrics['r2']:.4f}")
            print(f"  RMSE: ${metrics['rmse']:.2f}")
            print(f"  MAE: ${metrics['mae']:.2f}")


def example_composite_scoring():
    """Example: Complete analysis with composite scoring"""
    print("\n" + "="*60)
    print("Example 5: Composite Recommendation")
    print("="*60 + "\n")
    
    # Fetch data
    client = YahooFinanceClient()
    symbol = 'NVDA'
    print(f"Generating recommendation for {symbol}...")
    
    df = client.get_historical_data(symbol, period='1y')
    info = client.get_info(symbol)
    
    if df is not None:
        # Calculate indicators
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Train models
        print("Training ML models...")
        prophet = ProphetPredictor()
        prophet.train(df)
        
        xgboost = XGBoostPredictor()
        xgboost.train(df_with_indicators)
        
        # Calculate scores
        print("Calculating composite scores...")
        engine = ScoringEngine()
        scores = engine.calculate_composite_score(
            symbol, df_with_indicators, info, prophet, xgboost
        )
        
        # Display results
        print(f"\n{'='*50}")
        print(f"RECOMMENDATION FOR {symbol}")
        print(f"{'='*50}")
        print(f"\nComposite Score: {scores['composite_score']:.1f}/100")
        print(f"Recommendation: {scores['recommendation']}")
        print(f"\nScore Breakdown:")
        print(f"  Technical:    {scores['technical_score']:.1f}/100")
        print(f"  Fundamental:  {scores['fundamental_score']:.1f}/100")
        print(f"  Sentiment:    {scores['sentiment_score']:.1f}/100")
        print(f"  ML Prediction: {scores['ml_score']:.1f}/100")
        print(f"{'='*50}\n")


def example_etl_pipeline():
    """Example: Running ETL pipeline"""
    print("\n" + "="*60)
    print("Example 6: ETL Pipeline")
    print("="*60 + "\n")
    
    # Run ETL for multiple symbols
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    print(f"Running ETL pipeline for: {', '.join(symbols)}")
    
    pipeline = ETLPipeline(max_workers=4, output_dir='data')
    processed_data = pipeline.run(symbols, period='1y', save_format='csv')
    
    print(f"\nProcessed {len(processed_data)} stocks")
    print(f"Data saved to 'data/' directory")


def main():
    """Run all examples"""
    examples = [
        ("Basic Analysis", example_basic_analysis),
        ("Technical Analysis", example_technical_analysis),
        ("Sentiment Analysis", example_sentiment_analysis),
        ("ML Predictions", example_ml_predictions),
        ("Composite Scoring", example_composite_scoring),
        ("ETL Pipeline", example_etl_pipeline),
    ]
    
    print("\n" + "="*60)
    print("Stock Recommendation System - Example Usage")
    print("="*60)
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Run all examples")
    
    choice = input("\nSelect example to run (0-6): ").strip()
    
    if choice == '0':
        for name, func in examples:
            try:
                func()
            except Exception as e:
                logger.error(f"Error in {name}: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        try:
            examples[int(choice)-1][1]()
        except Exception as e:
            logger.error(f"Error: {e}")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
