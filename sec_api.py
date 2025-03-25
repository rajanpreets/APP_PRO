import requests
import pandas as pd
import os
import time
from datetime import datetime
import json
import logging
import re

# Configure logging
logger = logging.getLogger(__name__)

class SECAPI:
    """A class for fetching and processing data from the SEC API."""
    
    def __init__(self):
        """Initialize the SEC API client."""
        self.base_url = "https://data.sec.gov/api"
        self.headers = {
            'User-Agent': os.environ.get('SEC_USER_AGENT', 'Company Name AdminContact@email.com')
        }
        
        # Log important info
        logger.info(f"Initialized SEC API client with User-Agent: {self.headers['User-Agent']}")
        
        # List of major pharmaceutical companies
        self.pharma_companies = {
            'JNJ': 'Johnson & Johnson',
            'PFE': 'Pfizer Inc.',
            'NVS': 'Novartis AG',
            'MRK': 'Merck & Co., Inc.',
            'ABBV': 'AbbVie Inc.',
            'AMGN': 'Amgen Inc.',
            'BMY': 'Bristol-Myers Squibb Company',
            'GSK': 'GlaxoSmithKline plc',
            'AZN': 'AstraZeneca PLC',
            'SNY': 'Sanofi',
            'LLY': 'Eli Lilly and Company',
            'GILD': 'Gilead Sciences, Inc.',
            'BIIB': 'Biogen Inc.',
            'REGN': 'Regeneron Pharmaceuticals, Inc.',
            'VRTX': 'Vertex Pharmaceuticals Incorporated',
            'MRNA': 'Moderna, Inc.',
            'BHC': 'Bausch Health Companies Inc.',
            'TEVA': 'Teva Pharmaceutical Industries Limited',
            'ALXN': 'Alexion Pharmaceuticals, Inc.',
            'ZTS': 'Zoetis Inc.',
            # Additional major pharmaceutical companies
            'RHHBY': 'Roche Holding AG',
            'RPRX': 'Royalty Pharma plc',
            'HZNP': 'Horizon Therapeutics Public Limited Company',
            'JAZZ': 'Jazz Pharmaceuticals plc',
            'INCY': 'Incyte Corporation',
            'ALNY': 'Alnylam Pharmaceuticals, Inc.',
            'SGEN': 'Seagen Inc.',
            'UTHR': 'United Therapeutics Corporation',
            'NBIX': 'Neurocrine Biosciences, Inc.',
            'IONS': 'Ionis Pharmaceuticals, Inc.'
        }
        
        # Reverse mapping for company name to ticker lookup
        self.company_to_ticker = {company.lower(): ticker for ticker, company in self.pharma_companies.items()}
        
        # Create alternative mappings for shortened company names
        for ticker, company in list(self.pharma_companies.items()):
            # Add mapping without "Inc.", "Ltd.", etc.
            simplified_name = re.sub(r'\s+(Inc\.?|Ltd\.?|plc|LLC|Corporation|Company|AG|Co\.|&\s+Co\.)$', '', company, flags=re.IGNORECASE)
            if simplified_name.lower() != company.lower():
                self.company_to_ticker[simplified_name.lower()] = ticker
            
            # Add mapping for company name before "Pharmaceuticals", "Therapeutics", etc.
            short_name = re.sub(r'\s+(Pharmaceuticals|Therapeutics|Biosciences|Biotechnology).*$', '', company, flags=re.IGNORECASE)
            if short_name.lower() != company.lower() and short_name.lower() != simplified_name.lower():
                self.company_to_ticker[short_name.lower()] = ticker
    
    def get_ticker_from_company_name(self, company_name):
        """
        Convert a company name to its stock ticker symbol.
        
        Args:
            company_name (str): Company name to look up.
            
        Returns:
            str: Ticker symbol or None if not found.
        """
        logger.info(f"Looking up ticker for company name: {company_name}")
        
        # Clean and normalize the input company name
        company_name = company_name.lower().strip()
        
        # Check direct match in our dictionary
        if company_name in self.company_to_ticker:
            ticker = self.company_to_ticker[company_name]
            logger.debug(f"Found direct ticker match: {ticker} for {company_name}")
            return ticker
            
        # Check for partial matches
        for name, ticker in self.company_to_ticker.items():
            if company_name in name or name in company_name:
                logger.debug(f"Found partial ticker match: {ticker} for {company_name} via {name}")
                return ticker
                
        # If no match found in our dictionary, try SEC lookup
        try:
            # SEC ticker lookup endpoint
            url = "https://www.sec.gov/files/company_tickers.json"
            
            logger.debug(f"Searching SEC database for company: {company_name}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Search for the company name in the SEC database
            for _, company_info in data.items():
                sec_company_name = company_info.get('title', '').lower()
                if (company_name in sec_company_name or 
                    sec_company_name in company_name or 
                    self._similarity_score(company_name, sec_company_name) > 0.8):
                    ticker = company_info.get('ticker')
                    logger.debug(f"Found SEC ticker match: {ticker} for {company_name}")
                    return ticker
            
            logger.warning(f"No ticker found for company name: {company_name}")
            return None
                
        except Exception as e:
            logger.error(f"Error looking up ticker for {company_name}: {str(e)}")
            return None
    
    def _similarity_score(self, str1, str2):
        """
        Calculate a simple similarity score between two strings.
        
        Args:
            str1 (str): First string.
            str2 (str): Second string.
            
        Returns:
            float: Similarity score between 0 and 1.
        """
        # Convert to sets of words
        set1 = set(str1.lower().split())
        set2 = set(str2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1) + len(set2) - intersection
        
        if union == 0:
            return 0
        
        return intersection / union
    
    def search_company_by_drug(self, drug_name):
        """
        Map a drug name to potential pharmaceutical companies.
        
        Args:
            drug_name (str): Name of the drug to search for.
            
        Returns:
            list: List of potential companies associated with the drug.
        """
        logger.info(f"Searching for companies associated with drug: {drug_name}")
        relevant_companies = []
        
        # Try to find direct matches in company names
        for ticker, company_name in self.pharma_companies.items():
            if drug_name.lower() in company_name.lower():
                relevant_companies.append({
                    'ticker': ticker,
                    'name': company_name,
                    'match_type': 'company_name'
                })
                logger.debug(f"Found direct company name match: {company_name}")
        
        # If no direct matches, use SERPER API or other means to find the association
        if not relevant_companies:
            logger.debug(f"No direct company matches found for {drug_name}, using fallback")
            # In a real implementation, you'd query an external API or database
            # For now, we'll just return the top 3 companies as a fallback
            top_companies = list(self.pharma_companies.items())[:3]
            for ticker, company_name in top_companies:
                relevant_companies.append({
                    'ticker': ticker,
                    'name': company_name,
                    'match_type': 'fallback'
                })
        
        logger.info(f"Found {len(relevant_companies)} potential companies for {drug_name}")
        return relevant_companies
    
    def get_company_facts(self, ticker_or_name):
        """
        Fetch company facts from SEC API.
        
        Args:
            ticker_or_name (str): Company stock ticker symbol or company name.
            
        Returns:
            dict: Company facts data.
        """
        # First determine if we have a ticker or company name
        ticker = ticker_or_name.upper() if ticker_or_name.upper() in self.pharma_companies else None
        
        # If not a recognized ticker, try to get ticker from company name
        if not ticker:
            ticker = self.get_ticker_from_company_name(ticker_or_name)
            if not ticker:
                logger.warning(f"Could not find ticker for: {ticker_or_name}")
                return None
        
        logger.debug(f"Getting company facts for ticker: {ticker}")
        try:
            cik = self._get_cik_from_ticker(ticker)
            if not cik:
                logger.warning(f"Could not find CIK for ticker: {ticker}")
                return None
                
            # Add leading zeros to make it 10 digits
            padded_cik = cik.zfill(10)
            
            # Company facts endpoint
            url = f"{self.base_url}/xbrl/companyfacts/CIK{padded_cik}.json"
            
            logger.debug(f"Fetching SEC company facts from: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching company facts for {ticker}: {str(e)}")
            return None
    
    def get_company_submissions(self, ticker_or_name):
        """
        Fetch company submission history from SEC API.
        
        Args:
            ticker_or_name (str): Company stock ticker symbol or company name.
            
        Returns:
            dict: Company submission data.
        """
        # First determine if we have a ticker or company name
        ticker = ticker_or_name.upper() if ticker_or_name.upper() in self.pharma_companies else None
        
        # If not a recognized ticker, try to get ticker from company name
        if not ticker:
            ticker = self.get_ticker_from_company_name(ticker_or_name)
            if not ticker:
                logger.warning(f"Could not find ticker for: {ticker_or_name}")
                return None
        
        logger.debug(f"Getting company submissions for ticker: {ticker}")
        try:
            cik = self._get_cik_from_ticker(ticker)
            if not cik:
                logger.warning(f"Could not find CIK for ticker: {ticker}")
                return None
                
            # Add leading zeros to make it 10 digits
            padded_cik = cik.zfill(10)
            
            # Company submissions endpoint
            url = f"{self.base_url}/submissions/CIK{padded_cik}.json"
            
            logger.debug(f"Fetching SEC company submissions from: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching company submissions for {ticker}: {str(e)}")
            return None
    
    def get_company_concept(self, ticker_or_name, concept_name):
        """
        Fetch specific concept data for a company from SEC API.
        
        Args:
            ticker_or_name (str): Company stock ticker symbol or company name.
            concept_name (str): Name of the concept to fetch.
            
        Returns:
            dict: Company concept data.
        """
        # First determine if we have a ticker or company name
        ticker = ticker_or_name.upper() if ticker_or_name.upper() in self.pharma_companies else None
        
        # If not a recognized ticker, try to get ticker from company name
        if not ticker:
            ticker = self.get_ticker_from_company_name(ticker_or_name)
            if not ticker:
                logger.warning(f"Could not find ticker for: {ticker_or_name}")
                return None
        
        logger.debug(f"Getting company concept {concept_name} for ticker: {ticker}")
        try:
            cik = self._get_cik_from_ticker(ticker)
            if not cik:
                logger.warning(f"Could not find CIK for ticker: {ticker}")
                return None
                
            # Add leading zeros to make it 10 digits
            padded_cik = cik.zfill(10)
            
            # Company concept endpoint
            url = f"{self.base_url}/xbrl/companyconcept/CIK{padded_cik}/us-gaap/{concept_name}.json"
            
            logger.debug(f"Fetching SEC company concept from: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching company concept {concept_name} for {ticker}: {str(e)}")
            return None
    
    def _get_cik_from_ticker(self, ticker):
        """
        Convert ticker symbol to CIK (Central Index Key).
        
        Args:
            ticker (str): Company stock ticker symbol.
            
        Returns:
            str: CIK number or None if not found.
        """
        try:
            # SEC ticker to CIK lookup endpoint
            url = "https://www.sec.gov/files/company_tickers.json"
            
            logger.debug(f"Looking up CIK for ticker: {ticker}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Search for the ticker in the response
            for _, company_info in data.items():
                if company_info.get('ticker') == ticker.upper():
                    cik = str(company_info.get('cik_str'))
                    logger.debug(f"Found CIK for {ticker}: {cik}")
                    return cik
            
            logger.warning(f"No CIK found for ticker: {ticker}")
            return None
        except Exception as e:
            logger.error(f"Error converting ticker {ticker} to CIK: {str(e)}")
            return None
    
    def extract_financial_metrics(self, facts_data):
        """
        Extract key financial metrics from company facts data.
        
        Args:
            facts_data (dict): Company facts data from SEC API.
            
        Returns:
            dict: Key financial metrics.
        """
        if not facts_data:
            return {}
            
        metrics = {}
        
        try:
            # Extract company information
            metrics['companyName'] = facts_data.get('entityName')
            metrics['tradingSymbol'] = facts_data.get('tickers', [''])[0]
            
            # Extract key financial data if available
            us_gaap = facts_data.get('facts', {}).get('us-gaap', {})
            
            # Revenue
            if 'Revenues' in us_gaap:
                revenue_units = us_gaap['Revenues'].get('units', {})
                if 'USD' in revenue_units:
                    # Sort by filing date and get the most recent
                    sorted_revenues = sorted(
                        revenue_units['USD'], 
                        key=lambda x: x.get('fy', 0) * 10000 + x.get('fp_end', 0),
                        reverse=True
                    )
                    if sorted_revenues:
                        metrics['revenue'] = sorted_revenues[0].get('val')
                        metrics['revenueFiscalYear'] = sorted_revenues[0].get('fy')
                        metrics['revenueFiscalPeriod'] = sorted_revenues[0].get('fp')
            
            # Net Income
            if 'NetIncomeLoss' in us_gaap:
                income_units = us_gaap['NetIncomeLoss'].get('units', {})
                if 'USD' in income_units:
                    # Sort by filing date and get the most recent
                    sorted_income = sorted(
                        income_units['USD'], 
                        key=lambda x: x.get('fy', 0) * 10000 + x.get('fp_end', 0),
                        reverse=True
                    )
                    if sorted_income:
                        metrics['netIncome'] = sorted_income[0].get('val')
                        metrics['netIncomeFiscalYear'] = sorted_income[0].get('fy')
                        metrics['netIncomeFiscalPeriod'] = sorted_income[0].get('fp')
            
            # Research and Development Expense
            if 'ResearchAndDevelopmentExpense' in us_gaap:
                rd_units = us_gaap['ResearchAndDevelopmentExpense'].get('units', {})
                if 'USD' in rd_units:
                    # Sort by filing date and get the most recent
                    sorted_rd = sorted(
                        rd_units['USD'], 
                        key=lambda x: x.get('fy', 0) * 10000 + x.get('fp_end', 0),
                        reverse=True
                    )
                    if sorted_rd:
                        metrics['rdExpense'] = sorted_rd[0].get('val')
                        metrics['rdExpenseFiscalYear'] = sorted_rd[0].get('fy')
                        metrics['rdExpenseFiscalPeriod'] = sorted_rd[0].get('fp')
        except Exception as e:
            logger.error(f"Error extracting financial metrics: {str(e)}")
        
        return metrics
    
    def get_company_details(self, company_input):
        """
        Get financial details for a company or companies associated with a drug.
        
        Args:
            company_input (str): Drug name or company name to search for.
            
        Returns:
            pd.DataFrame: DataFrame with company financial information.
        """
        start_time = datetime.now()
        logger.info(f"Getting company details for input: {company_input}")
        
        companies = []
        
        # Check if input might be a company name rather than a drug
        ticker = self.get_ticker_from_company_name(company_input)
        if ticker:
            # Input appears to be a company name, use direct lookup
            company_name = self.pharma_companies.get(ticker, company_input)
            companies = [{
                'ticker': ticker,
                'name': company_name,
                'match_type': 'direct_company_lookup' 
            }]
            logger.debug(f"Input appears to be a company name, found ticker: {ticker}")
        else:
            # Assume input is a drug name and find associated companies
            companies = self.search_company_by_drug(company_input)
        
        if not companies:
            logger.warning(f"No companies found for input: {company_input}")
            return pd.DataFrame()
        
        company_data = []
        
        for company in companies:
            ticker = company['ticker']
            
            # Respect SEC API rate limits
            time.sleep(0.1)
            
            # Get company facts
            facts_data = self.get_company_facts(ticker)
            
            # Get company submissions
            submissions_data = self.get_company_submissions(ticker)
            
            # Extract metrics
            metrics = self.extract_financial_metrics(facts_data)
            
            # Add company data
            company_info = {
                'ticker': ticker,
                'name': company['name'],
                'match_type': company['match_type']
            }
            
            # Add company address if available
            if submissions_data and 'addresses' in submissions_data:
                address = submissions_data.get('addresses', {}).get('business', {})
                company_info['street1'] = address.get('street1', '')
                company_info['street2'] = address.get('street2', '')
                company_info['city'] = address.get('city', '')
                company_info['stateOrCountry'] = address.get('stateOrCountry', '')
                company_info['zipCode'] = address.get('zipCode', '')
            
            # Add metrics
            company_info.update(metrics)
            
            # Get recent filings if available
            if submissions_data and 'filings' in submissions_data:
                recent_filings = submissions_data.get('filings', {}).get('recent', {})
                if recent_filings:
                    forms = recent_filings.get('form', [])
                    filing_dates = recent_filings.get('filingDate', [])
                    accession_numbers = recent_filings.get('accessionNumber', [])
                    
                    # Get the most recent 10-K (annual report)
                    if '10-K' in forms:
                        idx = forms.index('10-K')
                        company_info['recent10K'] = filing_dates[idx] if idx < len(filing_dates) else ''
                        company_info['recent10KAccessionNumber'] = accession_numbers[idx] if idx < len(accession_numbers) else ''
                    
                    # Get the most recent 10-Q (quarterly report)
                    if '10-Q' in forms:
                        idx = forms.index('10-Q')
                        company_info['recent10Q'] = filing_dates[idx] if idx < len(filing_dates) else ''
                        company_info['recent10QAccessionNumber'] = accession_numbers[idx] if idx < len(accession_numbers) else ''
            
            company_data.append(company_info)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Completed SEC data fetching in {processing_time:.2f} seconds, found {len(company_data)} companies")
        
        return pd.DataFrame(company_data)
