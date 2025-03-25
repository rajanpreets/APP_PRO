import React, { useState } from 'react';
import './App.css';
import SearchBar from './components/SearchBar';
import SourceSelector from './components/SourceSelector';
import ResultsDashboard from './components/ResultsDashboard';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('drug');
  const [selectedSources, setSelectedSources] = useState(['clinical_trials', 'fda', 'ncbi', 'news', 'sec', 'snomed']);
  const [results, setResults] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (searchQuery, type, sources) => {
    setLoading(true);
    setError(null);
    setResults(null);
    setSummary(null);
    
    try {
      console.log('Searching for:', searchQuery, type, sources);
      
      // API call to your backend search endpoint
      const response = await fetch(`${API_URL}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          type: type,
          sources: sources,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Search failed with status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Search results:', data);
      
      // Initialize with empty objects for each source if they don't exist
      const processedData = {};
      sources.forEach(source => {
        // Ensure each source has at least an empty array
        processedData[source] = data[source] || [];
      });
      
      setResults(processedData);
      
      // After getting results, get the summary
      if (data && typeof data === 'object' && Object.keys(data).length > 0) {
        try {
          const summaryResponse = await fetch(`${API_URL}/api/summarize`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              query: searchQuery,
              type: type,
              data: data,
            }),
          });
          
          if (summaryResponse.ok) {
            const summaryData = await summaryResponse.json();
            console.log('Summary data:', summaryData);
            setSummary(summaryData || {});
          } else {
            console.error('Failed to get summary');
            setSummary({ error: 'Failed to generate summary' });
          }
        } catch (summaryErr) {
          console.error('Error getting summary:', summaryErr);
          setSummary({ error: summaryErr.message });
        }
      } else {
        setSummary({ message: 'No data available for summarization' });
      }
    } catch (err) {
      setError(err.message);
      console.error('Error searching:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Drug Information Dashboard</h1>
      </header>
      
      <main className="app-main">
        <div className="search-container">
          <SearchBar 
            onSearch={(q, type) => {
              setQuery(q);
              setSearchType(type);
              handleSearch(q, type, selectedSources);
            }}
            searchType={searchType}
          />
          
          <SourceSelector
            selectedSources={selectedSources}
            onChange={(sources) => {
              setSelectedSources(sources);
              if (query) {
                handleSearch(query, searchType, sources);
              }
            }}
          />
        </div>
        
        {error && <ErrorMessage message={error} />}
        {loading && <LoadingSpinner />}
        
        {!loading && (
          <ResultsDashboard 
            results={results} 
            summary={summary}
            query={query}
            searchType={searchType}
          />
        )}
      </main>
    </div>
  );
}

export default App;
