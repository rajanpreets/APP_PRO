import requests
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
from ..config import SERPER_API_KEY, SERPER_BASE_URL

logger = logging.getLogger(__name__)

class SerperAPI:
    def __init__(self):
        self.base_url = SERPER_BASE_URL
        self.headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }

    def get_news_data(self, query: str) -> Dict[str, Any]:
        """
        Fetch news data for a given query, categorized by regulatory, clinical, and commercial aspects
        
        Args:
            query (str): Search query
            
        Returns:
            Dict[str, Any]: Processed news data categorized by type
        """
        try:
            # Get news from the last 6 months
            six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
            
            # Prepare search queries for different aspects
            regulatory_query = f"{query} (FDA OR EMA OR regulatory OR approval OR drug approval) after:{six_months_ago}"
            clinical_query = f"{query} (clinical trial OR phase OR study OR research) after:{six_months_ago}"
            commercial_query = f"{query} (market OR sales OR launch OR partnership OR acquisition) after:{six_months_ago}"
            
            # Fetch data for each category
            regulatory_data = self._fetch_news(regulatory_query)
            clinical_data = self._fetch_news(clinical_query)
            commercial_data = self._fetch_news(commercial_query)
            
            return {
                "regulatory": regulatory_data,
                "clinical": clinical_data,
                "commercial": commercial_data
            }
            
        except Exception as e:
            logger.error(f"Serper API error: {str(e)}")
            return {
                "regulatory": {"error": str(e)},
                "clinical": {"error": str(e)},
                "commercial": {"error": str(e)}
            }

    def _fetch_news(self, query: str) -> Dict[str, Any]:
        """Fetch news data for a specific query"""
        try:
            payload = {
                "q": query,
                "type": "news",
                "num": 10
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return self._process_news_data(data)
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return {"error": str(e)}

    def _process_news_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process news data into a structured format"""
        results = []
        
        for news in data.get("news", []):
            processed = {
                "title": news.get("title", ""),
                "link": news.get("link", ""),
                "snippet": news.get("snippet", ""),
                "date": news.get("date", ""),
                "source": news.get("source", ""),
                "position": news.get("position", 0)
            }
            results.append(processed)
        
        return {
            "data": results,
            "total": len(results)
        } 