import React, { useState } from 'react';
import './App.css';
import SearchBar from './components/SearchBar';
import SourceSelector from './components/SourceSelector';
import ResultsDashboard from './components/ResultsDashboard';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';

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
      // API call to your backend search endpoint
      const response = await fetch('/api/search', {
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
        throw new Error('Search failed. Please try again later.');
      }
      
      const data = await response.json();
      setResults(data);
      
      // After getting results, get the summary
      if (Object.keys(data).length > 0) {
        const summaryResponse = await fetch('/api/summarize', {
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
          setSummary(summaryData);
        }
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
        
        {results && !loading && (
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
