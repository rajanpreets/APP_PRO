import os
from dotenv import load_dotenv
import fda_api
import ct_api
import sec_api
import ncbi_api
import serper_api
import llm_api
import snomed_api
import pandas as pd
import concurrent.futures

# Load environment variables
load_dotenv()

class DataIntegrator:
    """Main class to coordinate data retrieval from multiple APIs"""
    
    def __init__(self):
        """Initialize API client instances"""
        self.fda_client = fda_api.OpenFDA()
        self.ct_client = ct_api.ClinicalTrialsAPI()
        self.sec_client = sec_api.SECAPI()
        self.ncbi_client = ncbi_api.NCBIAPI()
        self.serper_client = serper_api.SerperAPI()
        self.llm_client = llm_api.GroqAPI()
        self.snomed_client = snomed_api.SnomedAPI()
        
    def search_drug(self, drug_name, sources=None):
        """
        Search for drug information across selected APIs
        
        Args:
            drug_name (str): Name of the drug to search
            sources (list): List of API sources to include
            
        Returns:
            dict: Consolidated results from all selected APIs
        """
        results = {}
        
        # Define a function to fetch data from each API
        def fetch_fda():
            try:
                return self.fda_client.open_fda_main(drug_name, 'drug')
            except Exception as e:
                return {'error': str(e)}
                
        def fetch_clinical_trials():
            try:
                return self.ct_client.get_clinical_trials_data(drug_name)
            except Exception as e:
                return {'error': str(e)}
                
        def fetch_sec():
            try:
                return self.sec_client.get_company_details(drug_name)
            except Exception as e:
                return {'error': str(e)}
                
        def fetch_ncbi():
            try:
                return self.ncbi_client.search_publications(drug_name)
            except Exception as e:
                return {'error': str(e)}
                
        def fetch_news():
            try:
                return self.serper_client.search_news(drug_name, num_results=20, days_back=30)
            except Exception as e:
                return {'error': str(e)}
                
        def fetch_snomed():
            try:
                return self.snomed_client.search_terms(drug_name)
            except Exception as e:
                return {'error': str(e)}
        
        # Create a dictionary of API fetching functions
        fetch_functions = {
            'fda': fetch_fda,
            'clinical_trials': fetch_clinical_trials,
            'sec': fetch_sec,
            'ncbi': fetch_ncbi,
            'news': fetch_news,
            'snomed': fetch_snomed
        }
        
        # Determine which sources to include
        if sources is None:
            selected_sources = list(fetch_functions.keys())
        else:
            selected_sources = [source for source in sources if source in fetch_functions]
        
        # Use ThreadPoolExecutor to fetch data concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected_sources)) as executor:
            # Create a dictionary mapping sources to their future results
            future_to_source = {
                executor.submit(fetch_functions[source]): source 
                for source in selected_sources
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    results[source] = future.result()
                except Exception as e:
                    results[source] = {'error': f"Error fetching data from {source}: {str(e)}"}
        
        return results
    
    def search_disease(self, disease_name, sources=None):
        """
        Search for disease information across selected APIs
        
        Args:
            disease_name (str): Name of the disease to search
            sources (list): List of API sources to include
            
        Returns:
            dict: Consolidated results from all selected APIs
        """
        results = {}
        
        # Define a function to fetch data from each API
        def fetch_fda():
            try:
                return self.fda_client.open_fda_main(disease_name, 'disease')
            except Exception as e:
                return {'error': str(e)}
                
        def fetch_clinical_trials():
            try:
                return self.ct_client.get_clinical_trials_data(disease_name)
            except Exception as e:
                return {'error': str(e)}
                
        def fetch_ncbi():
            try:
                return self.ncbi_client.search_publications(disease_name)
            except Exception as e:
                return {'error': str(e)}
                
        def fetch_serper():
            try:
                return self.serper_client.search_medical(disease_name)
            except Exception as e:
                return {'error': str(e)}
                
        def fetch_news():
            try:
                return self.serper_client.search_news(disease_name, num_results=20, days_back=30)
            except Exception as e:
                return {'error': str(e)}
                
        def fetch_snomed():
            try:
                return self.snomed_client.search_terms(disease_name)
            except Exception as e:
                return {'error': str(e)}
        
        # Create a dictionary of API fetching functions
        fetch_functions = {
            'fda': fetch_fda,
            'clinical_trials': fetch_clinical_trials,
            'ncbi': fetch_ncbi,
            'serper': fetch_serper,
            'news': fetch_news,
            'snomed': fetch_snomed
        }
        
        # Determine which sources to include
        if sources is None:
            selected_sources = list(fetch_functions.keys())
        else:
            selected_sources = [source for source in sources if source in fetch_functions]
        
        # Use ThreadPoolExecutor to fetch data concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected_sources)) as executor:
            # Create a dictionary mapping sources to their future results
            future_to_source = {
                executor.submit(fetch_functions[source]): source 
                for source in selected_sources
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    results[source] = future.result()
                except Exception as e:
                    results[source] = {'error': f"Error fetching data from {source}: {str(e)}"}
        
        return results
    
    def summarize_with_llm(self, data, query, search_type=None):
        """
        Use Groq LLM to summarize and analyze the collected data
        
        Args:
            data (dict): Data collected from various APIs
            query (str): The original search query
            search_type (str, optional): 'drug' or 'disease'
            
        Returns:
            dict: LLM-generated summaries and insights
        """
        try:
            if search_type:
                data['type'] = search_type
            return self.llm_client.summarize_data(data, query)
        except Exception as e:
            return {'error': str(e)}

# Instantiate the main integration class for use by the Flask app
data_integrator = DataIntegrator()
