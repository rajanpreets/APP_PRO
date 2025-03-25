import React from 'react';

const SourceSelector = ({ sources, selectedSources, onChange }) => {
  const handleSourceToggle = (sourceKey) => {
    if (selectedSources.includes(sourceKey)) {
      onChange(selectedSources.filter(key => key !== sourceKey));
    } else {
      onChange([...selectedSources, sourceKey]);
    }
  };

  const handleSelectAll = () => {
    onChange(Object.keys(sources));
  };

  const handleSelectNone = () => {
    onChange([]);
  };

  // Sort sources alphabetically by their labels
  const sortedSources = Object.entries(sources).sort((a, b) => a[1].localeCompare(b[1]));

  return (
    <div className="source-selector">
      <h3 className="source-selector-title">Data Sources</h3>
      
      <div className="source-selector-actions">
        <button 
          type="button" 
          className="btn btn-secondary btn-sm" 
          onClick={handleSelectAll}
        >
          Select All
        </button>
        <button 
          type="button" 
          className="btn btn-secondary btn-sm" 
          onClick={handleSelectNone}
        >
          Clear All
        </button>
      </div>
      
      <div className="source-options">
        {sortedSources.map(([key, label]) => (
          <label key={key} className="source-option">
            <input
              type="checkbox"
              checked={selectedSources.includes(key)}
              onChange={() => handleSourceToggle(key)}
            />
            <span className="source-label">{label}</span>
          </label>
        ))}
      </div>
      
      <style jsx>{`
        .source-selector {
          margin-top: 1.5rem;
          padding-top: 1.5rem;
          border-top: 1px solid var(--border-color);
        }
        
        .source-selector-title {
          font-size: 1.1rem;
          margin-bottom: 0.75rem;
          color: var(--primary-color);
        }
        
        .source-selector-actions {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        
        .btn-sm {
          padding: 0.25rem 0.5rem;
          font-size: 0.875rem;
        }
        
        .source-options {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 0.75rem;
        }
        
        .source-option {
          display: flex;
          align-items: center;
          padding: 0.35rem 0;
          cursor: pointer;
          transition: color 0.2s;
        }
        
        .source-option:hover {
          color: var(--secondary-color);
        }
        
        .source-option input {
          margin-right: 0.5rem;
        }
        
        .source-label {
          font-size: 0.95rem;
        }
        
        @media (max-width: 576px) {
          .source-options {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default SourceSelector;
