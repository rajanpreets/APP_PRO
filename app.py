from flask import Flask, request, jsonify
from flask_cors import CORS
import main
import json
import pandas as pd
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get the data integrator instance
data_integrator = main.data_integrator

@app.route('/api/search', methods=['POST'])
def search():
    """
    Endpoint to search for drug or disease information
    
    Request JSON:
    {
        "query": "query string",
        "type": "drug" or "disease",
        "sources": ["fda", "clinical_trials", etc.] (optional)
    }
    """
    try:
        data = request.json
        query = data.get('query', '')
        search_type = data.get('type', 'drug')
        sources = data.get('sources', None)
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        logger.info(f"Search request: query={query}, type={search_type}, sources={sources}")
        
        if search_type == 'drug':
            results = data_integrator.search_drug(query, sources)
        elif search_type == 'disease':
            results = data_integrator.search_disease(query, sources)
        else:
            return jsonify({"error": "Invalid search type"}), 400
        
        # Convert pandas DataFrames to JSON
        processed_results = {}
        for key, value in results.items():
            if isinstance(value, pd.DataFrame):
                processed_results[key] = value.to_dict(orient='records')
            else:
                processed_results[key] = value
        
        logger.info(f"Search completed successfully for {query}")
        return jsonify(processed_results)
    
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    """
    Endpoint to summarize data with LLM
    
    Request JSON:
    {
        "data": {data object},
        "query": "original query string",
        "type": "drug" or "disease" (optional)
    }
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
        logger.error(f"Error in summarize endpoint: {str(e)}", exc_info=True)
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
        "serper": "Google Search Results",
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
        "endpoints": {
            "/api/search": "POST - Search for drug or disease information",
            "/api/summarize": "POST - Generate summaries using LLM",
            "/api/sources": "GET - List available data sources",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Log startup information
    logger.info(f"Starting Healthcare Data Integration Platform API on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
