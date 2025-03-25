import React, { useState, useMemo } from 'react';

const ClinicalTrialsTab = ({ data }) => {
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTrial, setSelectedTrial] = useState(null);
  
  // Handle empty or error data
  if (!data || (Array.isArray(data) && data.length === 0)) {
    return (
      <div className="no-data">
        <p>No clinical trials found.</p>
      </div>
    );
  }
  
  // Convert to array if it's not already
  const dataArray = Array.isArray(data) ? data : [data];
  
  // Group trials by status
  const groupedTrials = useMemo(() => {
    const groups = {
      recruiting: [],
      active: [],
      completed: [],
      other: [],
      all: []
    };
    
    dataArray.forEach(trial => {
      // Add to 'all' group
      groups.all.push(trial);
      
      const status = trial.overallStatus?.toLowerCase() || '';
      
      if (status.includes('recruiting')) {
        groups.recruiting.push(trial);
      } else if (status.includes('active') || status === 'ongoing' || status.includes('enrolling')) {
        groups.active.push(trial);
      } else if (status === 'completed') {
        groups.completed.push(trial);
      } else {
        groups.other.push(trial);
      }
    });
    
    return groups;
  }, [dataArray]);
  
  // Filter trials by search term
  const filteredTrials = useMemo(() => {
    if (!searchTerm.trim()) {
      return groupedTrials[activeTab] || [];
    }
    
    const searchLower = searchTerm.toLowerCase();
    return (groupedTrials[activeTab] || []).filter(trial => {
      return (
        (trial.briefTitle && trial.briefTitle.toLowerCase().includes(searchLower)) ||
        (trial.officialTitle && trial.officialTitle.toLowerCase().includes(searchLower)) ||
        (trial.conditions && trial.conditions.toLowerCase().includes(searchLower)) ||
        (trial.interventions && trial.interventions.toLowerCase().includes(searchLower))
      );
    });
  }, [groupedTrials, activeTab, searchTerm]);
  
  // Format a date string
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="ct-tab">
      <div className="ct-header">
        <h3 className="ct-title">Clinical Trials ({dataArray.length})</h3>
        
        <div className="ct-tabs">
          <div 
            className={`ct-tab-item ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            All ({groupedTrials.all.length})
          </div>
          <div 
            className={`ct-tab-item ${activeTab === 'recruiting' ? 'active' : ''}`}
            onClick={() => setActiveTab('recruiting')}
          >
            Recruiting ({groupedTrials.recruiting.length})
          </div>
          <div 
            className={`ct-tab-item ${activeTab === 'active' ? 'active' : ''}`}
            onClick={() => setActiveTab('active')}
          >
            Active ({groupedTrials.active.length})
          </div>
          <div 
            className={`ct-tab-item ${activeTab === 'completed' ? 'active' : ''}`}
            onClick={() => setActiveTab('completed')}
          >
            Completed ({groupedTrials.completed.length})
          </div>
          <div 
            className={`ct-tab-item ${activeTab === 'other' ? 'active' : ''}`}
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
      
      <div className="ct-content">
        <div className="ct-list">
          {filteredTrials.length === 0 ? (
            <div className="no-trials">
              <p>No trials found in this category.</p>
            </div>
          ) : (
            <div className="trials-container">
              {filteredTrials.map((trial, idx) => (
                <div 
                  key={trial.nctId || idx}
                  className={`trial-item ${selectedTrial === trial ? 'active' : ''}`}
                  onClick={() => setSelectedTrial(trial)}
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
              ))}
            </div>
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
        .ct-tab {
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
          overflow-x: auto;
          margin-bottom: 1rem;
          border-bottom: 1px solid var(--border-color);
        }
        
        .ct-tab-item {
          padding: 0.6rem 1rem;
          cursor: pointer;
          white-space: nowrap;
          border-bottom: 3px solid transparent;
          transition: all 0.2s ease;
        }
        
        .ct-tab-item:hover {
          color: var(--secondary-color);
        }
        
        .ct-tab-item.active {
          color: var(--secondary-color);
          border-bottom-color: var(--secondary-color);
          font-weight: 500;
        }
        
        .ct-search {
          margin-bottom: 1.5rem;
        }
        
        .ct-content {
          display: grid;
          grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr);
          gap: 1.5rem;
        }
        
        .ct-list {
          border-right: 1px solid var(--border-color);
          max-height: 600px;
        }
        
        .trials-container {
          overflow-y: auto;
          max-height: 600px;
          padding-right: 1rem;
        }
        
        .trial-item {
          padding: 1rem;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          margin-bottom: 1rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .trial-item:hover {
          border-color: var(--secondary-color);
        }
        
        .trial-item.active {
          border-color: var(--secondary-color);
          background-color: rgba(52, 152, 219, 0.05);
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
          max-height: 600px;
        }
        
        .trial-details-title {
          font-size: 1.25rem;
          margin-bottom: 1rem;
          color: var(--primary-color);
          line-height: 1.4;
        }
        
        .trial-details-meta {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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
        
        .meta-value a {
          color: var(--secondary-color);
          text-decoration: none;
        }
        
        .meta-value a:hover {
          text-decoration: underline;
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
        
        .no-trials, .no-selection, .no-data {
          display: flex;
          height: 200px;
          justify-content: center;
          align-items: center;
          color: var(--light-text);
          border: 1px dashed var(--border-color);
          border-radius: 6px;
        }
        
        @media (max-width: 992px) {
          .ct-content {
            grid-template-columns: 1fr;
          }
          
          .ct-list {
            border-right: none;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 1.5rem;
            padding-bottom: 1.5rem;
          }
          
          .trials-container {
            max-height: 300px;
          }
        }
      `}</style>
    </div>
  );
};

export default ClinicalTrialsTab;
