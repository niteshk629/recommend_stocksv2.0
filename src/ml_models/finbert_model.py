"""FinBERT Sentiment Analysis Model"""
import logging
from typing import List, Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

logger = logging.getLogger(__name__)


class FinBERTAnalyzer:
    """Financial sentiment analysis using FinBERT"""
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.labels = ['negative', 'neutral', 'positive']
    
    def load_model(self) -> bool:
        """
        Load FinBERT model and tokenizer
        
        Returns:
            True if successful
        """
        try:
            logger.info(f"Loading FinBERT model: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("FinBERT model loaded successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error loading FinBERT model: {e}")
            return False
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a text
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with sentiment scores
        """
        if self.model is None or self.tokenizer is None:
            if not self.load_model():
                return {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0}
        
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Convert to dictionary
            sentiment_scores = {
                label: float(prob)
                for label, prob in zip(self.labels, probs[0].cpu().numpy())
            }
            
            return sentiment_scores
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0}
    
    def analyze_batch(self, texts: List[str], batch_size: int = 8) -> List[Dict[str, float]]:
        """
        Analyze sentiment for multiple texts
        
        Args:
            texts: List of texts
            batch_size: Batch size for processing
        
        Returns:
            List of sentiment dictionaries
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            for text in batch:
                sentiment = self.analyze_sentiment(text)
                results.append(sentiment)
        
        return results
    
    def get_overall_sentiment(self, texts: List[str]) -> Dict[str, float]:
        """
        Get aggregated sentiment from multiple texts
        
        Args:
            texts: List of texts
        
        Returns:
            Dictionary with average sentiment scores
        """
        if not texts:
            return {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0, 'score': 50.0}
        
        # Analyze all texts
        sentiments = self.analyze_batch(texts)
        
        # Calculate averages
        avg_sentiment = {
            'positive': np.mean([s['positive'] for s in sentiments]),
            'neutral': np.mean([s['neutral'] for s in sentiments]),
            'negative': np.mean([s['negative'] for s in sentiments])
        }
        
        # Calculate overall score (0-100)
        score = (avg_sentiment['positive'] - avg_sentiment['negative']) * 50 + 50
        avg_sentiment['score'] = score
        
        return avg_sentiment
    
    def get_sentiment_label(self, sentiment_scores: Dict[str, float]) -> str:
        """
        Get sentiment label from scores
        
        Args:
            sentiment_scores: Dictionary with sentiment scores
        
        Returns:
            Sentiment label ('positive', 'neutral', 'negative')
        """
        return max(sentiment_scores, key=sentiment_scores.get)
