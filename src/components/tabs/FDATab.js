import React, { useState } from 'react';

const FDATab = ({ data, searchType }) => {
  const [activeItem, setActiveItem] = useState(0);
  
  // Handle empty or error data
  if (!data || (Array.isArray(data) && data.length === 0)) {
    return (
      <div className="no-data">
        <p>No FDA information found.</p>
      </div>
    );
  }
  
  // Convert to array if it's not already
  const dataArray = Array.isArray(data) ? data : [data];
  
  // Format text content for display
  const formatText = (text) => {
    if (!text) return <p>No information available.</p>;
    
    return text.split('\n').map((paragraph, idx) => (
      <p key={idx}>{paragraph}</p>
    ));
  };
  
  // Get the current item
  const item = dataArray[activeItem];
  
  // Determine fields to display based on search type
  const getFields = () => {
    if (searchType === 'drug') {
      return [
        { id: 'description', label: 'Description' },
        { id: 'indications_and_usage', label: 'Indications & Usage' },
        { id: 'dosage_and_administration', label: 'Dosage & Administration' },
        { id: 'clinical_pharmacology', label: 'Clinical Pharmacology' },
        { id: 'mechanism_of_action', label: 'Mechanism of Action' },
        { id: 'contraindications', label: 'Contraindications' },
        { id: 'warnings', label: 'Warnings' },
        { id: 'precautions', label: 'Precautions' },
        { id: 'adverse_reactions', label: 'Adverse Reactions' },
        { id: 'drug_interactions', label: 'Drug Interactions' }
      ];
    } else {
      return [
        { id: 'brand_name', label: 'Brand Name' },
        { id: 'generic_name', label: 'Generic Name' },
        { id: 'indications_and_usage', label: 'Indications & Usage' },
        { id: 'manufacturer_name', label: 'Manufacturer' },
        { id: 'description', label: 'Description' }
      ];
    }
  };

  return (
    <div className="fda-tab">
      {dataArray.length > 1 && (
        <div className="item-selector">
          <label className="item-selector-label">Select Item:</label>
          <select 
            className="form-control"
            value={activeItem}
            onChange={(e) => setActiveItem(parseInt(e.target.value))}
          >
            {dataArray.map((item, idx) => (
              <option key={idx} value={idx}>
                {item.brand_name || item.generic_name || `Item ${idx + 1}`}
              </option>
            ))}
          </select>
        </div>
      )}
      
      <div className="fda-header">
        <div className="fda-drug-info">
          {item.brand_name && (
            <h3 className="drug-name">
              {item.brand_name}
              {item.generic_name && <span className="generic-name"> ({item.generic_name})</span>}
            </h3>
          )}
          {!item.brand_name && item.generic_name && (
            <h3 className="drug-name">{item.generic_name}</h3>
          )}
          
          {item.manufacturer_name && (
            <p className="manufacturer">Manufacturer: {item.manufacturer_name}</p>
          )}
        </div>
      </div>
      
      <div className="fda-content">
        {getFields().map(field => (
          item[field.id] ? (
            <div key={field.id} className="fda-section">
              <h4 className="section-title">{field.label}</h4>
              <div className="section-content">
                {formatText(item[field.id])}
              </div>
            </div>
          ) : null
        ))}
      </div>
      
      <style jsx>{`
        .fda-tab {
          padding: 0.5rem;
        }
        
        .item-selector {
          margin-bottom: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        
        .item-selector-label {
          font-weight: 500;
          white-space: nowrap;
        }
        
        .fda-header {
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid var(--border-color);
        }
        
        .drug-name {
          font-size: 1.25rem;
          color: var(--primary-color);
          margin-bottom: 0.5rem;
        }
        
        .generic-name {
          font-weight: normal;
          color: var(--light-text);
        }
        
        .manufacturer {
          font-size: 0.9rem;
          color: var(--light-text);
        }
        
        .fda-section {
          margin-bottom: 1.5rem;
        }
        
        .section-title {
          font-size: 1.1rem;
          color: var(--primary-color);
          margin-bottom: 0.75rem;
          padding-bottom: 0.35rem;
          border-bottom: 1px dashed var(--border-color);
        }
        
        .section-content {
          font-size: 0.95rem;
          line-height: 1.6;
        }
        
        .section-content p {
          margin-bottom: 0.75rem;
        }
        
        .no-data {
          padding: 2rem;
          text-align: center;
          color: var(--light-text);
        }
        
        @media (max-width: 768px) {
          .item-selector {
            flex-direction: column;
            align-items: flex-start;
          }
        }
      `}</style>
    </div>
  );
};

export default FDATab;
