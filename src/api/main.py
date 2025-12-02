"""FastAPI Application"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime

from ..data_integration import YahooFinanceClient
from ..feature_engineering import TechnicalIndicators, SentimentAnalyzer
from ..ml_models import ProphetPredictor, XGBoostPredictor
from ..scoring import ScoringEngine
from ..etl import ETLPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stock Recommendation API",
    description="API for stock analysis and recommendations",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class StockRequest(BaseModel):
    symbol: str
    period: str = "1y"
    include_predictions: bool = True

class StockResponse(BaseModel):
    symbol: str
    current_price: float
    recommendation: str
    composite_score: float
    technical_score: float
    fundamental_score: float
    sentiment_score: float
    ml_score: float
    timestamp: datetime

class BulkStockRequest(BaseModel):
    symbols: List[str]
    period: str = "1y"

# Initialize clients
yf_client = YahooFinanceClient()
scoring_engine = ScoringEngine()
sentiment_analyzer = SentimentAnalyzer()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Stock Recommendation API",
        "version": "2.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "recommend": "/api/recommend",
            "sentiment": "/api/sentiment/{symbol}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/analyze", response_model=StockResponse)
async def analyze_stock(request: StockRequest):
    """
    Analyze a single stock and return recommendations
    """
    try:
        # Fetch data
        df = yf_client.get_historical_data(request.symbol, period=request.period)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"Data not found for {request.symbol}")
        
        info = yf_client.get_info(request.symbol)
        
        # Calculate indicators
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Train models if predictions requested
        prophet_model = None
        xgboost_model = None
        
        if request.include_predictions:
            prophet_model = ProphetPredictor()
            prophet_model.train(df)
            
            xgboost_model = XGBoostPredictor()
            xgboost_model.train(df_with_indicators)
        
        # Calculate scores
        scores = scoring_engine.calculate_composite_score(
            request.symbol,
            df_with_indicators,
            info,
            prophet_model,
            xgboost_model
        )
        
        return StockResponse(
            symbol=request.symbol,
            current_price=float(df['Close'].iloc[-1]),
            recommendation=scores['recommendation'],
            composite_score=scores['composite_score'],
            technical_score=scores['technical_score'],
            fundamental_score=scores['fundamental_score'],
            sentiment_score=scores['sentiment_score'],
            ml_score=scores['ml_score'],
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error analyzing {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommend")
async def recommend_stocks(request: BulkStockRequest):
    """
    Analyze multiple stocks and return ranked recommendations
    """
    try:
        results = []
        
        for symbol in request.symbols:
            try:
                stock_request = StockRequest(symbol=symbol, period=request.period)
                result = await analyze_stock(stock_request)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        # Sort by composite score
        results.sort(key=lambda x: x.composite_score, reverse=True)
        
        return {
            "recommendations": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in bulk recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    """
    Get sentiment analysis for a stock
    """
    try:
        sentiment = sentiment_analyzer.analyze_stock_sentiment(symbol)
        score = sentiment_analyzer.get_sentiment_score(symbol)
        
        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "score": score,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/technical/{symbol}")
async def get_technical_analysis(symbol: str, period: str = "1y"):
    """
    Get technical analysis for a stock
    """
    try:
        df = yf_client.get_historical_data(symbol, period=period)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"Data not found for {symbol}")
        
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
        
        # Get latest values
        latest = df_with_indicators.iloc[-1]
        
        return {
            "symbol": symbol,
            "current_price": float(latest['Close']),
            "indicators": {
                "RSI": float(latest['RSI']) if 'RSI' in latest else None,
                "MACD": float(latest['MACD']) if 'MACD' in latest else None,
                "SMA_20": float(latest['SMA_20']) if 'SMA_20' in latest else None,
                "SMA_50": float(latest['SMA_50']) if 'SMA_50' in latest else None,
                "SMA_200": float(latest['SMA_200']) if 'SMA_200' in latest else None,
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting technical analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/etl/run")
async def run_etl(background_tasks: BackgroundTasks, symbols: List[str], period: str = "1y"):
    """
    Run ETL pipeline for specified symbols
    """
    def run_pipeline():
        pipeline = ETLPipeline()
        pipeline.run(symbols, period)
    
    background_tasks.add_task(run_pipeline)
    
    return {
        "message": "ETL pipeline started",
        "symbols": symbols,
        "period": period,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
