"""Streamlit Application"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_integration import YahooFinanceClient
from src.feature_engineering import TechnicalIndicators, SentimentAnalyzer
from src.ml_models import ProphetPredictor, XGBoostPredictor
from src.scoring import ScoringEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Stock Recommendation System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .recommendation-strong-buy {
        color: #00ff00;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .recommendation-buy {
        color: #90ee90;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .recommendation-hold {
        color: #ffa500;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .recommendation-sell {
        color: #ff0000;
        font-weight: bold;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_stock_data(symbol, period):
    """Load stock data with caching"""
    client = YahooFinanceClient()
    df = client.get_historical_data(symbol, period=period)
    info = client.get_info(symbol)
    return df, info


@st.cache_data(ttl=3600)
def calculate_indicators(df):
    """Calculate technical indicators with caching"""
    return TechnicalIndicators.calculate_all_indicators(df)


def create_candlestick_chart(df, symbol):
    """Create interactive candlestick chart with Plotly"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{symbol} Price', 'Volume', 'RSI'),
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )
    
    # Add moving averages
    if 'SMA_20' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(color='orange')),
            row=1, col=1
        )
    if 'SMA_50' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='blue')),
            row=1, col=1
        )
    
    # Volume bars
    colors = ['red' if row['Close'] < row['Open'] else 'green' for idx, row in df.iterrows()]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors),
        row=2, col=1
    )
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')),
            row=3, col=1
        )
        # Add RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    fig.update_layout(
        height=800,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig


def create_prediction_chart(historical_df, predictions):
    """Create prediction chart"""
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(
        go.Scatter(
            x=historical_df.index,
            y=historical_df['Close'],
            name='Historical',
            line=dict(color='blue')
        )
    )
    
    # Predictions
    if predictions is not None and not predictions.empty:
        fig.add_trace(
            go.Scatter(
                x=predictions['Date'],
                y=predictions['Predicted'],
                name='Predicted',
                line=dict(color='red', dash='dash')
            )
        )
        
        # Confidence interval
        fig.add_trace(
            go.Scatter(
                x=predictions['Date'],
                y=predictions['Upper_Bound'],
                fill=None,
                mode='lines',
                line_color='rgba(255,0,0,0)',
                showlegend=False
            )
        )
        fig.add_trace(
            go.Scatter(
                x=predictions['Date'],
                y=predictions['Lower_Bound'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(255,0,0,0)',
                name='Confidence Interval',
                fillcolor='rgba(255,0,0,0.2)'
            )
        )
    
    fig.update_layout(
        title='Price Prediction',
        xaxis_title='Date',
        yaxis_title='Price',
        height=500,
        hovermode='x unified'
    )
    
    return fig


def main():
    """Main application"""
    # Header
    st.markdown('<h1 class="main-header">📈 Hybrid Stock Recommendation System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # Stock selection
        symbol = st.text_input("Stock Symbol", value="AAPL", help="Enter stock ticker symbol (e.g., AAPL, GOOGL, MSFT)")
        
        # Period selection
        period = st.selectbox(
            "Time Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
        
        # Analysis options
        st.subheader("Analysis Options")
        show_technical = st.checkbox("Technical Analysis", value=True)
        show_sentiment = st.checkbox("Sentiment Analysis", value=True)
        show_predictions = st.checkbox("ML Predictions", value=True)
        
        # Run analysis button
        analyze_button = st.button("Analyze Stock", type="primary")
    
    # Main content
    if analyze_button:
        with st.spinner(f"Analyzing {symbol}..."):
            try:
                # Load data
                df, info = load_stock_data(symbol, period)
                
                if df is None or df.empty:
                    st.error(f"Could not fetch data for {symbol}. Please check the symbol and try again.")
                    return
                
                # Calculate indicators
                df_with_indicators = calculate_indicators(df)
                
                # Display current price
                current_price = df['Close'].iloc[-1]
                price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
                price_change_pct = (price_change / df['Close'].iloc[-2]) * 100
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Current Price", f"${current_price:.2f}", f"{price_change_pct:.2f}%")
                
                with col2:
                    if info:
                        st.metric("Market Cap", f"${info.get('marketCap', 0) / 1e9:.2f}B")
                
                with col3:
                    st.metric("52W High", f"${df['High'].max():.2f}")
                
                with col4:
                    st.metric("52W Low", f"${df['Low'].min():.2f}")
                
                # Tabs for different views
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Charts", "🎯 Recommendation", "📈 Predictions", "📋 Details"])
                
                with tab1:
                    st.subheader("Price Chart")
                    fig = create_candlestick_chart(df_with_indicators, symbol)
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    st.subheader("Composite Recommendation")
                    
                    # Calculate scores
                    scoring_engine = ScoringEngine()
                    
                    # Train models if predictions enabled
                    prophet_model = None
                    xgboost_model = None
                    
                    if show_predictions:
                        with st.spinner("Training prediction models..."):
                            prophet_model = ProphetPredictor()
                            prophet_model.train(df)
                            
                            xgboost_model = XGBoostPredictor()
                            xgboost_model.train(df_with_indicators)
                    
                    # Calculate composite score
                    scores = scoring_engine.calculate_composite_score(
                        symbol, df_with_indicators, info, prophet_model, xgboost_model
                    )
                    
                    # Display recommendation
                    recommendation = scores['recommendation']
                    rec_class = f"recommendation-{recommendation.lower().replace(' ', '-')}"
                    st.markdown(f'<p class="{rec_class}">Recommendation: {recommendation}</p>', unsafe_allow_html=True)
                    
                    # Display scores
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Composite Score", f"{scores['composite_score']:.1f}/100")
                        st.metric("Technical Score", f"{scores['technical_score']:.1f}/100")
                        st.metric("Sentiment Score", f"{scores['sentiment_score']:.1f}/100")
                    
                    with col2:
                        st.metric("Fundamental Score", f"{scores['fundamental_score']:.1f}/100")
                        st.metric("ML Score", f"{scores['ml_score']:.1f}/100")
                    
                    # Score breakdown chart
                    score_df = pd.DataFrame({
                        'Category': ['Technical', 'Fundamental', 'Sentiment', 'ML'],
                        'Score': [
                            scores['technical_score'],
                            scores['fundamental_score'],
                            scores['sentiment_score'],
                            scores['ml_score']
                        ]
                    })
                    
                    fig = px.bar(
                        score_df,
                        x='Category',
                        y='Score',
                        title='Score Breakdown',
                        color='Score',
                        color_continuous_scale='RdYlGn'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    if show_predictions and prophet_model:
                        st.subheader("Price Predictions")
                        
                        predictions = prophet_model.predict(periods=30)
                        
                        if predictions is not None:
                            fig = create_prediction_chart(df, predictions)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Display prediction table
                            st.dataframe(predictions.tail(10), use_container_width=True)
                    else:
                        st.info("Enable ML Predictions in the sidebar to see forecasts.")
                
                with tab4:
                    st.subheader("Stock Information")
                    
                    if info:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Company:**", info.get('longName', 'N/A'))
                            st.write("**Sector:**", info.get('sector', 'N/A'))
                            st.write("**Industry:**", info.get('industry', 'N/A'))
                            st.write("**P/E Ratio:**", f"{info.get('forwardPE', 'N/A')}")
                            st.write("**EPS:**", f"{info.get('trailingEps', 'N/A')}")
                        
                        with col2:
                            st.write("**Dividend Yield:**", f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else 'N/A')
                            st.write("**Beta:**", f"{info.get('beta', 'N/A')}")
                            st.write("**52W Change:**", f"{info.get('52WeekChange', 'N/A')}")
                            st.write("**Avg Volume:**", f"{info.get('averageVolume', 'N/A'):,}")
                    
                    st.subheader("Recent Data")
                    st.dataframe(df_with_indicators.tail(10), use_container_width=True)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Error in analysis: {e}", exc_info=True)
    
    else:
        # Welcome message
        st.info("👈 Enter a stock symbol in the sidebar and click 'Analyze Stock' to get started!")
        
        st.markdown("""
        ### Features
        - **Technical Analysis**: RSI, MACD, Bollinger Bands, Moving Averages, and more
        - **Sentiment Analysis**: News and social media sentiment
        - **ML Predictions**: Prophet and XGBoost models for price forecasting
        - **Composite Scoring**: Weighted scoring system for recommendations
        - **Interactive Charts**: Plotly-powered visualizations
        
        ### How to Use
        1. Enter a stock ticker symbol (e.g., AAPL, GOOGL, MSFT)
        2. Select the time period for analysis
        3. Choose which analysis types to include
        4. Click "Analyze Stock" to generate recommendations
        """)


if __name__ == "__main__":
    main()
