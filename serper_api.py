import requests
import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

class SerperAPI:
    """A class for fetching and processing data from the Serper API (Google Search API)."""
    
    def __init__(self):
        """Initialize the Serper API client."""
        self.api_key = os.environ.get('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        logger.info(f"Initialized SerperAPI client with API key: {'Present' if self.api_key else 'None'}")
    
    def search(self, query, num_results=20, search_type='search'):
        """
        Perform a search using the Serper API.
        
        Args:
            query (str): The search query.
            num_results (int): Number of results to return.
            search_type (str): Type of search ('search', 'news', 'images', 'places').
            
        Returns:
            pd.DataFrame: DataFrame with search results.
        """
        if not self.api_key:
            logger.warning("Serper API key is not configured.")
            return pd.DataFrame()
        
        # Construct the request payload
        payload = {
            'q': query,
            'num': num_results,
            'gl': 'us',  # Geolocation: United States
            'hl': 'en'   # Language: English
        }
        
        # Choose endpoint based on search type
        endpoint = self.base_url
        if search_type == 'news':
            endpoint = "https://google.serper.dev/news"
        elif search_type == 'images':
            endpoint = "https://google.serper.dev/images"
        elif search_type == 'places':
            endpoint = "https://google.serper.dev/places"
        
        logger.debug(f"Performing Serper API {search_type} search for: {query}")
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Transform data based on search type
            if search_type == 'search':
                return self._process_search_results(data)
            elif search_type == 'news':
                return self._process_news_results(data)
            else:
                # Return raw data for other types
                return pd.DataFrame(data.get('items', []))
                
        except Exception as e:
            logger.error(f"Error performing Serper API search: {str(e)}")
            return pd.DataFrame()
    
    def _process_search_results(self, data):
        """
        Process general search results.
        
        Args:
            data (dict): Raw search results.
            
        Returns:
            pd.DataFrame: Processed search results.
        """
        processed_results = []
        
        # Process organic search results
        organic_results = data.get('organic', [])
        for result in organic_results:
            processed_result = {
                'title': result.get('title', ''),
                'link': result.get('link', ''),
                'snippet': result.get('snippet', ''),
                'position': result.get('position', 0),
                'type': 'organic',
                'displayed_link': result.get('displayedLink', ''),
                'source': result.get('source', '')
            }
            processed_results.append(processed_result)
        
        # Process knowledge graph if available
        knowledge_graph = data.get('knowledgeGraph', {})
        if knowledge_graph:
            processed_result = {
                'title': knowledge_graph.get('title', ''),
                'link': knowledge_graph.get('website', ''),
                'snippet': knowledge_graph.get('description', ''),
                'position': 0,  # Knowledge graph usually appears at the top
                'type': 'knowledge_graph',
                'displayed_link': knowledge_graph.get('website', ''),
                'source': 'Knowledge Graph'
            }
            processed_results.append(processed_result)
        
        # Process answer box if available
        answer_box = data.get('answerBox', {})
        if answer_box:
            processed_result = {
                'title': answer_box.get('title', ''),
                'link': answer_box.get('link', ''),
                'snippet': answer_box.get('snippet', ''),
                'position': 0,  # Answer box usually appears at the top
                'type': 'answer_box',
                'displayed_link': answer_box.get('displayedLink', ''),
                'source': 'Answer Box'
            }
            processed_results.append(processed_result)
        
        # Process related searches if available
        related_searches = data.get('relatedSearches', [])
        for i, search in enumerate(related_searches):
            processed_result = {
                'title': search.get('query', ''),
                'link': '',  # No direct link for related searches
                'snippet': '',
                'position': i,
                'type': 'related_search',
                'displayed_link': '',
                'source': 'Related Search'
            }
            processed_results.append(processed_result)
        
        logger.debug(f"Processed {len(processed_results)} search results")
        return pd.DataFrame(processed_results)
    
    def _process_news_results(self, data):
        """
        Process news search results.
        
        Args:
            data (dict): Raw news search results.
            
        Returns:
            pd.DataFrame: Processed news results.
        """
        processed_results = []
        
        news_results = data.get('news', [])
        for i, result in enumerate(news_results):
            # Try to parse the date
            date_str = result.get('date', '')
            date = None
            
            try:
                if date_str:
                    if 'ago' in date_str.lower():
                        # Handle relative dates like "2 hours ago"
                        parts = date_str.lower().split()
                        if len(parts) >= 3 and parts[1] in ['hour', 'hours', 'day', 'days', 'week', 'weeks']:
                            num = int(parts[0])
                            unit = parts[1]
                            
                            if 'hour' in unit:
                                date = datetime.now() - timedelta(hours=num)
                            elif 'day' in unit:
                                date = datetime.now() - timedelta(days=num)
                            elif 'week' in unit:
                                date = datetime.now() - timedelta(weeks=num)
                    else:
                        # Try parsing absolute date
                        date = datetime.strptime(date_str, '%Y-%m-%d')
            except:
                # If parsing fails, leave date as None
                pass
            
            processed_result = {
                'title': result.get('title', ''),
                'link': result.get('link', ''),
                'snippet': result.get('snippet', ''),
                'position': i,
                'type': 'news',
                'displayed_link': result.get('source', ''),
                'source': result.get('source', ''),
                'date': date.strftime('%Y-%m-%d') if date else date_str,
                'thumbnail': result.get('imageUrl', '')
            }
            processed_results.append(processed_result)
        
        logger.debug(f"Processed {len(processed_results)} news results")
        return pd.DataFrame(processed_results)
    
    def scrape_content(self, url, timeout=10, max_retries=2):
        """
        Scrape content from a URL using BeautifulSoup.
        
        Args:
            url (str): The URL to scrape.
            timeout (int): Request timeout in seconds.
            max_retries (int): Maximum number of retry attempts.
            
        Returns:
            dict: Dictionary containing the scraped content.
        """
        if not url:
            return {"error": "No URL provided", "content": ""}
            
        logger.debug(f"Scraping content from URL: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        result = {
            "url": url,
            "title": "",
            "content": "",
            "text": "",
            "error": None,
            "publication_date": None
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                result["title"] = soup.title.text.strip() if soup.title else ""
                
                # Extract text content
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.extract()
                
                # Get text
                text = soup.get_text(separator=' ', strip=True)
                
                # Remove excessive whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Basic content cleaning
                result["text"] = text
                
                # Attempt to extract main content
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|article|main|post', re.I))
                if main_content:
                    cleaned_content = main_content.get_text(separator='\n', strip=True)
                    result["content"] = re.sub(r'\n+', '\n', cleaned_content)
                else:
                    # Fallback to paragraphs
                    paragraphs = soup.find_all('p')
                    if paragraphs:
                        result["content"] = '\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
                    else:
                        result["content"] = text[:2000]  # Limit to first 2000 chars if no structure found
                
                # Try to find publication date
                date_patterns = [
                    re.compile(r'(\d{4}-\d{2}-\d{2})'),  # ISO format
                    re.compile(r'publish.*?date', re.I),  # Common class name patterns
                    re.compile(r'date-published', re.I),
                    re.compile(r'post-date', re.I)
                ]
                
                for pattern in date_patterns:
                    if isinstance(pattern, re.Pattern):
                        # Regex pattern for direct text search
                        date_match = pattern.search(response.text)
                        if date_match:
                            try:
                                date_str = date_match.group(1)
                                result["publication_date"] = date_str
                                break
                            except:
                                pass
                    else:
                        # Class/attribute pattern
                        date_elements = soup.find_all(attrs={"class": pattern})
                        if date_elements:
                            result["publication_date"] = date_elements[0].get_text().strip()
                            break
                
                logger.debug(f"Successfully scraped content from URL: {url}")
                return result
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    error_msg = f"Request error: {str(e)}"
                    result["error"] = error_msg
                    logger.warning(error_msg)
            except Exception as e:
                if attempt == max_retries - 1:
                    error_msg = f"Parsing error: {str(e)}"
                    result["error"] = error_msg
                    logger.warning(error_msg)
            
            # Delay before retry
            time.sleep(1)
        
        return result

    def search_news(self, query, num_results=20, days_back=30, scrape_content=True):
        """
        Search for recent news articles related to the query.
        
        Args:
            query (str): The search query.
            num_results (int): Number of results to return.
            days_back (int): Number of days to look back for news.
            scrape_content (bool): Whether to scrape content from the news URLs.
            
        Returns:
            dict: Dictionary with categorized news articles and summaries.
        """
        start_time = datetime.now()
        logger.info(f"Searching news for: {query}, days_back={days_back}")
        
        # Add time period to the query
        time_query = f"{query} after:{days_back} days ago"
        
        news_df = self.search(time_query, num_results, search_type='news')
        
        if news_df.empty:
            logger.warning(f"No news results found for query: {query}")
            return {
                'regulatory': [],
                'commercial': [],
                'clinical': [],
                'other': [],
                'summaries': {
                    'regulatory': 'No regulatory news available.',
                    'commercial': 'No commercial news available.',
                    'clinical': 'No clinical development news available.',
                    'other': 'No other news available.'
                }
            }
        
        # Optionally scrape content from the URLs
        if scrape_content:
            logger.debug(f"Scraping content from {min(10, len(news_df))} news URLs")
            news_with_content = []
            for _, article in news_df.iterrows():
                if article.get('link'):
                    # Don't scrape too many URLs to avoid rate limiting
                    if len(news_with_content) >= 10:
                        news_with_content.append(article.to_dict())
                        continue
                    
                    # Add a small delay between requests
                    time.sleep(0.5)
                    
                    try:
                        scraped_content = self.scrape_content(article.get('link'))
                        article_dict = article.to_dict()
                        article_dict['content'] = scraped_content.get('content', '')
                        article_dict['full_text'] = scraped_content.get('text', '')
                        news_with_content.append(article_dict)
                    except Exception as e:
                        logger.error(f"Error scraping content from {article.get('link')}: {str(e)}")
                        news_with_content.append(article.to_dict())
                else:
                    news_with_content.append(article.to_dict())
        else:
            news_with_content = [article.to_dict() for _, article in news_df.iterrows()]
        
        logger.debug(f"Categorizing {len(news_with_content)} news articles")
        
        # Categorize news articles
        categories = {
            'regulatory': [],
            'commercial': [],
            'clinical': [],
            'other': []
        }
        
        regulatory_keywords = [
            'fda', 'ema', 'approval', 'regulation', 'patent', 'clinical trial', 
            'phase', 'regulatory', 'safety', 'recall', 'warning', 'compliance',
            'guidance', 'legal', 'lawsuit', 'settlement', 'legislation', 'law',
            'investigation', 'inspection', 'license', 'clearance', 'authorized',
            'rejected', 'delay', 'advisory committee', 'protocol', 'guideline'
        ]
        
        commercial_keywords = [
            'market', 'sales', 'revenue', 'profit', 'launch', 'commercial', 
            'distribution', 'partnership', 'deal', 'agreement', 'acquisition',
            'merger', 'investment', 'stock', 'shares', 'financial', 'price',
            'cost', 'reimbursement', 'insurance', 'discount', 'wholesale',
            'retail', 'prescriptions', 'marketing', 'advertising', 'promotion',
            'competition', 'competitor', 'market share', 'growth', 'forecast'
        ]
        
        clinical_keywords = [
            'clinical', 'trial', 'study', 'research', 'patient', 'treatment',
            'efficacy', 'outcome', 'endpoint', 'data', 'results', 'adverse',
            'effect', 'response', 'therapy', 'therapeutic', 'dosage', 'dose',
            'regimen', 'indication', 'contraindication', 'protocol', 'cohort',
            'placebo', 'randomized', 'blind', 'publication', 'journal', 'paper',
            'conference', 'presentation', 'abstract', 'poster', 'scientific'
        ]
        
        for article in news_with_content:
            text = f"{article.get('title', '')} {article.get('snippet', '')} {article.get('content', '')}"
            text = text.lower()
            
            # Count keyword matches in each category
            regulatory_score = sum(1 for kw in regulatory_keywords if kw in text)
            commercial_score = sum(1 for kw in commercial_keywords if kw in text)
            clinical_score = sum(1 for kw in clinical_keywords if kw in text)
            
            # Determine the category with the highest score
            max_score = max(regulatory_score, commercial_score, clinical_score)
            
            if max_score == 0:
                categories['other'].append(article)
            elif regulatory_score == max_score:
                categories['regulatory'].append(article)
            elif commercial_score == max_score:
                categories['commercial'].append(article)
            elif clinical_score == max_score:
                categories['clinical'].append(article)
        
        # Generate summaries for each category
        summaries = {}
        
        for category, articles in categories.items():
            if not articles:
                summaries[category] = f"No {category} news available."
                continue
            
            # Sort articles by date if available
            sorted_articles = sorted(
                articles, 
                key=lambda x: x.get('date', ''), 
                reverse=True
            )[:5]
            
            # Extract titles for the summary
            topics = []
            for article in sorted_articles:
                title = article.get('title', '')
                if title:
                    # Clean up title
                    title = re.sub(r'\s+', ' ', title).strip()
                    topics.append(title)
            
            if topics:
                # Create a summary based on the topics
                summary = f"Recent {category} news includes: " + "; ".join(topics) + "."
            else:
                summary = f"No significant {category} news available."
            
            summaries[category] = summary
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Completed news search and categorization in {processing_time:.2f} seconds")
        
        result = categories
        result['summaries'] = summaries
        
        return result
    
    def search_medical(self, query, num_results=20, scrape_content=True):
        """
        Search for medical information related to the query.
        
        Args:
            query (str): The search query.
            num_results (int): Number of results to return.
            scrape_content (bool): Whether to scrape content from the URLs.
            
        Returns:
            dict: Dictionary with search results including scraped content.
        """
        start_time = datetime.now()
        logger.info(f"Searching medical information for: {query}")
        
        # Add medical terms to the query to get more relevant results
        medical_query = f"{query} medical information clinical research"
        
        results_df = self.search(medical_query, num_results)
        
        if results_df.empty:
            logger.warning(f"No medical information found for query: {query}")
            return {"results": [], "error": "No medical information found"}
        
        # Process results
        results_list = []
        
        for _, result in results_df.iterrows():
            item = result.to_dict()
            
            # Scrape content if requested and link exists
            if scrape_content and item.get('link'):
                try:
                    # Don't scrape too many URLs to avoid rate limiting
                    if len(results_list) < 5:
                        # Add a small delay between requests
                        time.sleep(0.5)
                        
                        scraped_content = self.scrape_content(item.get('link'))
                        item['content'] = scraped_content.get('content', '')
                        item['full_text'] = scraped_content.get('text', '')
                except Exception as e:
                    logger.error(f"Error scraping content from {item.get('link')}: {str(e)}")
            
            results_list.append(item)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Completed medical search in {processing_time:.2f} seconds, found {len(results_list)} results")
        
        return {"results": results_list}
    
    def search_regulatory(self, query, num_results=20, scrape_content=True):
        """
        Search for regulatory information related to the query.
        
        Args:
            query (str): The search query.
            num_results (int): Number of results to return.
            scrape_content (bool): Whether to scrape content from the URLs.
            
        Returns:
            dict: Dictionary with regulatory search results including scraped content.
        """
        start_time = datetime.now()
        logger.info(f"Searching regulatory information for: {query}")
        
        # Add regulatory terms to the query to get more relevant results
        regulatory_query = f"{query} FDA approval regulatory status"
        
        results_df = self.search(regulatory_query, num_results)
        
        if results_df.empty:
            logger.warning(f"No regulatory information found for query: {query}")
            return {"results": [], "error": "No regulatory information found"}
        
        # Process results
        results_list = []
        
        for _, result in results_df.iterrows():
            item = result.to_dict()
            
            # Scrape content if requested and link exists
            if scrape_content and item.get('link'):
                try:
                    # Don't scrape too many URLs to avoid rate limiting
                    if len(results_list) < 5:
                        # Add a small delay between requests
                        time.sleep(0.5)
                        
                        scraped_content = self.scrape_content(item.get('link'))
                        item['content'] = scraped_content.get('content', '')
                        item['full_text'] = scraped_content.get('text', '')
                except Exception as e:
                    logger.error(f"Error scraping content from {item.get('link')}: {str(e)}")
            
            results_list.append(item)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Completed regulatory search in {processing_time:.2f} seconds, found {len(results_list)} results")
        
        return {"results": results_list}
