import requests
import pandas as pd
import time
import os
from datetime import datetime, timedelta
import json
import logging
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger(__name__)

class NCBIAPI:
    """A class for fetching and processing data from the NCBI API."""
    
    def __init__(self):
        """Initialize the NCBI API client."""
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.api_key = os.environ.get('NCBI_API_KEY', '')
        self.email = os.environ.get('NCBI_EMAIL', 'your.email@example.com')
        self.tool = "healthcare_dashboard"
        
        # Different rate limits with/without API key
        self.requests_per_second = 10 if self.api_key else 3
        self.last_request_time = 0
        
        logger.info(f"Initialized NCBI API client with API key: {'Present' if self.api_key else 'None'}")
    
    def _respect_rate_limit(self):
        """Ensure API rate limits are respected."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Wait if necessary to respect rate limit
        if time_since_last_request < (1.0 / self.requests_per_second):
            wait_time = (1.0 / self.requests_per_second) - time_since_last_request
            logger.debug(f"Waiting {wait_time:.2f}s to respect NCBI rate limits")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def search_publications(self, query, max_results=100, days_back=90):
        """
        Search for scientific publications related to the query.
        
        Args:
            query (str): The search query (drug or disease name).
            max_results (int): Maximum number of results to return.
            days_back (int): Number of days to look back for publications.
            
        Returns:
            pd.DataFrame: DataFrame with publication information.
        """
        start_time = datetime.now()
        logger.info(f"Searching NCBI publications for: {query}, days_back={days_back}")
        
        self._respect_rate_limit()
        
        # Calculate date range
        date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
        date_to = datetime.now().strftime("%Y/%m/%d")
        
        # Construct the search parameters
        params = {
            "db": "pubmed",
            "term": f"{query}[Title/Abstract]",
            "mindate": date_from,
            "maxdate": date_to,
            "retmode": "json",
            "retmax": max_results,
            "sort": "relevance",
            "tool": self.tool,
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        # Make the search request
        try:
            logger.debug(f"NCBI search request with params: {params}")
            search_url = f"{self.base_url}/esearch.fcgi"
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            search_data = response.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                logger.warning(f"No publications found for query: {query}")
                return pd.DataFrame()
            
            logger.debug(f"Found {len(id_list)} publication IDs")
            
            # Fetch detailed information for each publication
            publications = self._fetch_publication_details(id_list)
            
            # Fetch MeSH terms for each publication
            for pub in publications:
                pub_id = pub.get("pmid")
                if pub_id:
                    mesh_terms = self._fetch_mesh_terms(pub_id)
                    pub["mesh_terms"] = mesh_terms
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            logger.info(f"Completed NCBI search in {processing_time:.2f} seconds, found {len(publications)} publications")
            
            return pd.DataFrame(publications)
            
        except Exception as e:
            logger.error(f"Error searching NCBI publications: {str(e)}")
            return pd.DataFrame()
    
    def _fetch_publication_details(self, id_list):
        """
        Fetch detailed information for a list of publication IDs.
        
        Args:
            id_list (list): List of PubMed IDs.
            
        Returns:
            list: List of publication details.
        """
        self._respect_rate_limit()
        logger.debug(f"Fetching details for {len(id_list)} publications")
        
        # Convert ID list to comma-separated string
        ids = ",".join(id_list)
        
        params = {
            "db": "pubmed",
            "id": ids,
            "retmode": "json",
            "rettype": "abstract",
            "tool": self.tool,
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        try:
            fetch_url = f"{self.base_url}/efetch.fcgi"
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("PubmedArticleSet", {}).get("PubmedArticle", [])
            
            publications = []
            
            for article in articles:
                # Extract article data
                pub = {}
                
                # Get PubMed ID
                pub["pmid"] = article.get("MedlineCitation", {}).get("PMID", {}).get("content", "")
                
                # Get article metadata
                article_data = article.get("MedlineCitation", {}).get("Article", {})
                
                # Get title
                pub["title"] = article_data.get("ArticleTitle", "")
                
                # Get journal info
                journal = article_data.get("Journal", {})
                pub["journal"] = journal.get("Title", "")
                
                # Get publication date
                pub_date = journal.get("JournalIssue", {}).get("PubDate", {})
                year = pub_date.get("Year", "")
                month = pub_date.get("Month", "")
                day = pub_date.get("Day", "")
                
                pub["publication_date"] = f"{year}/{month}/{day}" if year else ""
                
                # Get authors
                authors = article_data.get("AuthorList", {}).get("Author", [])
                author_names = []
                
                for author in authors:
                    last_name = author.get("LastName", "")
                    fore_name = author.get("ForeName", "")
                    if last_name and fore_name:
                        author_names.append(f"{last_name} {fore_name}")
                    elif last_name:
                        author_names.append(last_name)
                
                pub["authors"] = ", ".join(author_names)
                
                # Get abstract
                abstract_text = []
                abstract = article_data.get("Abstract", {}).get("AbstractText", [])
                
                if isinstance(abstract, list):
                    for section in abstract:
                        if isinstance(section, dict):
                            label = section.get("Label", "")
                            content = section.get("content", "")
                            if label and content:
                                abstract_text.append(f"{label}: {content}")
                            elif content:
                                abstract_text.append(content)
                        elif section:
                            abstract_text.append(section)
                elif abstract:
                    abstract_text.append(abstract)
                
                pub["abstract"] = " ".join(abstract_text)
                
                # Get keywords
                keywords = article.get("MedlineCitation", {}).get("KeywordList", [])
                keyword_list = []
                
                if isinstance(keywords, list):
                    for kw_list in keywords:
                        kw = kw_list.get("Keyword", [])
                        if isinstance(kw, list):
                            keyword_list.extend([k for k in kw if k])
                        elif kw:
                            keyword_list.append(kw)
                
                pub["keywords"] = ", ".join(keyword_list)
                
                publications.append(pub)
            
            logger.debug(f"Successfully processed {len(publications)} publication details")
            return publications
            
        except Exception as e:
            logger.error(f"Error fetching publication details: {str(e)}")
            return []
    
    def _fetch_mesh_terms(self, pub_id):
        """
        Fetch MeSH terms for a publication.
        
        Args:
            pub_id (str): PubMed ID.
            
        Returns:
            list: List of MeSH terms.
        """
        self._respect_rate_limit()
        logger.debug(f"Fetching MeSH terms for publication {pub_id}")
        
        params = {
            "db": "pubmed",
            "id": pub_id,
            "retmode": "xml",  # XML is better for extracting MeSH terms
            "tool": self.tool,
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        try:
            fetch_url = f"{self.base_url}/efetch.fcgi"
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()
            
            # Parse the XML response
            soup = BeautifulSoup(response.content, "lxml")
            
            mesh_terms = []
            mesh_headings = soup.find_all("MeshHeading")
            
            for heading in mesh_headings:
                descriptor = heading.find("DescriptorName")
                if descriptor:
                    term = descriptor.get_text().strip()
                    mesh_terms.append(term)
                    
                    # Get qualifiers if any
                    qualifiers = heading.find_all("QualifierName")
                    for qualifier in qualifiers:
                        q_term = qualifier.get_text().strip()
                        mesh_terms.append(f"{term}/{q_term}")
            
            logger.debug(f"Found {len(mesh_terms)} MeSH terms for publication {pub_id}")
            return mesh_terms
            
        except Exception as e:
            logger.error(f"Error fetching MeSH terms for publication {pub_id}: {str(e)}")
            return []
    
    def search_mesh_term(self, term):
        """
        Search for MeSH terms related to a query.
        
        Args:
            term (str): The search term.
            
        Returns:
            list: List of matching MeSH terms.
        """
        start_time = datetime.now()
        logger.info(f"Searching MeSH terms for: {term}")
        
        self._respect_rate_limit()
        
        params = {
            "db": "mesh",
            "term": term,
            "retmode": "json",
            "retmax": 20,
            "tool": self.tool,
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        try:
            search_url = f"{self.base_url}/esearch.fcgi"
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            search_data = response.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                logger.warning(f"No MeSH terms found for: {term}")
                return []
            
            # Fetch detailed information for each MeSH term
            mesh_terms = self._fetch_mesh_details(id_list)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            logger.info(f"Completed MeSH search in {processing_time:.2f} seconds, found {len(mesh_terms)} terms")
            
            return mesh_terms
            
        except Exception as e:
            logger.error(f"Error searching MeSH terms: {str(e)}")
            return []
    
    def _fetch_mesh_details(self, id_list):
        """
        Fetch detailed information for a list of MeSH term IDs.
        
        Args:
            id_list (list): List of MeSH term IDs.
            
        Returns:
            list: List of MeSH term details.
        """
        self._respect_rate_limit()
        logger.debug(f"Fetching details for {len(id_list)} MeSH terms")
        
        # Convert ID list to comma-separated string
        ids = ",".join(id_list)
        
        params = {
            "db": "mesh",
            "id": ids,
            "retmode": "xml",  # XML provides more structured data for MeSH
            "tool": self.tool,
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        try:
            fetch_url = f"{self.base_url}/efetch.fcgi"
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()
            
            # Parse the XML response
            soup = BeautifulSoup(response.content, "lxml")
            
            mesh_terms = []
            
            for record in soup.find_all("DescriptorRecord"):
                mesh_term = {}
                
                # Get MeSH term ID
                descriptor_ui = record.find("DescriptorUI")
                if descriptor_ui:
                    mesh_term["id"] = descriptor_ui.get_text().strip()
                
                # Get MeSH term name
                descriptor_name = record.find("DescriptorName")
                if descriptor_name:
                    mesh_term["name"] = descriptor_name.get_text().strip()
                
                # Get scope note (description)
                scope_note = record.find("ScopeNote")
                if scope_note:
                    mesh_term["description"] = scope_note.get_text().strip()
                
                # Get tree numbers
                tree_numbers = []
                for tn in record.find_all("TreeNumber"):
                    tree_numbers.append(tn.get_text().strip())
                mesh_term["tree_numbers"] = tree_numbers
                
                # Get concepts
                concepts = []
                for concept in record.find_all("Concept"):
                    concept_data = {
                        "name": concept.find("ConceptName").find("String").get_text().strip() if concept.find("ConceptName") else "",
                        "scope_note": concept.find("ScopeNote").get_text().strip() if concept.find("ScopeNote") else ""
                    }
                    concepts.append(concept_data)
                mesh_term["concepts"] = concepts
                
                mesh_terms.append(mesh_term)
            
            logger.debug(f"Successfully processed {len(mesh_terms)} MeSH term details")
            return mesh_terms
            
        except Exception as e:
            logger.error(f"Error fetching MeSH term details: {str(e)}")
            return []
