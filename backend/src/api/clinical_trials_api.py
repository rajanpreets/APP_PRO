import requests
import pandas as pd
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ClinicalTrialsAPI:
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api/query/study_fields"
        self.fields = [
            "NCTId",
            "BriefTitle",
            "OfficialTitle",
            "Condition",
            "Phase",
            "OverallStatus",
            "StartDate",
            "CompletionDate",
            "EnrollmentCount",
            "InterventionName",
            "InterventionType",
            "LeadSponsorName",
            "LocationFacility",
            "LocationCountry",
            "ResultsFirstPostDate",
            "ResultsFirstSubmitDate",
            "StudyType",
            "WhyStopped",
            "HasResults"
        ]

    def get_clinical_trials_data(self, query: str) -> Dict[str, Any]:
        """
        Fetch clinical trials data for a given query
        
        Args:
            query (str): Search query
            
        Returns:
            Dict[str, Any]: Processed clinical trials data
        """
        try:
            # Get trials from the last 5 years
            five_years_ago = (datetime.now() - timedelta(days=5*365)).strftime("%Y-%m-%d")
            
            params = {
                "expr": query,
                "fields": ",".join(self.fields),
                "min_rnk": 1,
                "max_rnk": 10,
                "fmt": "json",
                "study_fields": "HasResults",
                "study_fields_value": "true",
                "date_from": five_years_ago
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._process_data(data)
            
        except Exception as e:
            logger.error(f"Clinical Trials API error: {str(e)}")
            return {"error": str(e)}

    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process clinical trials data into a structured format"""
        results = []
        
        for study in data.get("StudyFieldsResponse", {}).get("StudyFields", []):
            processed = {
                "nct_id": study.get("NCTId", [""])[0],
                "brief_title": study.get("BriefTitle", [""])[0],
                "official_title": study.get("OfficialTitle", [""])[0],
                "condition": study.get("Condition", [""])[0],
                "phase": study.get("Phase", [""])[0],
                "status": study.get("OverallStatus", [""])[0],
                "start_date": study.get("StartDate", [""])[0],
                "completion_date": study.get("CompletionDate", [""])[0],
                "enrollment": study.get("EnrollmentCount", [""])[0],
                "intervention": study.get("InterventionName", [""])[0],
                "intervention_type": study.get("InterventionType", [""])[0],
                "sponsor": study.get("LeadSponsorName", [""])[0],
                "location": study.get("LocationFacility", [""])[0],
                "country": study.get("LocationCountry", [""])[0],
                "has_results": study.get("HasResults", [""])[0]
            }
            results.append(processed)
        
        return {"data": results} 