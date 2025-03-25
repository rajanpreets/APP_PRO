import React, { useState } from 'react';

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
      
      <style jsx>{`
        .search-bar {
          width: 100%;
        }
        
        .search-type-selector {
          display: flex;
          gap: 1.5rem;
          margin-bottom: 1rem;
        }
        
        .radio-label {
          display: flex;
          align-items: center;
          cursor: pointer;
        }
        
        .radio-label input {
          margin-right: 0.5rem;
        }
        
        .search-input-container {
          display: flex;
          gap: 0.5rem;
        }
        
        .search-input {
          flex-grow: 1;
        }
        
        .search-button {
          white-space: nowrap;
          min-width: 120px;
        }
        
        @media (max-width: 576px) {
          .search-input-container {
            flex-direction: column;
          }
          
          .search-button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default SearchBar;
