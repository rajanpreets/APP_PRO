from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
import pandas as pd
from datetime import datetime

# Import your data integrator
from integrator import data_integrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
