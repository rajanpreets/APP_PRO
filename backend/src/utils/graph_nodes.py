from typing import Dict, Any, List
import logging
from ..api.fda_api import OpenFDA
from ..api.clinical_trials_api import ClinicalTrialsAPI
from ..api.ncbi_api import NCBIApi
from ..api.serper_api import SerperAPI

logger = logging.getLogger(__name__)

def create_fda_node():
    """Create a node for FDA data fetching"""
    fda_client = OpenFDA()
    
    def fda_node(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            query = state.get("query", "")
            search_type = state.get("search_type", "drug")
            
            fda_data = fda_client.open_fda_main(query, search_type)
            
            return {
                **state,
                "fda_data": fda_data
            }
        except Exception as e:
            logger.error(f"FDA node error: {str(e)}")
            return {
                **state,
                "fda_data": {"error": str(e)}
            }
    
    return fda_node

def create_clinical_trials_node():
    """Create a node for Clinical Trials data fetching"""
    clinical_trials_client = ClinicalTrialsAPI()
    
    def clinical_trials_node(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            query = state.get("query", "")
            
            clinical_trials_data = clinical_trials_client.get_clinical_trials_data(query)
            
            return {
                **state,
                "clinical_trials_data": clinical_trials_data
            }
        except Exception as e:
            logger.error(f"Clinical Trials node error: {str(e)}")
            return {
                **state,
                "clinical_trials_data": {"error": str(e)}
            }
    
    return clinical_trials_node

def create_ncbi_node():
    """Create a node for NCBI data fetching"""
    ncbi_client = NCBIApi()
    
    def ncbi_node(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            query = state.get("query", "")
            
            ncbi_data = ncbi_client.get_pubmed_data(query)
            
            return {
                **state,
                "ncbi_data": ncbi_data
            }
        except Exception as e:
            logger.error(f"NCBI node error: {str(e)}")
            return {
                **state,
                "ncbi_data": {"error": str(e)}
            }
    
    return ncbi_node

def create_serper_node():
    """Create a node for Serper news data fetching"""
    serper_client = SerperAPI()
    
    def serper_node(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            query = state.get("query", "")
            
            news_data = serper_client.get_news_data(query)
            
            return {
                **state,
                "news_data": news_data
            }
        except Exception as e:
            logger.error(f"Serper node error: {str(e)}")
            return {
                **state,
                "news_data": {"error": str(e)}
            }
    
    return serper_node

def create_summary_node(llm):
    """Create a node for generating summaries using the language model"""
    
    def summary_node(state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Extract data from state
            fda_data = state.get("fda_data", {})
            clinical_trials_data = state.get("clinical_trials_data", {})
            ncbi_data = state.get("ncbi_data", {})
            news_data = state.get("news_data", {})
            
            # Prepare context for the LLM
            context = {
                "fda": fda_data.get("data", []),
                "clinical_trials": clinical_trials_data.get("data", []),
                "pubmed": ncbi_data.get("data", []),
                "news": {
                    "regulatory": news_data.get("regulatory", {}).get("data", []),
                    "clinical": news_data.get("clinical", {}).get("data", []),
                    "commercial": news_data.get("commercial", {}).get("data", [])
                }
            }
            
            # Generate summary using the LLM
            prompt = f"""Based on the following medical research data, provide a comprehensive summary:

FDA Data:
{context['fda']}

Clinical Trials Data:
{context['clinical_trials']}

PubMed Articles:
{context['pubmed']}

Recent News:
Regulatory Updates:
{context['news']['regulatory']}

Clinical Developments:
{context['news']['clinical']}

Commercial Updates:
{context['news']['commercial']}

Please provide:
1. Key findings and conclusions
2. Treatment options and their effectiveness
3. Safety considerations and side effects
4. Recent developments and future directions
5. Market and commercial implications
6. Recommendations for healthcare providers

Format the response in a clear, structured manner."""

            response = llm.invoke(prompt)
            
            return {
                **state,
                "summary": response
            }
        except Exception as e:
            logger.error(f"Summary node error: {str(e)}")
            return {
                **state,
                "summary": {"error": str(e)}
            }
    
    return summary_node 