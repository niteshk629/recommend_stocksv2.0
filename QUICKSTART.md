# Quick Start Guide

Get up and running with the Hybrid Stock Recommendation System in minutes!

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (optional, for containerized deployment)
- Git

## Installation Methods

### Method 1: Quick Start with Docker (Recommended)

This is the fastest way to get started without worrying about dependencies.

```bash
# 1. Clone the repository
git clone https://github.com/niteshk629/recommend_stocksv2.0.git
cd recommend_stocksv2.0

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (optional for basic features)

# 3. Start all services
docker-compose up -d

# 4. Access the applications
# - Streamlit UI: http://localhost:8501
# - FastAPI: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Method 2: Manual Setup

For development or if you prefer not to use Docker.

```bash
# 1. Clone the repository
git clone https://github.com/niteshk629/recommend_stocksv2.0.git
cd recommend_stocksv2.0

# 2. Run the setup script
bash scripts/setup.sh

# 3. Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (optional)

# 5. Start the Streamlit UI
streamlit run src/ui/app.py

# In another terminal, start the FastAPI server
source venv/bin/activate
uvicorn src.api.main:app --reload
```

## Your First Analysis

### Using the Streamlit UI

1. Open your browser to http://localhost:8501
2. In the sidebar, enter a stock symbol (e.g., `AAPL`)
3. Select the time period (default: 1 year)
4. Check the analysis options you want to include
5. Click "Analyze Stock"
6. View the comprehensive analysis with charts and recommendations

### Using the API

#### Analyze a Single Stock
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "period": "1y",
    "include_predictions": true
  }'
```

#### Get Multiple Recommendations
```bash
curl -X POST "http://localhost:8000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA"],
    "period": "1y"
  }'
```

#### Get Technical Analysis
```bash
curl "http://localhost:8000/api/technical/AAPL?period=1y"
```

### Using Python

Run the example script to see various features:

```bash
python example_usage.py
```

Or write your own script:

```python
from src.data_integration import YahooFinanceClient
from src.feature_engineering import TechnicalIndicators
from src.scoring import ScoringEngine

# Initialize
client = YahooFinanceClient()
engine = ScoringEngine()

# Fetch data
df = client.get_historical_data('AAPL', period='1y')
info = client.get_info('AAPL')

# Calculate indicators
df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)

# Get recommendation
scores = engine.calculate_composite_score('AAPL', df_with_indicators, info)

print(f"Recommendation: {scores['recommendation']}")
print(f"Score: {scores['composite_score']:.1f}/100")
```

## Configuration

### Basic Configuration

Edit `config/config.yaml` to customize the system:

```yaml
scoring:
  weights:
    technical: 0.3      # Adjust weight of technical analysis
    fundamental: 0.2    # Adjust weight of fundamentals
    sentiment: 0.2      # Adjust weight of sentiment
    ml_prediction: 0.3  # Adjust weight of ML predictions
  
  thresholds:
    strong_buy: 80  # Score threshold for Strong Buy
    buy: 60         # Score threshold for Buy
    hold: 40        # Score threshold for Hold
    sell: 20        # Below this is Sell
```

### API Keys (Optional but Recommended)

Edit `.env` file to add your API keys:

```bash
# For sentiment analysis (optional)
NEWS_API_KEY=your_news_api_key_here

# For Groww API (optional)
GROWW_API_KEY=your_groww_api_key_here

# For Zerodha Kite (optional)
ZERODHA_API_KEY=your_zerodha_api_key_here
ZERODHA_API_SECRET=your_zerodha_api_secret_here
```

**Note**: The system works without API keys but with limited features. Yahoo Finance integration works out of the box.

## Understanding the Output

### Recommendation Levels

- **Strong Buy (80-100)**: Strong positive signals across all metrics
- **Buy (60-79)**: Positive signals, good buying opportunity
- **Hold (40-59)**: Mixed signals, consider holding current position
- **Sell (0-39)**: Negative signals, consider selling

### Score Components

1. **Technical Score (30%)**
   - Based on RSI, MACD, Moving Averages, Bollinger Bands
   - Indicates technical momentum and trends

2. **Fundamental Score (20%)**
   - Based on P/E ratio, PEG, ROE, profit margins, revenue growth
   - Indicates company financial health

3. **Sentiment Score (20%)**
   - Based on news and social media sentiment
   - Indicates market perception

4. **ML Score (30%)**
   - Based on Prophet and XGBoost predictions
   - Indicates likely future price movement

## Common Use Cases

### 1. Daily Stock Screening

Run bulk analysis every morning:

```bash
curl -X POST "http://localhost:8000/api/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"],
    "period": "1y"
  }' | jq '.recommendations | sort_by(.composite_score) | reverse'
```

### 2. Deep Dive Analysis

Use Streamlit UI for comprehensive analysis:
- View interactive charts
- See detailed technical indicators
- Review 30-day predictions
- Compare multiple stocks

### 3. Portfolio Monitoring

Create a watchlist and monitor regularly:

```python
from src.scoring import ScoringEngine

watchlist = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
engine = ScoringEngine()

for symbol in watchlist:
    # Analyze and get recommendation
    # Send alerts if recommendation changes
```

### 4. Automated Trading Signals

Integrate with trading platforms:

```python
# Example: Generate buy signals
scores = engine.calculate_composite_score(symbol, df, info)
if scores['recommendation'] == 'STRONG BUY':
    # Execute buy order
    pass
```

## Troubleshooting

### Docker Issues

**Problem**: Container won't start
```bash
# Check logs
docker-compose logs streamlit
docker-compose logs api

# Restart services
docker-compose restart
```

**Problem**: Port already in use
```bash
# Edit docker-compose.yml to use different ports
ports:
  - "8502:8501"  # Changed from 8501
```

### Python Issues

**Problem**: Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Problem**: Data not loading
```bash
# Check network connection
# Yahoo Finance requires internet access
# Try different stock symbols
```

### Performance Issues

**Problem**: Slow analysis
- Reduce the time period (use "1mo" instead of "1y")
- Disable ML predictions in the UI
- Use the API instead of UI for bulk operations

**Problem**: High memory usage
- Analyze fewer stocks at once
- Clear cache regularly
- Restart the services

## Next Steps

1. **Read the full documentation**: Check `README.md` for detailed features
2. **Explore the architecture**: See `ARCHITECTURE.md` for system design
3. **Contribute**: Read `CONTRIBUTING.md` to contribute
4. **Run tests**: Execute `bash scripts/run_tests.sh`
5. **Customize**: Modify scoring weights and thresholds
6. **Integrate**: Use the API in your own applications

## Getting Help

- **Issues**: https://github.com/niteshk629/recommend_stocksv2.0/issues
- **Discussions**: https://github.com/niteshk629/recommend_stocksv2.0/discussions
- **Documentation**: See README.md and ARCHITECTURE.md

## Resources

- [Yahoo Finance API Documentation](https://github.com/ranaroussi/yfinance)
- [Prophet Documentation](https://facebook.github.io/prophet/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

Happy Trading! 📈🚀
