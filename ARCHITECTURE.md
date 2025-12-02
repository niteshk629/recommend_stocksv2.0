# System Architecture

## Overview

The Hybrid Stock Recommendation System is designed as a modular, microservices-based architecture that integrates multiple data sources, ML models, and analytics engines to provide comprehensive stock recommendations.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           User Interfaces                                │
├─────────────────────────────────────────────────────────────────────────┤
│  Streamlit UI (Port 8501)   │   FastAPI (Port 8000)   │   CLI Tools    │
└────────────┬─────────────────┴─────────────┬──────────┴────────────────┘
             │                               │
             │                               │
┌────────────┴───────────────────────────────┴──────────────────────────┐
│                        Application Layer                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   Scoring    │  │     ML       │  │   Feature    │                 │
│  │   Engine     │  │   Models     │  │ Engineering  │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
│         │                  │                  │                         │
│         └──────────────────┴──────────────────┘                         │
│                           │                                             │
│                  ┌────────┴─────────┐                                  │
│                  │   ETL Pipeline   │                                  │
│                  └────────┬─────────┘                                  │
└───────────────────────────┼──────────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────────┐
│                  Data Integration Layer                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   Yahoo      │  │    Groww     │  │   Zerodha    │                 │
│  │   Finance    │  │     API      │  │   Kite API   │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│  ┌──────────────┐  ┌──────────────┐                                   │
│  │   News API   │  │   Social     │                                   │
│  │              │  │   Media      │                                   │
│  └──────────────┘  └──────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────────┐
│                    Storage Layer                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   MongoDB    │  │    Redis     │  │  File System │                 │
│  │  (Database)  │  │   (Cache)    │  │  (CSV/PKL)   │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Integration Layer

#### Yahoo Finance Client
- **Purpose**: Historical stock data, fundamentals, real-time prices
- **Features**:
  - OHLCV data fetching
  - Company fundamentals
  - Real-time quote data
  - Parallel processing support
- **File**: `src/data_integration/yahoo_finance.py`

#### Groww API Client
- **Purpose**: Mutual funds and Indian market data
- **Features**:
  - Mutual fund schemes
  - Stock search
  - Real-time quotes
- **File**: `src/data_integration/groww_client.py`

#### Zerodha Kite Client
- **Purpose**: Real-time trading data
- **Features**:
  - Live quotes
  - Historical OHLC data
  - Instrument information
- **File**: `src/data_integration/zerodha_client.py`

### 2. ETL Pipeline

#### Data Extractor
- **Purpose**: Parallel data extraction from multiple sources
- **Features**:
  - ThreadPoolExecutor for concurrent fetching
  - Historical and real-time data extraction
  - Fundamental data aggregation
- **File**: `src/etl/extractors.py`

#### Data Transformer
- **Purpose**: Data cleaning and preprocessing
- **Features**:
  - Missing value handling
  - Outlier detection and treatment
  - Data normalization
  - Returns calculation
- **File**: `src/etl/transformers.py`

#### Data Loader
- **Purpose**: Persist processed data
- **Features**:
  - CSV and Parquet support
  - Metadata management
  - Batch operations
- **File**: `src/etl/loaders.py`

### 3. Feature Engineering

#### Technical Indicators
- **Purpose**: Calculate technical analysis indicators
- **Indicators**:
  - Moving Averages (SMA, EMA)
  - Momentum (RSI, Stochastic)
  - Trend (MACD, ADX)
  - Volatility (Bollinger Bands, ATR)
  - Volume (OBV)
- **File**: `src/feature_engineering/technical_indicators.py`

#### Sentiment Analyzer
- **Purpose**: Analyze sentiment from news and social media
- **Features**:
  - TextBlob for quick sentiment
  - News API integration
  - Aggregated sentiment scoring
  - Confidence weighting
- **File**: `src/feature_engineering/sentiment_analyzer.py`

### 4. ML Models

#### Prophet Model
- **Purpose**: Time series forecasting
- **Features**:
  - Seasonal decomposition
  - Holiday effects
  - Trend changepoint detection
  - Confidence intervals
- **File**: `src/ml_models/prophet_model.py`

#### XGBoost Model
- **Purpose**: Price prediction with gradient boosting
- **Features**:
  - Feature importance analysis
  - Cross-validation
  - Lag feature engineering
  - Model persistence
- **File**: `src/ml_models/xgboost_model.py`

#### FinBERT Model
- **Purpose**: Financial sentiment analysis
- **Features**:
  - Transformer-based NLP
  - Financial domain-specific
  - Batch processing
  - GPU support
- **File**: `src/ml_models/finbert_model.py`

### 5. Scoring Engine

#### Composite Scorer
- **Purpose**: Aggregate multiple signals into recommendations
- **Scoring Components**:
  - Technical Analysis (30% weight)
  - Fundamental Analysis (20% weight)
  - Sentiment Analysis (20% weight)
  - ML Predictions (30% weight)
- **Recommendations**: Strong Buy, Buy, Hold, Sell
- **File**: `src/scoring/scoring_engine.py`

### 6. User Interfaces

#### Streamlit UI
- **Purpose**: Interactive web dashboard
- **Features**:
  - Real-time chart updates
  - Plotly visualizations
  - Multi-tab interface
  - Caching for performance
- **Port**: 8501
- **File**: `src/ui/app.py`

#### FastAPI
- **Purpose**: RESTful API for programmatic access
- **Endpoints**:
  - `/api/analyze` - Single stock analysis
  - `/api/recommend` - Bulk recommendations
  - `/api/sentiment/{symbol}` - Sentiment analysis
  - `/api/technical/{symbol}` - Technical indicators
  - `/api/etl/run` - Trigger ETL pipeline
- **Port**: 8000
- **Documentation**: Auto-generated at `/docs`
- **File**: `src/api/main.py`

## Data Flow

### Analysis Pipeline
```
User Request
    ↓
Data Fetch (Yahoo Finance, Groww, Zerodha)
    ↓
ETL Pipeline (Extract → Transform → Load)
    ↓
Feature Engineering (Technical + Sentiment)
    ↓
ML Models (Prophet + XGBoost + FinBERT)
    ↓
Scoring Engine (Composite Score)
    ↓
Recommendation (Strong Buy/Buy/Hold/Sell)
    ↓
User Interface (Streamlit/API)
```

### Caching Strategy
- **Redis**: API responses, sentiment scores
- **Streamlit**: DataFrame caching with TTL
- **File System**: Historical data, trained models

## Deployment Architecture

### Docker Compose Services
```yaml
services:
  - streamlit:    # UI Service (port 8501)
  - api:          # FastAPI Service (port 8000)
  - mongodb:      # Database (port 27017)
  - redis:        # Cache (port 6379)
```

### CI/CD Pipeline
```
Git Push
    ↓
GitHub Actions / Jenkins
    ↓
Code Quality Checks (flake8, pylint)
    ↓
Unit Tests (pytest)
    ↓
Security Scan (safety, bandit)
    ↓
Docker Build
    ↓
Push to Registry
    ↓
Deploy to Staging
    ↓
Manual Approval
    ↓
Deploy to Production
```

## Scalability Considerations

### Horizontal Scaling
- Multiple Streamlit instances behind load balancer
- FastAPI workers with uvicorn
- MongoDB replica sets
- Redis cluster mode

### Performance Optimization
- Parallel data fetching with ThreadPoolExecutor
- Async operations in FastAPI
- Data caching with Redis
- Model caching in memory
- Batch processing for bulk operations

### Monitoring & Observability
- Application logs (Python logging)
- Health check endpoints
- Metrics collection (Prometheus compatible)
- Error tracking
- Performance monitoring

## Security

### API Security
- API key authentication
- Rate limiting
- CORS configuration
- Input validation
- SQL injection prevention

### Data Security
- Environment variable management
- Secrets in .env files
- Docker secrets for production
- HTTPS in production
- Database authentication

## Technology Stack

### Backend
- Python 3.10+
- FastAPI (async web framework)
- Streamlit (UI framework)

### Data Processing
- Pandas (data manipulation)
- NumPy (numerical computing)
- yfinance (Yahoo Finance API)

### Machine Learning
- Prophet (time series)
- XGBoost (gradient boosting)
- Transformers (FinBERT)
- scikit-learn (utilities)

### Storage
- MongoDB (NoSQL database)
- Redis (in-memory cache)
- Parquet/CSV (file storage)

### DevOps
- Docker (containerization)
- Docker Compose (orchestration)
- Jenkins (CI/CD)
- GitHub Actions (CI/CD)

### Monitoring
- Python logging
- Health checks
- Container monitoring

## Future Enhancements

### Planned Features
1. Real-time WebSocket updates
2. Portfolio optimization
3. Backtesting framework
4. Risk management module
5. Options trading analysis
6. Mobile application
7. Email/SMS notifications
8. Multi-language support
9. Advanced charting with TradingView
10. Social trading features

### Technical Improvements
1. GraphQL API
2. Kubernetes deployment
3. Microservices architecture
4. Event-driven processing
5. Distributed tracing
6. Advanced caching strategies
7. Machine learning model versioning
8. A/B testing framework
9. Feature flags
10. Blue-green deployments
