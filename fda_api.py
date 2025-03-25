import requests
import re
import pandas as pd
import os
import logging
from datetime import datetime
import time

# Configure logging
logger = logging.getLogger(__name__)

class FilterParserData:
    """Helper class for parsing and cleaning FDA API data"""
    
    @staticmethod
    def clean_openfda_value(value):
        """
        Clean values returned from the OpenFDA API.
        
        Args:
            value: The value to clean, which could be a list, string, or other data type.
            
        Returns:
            The cleaned value, typically as a string if it was originally a list.
        """
        if isinstance(value, list):
            return ', '.join(str(item) for item in value)
        return value

class OpenFDA:
    """A class for fetching and processing data from the Open FDA API."""

    def __init__(self, api_key=None):
        """
        Initialize the OpenFDA client.
        
        Args:
            api_key (str, optional): FDA API key for higher rate limits.
        """
        self.api_key = api_key or os.environ.get('FDA_API_KEY')
        logger.info(f"Initialized OpenFDA client with API key: {'Present' if self.api_key else 'None'}")
    
    def total_rows_in_openfda(self, user_keyword, keyword_domain, timeout=5, max_retries=3):
        """
        Fetch the total number of results matching the given keyword and domain from the Open FDA API.

        Args:
            user_keyword (str): The keyword to search for in the Open FDA API.
            keyword_domain (str): The domain to search within (e.g., "disease" or "drug").
            timeout (int, optional): The maximum number of seconds to wait for the request to complete. Defaults to 5.
            max_retries (int, optional): The maximum number of times to retry the request if it fails. Defaults to 3.

        Returns:
            int: The total number of results found, or None if the request fails.
        """
        api_url = self.open_fda_url_selection(user_keyword, keyword_domain)
        logger.debug(f"Getting total rows from FDA API: {api_url}")
        
        for retry in range(max_retries):
            try:
                timeout_occurred = False
                response = requests.get(api_url, timeout=timeout)
                response.raise_for_status()
                if response.status_code == 200:
                    data = response.json()
                    total = data["meta"]["results"]["total"]
                    logger.debug(f"Total FDA results for {user_keyword} in {keyword_domain}: {total}")
                    return total
            except requests.exceptions.Timeout:
                timeout_occurred = True
                logger.warning(f"FDA API request timed out (attempt {retry+1}/{max_retries}). Retrying...")
            except requests.exceptions.RequestException as e:
                logger.error(f"FDA API request error: {str(e)}")
                break

            if not timeout_occurred:
                break
                
            # Add exponential backoff for retries
            time.sleep(2 ** retry)

        logger.warning(f"Failed to get total rows for {user_keyword} in {keyword_domain}")
        return None

    def open_fda_url_selection(self, user_keyword, keyword_domain, limit=1):
        """
        Generate the API URL for fetching data from the Open FDA API based on the given keyword and domain.

        Args:
            user_keyword (str): The keyword to search for in the Open FDA API.
            keyword_domain (str): The domain to search within (e.g., "disease" or "drug").
            limit (int, optional): The maximum number of results to return. Defaults to 1.

        Returns:
            str: The generated API URL.
        """
        api_params = f"&api_key={self.api_key}" if self.api_key else ""
        
        if keyword_domain == "disease":
            open_fda_api_url = f'https://api.fda.gov/drug/label.json?search=indications_and_usage:"{user_keyword}"&limit={limit}{api_params}'
        elif keyword_domain == "drug":
            open_fda_api_url = f'https://api.fda.gov/drug/label.json?search=brand_name.exact:"{user_keyword}"+generic_name.exact:"{user_keyword}"&limit={limit}{api_params}'
        return open_fda_api_url

    def open_fda_data(self, user_keyword, keyword_domain, limit, timeout=5, max_retries=3):
        """
        Fetch data from the Open FDA API for the given keyword, domain, and limit, and return a list of dictionaries containing the extracted data.

        Args:
            user_keyword (str): The keyword to search for in the Open FDA API.
            keyword_domain (str): The domain to search within (e.g., "disease" or "drug").
            limit (int): The maximum number of results to return.
            timeout (int, optional): The maximum number of seconds to wait for the request to complete. Defaults to 5.
            max_retries (int, optional): The maximum number of times to retry the request if it fails. Defaults to 3.

        Returns:
            list: A list of dictionaries containing the extracted data, or None if the request fails.
        """
        if limit is not None and limit > 1000:
            limit = 1000

        api_url = self.open_fda_url_selection(user_keyword, keyword_domain, limit)
        logger.debug(f"Fetching FDA data from: {api_url}")
        
        needed_column_names = {
            'adverse_reactions',
            'application_number',
            'brand_name',
            'clinical_pharmacology',
            'clinical_studies',
            'contraindications',
            'description',
            'dosage_and_administration',
            'drug_interactions',
            'generic_name',
            'how_supplied',
            'indications_and_usage',
            'information_for_patients',
            'is_original_packager',
            'manufacturer_name',
            'mechanism_of_action',
            'pharm_class_cs',
            'pharm_class_epc',
            'pharm_class_moa',
            'pharmacodynamics',
            'pharmacokinetics',
            'product_type',
            'route',
            'substance_name',
            'upc',
            'warnings',
            'warnings_and_cautions',
            'laboratory_tests',
            'drug_interactions',
            'precautions',
            'adverse_reactions'
        }
        
        for retry in range(max_retries):
            try:
                timeout_occurred = False
                response = requests.get(api_url, timeout=timeout)
                response.raise_for_status()
                if response.status_code == 200:
                    data = response.json()
                    api_data = []
                    for current_data in data["results"]:
                        api_unit_data = {}
                        for key, value in current_data.items():
                            if key == "openfda":
                                for openfda_key, openfda_value in value.items():
                                    if openfda_key in needed_column_names:
                                        api_unit_data[openfda_key] = (
                                            FilterParserData.clean_openfda_value(
                                                openfda_value
                                            )
                                        )
                            else:
                                if key in needed_column_names:
                                    api_unit_data[key] = (
                                        FilterParserData.clean_openfda_value(value)
                                    )
                        api_data.append(api_unit_data)
                    logger.debug(f"Successfully fetched {len(api_data)} FDA records for {user_keyword}")
                    return api_data
            except requests.exceptions.Timeout:
                timeout_occurred = True
                logger.warning(f"FDA API data request timed out (attempt {retry+1}/{max_retries}). Retrying...")
            except requests.exceptions.RequestException as e:
                logger.error(f"FDA API data request error: {str(e)}")
                break
            if not timeout_occurred:
                break
                
            # Add exponential backoff for retries
            time.sleep(2 ** retry)
            
        logger.warning(f"Failed to fetch FDA data for {user_keyword} in {keyword_domain}")
        return None

    def remove_column_headers_from_text(self, df):
        """
        Remove column headers from text columns in the DataFrame.
        
        Args:
            df (pandas.DataFrame): DataFrame with text columns.
            
        Returns:
            pandas.DataFrame: DataFrame with cleaned text columns.
        """
        columns_to_clean = {
            'description': 'Description',
            'clinical_pharmacology': 'Clinical Pharmacology',
            'indications_and_usage': 'Indications and Usage',
            'contraindications': 'Contraindications',
            'information_for_patients': 'Information for Patients',
            'drug_interactions': 'Drug Interactions',
            'adverse_reactions': 'Adverse Reactions',
            'dosage_and_administration': 'Dosage and Administration',
            'how_supplied': 'How Supplied',
            'pharmacokinetics': 'Pharmacokinetics',
            'warnings_and_cautions': 'Warnings and Cautions',
            'clinical_studies': 'Clinical Studies',
            'pharmacodynamics': 'Pharmacodynamic Drug Interaction Studies',
            'precautions' : 'PRECAUTIONS',
            'drug_interactions' : 'Drug Interactions',
            'warnings' : 'WARNINGS',
            'adverse_reactions' : 'ADVERSE REACTIONS'
        }
    
        for column, header in columns_to_clean.items():
            if column in df.columns:
                pattern = r'^((?:\S+\s+){0,2})' + re.escape(header) + r'\s*:?\s*'
                
                def clean_text(text):
                    if isinstance(text, str):
                        match = re.match(pattern, text, flags=re.IGNORECASE)
                        if match:
                            preceding = match.group(1).strip()
                            if len(preceding.split()) <= 2:
                                return text[match.end():].strip()
                    return text  # Return original text if no match or > 2 preceding words
                
                df[column] = df[column].apply(clean_text)
        
        return df

    def open_fda_main(self, user_keyword, domain):
        """
        Fetch and process data from the Open FDA API for the given keyword and domain, and return a pandas DataFrame containing the extracted data.

        Args:
            user_keyword (str): The keyword to search for in the Open FDA API.
            domain (str): The domain to search within (e.g., "disease" or "drug").

        Returns:
            pd.DataFrame: A pandas DataFrame containing the fetched and processed data, or None if the request fails.
        """
        start_time = datetime.now()
        logger.info(f"Starting FDA API search for {user_keyword} in domain {domain}")
        
        # Get total results count
        total_rows = self.total_rows_in_openfda(user_keyword, domain)
        
        # Fetch the data
        open_fda_data = self.open_fda_data(user_keyword, domain, total_rows)
        
        if not open_fda_data:
            logger.warning(f"No FDA data found for {user_keyword} in domain {domain}")
            return pd.DataFrame()
        
        # Create DataFrame    
        df = pd.DataFrame(open_fda_data)
        
        # Filter for drugs that match the query term if in drug domain
        if domain == 'drug':
            # Filter for entries that match the drug name
            if 'brand_name' in df.columns and 'generic_name' in df.columns:
                original_count = len(df)
                df = df[
                    df['brand_name'].str.lower().str.contains(user_keyword.lower(), na=False) | 
                    df['generic_name'].str.lower().str.contains(user_keyword.lower(), na=False)
                ]
                filtered_count = len(df)
                logger.debug(f"Filtered FDA results from {original_count} to {filtered_count} matching records")
            
        # Clean text fields
        df = self.remove_column_headers_from_text(df)

        # Drop rows with no brand name or generic name
        if 'brand_name' in df.columns and 'generic_name' in df.columns:
            original_count = len(df)
            df = df.dropna(subset=['brand_name', 'generic_name'], how='all')
            dropped_count = original_count - len(df)
            if dropped_count > 0:
                logger.debug(f"Dropped {dropped_count} rows with no brand or generic name")
        
        # Reorder columns to bring important ones to the front
        columns_to_front = [col for col in [
            'brand_name', 'generic_name', 'manufacturer_name', 
            'application_number', 'indications_and_usage'
        ] if col in df.columns]

        # Reorder the columns by combining the selected columns with the remaining ones
        if columns_to_front:
            df = df[columns_to_front + [col for col in df.columns if col not in columns_to_front]]
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Completed FDA API search in {processing_time:.2f} seconds, found {len(df)} records")
        
        return df
