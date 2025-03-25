import requests
import pandas as pd
from dateutil.parser import parse
from dateutil.parser import ParserError
import os
import logging
import time
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class ClinicalTrialsAPI:
    """A class for fetching and processing data from the ClinicalTrials.gov API."""
    
    def __init__(self):
        """Initialize the ClinicalTrials.gov API client."""
        logger.info("Initialized ClinicalTrials.gov API client")
    
    def get_clinical_trials_data(self, search_term, max_pages=5):
        """
        Fetch clinical trials data for the given search term.
        
        Args:
            search_term (str): The term to search for in the Clinical Trials API.
            max_pages (int, optional): Maximum number of pages to fetch. Defaults to 5.
            
        Returns:
            pd.DataFrame: A pandas DataFrame containing the fetched and processed data.
        """
        start_time = datetime.now()
        logger.info(f"Starting clinical trials search for: {search_term}")
        
        base_url = "https://clinicaltrials.gov/api/v2/studies"
        params = {
            "query.term": str(search_term),
            "pageSize": 100,  # Maximum page size allowed
            "pageToken": None  # Set initial page token to None
        }

        all_studies = {}
        i = 0
        
        while i < max_pages:
            try:
                logger.debug(f"Fetching clinical trials page {i+1}")
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                
                if response.status_code == 200:
                    data = response.json()
                    studies = data.get("studies", [])
                    
                    if not studies:
                        logger.debug("No more studies found")
                        break  # No more studies found
                    
                    if i == 0:
                        all_studies.update(data)  # Add the studies from this page to the dictionary
                        page_token = data.get("nextPageToken")
                    elif i > 0:
                        # Extend the studies list with new studies
                        all_studies["studies"].extend(data.get("studies", []))
                        page_token = data.get("nextPageToken")
                        
                    if not page_token:
                        logger.debug("No next page token")
                        break  # Exit the loop when there are no more pages
                        
                    params['pageToken'] = page_token  # Set the page token for the next request
                    i += 1
                    logger.debug(f"Clinical Trials API: Page {i} processed")
                else:
                    logger.warning(f"Error fetching data: {response.status_code}")
                    break  # Exit on error
            except Exception as e:
                logger.error(f"Error in clinical trials API: {str(e)}")
                break
                
            # Add a small delay to respect API rate limits
            time.sleep(0.5)
                
        # Process studies and convert to DataFrame
        processed_studies = []
        
        if "studies" in all_studies:
            study_count = len(all_studies["studies"])
            logger.debug(f"Processing {study_count} clinical trials")
            
            for study in all_studies["studies"]:
                processed_study = self._normalize_study(study)
                processed_studies.append(processed_study)
        
        if processed_studies:
            result_df = pd.DataFrame(processed_studies)
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            logger.info(f"Completed clinical trials search in {processing_time:.2f} seconds, found {len(result_df)} trials")
            return result_df
        else:
            logger.warning(f"No clinical trials found for: {search_term}")
            return pd.DataFrame()

    def _normalize_study(self, study):
        """
        Extract and normalize data from a clinical trial study object.
        
        Args:
            study (dict): The study object returned by the ClinicalTrials.gov API.
            
        Returns:
            dict: A dictionary containing the normalized study data.
        """
        flat_data = {}
        
        try:
            # Extract identification module
            identification = study.get('protocolSection', {}).get('identificationModule', {})
            flat_data['nctId'] = identification.get('nctId')
            flat_data['organization'] = identification.get('organization', {}).get('fullName')
            flat_data['organizationType'] = identification.get('organization', {}).get('class')
            flat_data['briefTitle'] = identification.get('briefTitle')
            flat_data['officialTitle'] = identification.get('officialTitle')
            
            # Extract status module
            status = study.get('protocolSection', {}).get('statusModule', {})
            flat_data['statusVerifiedDate'] = status.get('statusVerifiedDate')
            flat_data['overallStatus'] = status.get('overallStatus')
            flat_data['hasExpandedAccess'] = status.get('expandedAccessInfo', {}).get('hasExpandedAccess')
            flat_data['startDate'] = status.get('startDateStruct', {}).get('date')
            flat_data['completionDate'] = status.get('completionDateStruct', {}).get('date')
            flat_data['completionDateType'] = status.get('completionDateStruct', {}).get('type')
            flat_data['studyFirstSubmitDate'] = status.get('studyFirstSubmitDate')
            flat_data['studyFirstPostDate'] = status.get('studyFirstPostDateStruct', {}).get('date')
            flat_data['lastUpdatePostDate'] = status.get('lastUpdatePostDateStruct', {}).get('date')
            flat_data['lastUpdatePostDateType'] = status.get('lastUpdatePostDateStruct', {}).get('type')

            # Results status
            flat_data['HasResults'] = study.get('hasResults')
            
            # Extract sponsor collaborators module
            sponsor = study.get('protocolSection', {}).get('sponsorCollaboratorsModule', {})
            flat_data['responsibleParty'] = sponsor.get('responsibleParty', {}).get('oldNameTitle')
            flat_data['leadSponsor'] = sponsor.get('leadSponsor', {}).get('name')
            flat_data['leadSponsorType'] = sponsor.get('leadSponsor', {}).get('class')
            
            collaborators = sponsor.get('collaborators', [])
            if collaborators:
                flat_data['collaborators'] = ', '.join([collab.get('name', '') for collab in collaborators if collab.get('name')])
                flat_data['collaboratorsType'] = ', '.join([collab.get('class', '') for collab in collaborators if collab.get('class')])
            else:
                flat_data['collaborators'] = ''
                flat_data['collaboratorsType'] = ''
            
            # Extract description module
            description = study.get('protocolSection', {}).get('descriptionModule', {})
            flat_data['briefSummary'] = description.get('briefSummary')
            flat_data['detailedDescription'] = description.get('detailedDescription')
            
            # Extract conditions module
            conditions = study.get('protocolSection', {}).get('conditionsModule', {})
            flat_data['conditions'] = ', '.join(conditions.get('conditions', []))
            
            # Extract design module
            design = study.get('protocolSection', {}).get('designModule', {})
            flat_data['studyType'] = design.get('studyType')
            flat_data['phases'] = ', '.join(design.get('phases', []))
            flat_data['allocation'] = design.get('designInfo', {}).get('allocation')
            flat_data['interventionModel'] = design.get('designInfo', {}).get('interventionModel')
            flat_data['primaryPurpose'] = design.get('designInfo', {}).get('primaryPurpose')
            
            # Handle masking information
            masking_info = design.get('designInfo', {}).get('maskingInfo', {})
            flat_data['masking'] = masking_info.get('masking')
            who_masked = masking_info.get('whoMasked', [])
            if who_masked:
                flat_data['whoMasked'] = ', '.join(who_masked)
            else:
                flat_data['whoMasked'] = ''
                
            # Handle enrollment information
            enrollment_info = design.get('enrollmentInfo', {})
            flat_data['enrollmentCount'] = enrollment_info.get('count')
            flat_data['enrollmentType'] = enrollment_info.get('type')
            
            # Extract arms interventions module
            arms = study.get('protocolSection', {}).get('armsInterventionsModule', {}).get('armGroups', [])
            if arms:
                flat_data['arms'] = ', '.join([arm.get('label', '') for arm in arms if arm.get('label')])
                
                # Collect all intervention names across arm groups
                intervention_names = set()
                for arm in arms:
                    for intervention in arm.get('interventionNames', []):
                        intervention_names.add(intervention)
                
                flat_data['interventions'] = ', '.join(intervention_names)
            else:
                flat_data['arms'] = ''
                flat_data['interventions'] = ''

            # Process interventions
            interventions = study.get('protocolSection', {}).get('armsInterventionsModule', {}).get('interventions', [])
            
            drug_interventions = [intervention.get('name', '') for intervention in interventions 
                                if intervention.get('type', '').lower() == 'drug' and intervention.get('name')]
            
            biological_interventions = [intervention.get('name', '') for intervention in interventions 
                                        if intervention.get('type', '').lower() == 'biological' and intervention.get('name')]
            
            other_interventions = [intervention.get('name', '') for intervention in interventions 
                                if intervention.get('type', '').lower() not in ['drug', 'biological'] and intervention.get('name')]
            
            flat_data['interventionDrug'] = ', '.join(drug_interventions)
            flat_data['interventionBiological'] = ', '.join(biological_interventions)
            flat_data['interventionOthers'] = ', '.join(other_interventions)
            
            # Collect intervention descriptions
            intervention_descriptions = []
            for intervention in interventions:
                name = intervention.get('name', '')
                description = intervention.get('description', '')
                if name and description:
                    intervention_descriptions.append(f"{name}: {description}")
                    
            flat_data['interventionDescription'] = '\n'.join(intervention_descriptions)

            # Extract the outcome module
            outcome = study.get('protocolSection', {}).get('outcomesModule', {})
            
            # Primary outcomes
            primary_outcomes = []
            for i, primary_outcome in enumerate(outcome.get('primaryOutcomes', [])):
                measure = primary_outcome.get('measure', 'None')
                primary_outcomes.append(f"Primary Outcome {i + 1}: {measure}")
            
            flat_data['primaryOutcomes'] = '\n'.join(primary_outcomes)
            
            # Secondary outcomes
            secondary_outcomes = []
            for i, secondary_outcome in enumerate(outcome.get('secondaryOutcomes', [])):
                measure = secondary_outcome.get('measure', 'None')
                secondary_outcomes.append(f"Secondary Outcome {i + 1}: {measure}")
                
            flat_data['secondaryOutcomes'] = '\n'.join(secondary_outcomes)
            
            # Extract Eligibility
            eligibility = study.get('protocolSection', {}).get('eligibilityModule', {})
            flat_data['eligibilityCriteria'] = eligibility.get('eligibilityCriteria')
            flat_data['healthyVolunteers'] = eligibility.get('healthyVolunteers')
            flat_data['eligibilityGender'] = eligibility.get('sex')
            flat_data['eligibilityMinimumAge'] = eligibility.get('minimumAge')
            flat_data['eligibilityMaximumAge'] = eligibility.get('maximumAge')
            
            # Handle standard ages as a list
            std_ages = eligibility.get('stdAges', [])
            if std_ages:
                flat_data['eligibilityStandardAges'] = ', '.join(std_ages)
            else:
                flat_data['eligibilityStandardAges'] = ''
                
        except Exception as e:
            logger.error(f"Error normalizing study data: {str(e)}")
            
        return flat_data
