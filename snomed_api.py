import requests
import pandas as pd
import os
import logging
import time
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class SnomedAPI:
    """A class for interacting with SNOMED CT terminology."""
    
    def __init__(self):
        """Initialize the SNOMED CT API client."""
        self.api_key = os.environ.get('SNOMED_API_KEY')
        # Default to the US edition
        self.edition = os.environ.get('SNOMED_EDITION', 'en-us')
        self.version = os.environ.get('SNOMED_VERSION', 'current')
        
        # SNOMED endpoint options
        # 1. SNOMED on FHIR API (preferred)
        self.fhir_url = "https://snowstorm-fhir.ontoserver.csiro.au/fhir"
        
        # 2. Snowstorm API (alternative)
        self.snowstorm_url = "https://snowstorm.ihtsdotools.org/snowstorm/snomed-ct"
        
        # 3. NIH UMLS API (fallback)
        self.umls_api_key = os.environ.get('UMLS_API_KEY')
        self.umls_url = "https://uts-ws.nlm.nih.gov/rest/search/current"
        
        # Cache to store results and reduce API calls
        self.cache = {}
        
        logger.info(f"Initialized SNOMED API client with API key: {'Present' if self.api_key else 'None'}")
    
    def search_terms(self, query, max_results=20):
        """
        Search for SNOMED CT concepts related to the query.
        
        Args:
            query (str): The search term.
            max_results (int): Maximum number of results to return.
            
        Returns:
            pd.DataFrame: DataFrame with SNOMED CT concepts.
        """
        start_time = datetime.now()
        logger.info(f"Searching SNOMED CT terms for: {query}")
        
        # Check cache first
        cache_key = f"{query}_{max_results}"
        if cache_key in self.cache:
            logger.debug(f"Returning cached SNOMED results for: {query}")
            return self.cache[cache_key]
        
        # Try different API methods in order of preference
        results = None
        
        # 1. Try FHIR API first
        if not results:
            try:
                results = self._search_fhir(query, max_results)
            except Exception as e:
                logger.warning(f"FHIR SNOMED search failed: {str(e)}")
        
        # 2. Try Snowstorm API as backup
        if not results:
            try:
                results = self._search_snowstorm(query, max_results)
            except Exception as e:
                logger.warning(f"Snowstorm SNOMED search failed: {str(e)}")
        
        # 3. Try UMLS API as last resort
        if not results and self.umls_api_key:
            try:
                results = self._search_umls(query, max_results)
            except Exception as e:
                logger.warning(f"UMLS search failed: {str(e)}")
        
        # If all searches fail, return empty DataFrame
        if not results:
            logger.warning(f"All SNOMED search methods failed for: {query}")
            return pd.DataFrame()
        
        # Cache the results
        self.cache[cache_key] = results
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Completed SNOMED search in {processing_time:.2f} seconds, found {len(results)} terms")
        
        return results
    
    def _search_fhir(self, query, max_results=20):
        """
        Search SNOMED CT using the FHIR API.
        
        Args:
            query (str): The search term.
            max_results (int): Maximum number of results to return.
            
        Returns:
            pd.DataFrame: DataFrame with SNOMED CT concepts.
        """
        logger.debug(f"Searching SNOMED via FHIR API for: {query}")
        
        # Construct the FHIR search URL
        url = f"{self.fhir_url}/ValueSet/$expand"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Construct the FHIR request body
        payload = {
            "resourceType": "Parameters",
            "parameter": [
                {
                    "name": "valueSet",
                    "resource": {
                        "resourceType": "ValueSet",
                        "compose": {
                            "include": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "filter": [
                                        {
                                            "property": "term",
                                            "op": "regex",
                                            "value": query
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                },
                {
                    "name": "count",
                    "valueInteger": max_results
                }
            ]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            expansion = data.get("expansion", {})
            contains = expansion.get("contains", [])
            
            if not contains:
                logger.warning("No SNOMED terms found via FHIR API")
                return None
            
            # Process results into a DataFrame
            results = []
            for item in contains:
                concept = {
                    "code": item.get("code", ""),
                    "display": item.get("display", ""),
                    "system": item.get("system", ""),
                    "version": item.get("version", ""),
                    "api_source": "FHIR"
                }
                results.append(concept)
            
            df = pd.DataFrame(results)
            logger.debug(f"Found {len(df)} SNOMED terms via FHIR API")
            return df
            
        except Exception as e:
            logger.error(f"FHIR SNOMED search error: {str(e)}")
            raise
    
    def _search_snowstorm(self, query, max_results=20):
        """
        Search SNOMED CT using the Snowstorm API.
        
        Args:
            query (str): The search term.
            max_results (int): Maximum number of results to return.
            
        Returns:
            pd.DataFrame: DataFrame with SNOMED CT concepts.
        """
        logger.debug(f"Searching SNOMED via Snowstorm API for: {query}")
        
        # Construct the Snowstorm search URL
        url = f"{self.snowstorm_url}/browser/{self.edition}/{self.version}/concepts"
        
        params = {
            "term": query,
            "activeFilter": "true",
            "offset": 0,
            "limit": max_results
        }
        
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            
            if not items:
                logger.warning("No SNOMED terms found via Snowstorm API")
                return None
            
            # Process results into a DataFrame
            results = []
            for item in items:
                concept = {
                    "code": item.get("conceptId", ""),
                    "display": item.get("pt", {}).get("term", ""),
                    "system": "http://snomed.info/sct",
                    "version": self.version,
                    "module": item.get("moduleId", ""),
                    "active": item.get("active", True),
                    "api_source": "Snowstorm"
                }
                
                # Add definition status if available
                definition_status = item.get("definitionStatus", {})
                if definition_status:
                    concept["definition_status"] = definition_status.get("term", "")
                
                # Add semantic tag if available
                fsn = item.get("fsn", {})
                if fsn:
                    concept["full_name"] = fsn.get("term", "")
                    
                    # Extract semantic tag from FSN (format: Term (semantic tag))
                    full_name = fsn.get("term", "")
                    if full_name and "(" in full_name and full_name.endswith(")"):
                        semantic_tag = full_name.split("(")[-1].rstrip(")")
                        concept["semantic_tag"] = semantic_tag
                
                results.append(concept)
            
            df = pd.DataFrame(results)
            logger.debug(f"Found {len(df)} SNOMED terms via Snowstorm API")
            return df
            
        except Exception as e:
            logger.error(f"Snowstorm SNOMED search error: {str(e)}")
            raise
    
    def _search_umls(self, query, max_results=20):
        """
        Search SNOMED CT using the NIH UMLS API.
        
        Args:
            query (str): The search term.
            max_results (int): Maximum number of results to return.
            
        Returns:
            pd.DataFrame: DataFrame with SNOMED CT concepts from UMLS.
        """
        if not self.umls_api_key:
            logger.warning("UMLS API key not configured")
            return None
            
        logger.debug(f"Searching SNOMED via UMLS API for: {query}")
        
        # Construct the UMLS search URL
        url = f"{self.umls_url}"
        
        params = {
            "string": query,
            "sabs": "SNOMEDCT_US",  # Only SNOMED CT US terms
            "returnIdType": "code",
            "apiKey": self.umls_api_key,
            "pageSize": max_results
        }
        
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("result", {}).get("results", [])
            
            if not results:
                logger.warning("No SNOMED terms found via UMLS API")
                return None
            
            # Process results into a DataFrame
            processed_results = []
            for item in results:
                if "SNOMEDCT_US" in item.get("rootSource", ""):
                    concept = {
                        "code": item.get("ui", ""),
                        "display": item.get("name", ""),
                        "system": "http://snomed.info/sct",
                        "semantic_type": item.get("rootSource", ""),
                        "uri": item.get("uri", ""),
                        "api_source": "UMLS"
                    }
                    processed_results.append(concept)
            
            df = pd.DataFrame(processed_results)
            logger.debug(f"Found {len(df)} SNOMED terms via UMLS API")
            return df
            
        except Exception as e:
            logger.error(f"UMLS search error: {str(e)}")
            raise
    
    def get_concept_details(self, concept_id):
        """
        Get detailed information for a SNOMED CT concept.
        
        Args:
            concept_id (str): The SNOMED CT concept ID.
            
        Returns:
            dict: Dictionary with concept details.
        """
        logger.info(f"Getting details for SNOMED concept: {concept_id}")
        
        # Check cache first
        cache_key = f"concept_{concept_id}"
        if cache_key in self.cache:
            logger.debug(f"Returning cached concept details for: {concept_id}")
            return self.cache[cache_key]
        
        # Try different API methods in order of preference
        details = None
        
        # 1. Try FHIR API first
        if not details:
            try:
                details = self._get_concept_fhir(concept_id)
            except Exception as e:
                logger.warning(f"FHIR concept details failed: {str(e)}")
        
        # 2. Try Snowstorm API as backup
        if not details:
            try:
                details = self._get_concept_snowstorm(concept_id)
            except Exception as e:
                logger.warning(f"Snowstorm concept details failed: {str(e)}")
        
        # 3. Try UMLS API as last resort
        if not details and self.umls_api_key:
            try:
                details = self._get_concept_umls(concept_id)
            except Exception as e:
                logger.warning(f"UMLS concept details failed: {str(e)}")
        
        # If all methods fail, return None
        if not details:
            logger.warning(f"All concept detail methods failed for: {concept_id}")
            return None
        
        # Cache the results
        self.cache[cache_key] = details
        
        return details
    
    def _get_concept_fhir(self, concept_id):
        """
        Get concept details using the FHIR API.
        
        Args:
            concept_id (str): The SNOMED CT concept ID.
            
        Returns:
            dict: Dictionary with concept details.
        """
        logger.debug(f"Getting concept details via FHIR API for: {concept_id}")
        
        # Construct the FHIR lookup URL
        url = f"{self.fhir_url}/CodeSystem/$lookup"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Construct the FHIR request body
        payload = {
            "resourceType": "Parameters",
            "parameter": [
                {
                    "name": "code",
                    "valueString": concept_id
                },
                {
                    "name": "system",
                    "valueString": "http://snomed.info/sct"
                },
                {
                    "name": "property",
                    "valueString": "*"
                }
            ]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            parameters = data.get("parameter", [])
            
            if not parameters:
                logger.warning(f"No concept details found via FHIR API for: {concept_id}")
                return None
            
            # Process the parameters into a structured format
            details = {
                "code": concept_id,
                "system": "http://snomed.info/sct",
                "api_source": "FHIR",
                "properties": {}
            }
            
            for param in parameters:
                name = param.get("name", "")
                
                # Handle display property
                if name == "display":
                    details["display"] = param.get("valueString", "")
                
                # Handle property parameters
                elif name == "property":
                    prop_name = param.get("part", [])[0].get("valueString", "")
                    
                    # Get the value part
                    value_part = param.get("part", [])[1]
                    
                    # Handle different value types
                    for value_type in ["valueString", "valueCode", "valueBoolean"]:
                        if value_type in value_part:
                            details["properties"][prop_name] = value_part.get(value_type)
                            break
            
            logger.debug(f"Successfully retrieved concept details via FHIR API for: {concept_id}")
            return details
            
        except Exception as e:
            logger.error(f"FHIR concept details error: {str(e)}")
            raise
    
    def _get_concept_snowstorm(self, concept_id):
        """
        Get concept details using the Snowstorm API.
        
        Args:
            concept_id (str): The SNOMED CT concept ID.
            
        Returns:
            dict: Dictionary with concept details.
        """
        logger.debug(f"Getting concept details via Snowstorm API for: {concept_id}")
        
        # Construct the Snowstorm URL
        url = f"{self.snowstorm_url}/browser/{self.edition}/{self.version}/concepts/{concept_id}"
        
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or "conceptId" not in data:
                logger.warning(f"No concept details found via Snowstorm API for: {concept_id}")
                return None
            
            # Process the response into a structured format
            details = {
                "code": data.get("conceptId", ""),
                "display": data.get("pt", {}).get("term", ""),
                "full_name": data.get("fsn", {}).get("term", ""),
                "system": "http://snomed.info/sct",
                "version": self.version,
                "active": data.get("active", True),
                "module": data.get("moduleId", ""),
                "api_source": "Snowstorm",
                "properties": {}
            }
            
            # Add definition status if available
            definition_status = data.get("definitionStatus", {})
            if definition_status:
                details["properties"]["definitionStatus"] = definition_status.get("term", "")
            
            # Extract semantic tag from FSN (format: Term (semantic tag))
            full_name = data.get("fsn", {}).get("term", "")
            if full_name and "(" in full_name and full_name.endswith(")"):
                semantic_tag = full_name.split("(")[-1].rstrip(")")
                details["properties"]["semanticTag"] = semantic_tag
            
            # Add descriptions if available
            descriptions = data.get("descriptions", [])
            if descriptions:
                details["descriptions"] = []
                for desc in descriptions:
                    description = {
                        "id": desc.get("descriptionId", ""),
                        "term": desc.get("term", ""),
                        "type": desc.get("type", {}).get("term", ""),
                        "lang": desc.get("lang", "")
                    }
                    details["descriptions"].append(description)
            
            # Add relationships if available
            relationships = data.get("relationships", [])
            if relationships:
                details["relationships"] = []
                for rel in relationships:
                    relationship = {
                        "type": rel.get("type", {}).get("term", ""),
                        "typeId": rel.get("type", {}).get("conceptId", ""),
                        "target": rel.get("target", {}).get("term", ""),
                        "targetId": rel.get("target", {}).get("conceptId", ""),
                        "active": rel.get("active", True)
                    }
                    details["relationships"].append(relationship)
            
            logger.debug(f"Successfully retrieved concept details via Snowstorm API for: {concept_id}")
            return details
            
        except Exception as e:
            logger.error(f"Snowstorm concept details error: {str(e)}")
            raise
    
    def _get_concept_umls(self, concept_id):
        """
        Get concept details using the UMLS API.
        
        Args:
            concept_id (str): The SNOMED CT concept ID.
            
        Returns:
            dict: Dictionary with concept details.
        """
        if not self.umls_api_key:
            logger.warning("UMLS API key not configured")
            return None
            
        logger.debug(f"Getting concept details via UMLS API for: {concept_id}")
        
        # Construct the UMLS URL
        url = f"https://uts-ws.nlm.nih.gov/rest/content/current/source/SNOMEDCT_US/{concept_id}"
        
        params = {
            "apiKey": self.umls_api_key
        }
        
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or "result" not in data:
                logger.warning(f"No concept details found via UMLS API for: {concept_id}")
                return None
            
            result = data.get("result", {})
            
            # Process the response into a structured format
            details = {
                "code": concept_id,
                "display": result.get("name", ""),
                "system": "http://snomed.info/sct",
                "api_source": "UMLS",
                "properties": {
                    "ui": result.get("ui", ""),
                    "rootSource": result.get("rootSource", ""),
                    "umlsReleaseVersion": result.get("umlsReleaseVersion", "")
                }
            }
            
            # Add semantic types if available
            semantic_types_url = result.get("semanticTypes", "")
            if semantic_types_url:
                try:
                    st_response = requests.get(semantic_types_url, params=params, headers=headers)
                    st_response.raise_for_status()
                    
                    st_data = st_response.json()
                    st_results = st_data.get("result", [])
                    
                    details["properties"]["semanticTypes"] = []
                    for st in st_results:
                        semantic_type = {
                            "name": st.get("name", ""),
                            "uri": st.get("uri", ""),
                            "ui": st.get("ui", "")
                        }
                        details["properties"]["semanticTypes"].append(semantic_type)
                except Exception as e:
                    logger.warning(f"Error fetching semantic types for {concept_id}: {str(e)}")
            
            # Add definitions if available
            definitions_url = result.get("definitions", "")
            if definitions_url:
                try:
                    def_response = requests.get(definitions_url, params=params, headers=headers)
                    def_response.raise_for_status()
                    
                    def_data = def_response.json()
                    def_results = def_data.get("result", [])
                    
                    details["properties"]["definitions"] = []
                    for defn in def_results:
                        definition = {
                            "value": defn.get("value", ""),
                            "source": defn.get("source", "")
                        }
                        details["properties"]["definitions"].append(definition)
                except Exception as e:
                    logger.warning(f"Error fetching definitions for {concept_id}: {str(e)}")
            
            logger.debug(f"Successfully retrieved concept details via UMLS API for: {concept_id}")
            return details
            
        except Exception as e:
            logger.error(f"UMLS concept details error: {str(e)}")
            raise
