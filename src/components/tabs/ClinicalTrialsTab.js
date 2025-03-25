import React, { useState, useMemo } from 'react';

const ClinicalTrialsTab = ({ data }) => {
  const [activeTab, setActiveTab] = useState('ongoing');
  const [selectedTrial, setSelectedTrial] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Move useMemo hooks to the top level, before any conditional returns
  // Group trials by status - always run this even if data is empty
  const groupedTrials = useMemo(() => {
    const groups = {
      ongoing: [],
      completed: [],
      recruiting: [],
      other: []
    };
    
    // Only process if we have valid data
    if (data && Array.isArray(data) && data.length > 0) {
      data.forEach(trial => {
        const status = trial.overallStatus?.toLowerCase() || '';
        
        if (status.includes('recruit')) {
          groups.recruiting.push(trial);
        } else if (status.includes('active') || status.includes('enrolling') || status === 'not yet recruiting') {
          groups.ongoing.push(trial);
        } else if (status === 'completed') {
          groups.completed.push(trial);
        } else {
          groups.other.push(trial);
        }
      });
    }
    
    return groups;
  }, [data]);
  
  // Filter trials based on search term - always run this even if data is empty
  const filteredTrials = useMemo(() => {
    // Default to empty array
    const currentTabTrials = groupedTrials[activeTab] || [];
    
    if (!searchTerm.trim()) {
      return currentTabTrials;
    }
    
    const searchLower = searchTerm.toLowerCase();
    return currentTabTrials.filter(trial => {
      return (
        (trial.briefTitle && trial.briefTitle.toLowerCase().includes(searchLower)) ||
        (trial.officialTitle && trial.officialTitle.toLowerCase().includes(searchLower)) ||
        (trial.conditions && trial.conditions.toLowerCase().includes(searchLower)) ||
        (trial.interventions && trial.interventions.toLowerCase().includes(searchLower))
      );
    });
  }, [groupedTrials, activeTab, searchTerm]);
  
  // Handle empty data after hooks are defined
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className="no-data">
        <p>No clinical trials found.</p>
      </div>
    );
  }
  
  // Handle trial selection
  const handleTrialSelect = (trial) => {
    setSelectedTrial(trial);
  };
  
  // Format date string
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="clinical-trials-results">
      <div className="ct-header">
        <h3 className="ct-title">Clinical Trials ({data.length})</h3>
        
        <div className="ct-tabs">
          <div 
            className={`ct-tab ${activeTab === 'recruiting' ? 'active' : ''}`}
            onClick={() => setActiveTab('recruiting')}
          >
            Recruiting ({groupedTrials.recruiting.length})
          </div>
          <div 
            className={`ct-tab ${activeTab === 'ongoing' ? 'active' : ''}`}
            onClick={() => setActiveTab('ongoing')}
          >
            Ongoing ({groupedTrials.ongoing.length})
          </div>
          <div 
            className={`ct-tab ${activeTab === 'completed' ? 'active' : ''}`}
            onClick={() => setActiveTab('completed')}
          >
            Completed ({groupedTrials.completed.length})
          </div>
          <div 
            className={`ct-tab ${activeTab === 'other' ? 'active' : ''}`}
            onClick={() => setActiveTab('other')}
          >
            Other ({groupedTrials.other.length})
          </div>
        </div>
      </div>
      
      <div className="ct-search">
        <input
          type="text"
          className="form-control"
          placeholder="Search trials..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      
      <div className="ct-layout">
        <div className="ct-list">
          {filteredTrials.length === 0 ? (
            <div className="no-trials">
              <p>No trials found in this category.</p>
            </div>
          ) : (
            filteredTrials.map((trial, idx) => (
              <div 
                key={trial.nctId || idx}
                className={`trial-item ${selectedTrial === trial ? 'active' : ''}`}
                onClick={() => handleTrialSelect(trial)}
              >
                <h4 className="trial-title">
                  {trial.briefTitle || 'Untitled Trial'}
                </h4>
                <div className="trial-meta">
                  <span className="trial-id">ID: {trial.nctId || 'Unknown'}</span>
                  <span className="trial-status">{trial.overallStatus || 'Unknown Status'}</span>
                  {trial.phases && <span className="trial-phase">{trial.phases}</span>}
                </div>
                <p className="trial-sponsor">
                  {trial.leadSponsor || 'Unknown Sponsor'}
                </p>
              </div>
            ))
          )}
        </div>
        
        <div className="ct-details">
          {selectedTrial ? (
            <div className="trial-details">
              <h3 className="trial-details-title">
                {selectedTrial.briefTitle}
              </h3>
              
              <div className="trial-details-meta">
                <div className="meta-item">
                  <span className="meta-label">NCT ID:</span>
                  <span className="meta-value">
                    <a 
                      href={`https://clinicaltrials.gov/study/${selectedTrial.nctId}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {selectedTrial.nctId}
                    </a>
                  </span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Status:</span>
                  <span className="meta-value">{selectedTrial.overallStatus}</span>
                </div>
                {selectedTrial.phases && (
                  <div className="meta-item">
                    <span className="meta-label">Phase:</span>
                    <span className="meta-value">{selectedTrial.phases}</span>
                  </div>
                )}
                {selectedTrial.startDate && (
                  <div className="meta-item">
                    <span className="meta-label">Start Date:</span>
                    <span className="meta-value">{formatDate(selectedTrial.startDate)}</span>
                  </div>
                )}
                {selectedTrial.completionDate && (
                  <div className="meta-item">
                    <span className="meta-label">Completion Date:</span>
                    <span className="meta-value">{formatDate(selectedTrial.completionDate)}</span>
                  </div>
                )}
              </div>
              
              {selectedTrial.briefSummary && (
                <div className="details-section">
                  <h4 className="section-title">Brief Summary</h4>
                  <p>{selectedTrial.briefSummary}</p>
                </div>
              )}
              
              {selectedTrial.conditions && (
                <div className="details-section">
                  <h4 className="section-title">Conditions</h4>
                  <p>{selectedTrial.conditions}</p>
                </div>
              )}
              
              {selectedTrial.interventionDrug && (
                <div className="details-section">
                  <h4 className="section-title">Drug Interventions</h4>
                  <p>{selectedTrial.interventionDrug}</p>
                </div>
              )}
              
              {selectedTrial.primaryOutcomes && (
                <div className="details-section">
                  <h4 className="section-title">Primary Outcomes</h4>
                  <div className="formatted-text">
                    {selectedTrial.primaryOutcomes.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedTrial.eligibilityCriteria && (
                <div className="details-section">
                  <h4 className="section-title">Eligibility Criteria</h4>
                  <div className="formatted-text eligibility">
                    {selectedTrial.eligibilityCriteria.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="no-selection">
              <p>Select a trial to view details</p>
            </div>
          )}
        </div>
      </div>
      
      <style jsx>{`
        .clinical-trials-results {
          padding: 0.5rem;
        }
        
        .ct-header {
          margin-bottom: 1.5rem;
        }
        
        .ct-title {
          font-size: 1.25rem;
          margin-bottom: 1rem;
          color: var(--primary-color);
        }
        
        .ct-tabs {
          display: flex;
          border-bottom: 1px solid var(--border-color);
        }
        
        .ct-tab {
          padding: 0.75rem 1rem;
          cursor: pointer;
          font-size: 0.9rem;
          border-bottom: 3px solid transparent;
        }
        
        .ct-tab:hover {
          color: var(--secondary-color);
        }
        
        .ct-tab.active {
          border-bottom-color: var(--secondary-color);
          color: var(--secondary-color);
          font-weight: 500;
        }
        
        .ct-search {
          margin-bottom: 1.5rem;
        }
        
        .ct-layout {
          display: grid;
          grid-template-columns: 1fr 2fr;
          gap: 1.5rem;
          min-height: 500px;
        }
        
        .ct-list {
          border-right: 1px solid var(--border-color);
          overflow-y: auto;
          max-height: 700px;
          padding-right: 1rem;
        }
        
        .trial-item {
          padding: 1rem;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          margin-bottom: 1rem;
          cursor: pointer;
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        
        .trial-item:hover {
          border-color: var(--secondary-color);
        }
        
        .trial-item.active {
          border-color: var(--secondary-color);
          box-shadow: 0 2px 8px rgba(52, 152, 219, 0.1);
        }
        
        .trial-title {
          font-size: 1rem;
          margin-bottom: 0.5rem;
          color: var(--primary-color);
          line-height: 1.4;
        }
        
        .trial-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
          margin-bottom: 0.5rem;
          font-size: 0.8rem;
        }
        
        .trial-id {
          color: var(--light-text);
        }
        
        .trial-status {
          background-color: rgba(52, 152, 219, 0.1);
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
          color: var(--secondary-color);
        }
        
        .trial-phase {
          background-color: rgba(46, 204, 113, 0.1);
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
          color: var(--success-color);
        }
        
        .trial-sponsor {
          font-size: 0.85rem;
          color: var(--light-text);
        }
        
        .ct-details {
          overflow-y: auto;
          max-height: 700px;
          padding-left: 1rem;
        }
        
        .no-data, .no-trials, .no-selection {
          display: flex;
          height: 200px;
          justify-content: center;
          align-items: center;
          color: var(--light-text);
          border: 1px dashed var(--border-color);
          border-radius: 6px;
        }
        
        .trial-details-title {
          font-size: 1.25rem;
          margin-bottom: 1rem;
          color: var(--primary-color);
          line-height: 1.4;
        }
        
        .trial-details-meta {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid var(--border-color);
        }
        
        .meta-item {
          display: flex;
          flex-direction: column;
        }
        
        .meta-label {
          font-size: 0.8rem;
          color: var(--light-text);
          margin-bottom: 0.25rem;
        }
        
        .meta-value {
          font-size: 0.95rem;
          font-weight: 500;
        }
        
        .details-section {
          margin-bottom: 1.5rem;
        }
        
        .section-title {
          font-size: 1.1rem;
          color: var(--primary-color);
          margin-bottom: 0.75rem;
          padding-bottom: 0.35rem;
          border-bottom: 1px dashed var(--border-color);
        }
        
        .formatted-text p {
          margin-bottom: 0.75rem;
          font-size: 0.95rem;
          line-height: 1.6;
        }
        
        .eligibility {
          max-height: 300px;
          overflow-y: auto;
          padding: 1rem;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          background-color: rgba(52, 152, 219, 0.05);
        }
        
        @media (max-width: 992px) {
          .ct-layout {
            grid-template-columns: 1fr;
          }
          
          .ct-list {
            border-right: none;
            border-bottom: 1px solid var(--border-color);
            padding-right: 0;
            padding-bottom: 1rem;
            max-height: 400px;
          }
          
          .ct-details {
            padding-left: 0;
            padding-top: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default ClinicalTrialsTab;
