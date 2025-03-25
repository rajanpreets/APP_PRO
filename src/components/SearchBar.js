import React, { useState } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('drug');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (query.trim()) {
      setIsSubmitting(true);
      await onSearch(query, searchType);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Search for:</label>
          <div className="search-type-selector">
            <label className="radio-label">
              <input
                type="radio"
                value="drug"
                checked={searchType === 'drug'}
                onChange={() => setSearchType('drug')}
              />
              <span>Drug</span>
            </label>
            <label className="radio-label">
              <input
                type="radio"
                value="disease"
                checked={searchType === 'disease'}
                onChange={() => setSearchType('disease')}
              />
              <span>Disease</span>
            </label>
          </div>
        </div>
        
        <div className="form-group search-input-container">
          <input
            type="text"
            className="form-control search-input"
            placeholder={`Enter ${searchType} name...`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isSubmitting}
          />
          <button 
            type="submit" 
            className="btn btn-primary search-button"
            disabled={!query.trim() || isSubmitting}
          >
            {isSubmitting ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SearchBar;
