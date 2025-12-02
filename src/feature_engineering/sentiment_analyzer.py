"""Sentiment Analysis Module"""
import logging
from typing import List, Dict, Optional
import requests
from textblob import TextBlob
import os

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment from news and social media"""
    
    def __init__(self, news_api_key: Optional[str] = None):
        self.news_api_key = news_api_key or os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"
    
    def analyze_text_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a text using TextBlob
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with polarity and subjectivity scores
        """
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            return {
                'polarity': sentiment.polarity,  # -1 (negative) to 1 (positive)
                'subjectivity': sentiment.subjectivity  # 0 (objective) to 1 (subjective)
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0}
    
    def fetch_news(
        self,
        query: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = 'en'
    ) -> List[Dict]:
        """
        Fetch news articles from News API
        
        Args:
            query: Search query
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            language: Language code
        
        Returns:
            List of news articles
        """
        if not self.news_api_key:
            logger.warning("News API key not set")
            return []
        
        try:
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'apiKey': self.news_api_key,
                'language': language,
                'sortBy': 'publishedAt'
            }
            
            if from_date:
                params['from'] = from_date
            if to_date:
                params['to'] = to_date
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])
            else:
                logger.warning(f"Failed to fetch news: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def analyze_stock_sentiment(self, symbol: str) -> Dict[str, float]:
        """
        Analyze overall sentiment for a stock
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with aggregated sentiment scores
        """
        # Fetch news articles
        articles = self.fetch_news(f"{symbol} stock")
        
        if not articles:
            logger.warning(f"No articles found for {symbol}")
            return {
                'avg_polarity': 0.0,
                'avg_subjectivity': 0.0,
                'article_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        # Analyze sentiment of each article
        sentiments = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for article in articles:
            # Combine title and description for analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            sentiment = self.analyze_text_sentiment(text)
            sentiments.append(sentiment)
            
            # Categorize sentiment
            polarity = sentiment['polarity']
            if polarity > 0.1:
                positive_count += 1
            elif polarity < -0.1:
                negative_count += 1
            else:
                neutral_count += 1
        
        # Calculate aggregate scores
        avg_polarity = sum(s['polarity'] for s in sentiments) / len(sentiments)
        avg_subjectivity = sum(s['subjectivity'] for s in sentiments) / len(sentiments)
        
        return {
            'avg_polarity': avg_polarity,
            'avg_subjectivity': avg_subjectivity,
            'article_count': len(articles),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count
        }
    
    def get_sentiment_score(self, symbol: str) -> float:
        """
        Get normalized sentiment score (0-100)
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Sentiment score between 0 and 100
        """
        sentiment = self.analyze_stock_sentiment(symbol)
        
        # Convert polarity (-1 to 1) to score (0 to 100)
        polarity = sentiment['avg_polarity']
        score = (polarity + 1) * 50
        
        # Weight by article count (more articles = more confidence)
        article_count = sentiment['article_count']
        if article_count > 0:
            confidence = min(article_count / 10, 1.0)  # Cap at 10 articles
            score = score * confidence + 50 * (1 - confidence)
        
        return score
