import requests
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NCBIApi:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = "your-email@example.com"  # Replace with actual email
        self.tool = "MedicalSearchApp"

    def get_pubmed_data(self, query: str) -> Dict[str, Any]:
        """
        Fetch PubMed articles for a given query
        
        Args:
            query (str): Search query
            
        Returns:
            Dict[str, Any]: Processed PubMed data
        """
        try:
            # Get articles from the last 5 years
            five_years_ago = (datetime.now() - timedelta(days=5*365)).strftime("%Y/%m/%d")
            
            # First, search for articles
            search_params = {
                "db": "pubmed",
                "term": f"{query} AND {five_years_ago}[Date - Publication]",
                "retmode": "json",
                "retmax": 10,
                "email": self.email,
                "tool": self.tool
            }
            
            search_response = requests.get(f"{self.base_url}/esearch.fcgi", params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            # Get article IDs
            article_ids = search_data.get("esearchresult", {}).get("idlist", [])
            
            # Fetch details for each article
            articles = []
            for article_id in article_ids:
                fetch_params = {
                    "db": "pubmed",
                    "id": article_id,
                    "retmode": "json",
                    "email": self.email,
                    "tool": self.tool
                }
                
                fetch_response = requests.get(f"{self.base_url}/esummary.fcgi", params=fetch_params)
                fetch_response.raise_for_status()
                article_data = fetch_response.json()
                
                if article_data.get("result", {}).get(article_id):
                    articles.append(self._process_article(article_data["result"][article_id]))
            
            return {"data": articles}
            
        except Exception as e:
            logger.error(f"NCBI API error: {str(e)}")
            return {"error": str(e)}

    def _process_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single PubMed article into a structured format"""
        return {
            "pmid": article.get("uid", ""),
            "title": article.get("title", ""),
            "authors": article.get("authors", []),
            "journal": article.get("fulljournalname", ""),
            "publication_date": article.get("pubdate", ""),
            "abstract": article.get("abstract", ""),
            "doi": article.get("doi", ""),
            "pmc": article.get("pmc", ""),
            "keywords": article.get("keywords", []),
            "mesh_terms": article.get("mesh", []),
            "citation_count": article.get("citedbycount", 0)
        } 