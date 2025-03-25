import React, { useState, useEffect } from 'react';
import './App.css';
import SearchBar from './components/SearchBar';
import SourceSelector from './components/SourceSelector';
import ResultsDashboard from './components/ResultsDashboard';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import axios from 'axios';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('drug');
  const [selectedSources, setSelectedSources] = useState([]);
  const [availableSources, setAvailableSources] = useState({});
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);

  // Get API URL from environment variable or use default
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  // Create axios instance with base URL
  const api = axios.create({
    baseURL: API_URL,
    timeout: 60000 // Long timeout for complex queries
  });

  // Fetch available sources on component mount
  useEffect(() => {
    const fetchSources = async () => {
      try {
        setLoading(true);
        const response = await api.get('/api/sources');
        setAvailableSources(response.data);
        // Default select all sources
        setSelectedSources(Object.keys(response.data));
      } catch (error) {
        console.error('Error fetching sources:', error);
        setError('Unable to fetch available data sources. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchSources();
  }, []);

  const handleSearch = async (query, type) => {
    setSearchQuery(query);
    setSearchType(type);
    setLoading(true);
    setError(null);
    setResults(null);
    setSummary(null);

    try {
      // Make search request to backend
      const searchResponse = await api.post('/api/search', {
        query: query,
        type: type,
        sources: selectedSources,
      });

      const searchData = searchResponse.data;
      setResults(searchData);

      // Request summary of the data
      const summaryResponse = await api.post('/api/summarize', {
        data: searchData,
        query: query,
        type: type
      });

      setSummary(summaryResponse.data);
    } catch (error) {
      console.error('Error during search:', error);
      setError(
        error.response?.data?.error || 
        error.message || 
        'An unexpected error occurred. Please try again later.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSourceChange = (sources) => {
    setSelectedSources(sources);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Healthcare Data Integration Platform</h1>
      </header>
      <main>
        <div className="search-container">
          <SearchBar onSearch={handleSearch} />
          <SourceSelector 
            sources={availableSources} 
            selectedSources={selectedSources} 
            onChange={handleSourceChange} 
          />
        </div>
        
        {loading && <LoadingSpinner />}
        {error && <ErrorMessage message={error} />}
        
        {!loading && !error && results && (
          <ResultsDashboard 
            results={results} 
            summary={summary}
            query={searchQuery}
            searchType={searchType}
          />
        )}
      </main>
      <footer>
        <p>© {new Date().getFullYear()} Healthcare Data Integration Platform</p>
      </footer>
    </div>
  );
}

export default App;
