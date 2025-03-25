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
    <div style={{ width: '100%' }}>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Search for:</label>
          <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                value="drug"
                checked={searchType === 'drug'}
                onChange={() => setSearchType('drug')}
                style={{ marginRight: '0.5rem' }}
              />
              <span>Drug</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                value="disease"
                checked={searchType === 'disease'}
                onChange={() => setSearchType('disease')}
                style={{ marginRight: '0.5rem' }}
              />
              <span>Disease</span>
            </label>
          </div>
        </div>
        
        <div className="form-group" style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            className="form-control"
            style={{ flexGrow: 1 }}
            placeholder={`Enter ${searchType} name...`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isSubmitting}
          />
          <button 
            type="submit" 
            className="btn btn-primary"
            style={{ whiteSpace: 'nowrap', minWidth: '120px' }}
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
