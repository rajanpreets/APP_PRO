import requests
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class OpenFDA:
    def __init__(self):
        self.base_url = "https://api.fda.gov"
        self.api_key = "YOUR_FDA_API_KEY"  # Replace with actual API key

    def open_fda_main(self, query: str, search_type: str = 'drug') -> Dict[str, Any]:
        """
        Main function to fetch data from OpenFDA API
        
        Args:
            query (str): Search query
            search_type (str): Type of search ('drug' or 'disease')
            
        Returns:
            Dict[str, Any]: Processed FDA data
        """
        try:
            if search_type == 'drug':
                return self._search_drug(query)
            else:
                return self._search_disease(query)
        except Exception as e:
            logger.error(f"OpenFDA API error: {str(e)}")
            return {"error": str(e)}

    def _search_drug(self, query: str) -> Dict[str, Any]:
        """Search for drug information"""
        endpoint = f"{self.base_url}/drug/label.json"
        params = {
            "api_key": self.api_key,
            "search": f"openfda.brand_name:{query}",
            "limit": 10
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        data = response.json()
        return self._process_drug_data(data)

    def _search_disease(self, query: str) -> Dict[str, Any]:
        """Search for disease information"""
        endpoint = f"{self.base_url}/drug/label.json"
        params = {
            "api_key": self.api_key,
            "search": f"openfda.indications_and_usage:{query}",
            "limit": 10
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        data = response.json()
        return self._process_disease_data(data)

    def _process_drug_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process drug data into a structured format"""
        results = []
        
        for result in data.get("results", []):
            processed = {
                "brand_name": result.get("openfda", {}).get("brand_name", [""])[0],
                "generic_name": result.get("openfda", {}).get("generic_name", [""])[0],
                "manufacturer": result.get("openfda", {}).get("manufacturer_name", [""])[0],
                "substance_name": result.get("openfda", {}).get("substance_name", [""])[0],
                "route": result.get("openfda", {}).get("route", [""])[0],
                "indications": result.get("indications_and_usage", [""])[0],
                "warnings": result.get("warnings", [""])[0],
                "adverse_reactions": result.get("adverse_reactions", [""])[0]
            }
            results.append(processed)
        
        return {"data": results}

    def _process_disease_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process disease data into a structured format"""
        results = []
        
        for result in data.get("results", []):
            processed = {
                "brand_name": result.get("openfda", {}).get("brand_name", [""])[0],
                "indications": result.get("indications_and_usage", [""])[0],
                "contraindications": result.get("contraindications", [""])[0],
                "warnings": result.get("warnings", [""])[0],
                "adverse_reactions": result.get("adverse_reactions", [""])[0]
            }
            results.append(processed)
        
        return {"data": results} 