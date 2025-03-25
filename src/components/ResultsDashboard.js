import React, { useState, useEffect } from 'react';
import SummaryTab from './tabs/SummaryTab';
import FDATab from './tabs/FDATab';
import ClinicalTrialsTab from './tabs/ClinicalTrialsTab';
import NCBITab from './tabs/NCBITab';
import NewsTab from './tabs/NewsTab';
import SECTab from './tabs/SECTab';
import SNOMEDTab from './tabs/SNOMEDTab';

const ResultsDashboard = ({ results, summary, query, searchType }) => {
  const [activeTab, setActiveTab] = useState('summary');
  const [availableTabs, setAvailableTabs] = useState([]);

  // Determine which tabs should be available based on the results and searchType
  useEffect(() => {
    const tabs = [
      { id: 'summary', label: 'Summary', visible: !!summary && !summary.error },
      { id: 'fda', label: 'FDA', visible: results.fda && !results.fda.error },
      { id: 'clinical_trials', label: 'Clinical Trials', visible: results.clinical_trials && !results.clinical_trials.error },
      { id: 'ncbi', label: 'NCBI Publications', visible: results.ncbi && !results.ncbi.error },
      { id: 'news', label: 'News', visible: results.news && !results.news.error },
      { id: 'sec', label: 'SEC Company Info', visible: searchType === 'drug' && results.sec && !results.sec.error },
      { id: 'snomed', label: 'Medical Terms', visible: results.snomed && !results.snomed.error }
    ];

    const availableTabs = tabs.filter(tab => tab.visible);
    setAvailableTabs(availableTabs);

    // If the active tab is not available, set it to the first available tab
    if (availableTabs.length > 0 && !availableTabs.some(tab => tab.id === activeTab)) {
      setActiveTab(availableTabs[0].id);
    }
  }, [results, summary, searchType, activeTab]);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'summary':
        return <SummaryTab summary={summary} query={query} searchType={searchType} />;
      case 'fda':
        return <FDATab data={results.fda} searchType={searchType} />;
      case 'clinical_trials':
        return <ClinicalTrialsTab data={results.clinical_trials} />;
      case 'ncbi':
        return <NCBITab data={results.ncbi} />;
      case 'news':
        return <NewsTab data={results.news} />;
      case 'sec':
        return <SECTab data={results.sec} />;
      case 'snomed':
        return <SNOMEDTab data={results.snomed} query={query} />;
      default:
        return <div>Select a tab to view results</div>;
    }
  };

  return (
    <div className="results-dashboard">
      <div className="card results-card">
        <div className="card-header">
          <h2 className="card-title">Results for: {query}</h2>
          <span className="search-type-badge">
            {searchType === 'drug' ? 'Drug' : 'Disease'}
          </span>
        </div>

        {availableTabs.length > 0 ? (
          <>
            <div className="tabs">
              {availableTabs.map(tab => (
                <div
                  key={tab.id}
                  className={`tab ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  {tab.label}
                </div>
              ))}
            </div>

            <div className="tab-content">
              {renderTabContent()}
            </div>
          </>
        ) : (
          <div className="no-results">
            <p>No results available. Try adjusting your search or selecting different data sources.</p>
          </div>
        )}
      </div>

      <style jsx>{`
        .results-dashboard {
          width: 100%;
        }
        
        .results-card {
          overflow: hidden;
        }
        
        .search-type-badge {
          background-color: var(--secondary-color);
          color: white;
          font-size: 0.85rem;
          padding: 0.35rem 0.75rem;
          border-radius: 20px;
        }
        
        .tabs {
          display: flex;
          flex-wrap: nowrap;
          overflow-x: auto;
          border-bottom: 1px solid var(--border-color);
          margin-bottom: 0;
          padding-bottom: 0;
          -webkit-overflow-scrolling: touch;
        }
        
        .tab {
          padding: 0.75rem 1rem;
          cursor: pointer;
          white-space: nowrap;
          border-bottom: 3px solid transparent;
          transition: all 0.2s ease;
        }
        
        .tab:hover {
          color: var(--secondary-color);
        }
        
        .tab.active {
          border-bottom-color: var(--secondary-color);
          color: var(--secondary-color);
          font-weight: 500;
        }
        
        .tab-content {
          padding: 1.5rem 0.5rem 0.5rem;
          min-height: 400px;
        }
        
        .no-results {
          padding: 3rem 1rem;
          text-align: center;
          color: var(--light-text);
        }

        @media (max-width: 768px) {
          .tab {
            padding: 0.6rem 0.8rem;
            font-size: 0.9rem;
          }
          
          .tab-content {
            padding: 1rem 0.25rem 0.25rem;
          }
        }
      `}</style>
    </div>
  );
};

export default ResultsDashboard;
