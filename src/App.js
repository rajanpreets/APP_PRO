import React, { useState, useEffect } from 'react';
// Import any other components or dependencies you're using

function App() {
  // Define state variables with useState hooks
  const [loading, setLoading] = useState(false);
  const [availableSources, setAvailableSources] = useState({});
  const [selectedSources, setSelectedSources] = useState([]);
  // Include any other state variables your app needs

  // Fetch sources when component mounts
  useEffect(() => {
    fetchSources();
  }, []);

  // Function to fetch available sources from API
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

  // Function to handle source selection changes
  const handleSourceChange = (source) => {
    setSelectedSources(prev => {
      if (prev.includes(source)) {
        return prev.filter(s => s !== source);
      } else {
        return [...prev, source];
      }
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Drug Information Dashboard</h1>
      </header>
      
      <main>
        {loading ? (
          <div className="loading">Loading sources...</div>
        ) : (
          <div className="content">
            <div className="sources-selection">
              <h2>Data Sources</h2>
              {Object.entries(availableSources).map(([key, name]) => (
                <div key={key} className="source-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={selectedSources.includes(key)}
                      onChange={() => handleSourceChange(key)}
                    />
                    {name}
                  </label>
                </div>
              ))}
            </div>
            
            <div className="results-area">
              {/* Render your search results or data display here */}
              {selectedSources.length > 0 ? (
                <p>Selected sources: {selectedSources.join(', ')}</p>
              ) : (
                <p>No sources selected. Please select at least one data source.</p>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
