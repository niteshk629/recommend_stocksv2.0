# Hybrid Stock Recommendation System v2.0

A comprehensive stock analysis and recommendation system that integrates multiple data sources, machine learning models, and real-time analytics.

## Features

### Data Integration
- **Yahoo Finance API**: Historical stock data and fundamentals
- **Groww API**: Real-time trading and mutual fund data
- **Zerodha Kite API**: Real-time market data and trading
- **News & Social Media**: Sentiment analysis from multiple sources

### ETL Pipeline
- Modular extraction, transformation, and loading
- Parallel data processing with thread pool
- Data cleaning and outlier handling
- Support for CSV and Parquet formats

### Feature Engineering
- **Technical Indicators**: 
  - SMA, EMA, RSI, MACD
  - Bollinger Bands, ATR, Stochastic
  - On-Balance Volume (OBV)
- **Sentiment Analysis**:
  - News sentiment via TextBlob
  - FinBERT for financial text analysis
  - Aggregated sentiment scoring

### ML Models
- **Prophet**: Time series forecasting with seasonality
- **XGBoost**: Gradient boosting for price prediction
- **FinBERT**: Transformer-based sentiment analysis

### Composite Scoring Engine
- Weighted scoring combining:
  - Technical Analysis (30%)
  - Fundamental Analysis (20%)
  - Sentiment Analysis (20%)
  - ML Predictions (30%)
- Recommendation levels: Strong Buy, Buy, Hold, Sell

### User Interfaces
- **Streamlit UI**: Interactive web dashboard with Plotly charts
- **FastAPI**: RESTful API for programmatic access
- **TradingView Integration**: Advanced charting capabilities

### Infrastructure
- **Dockerized Microservices**: Containerized deployment
- **MongoDB**: Data persistence
- **Redis**: Caching layer
- **CI/CD**: Jenkins pipeline with automated testing

## Installation

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- MongoDB (optional, for persistence)
- Redis (optional, for caching)

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/niteshk629/recommend_stocksv2.0.git
cd recommend_stocksv2.0
```

2. Set up environment:
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run with Docker Compose:
```bash
docker-compose up -d
```

5. Access the applications:
- Streamlit UI: http://localhost:8501
- FastAPI: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit UI
streamlit run src/ui/app.py

# Run FastAPI (in another terminal)
uvicorn src.api.main:app --reload
```

## Usage

### Streamlit UI

1. Enter a stock symbol (e.g., AAPL, GOOGL, MSFT)
2. Select analysis period
3. Choose analysis types to include
4. Click "Analyze Stock"
5. View comprehensive analysis with charts and recommendations

### API Endpoints

#### Analyze Single Stock
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "period": "1y", "include_predictions": true}'
```

#### Bulk Recommendations
```bash
curl -X POST "http://localhost:8000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "GOOGL", "MSFT"], "period": "1y"}'
```

#### Get Sentiment
```bash
curl "http://localhost:8000/api/sentiment/AAPL"
```

#### Technical Analysis
```bash
curl "http://localhost:8000/api/technical/AAPL?period=1y"
```

### Python API

```python
from src.data_integration import YahooFinanceClient
from src.feature_engineering import TechnicalIndicators
from src.scoring import ScoringEngine

# Fetch data
client = YahooFinanceClient()
df = client.get_historical_data('AAPL', period='1y')
info = client.get_info('AAPL')

# Calculate indicators
df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)

# Get recommendation
engine = ScoringEngine()
scores = engine.calculate_composite_score('AAPL', df_with_indicators, info)
print(f"Recommendation: {scores['recommendation']}")
print(f"Composite Score: {scores['composite_score']}")
```

## Architecture

```
recommend_stocksv2.0/
├── src/
│   ├── data_integration/    # Data fetching from APIs
│   ├── etl/                 # ETL pipeline
│   ├── feature_engineering/ # Technical & sentiment features
│   ├── ml_models/          # Prophet, XGBoost, FinBERT
│   ├── scoring/            # Composite scoring engine
│   ├── api/                # FastAPI application
│   └── ui/                 # Streamlit application
├── config/                 # Configuration files
├── docker/                 # Docker configurations
├── tests/                  # Test suite
├── Dockerfile              # Main Docker image
├── docker-compose.yml      # Multi-container setup
├── Jenkinsfile            # CI/CD pipeline
└── requirements.txt        # Python dependencies
```

## Configuration

Edit `config/config.yaml` to customize:

```yaml
scoring:
  weights:
    technical: 0.3
    fundamental: 0.2
    sentiment: 0.2
    ml_prediction: 0.3
  
  thresholds:
    strong_buy: 80
    buy: 60
    hold: 40
    sell: 20
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_scoring_engine.py -v
```

## CI/CD Pipeline

The Jenkins pipeline includes:
1. Code checkout
2. Environment setup
3. Code quality checks (flake8, pylint)
4. Unit tests with coverage
5. Security scanning (safety, bandit)
6. Docker image build
7. Image testing
8. Push to registry
9. Deployment to staging/production

## API Keys Required

1. **Groww API**: For mutual fund data
2. **Zerodha Kite**: For real-time trading data
3. **News API**: For sentiment analysis from news

Add these to your `.env` file.

## Performance

- Data caching with Redis reduces API calls
- Parallel processing for multiple stocks
- Optimized Docker images with multi-stage builds
- Async operations in FastAPI

## Security

- Environment variables for sensitive data
- API authentication support
- CORS configuration
- Regular security scanning in CI/CD
- Docker security best practices

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: https://github.com/niteshk629/recommend_stocksv2.0/issues

## Acknowledgments

- Yahoo Finance for market data
- Prophet by Facebook for time series forecasting
- XGBoost for gradient boosting
- FinBERT by ProsusAI for financial sentiment
- Streamlit for UI framework
- FastAPI for API framework
