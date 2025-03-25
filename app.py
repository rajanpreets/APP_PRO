from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import pandas as pd
import logging
from datetime import datetime

# Import API modules
import fda_api
import ct_api
import sec_api
import ncbi_api
import serper_api
import llm_api
import snomed_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes and origins

# Create API clients
try:
    fda_client = fda_api.OpenFDA()
    ct_client = ct_api.ClinicalTrialsAPI()
    sec_client = sec_api.SECAPI()
    ncbi_client = ncbi_api.NCBIAPI()
    serper_client = serper_api.SerperAPI()
    llm_client = llm_api.GroqAPI()
    snomed_client = snomed_api.SnomedAPI()
    logger.info("API clients initialized successfully")
except Exception as e:
    logger.error(f"Error initializing API clients: {str(e)}")

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
        
        results = {}
        
        # Process each source based on selection
        if not sources or 'fda' in sources:
            try:
                results['fda'] = fda_client.open_fda_main(query, search_type)
                if isinstance(results['fda'], pd.DataFrame):
                    results['fda'] = results['fda'].to_dict(orient='records')
            except Exception as e:
                results['fda'] = {"error": str(e)}
                
        if not sources or 'clinical_trials' in sources:
            try:
                results['clinical_trials'] = ct_client.get_clinical_trials_data(query)
                if isinstance(results['clinical_trials'], pd.DataFrame):
                    results['clinical_trials'] = results['clinical_trials'].to_dict(orient='records')
            except Exception as e:
                results['clinical_trials'] = {"error": str(e)}
                
        if not sources or 'sec' in sources:
            try:
                results['sec'] = sec_client.get_company_details(query)
                if isinstance(results['sec'], pd.DataFrame):
                    results['sec'] = results['sec'].to_dict(orient='records')
            except Exception as e:
                results['sec'] = {"error": str(e)}
                
        if not sources or 'ncbi' in sources:
            try:
                results['ncbi'] = ncbi_client.search_publications(query)
                if isinstance(results['ncbi'], pd.DataFrame):
                    results['ncbi'] = results['ncbi'].to_dict(orient='records')
            except Exception as e:
                results['ncbi'] = {"error": str(e)}
                
        if not sources or 'news' in sources:
            try:
                results['news'] = serper_client.search_news(query)
            except Exception as e:
                results['news'] = {"error": str(e)}
                
        if not sources or 'snomed' in sources:
            try:
                results['snomed'] = snomed_client.search_terms(query)
                if isinstance(results['snomed'], pd.DataFrame):
                    results['snomed'] = results['snomed'].to_dict(orient='records')
            except Exception as e:
                results['snomed'] = {"error": str(e)}
        
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
        
        summary = llm_client.summarize_data(query_data, query)
        
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

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        "name": "Healthcare Data Integration Platform API",
        "version": "1.0.0",
        "status": "operational"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(host='0.0.0.0', port=port, debug=debug)
