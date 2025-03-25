import os
import requests
import time
import json
import pandas as pd
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class GroqAPI:
    """A class for interfacing with the Groq LLM API."""
    
    def __init__(self):
        """Initialize the Groq API client."""
        self.api_key = os.environ.get('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama3-70b-8192"  # Default model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info(f"Initialized Groq LLM API client with API key: {'Present' if self.api_key else 'None'}")
    
    def generate_text(self, prompt, max_tokens=1024, temperature=0.7, retry_count=2):
        """
        Generate text using the Groq API.
        
        Args:
            prompt (str): The prompt to send to the model.
            max_tokens (int): Maximum number of tokens to generate.
            temperature (float): Temperature for controlling randomness.
            retry_count (int): Number of retries if request fails.
            
        Returns:
            str: Generated text.
        """
        if not self.api_key:
            logger.error("Groq API key is not configured")
            return "Groq API key is not configured. Please set the GROQ_API_KEY environment variable."
        
        logger.debug(f"Sending request to Groq LLM API with prompt length: {len(prompt)}")
        
        for attempt in range(retry_count + 1):
            try:
                url = f"{self.base_url}/chat/completions"
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
                response = requests.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                logger.debug(f"Successfully generated text with Groq LLM API, length: {len(generated_text)}")
                return generated_text
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error generating text with Groq API (attempt {attempt+1}/{retry_count+1}): {str(e)}")
                if attempt < retry_count:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.debug(f"Retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                else:
                    return f"Error: Failed to generate text after {retry_count+1} attempts. Last error: {str(e)}"
            except Exception as e:
                logger.error(f"Unexpected error with Groq API: {str(e)}")
                return f"Error: {str(e)}"
    
    def analyze_drug_information(self, drug_name, drug_data):
        """
        Analyze drug information using the Groq API.
        
        Args:
            drug_name (str): Name of the drug.
            drug_data (dict): Data about the drug from various sources.
            
        Returns:
            dict: Analysis results.
        """
        start_time = datetime.now()
        logger.info(f"Analyzing drug information for: {drug_name}")
        
        # Prepare prompt with drug information
        prompt = f"""
        Please analyze the following information about the drug {drug_name} and provide:
        1. A concise summary of the drug's indications and mechanism of action (2-3 sentences)
        2. Key clinical information including common dosage forms and administration routes
        3. Notable regulatory information (approval status, recent regulatory changes)
        4. Important safety considerations including major adverse effects and contraindications
        5. A brief overview of recent research or clinical trials

        Here's the information I have about {drug_name}:
        """
        
        # Add FDA data if available
        if 'fda' in drug_data and not isinstance(drug_data['fda'], dict):
            try:
                fda_df = drug_data['fda']
                if not fda_df.empty:
                    prompt += "\n\nFDA Information:\n"
                    for col in ['indications_and_usage', 'description', 'clinical_pharmacology', 'mechanism_of_action']:
                        if col in fda_df.columns and not pd.isna(fda_df.iloc[0].get(col)):
                            content = str(fda_df.iloc[0].get(col))
                            if len(content) > 500:  # Limit very long content
                                content = content[:500] + "..."
                            prompt += f"- {col.replace('_', ' ').title()}: {content}\n"
            except Exception as e:
                logger.error(f"Error processing FDA data: {str(e)}")
        
        # Add clinical trials data if available
        if 'clinical_trials' in drug_data and not isinstance(drug_data['clinical_trials'], dict):
            try:
                ct_df = drug_data['clinical_trials']
                if not ct_df.empty:
                    prompt += "\n\nRecent Clinical Trials:\n"
                    trial_count = min(3, len(ct_df))  # Limit to 3 trials
                    for i in range(trial_count):
                        trial = ct_df.iloc[i]
                        prompt += f"- Trial {i+1}: {trial.get('briefTitle', 'Untitled')}\n"
                        prompt += f"  Status: {trial.get('overallStatus', 'Unknown')}\n"
                        if 'phases' in trial and trial['phases']:
                            prompt += f"  Phase: {trial.get('phases', 'Unknown')}\n"
            except Exception as e:
                logger.error(f"Error processing clinical trials data: {str(e)}")
        
        # Add news mentions if available
        if 'news' in drug_data and isinstance(drug_data['news'], dict):
            if 'summaries' in drug_data['news']:
                prompt += "\n\nRecent News:\n"
                for category, summary in drug_data['news']['summaries'].items():
                    if summary and not summary.startswith("No"):
                        prompt += f"- {category.capitalize()}: {summary}\n"
            elif isinstance(drug_data['news'], pd.DataFrame) or (isinstance(drug_data['news'], dict) and 'regulatory' in drug_data['news']):
                prompt += "\n\nRecent News:\n"
                # If it's coming from the SerperAPI directly
                news_categories = ['regulatory', 'commercial', 'clinical', 'other']
                for category in news_categories:
                    if category in drug_data['news'] and drug_data['news'][category]:
                        articles = drug_data['news'][category][:3]  # Get the first 3 articles
                        if articles:
                            prompt += f"- {category.capitalize()} news:\n"
                            for article in articles:
                                title = article.get('title', 'Untitled')
                                prompt += f"  • {title}\n"
        
        # Generate analysis
        analysis_text = self.generate_text(prompt)
        
        # Structure the response
        sections = analysis_text.split("\n\n")
        analysis = {}
        
        current_section = "overview"
        for section in sections:
            if section.lower().startswith("summary") or section.lower().startswith("1."):
                current_section = "summary"
                analysis[current_section] = section
            elif section.lower().startswith("clinical") or section.lower().startswith("2."):
                current_section = "clinical"
                analysis[current_section] = section
            elif section.lower().startswith("regulatory") or section.lower().startswith("3."):
                current_section = "regulatory"
                analysis[current_section] = section
            elif section.lower().startswith("safety") or section.lower().startswith("4."):
                current_section = "safety"
                analysis[current_section] = section
            elif section.lower().startswith("research") or section.lower().startswith("5."):
                current_section = "research"
                analysis[current_section] = section
            elif section.strip() and current_section in analysis:
                analysis[current_section] += "\n\n" + section
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Completed drug analysis in {processing_time:.2f} seconds")
        
        return analysis
    
    def analyze_disease_information(self, disease_name, disease_data):
        """
        Analyze disease information using the Groq API.
        
        Args:
            disease_name (str): Name of the disease.
            disease_data (dict): Data about the disease from various sources.
            
        Returns:
            dict: Analysis results.
        """
        start_time = datetime.now()
        logger.info(f"Analyzing disease information for: {disease_name}")
        
        # Prepare prompt with disease information
        prompt = f"""
        Please analyze the following information about {disease_name} and provide:
        1. A concise overview of the disease including definition, prevalence, and key characteristics (2-3 sentences)
        2. Main symptoms and clinical presentation
        3. Current treatment approaches and standard of care
        4. Recent research developments or clinical trials
        5. Major unmet needs and future directions for treatment

        Here's the information I have about {disease_name}:
        """
        
        # Add FDA data if available
        if 'fda' in disease_data and not isinstance(disease_data['fda'], dict):
            try:
                fda_df = disease_data['fda']
                if not fda_df.empty:
                    prompt += "\n\nFDA Approved Treatments:\n"
                    for i in range(min(5, len(fda_df))):
                        row = fda_df.iloc[i]
                        drug_name = row.get('brand_name') or row.get('generic_name') or 'Unknown'
                        prompt += f"- {drug_name}\n"
                        if 'indications_and_usage' in row and not pd.isna(row['indications_and_usage']):
                            indications = str(row['indications_and_usage'])
                            if len(indications) > 300:  # Limit very long content
                                indications = indications[:300] + "..."
                            prompt += f"  Indications: {indications}\n"
            except Exception as e:
                logger.error(f"Error processing FDA data: {str(e)}")
        
        # Add clinical trials data if available
        if 'clinical_trials' in disease_data and not isinstance(disease_data['clinical_trials'], dict):
            try:
                ct_df = disease_data['clinical_trials']
                if not ct_df.empty:
                    prompt += "\n\nOngoing Clinical Trials:\n"
                    trial_count = min(3, len(ct_df))  # Limit to 3 trials
                    for i in range(trial_count):
                        trial = ct_df.iloc[i]
                        prompt += f"- Trial {i+1}: {trial.get('briefTitle', 'Untitled')}\n"
                        prompt += f"  Status: {trial.get('overallStatus', 'Unknown')}\n"
                        if 'phases' in trial and trial['phases']:
                            prompt += f"  Phase: {trial.get('phases', 'Unknown')}\n"
            except Exception as e:
                logger.error(f"Error processing clinical trials data: {str(e)}")
        
        # Add NCBI publications if available
        if 'ncbi' in disease_data and not isinstance(disease_data['ncbi'], dict):
            try:
                ncbi_df = disease_data['ncbi']
                if not ncbi_df.empty:
                    prompt += "\n\nRecent Research Publications:\n"
                    pub_count = min(3, len(ncbi_df))  # Limit to 3 publications
                    for i in range(pub_count):
                        pub = ncbi_df.iloc[i]
                        prompt += f"- Publication {i+1}: {pub.get('title', 'Untitled')}\n"
                        if 'abstract' in pub and pub['abstract']:
                            abstract = pub['abstract']
                            if len(abstract) > 300:  # Limit very long content
                                abstract = abstract[:300] + "..."
                            prompt += f"  Abstract: {abstract}\n"
            except Exception as e:
                logger.error(f"Error processing NCBI data: {str(e)}")
        
        # Add news mentions if available
        if 'news' in disease_data and isinstance(disease_data['news'], dict):
            if 'summaries' in disease_data['news']:
                prompt += "\n\nRecent News:\n"
                for category, summary in disease_data['news']['summaries'].items():
                    if summary and not summary.startswith("No"):
                        prompt += f"- {category.capitalize()}: {summary}\n"
            elif isinstance(disease_data['news'], pd.DataFrame) or (isinstance(disease_data['news'], dict) and 'regulatory' in disease_data['news']):
                prompt += "\n\nRecent News:\n"
                # If it's coming from the SerperAPI directly
                news_categories = ['regulatory', 'commercial', 'clinical', 'other']
                for category in news_categories:
                    if category in disease_data['news'] and disease_data['news'][category]:
                        articles = disease_data['news'][category][:3]  # Get the first 3 articles
                        if articles:
                            prompt += f"- {category.capitalize()} news:\n"
                            for article in articles:
                                title = article.get('title', 'Untitled')
                                prompt += f"  • {title}\n"
        
        # Add Serper data if available
        if 'serper' in disease_data and isinstance(disease_data['serper'], dict) and 'results' in disease_data['serper']:
            try:
                serper_results = disease_data['serper']['results']
                if serper_results:
                    prompt += "\n\nAdditional Medical Information:\n"
                    result_count = min(3, len(serper_results))
                    for i in range(result_count):
                        result = serper_results[i]
                        prompt += f"- Source {i+1}: {result.get('title', 'Untitled')}\n"
                        if 'content' in result and result['content']:
                            content = result['content']
                            if len(content) > 300:
                                content = content[:300] + "..."
                            prompt += f"  Content: {content}\n"
            except Exception as e:
                logger.error(f"Error processing Serper data: {str(e)}")
        
        # Generate analysis
        analysis_text = self.generate_text(prompt)
        
        # Structure the response
        sections = analysis_text.split("\n\n")
        analysis = {}
        
        current_section = "overview"
        for section in sections:
            if section.lower().startswith("overview") or section.lower().startswith("1."):
                current_section = "overview"
                analysis[current_section] = section
            elif section.lower().startswith("symptoms") or section.lower().startswith("2."):
                current_section = "symptoms"
                analysis[current_section] = section
            elif section.lower().startswith("treatment") or section.lower().startswith("3."):
                current_section = "treatment"
                analysis[current_section] = section
            elif section.lower().startswith("research") or section.lower().startswith("4."):
                current_section = "research"
                analysis[current_section] = section
            elif section.lower().startswith("unmet") or section.lower().startswith("5."):
                current_section = "unmet_needs"
                analysis[current_section] = section
            elif section.strip() and current_section in analysis:
                analysis[current_section] += "\n\n" + section
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"Completed disease analysis in {processing_time:.2f} seconds")
        
        return analysis
    
    def summarize_data(self, data, query):
        """
        Generate a comprehensive summary of all collected data.
        
        Args:
            data (dict): All collected data from various sources.
            query (str): The original search query.
            
        Returns:
            dict: Summary sections.
        """
        try:
            # Determine if query is a drug or disease
            query_type = 'drug'
            if 'type' in data:
                query_type = data['type']
            elif 'fda' in data:
                try:
                    fda_df = data['fda']
                    if isinstance(fda_df, pd.DataFrame) and not fda_df.empty:
                        if 'brand_name' in fda_df.columns or 'generic_name' in fda_df.columns:
                            query_type = 'drug'
                        else:
                            query_type = 'disease'
                except:
                    pass
            
            logger.info(f"Summarizing data for {query} as {query_type}")
            
            # Call appropriate analysis function
            if query_type == 'drug':
                return self.analyze_drug_information(query, data)
            else:
                return self.analyze_disease_information(query, data)
        except Exception as e:
            error_msg = f"Error summarizing data: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "overview": "Unable to generate summary due to an error."
            }
