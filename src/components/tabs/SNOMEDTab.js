import React, { useState } from 'react';

const SNOMEDTab = ({ data, query }) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className="no-data">
        <p>No SNOMED CT terminology data available.</p>
      </div>
    );
  }

  // Filter terms based on search
  const filteredTerms = searchTerm.trim() 
    ? data.filter(term => 
        term.display?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        term.code?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : data;

  return (
    <div className="snomed-tab">
      <div className="tab-header">
        <h3 className="tab-title">SNOMED CT Medical Terminology</h3>
        <p className="tab-description">
          Showing medical terms and concepts related to "{query}" from SNOMED CT, 
          a comprehensive clinical healthcare terminology.
        </p>
      </div>
      
      <div className="search-container">
        <input
          type="text"
          placeholder="Search terms..."
          className="form-control"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      
      <div className="terms-list">
        <div className="list-header">
          <div className="code-column">Code</div>
          <div className="term-column">Term</div>
          <div className="tag-column">Semantic Tag</div>
        </div>
        
        {filteredTerms.length === 0 ? (
          <div className="no-results">
            <p>No matching terms found.</p>
          </div>
        ) : (
          filteredTerms.map((term, idx) => (
            <div key={term.code || idx} className="term-item">
              <div className="code-column">{term.code}</div>
              <div className="term-column">{term.display}</div>
              <div className="tag-column">
                {term.properties?.semanticTag || 
                 (term.full_name && term.full_name.includes('(') && 
                  term.full_name.split('(').pop().replace(')', ''))}
              </div>
            </div>
          ))
        )}
      </div>
      
      <div className="info-footer">
        <p>
          SNOMED CT (Systematized Nomenclature of Medicine -- Clinical Terms) is a standardized, 
          multilingual vocabulary of clinical terminology used by physicians and other health care providers 
          for the electronic exchange of clinical health information.
        </p>
      </div>
      
      <style jsx>{`
        .snomed-tab {
          padding: 0.5rem;
        }
        
        .tab-header {
          margin-bottom: 1.5rem;
        }
        
        .tab-title {
          font-size: 1.25rem;
          color: var(--primary-color);
          margin-bottom: 0.5rem;
        }
        
        .tab-description {
          color: var(--light-text);
          font-size: 0.95rem;
        }
        
        .search-container {
          margin-bottom: 1.5rem;
        }
        
        .terms-list {
          border: 1px solid var(--border-color);
          border-radius: 6px;
          overflow: hidden;
        }
        
        .list-header {
          display: flex;
          background-color: var(--primary-color);
          color: white;
          padding: 0.75rem 1rem;
          font-weight: 500;
          font-size: 0.9rem;
        }
        
        .term-item {
          display: flex;
          padding: 0.75rem 1rem;
          border-bottom: 1px solid var(--border-color);
          transition: background-color 0.2s;
        }
        
        .term-item:last-child {
          border-bottom: none;
        }
        
        .term-item:hover {
          background-color: rgba(52, 152, 219, 0.05);
        }
        
        .code-column {
          width: 120px;
          font-family: monospace;
          color: var(--primary-color);
        }
        
        .term-column {
          flex-grow: 1;
          padding-right: 1rem;
        }
        
        .tag-column {
          width: 120px;
          font-size: 0.85rem;
          color: var(--light-text);
          text-align: right;
        }
        
        .no-data, .no-results {
          padding: 3rem 1rem;
          text-align: center;
          color: var(--light-text);
        }
        
        .info-footer {
          margin-top: 1.5rem;
          padding-top: 1rem;
          border-top: 1px solid var(--border-color);
          font-size: 0.85rem;
          color: var(--light-text);
          font-style: italic;
        }
      `}</style>
    </div>
  );
};

export default SNOMEDTab;
