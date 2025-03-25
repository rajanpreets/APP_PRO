// In the fetchSources function in App.js
const fetchSources = async () => {
  try {
    setLoading(true);
    const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/sources`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    setAvailableSources(data);
    // Default select all sources
    setSelectedSources(Object.keys(data));
  } catch (error) {
    console.error('Error fetching sources:', error);
    // Set fallback sources if API fails
    const fallbackSources = {
      'fda': 'FDA Drug Information',
      'clinical_trials': 'Clinical Trials',
      'sec': 'SEC Company Information',
      'ncbi': 'NCBI Publications',
      'news': 'Latest News',
      'snomed': 'SNOMED-CT Medical Terminology'
    };
    setAvailableSources(fallbackSources);
    setSelectedSources(Object.keys(fallbackSources));
  } finally {
    setLoading(false);
  }
};
