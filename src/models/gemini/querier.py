"""Gemini API querier for trading analysis"""

import os
import json
import re
from typing import Any, Dict, List
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
    
    def analyze_sentiment_batch(self, articles: dict) -> dict:
        # Build article list with numbered indices to avoid key escaping issues
        articles_list = []
        article_map_by_index = {}
        for idx, (title, desc) in enumerate(articles.items()):
            articles_list.append(f"Article {idx + 1}: {title}\nDescription: {desc}")
            article_map_by_index[f"article_{idx + 1}"] = title
        
        merged_text = "\n\n".join(articles_list)

        prompt = f"""Analyze sentiment for the following financial news articles.

Return ONLY a JSON object. Start with {{ and end with }}. No markdown code fences.

For each article, respond with:
- sentiment: must be exactly "positive", "negative", or "neutral"
- score: a number between 0 and 1
- reasoning: a brief one-sentence explanation

News Articles:
{merged_text}

Respond with this JSON structure:
{{
  "article_1": {{
    "sentiment": "positive",
    "score": 0.8,
    "reasoning": "explanation"
  }},
  "article_2": {{
    "sentiment": "negative",
    "score": 0.3,
    "reasoning": "explanation"
  }}
}}

Start your response with only a curly bracket {{ . No markdown. No commentary."""

        response = self.model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Clean up response
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        try:
            parsed = json.loads(raw_text)
            # Map back to original titles
            result = {}
            for idx, (article_key, original_title) in enumerate(article_map_by_index.items()):
                if article_key in parsed:
                    result[original_title] = parsed[article_key]
                else:
                    result[original_title] = {
                        "sentiment": "neutral",
                        "score": 0.5,
                        "reasoning": "Missing in response"
                    }
            return result
        except json.JSONDecodeError:
            return {
                title: {
                    "sentiment": "neutral",
                    "score": 0.5,
                    "reasoning": "Could not parse sentiment"
                }
                for title in articles
            }

    def predict_price_movement(self, companies: dict, context: str) -> dict:
        
        prompt = f"""Analyze this financial news context and identify stock trading opportunities.

For each distinct company or stock mentioned, provide:
- The company name
- Its stock ticker symbol (or null if unknown)
- Trading action: buy, sell, or hold
- Confidence score from 0 to 1
- Brief reasoning in one sentence

News Context:
{context}

Respond with ONLY this JSON structure. No markdown code fences. Start with {{ .
Structure:
{{
  "AAPL": {{
    "name": "Apple",
    "action": "buy",
    "confidence": 0.7,
    "reasoning": "Strong earnings growth"
  }},
  "TSLA": {{
    "name": "Tesla",
    "action": "hold",
    "confidence": 0.5,
    "reasoning": "Mixed signals"
  }}
}}

Return ONLY the JSON object. No markdown. No explanations. Start with {{ ."""

        response = self.model.generate_content(prompt)

        try:
            raw_json = response.candidates[0].content.parts[0].text
        except (AttributeError, IndexError):
            raw_json = response.text
        
        # Clean up markdown code fences if present
        raw_json = raw_json.strip()
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]
        raw_json = raw_json.strip()

        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            return companies

        # Handle both old array format and new dict format
        if isinstance(data, list):
            preds = data
            for item in preds:
                ticker = item.get("ticker")
                if ticker:
                    companies[ticker] = {
                        "action": item.get("action", "hold"),
                        "confidence": item.get("confidence", 0.5),
                        "reasoning": item.get("reasoning"),
                        "name": item.get("name")
                    }
        elif isinstance(data, dict):
            for ticker, item in data.items():
                if ticker and ticker != "predictions":
                    companies[ticker] = {
                        "action": item.get("action", "hold"),
                        "confidence": item.get("confidence", 0.5),
                        "reasoning": item.get("reasoning"),
                        "name": item.get("name", ticker)
                    }

        return companies
    
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

    def analyze_trading_signal(self, analysis_data: List[Dict[str, Any]]) -> Dict[str, Any]:
            """
            Performs comprehensive trading signal analysis for ALL stocks using 
            ONE single Gemini API call. This function holds the single LLM API call.
            
            Args:
                analysis_data: A list of dicts, each containing 
                            'symbol', 'category', 'price_history', and 'news'.

            Returns:
                A dict structured by the original category keys.
            """

            # --- 1. Prompt Construction Phase ---
            
            # Use the entire data payload (like the NVDA, SPY, ULTA data you provided)
            data_json = json.dumps(analysis_data, indent=2)
            
            prompt = f"""Analyze stock data and generate trading signals.

You MUST return ONLY valid raw JSON. Do NOT use markdown code fences. Do NOT write explanations.

Stock Analysis Data:
{data_json}

For each stock, determine:
- action: "buy", "sell", or "hold"
- strength: a number from 0.0 to 1.0
- reasoning: one sentence explanation

Return a JSON object with three keys. Each key maps stock symbols to analysis:

{{
  "portfolio_signals": {{
    "AAPL": {{ "action": "buy", "strength": 0.8, "reasoning": "Reason here" }},
    "TSLA": {{ "action": "hold", "strength": 0.5, "reasoning": "Reason here" }}
  }},
  "news_opportunities": {{
    "NVDA": {{ "action": "buy", "strength": 0.7, "reasoning": "Reason here" }}
  }},
  "new_buy_candidates": {{
    "META": {{ "action": "buy", "strength": 0.6, "reasoning": "Reason here" }}
  }}
}}

Return ONLY this JSON. Start with a curly bracket. No markdown. No code fences. No text."""
            
            # --- 2. Single API Call Execution Phase ---
            try:
                # THIS IS THE SINGLE API CALL
                response = self.model.generate_content(prompt)
                raw = response.candidates[0].content.parts[0].text
                raw = raw.strip()
                
                # Clean up any markdown fences that might appear
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                raw = raw.strip()
                
                model_results = json.loads(raw)
            except Exception as e:
                # Fallback for API or JSON parsing failure
                print(f"API call or JSON parsing failed: {e}")
                model_results = {
                    "portfolio_signals": {},
                    "news_opportunities": {},
                    "new_buy_candidates": {}
                }
            
            return model_results