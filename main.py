from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
import pandas as pd
from datetime import datetime

# Import API modules directly
import fda_api
import ct_api
import sec_api
import ncbi_api
import serper_api
import llm_api
import snomed_api
from dotenv import load_dotenv
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define DataIntegrator class here
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

# Instantiate the data integrator
data_integrator = DataIntegrator()

# Initialize Flask app
app = Flask(__name__, static_folder='build')
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes and origins

@app.route('/api/search', methods=['POST'])
def search():
    """
    Endpoint to search for drug or disease information
    """
    try:
        data = request.json
        query = data.get('query', '')
        search_type = data.get('type', 'drug')
        sources = data.get('sources', None)
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        logger.info(f"Search request: query={query}, type={search_type}, sources={sources}")
        
        # Use the data integrator to search based on type
        if search_type == 'drug':
            results = data_integrator.search_drug(query, sources)
        else:
            results = data_integrator.search_disease(query, sources)
        
        # Convert any pandas DataFrames to dictionaries
        for key in results:
            if isinstance(results[key], pd.DataFrame):
                results[key] = results[key].to_dict(orient='records')
        
        logger.info(f"Search completed successfully for {query}")
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    """
    Endpoint to summarize data with LLM
    """
    try:
        data = request.json
        query_data = data.get('data', {})
        query = data.get('query', '')
        search_type = data.get('type', None)
        
        if not query_data or not query:
            return jsonify({"error": "Both data and query parameters are required"}), 400
        
        logger.info(f"Summarize request: query={query}, type={search_type}")
        
        summary = data_integrator.summarize_with_llm(query_data, query, search_type)
        
        logger.info(f"Summarization completed successfully for {query}")
        return jsonify(summary)
    
    except Exception as e:
        logger.error(f"Error in summarize endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sources', methods=['GET'])
def get_sources():
    """Return available data sources"""
    sources = {
        "fda": "FDA Drug Information",
        "clinical_trials": "Clinical Trials",
        "sec": "SEC Company Information",
        "ncbi": "NCBI Publications",
        "news": "Latest News",
        "snomed": "SNOMED-CT Medical Terminology"
    }
    return jsonify(sources)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "healthy", "version": "1.0.0"})

# Add these routes to serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('build', path)):
        return send_from_directory('build', path)
    else:
        return send_from_directory('build', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(host='0.0.0.0', port=port, debug=debug)
