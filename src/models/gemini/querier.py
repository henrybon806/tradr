"""Gemini API querier for trading analysis"""

import os
import json
from typing import Optional
import google.generativeai as genai
from src.core.config import Config


class GeminiQuerier:
    """Query Gemini API for trading analysis and sentiment"""
    
    def __init__(self):
        """Initialize Gemini API with API key"""
        api_key = os.getenv("GEMINI_API_KEY", Config.GEMINI_API_KEY)
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or config")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment of text (news, social media, etc.)
        Returns: {"sentiment": "positive|negative|neutral", "score": 0.0-1.0, "reasoning": str}
        """
        prompt = f"""Analyze the sentiment of the following text about stocks/trading. 
        Return a JSON response with:
        - sentiment: "positive", "negative", or "neutral"
        - score: confidence score from 0.0 to 1.0
        - reasoning: brief explanation
        
        Text: {text}
        
        Return only valid JSON, no markdown."""
        
        response = self.model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {
                "sentiment": "neutral",
                "score": 0.5,
                "reasoning": "Could not parse sentiment"
            }
    
    def predict_price_movement(self, symbol: str, context: str) -> dict:
        """
        Predict price movement based on news/context
        Returns: {"direction": "up|down|neutral", "confidence": 0.0-1.0, "reasoning": str}
        """
        prompt = f"""Based on the following context about {symbol}, predict if the stock price will go up, down, or stay neutral.
        Return a JSON response with:
        - direction: "up", "down", or "neutral"
        - confidence: confidence score from 0.0 to 1.0
        - reasoning: brief explanation of your prediction
        
        Context: {context}
        
        Return only valid JSON, no markdown."""
        
        response = self.model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {
                "direction": "neutral",
                "confidence": 0.5,
                "reasoning": "Could not parse prediction"
            }
    
    def analyze_trading_signal(self, symbol: str, price_history: str, news: str) -> dict:
        """
        Comprehensive trading signal analysis
        Returns: {"action": "buy|sell|hold", "strength": 0.0-1.0, "reasoning": str}
        """
        prompt = f"""Analyze the trading signal for {symbol} based on the following information:
        
        Price History: {price_history}
        
        Recent News: {news}
        
        Return a JSON response with:
        - action: "buy", "sell", or "hold"
        - strength: signal strength from 0.0 to 1.0
        - reasoning: detailed explanation of the signal
        
        Return only valid JSON, no markdown."""
        
        response = self.model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {
                "action": "hold",
                "strength": 0.5,
                "reasoning": "Could not parse signal"
            }
    
    def summarize_news(self, articles: list) -> str:
        """
        Summarize multiple news articles
        Returns: summary string
        """
        articles_text = "\n".join([f"- {article}" for article in articles])
        prompt = f"""Summarize the following news articles into a concise paragraph:
        
        {articles_text}
        
        Summary (max 3 sentences):"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def query(self, prompt: str) -> str:
        """
        Generic query to Gemini
        Returns: response text
        """
        response = self.model.generate_content(prompt)
        return response.text


if __name__ == "__main__":
    querier = GeminiQuerier()
    
    # Test sentiment analysis
    sentiment = querier.analyze_sentiment("Apple announced record profits this quarter!")
    print("Sentiment Analysis:", sentiment)
    
    # Test price prediction
    prediction = querier.predict_price_movement("AAPL", "Strong earnings, tech sector growth")
    print("\nPrice Prediction:", prediction)
    
    # Test trading signal
    signal = querier.analyze_trading_signal(
        "TSLA",
        "Recent price: $250, 52-week range: $200-$300",
        "Tesla announces new factory, demand remains strong"
    )
    print("\nTrading Signal:", signal)
