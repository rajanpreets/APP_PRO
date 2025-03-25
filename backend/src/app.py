from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from langgraph.graph import Graph
from groq import Groq
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Literal
from datetime import datetime

from src.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    ALLOWED_ORIGINS,
    LOG_LEVEL,
    LOG_FORMAT
)
from src.utils.graph_nodes import (
    create_fda_node,
    create_clinical_trials_node,
    create_ncbi_node,
    create_serper_node,
    create_summary_node
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=ALLOWED_ORIGINS)

# Initialize Groq client
client = Groq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS
)

# Define request model
class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, description="The search query")
    search_type: Literal["drug", "disease"] = Field(
        default="drug",
        description="The type of search to perform"
    )

def create_search_graph() -> Graph:
    """Create the LangGraph for search operations"""
    # Create nodes
    fda_node = create_fda_node()
    clinical_trials_node = create_clinical_trials_node()
    ncbi_node = create_ncbi_node()
    serper_node = create_serper_node()
    summary_node = create_summary_node(client)
    
    # Create graph
    graph = Graph()
    
    # Add nodes
    graph.add_node("fda", fda_node)
    graph.add_node("clinical_trials", clinical_trials_node)
    graph.add_node("ncbi", ncbi_node)
    graph.add_node("serper", serper_node)
    graph.add_node("summary", summary_node)
    
    # Add edges (parallel execution)
    graph.add_edge("fda", "summary")
    graph.add_edge("clinical_trials", "summary")
    graph.add_edge("ncbi", "summary")
    graph.add_edge("serper", "summary")
    
    # Set entry points
    graph.set_entry_points(["fda", "clinical_trials", "ncbi", "serper"])
    
    return graph

# Create search graph
search_graph = create_search_graph()

@app.route("/api/search", methods=["POST"])
def search():
    """Handle search requests"""
    try:
        # Validate request
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing query parameter"}), 400
            
        search_query = SearchQuery(**data)
        
        # Initialize state
        state = {
            "query": search_query.query,
            "search_type": search_query.search_type
        }
        
        # Execute graph
        result = search_graph.invoke(state)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 