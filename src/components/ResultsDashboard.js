import React, { useState } from 'react';
import './ResultsDashboard.css';

// Import all tab components - adjust the paths if needed
import SummaryTab from './tabs/SummaryTab';
import FDATab from './tabs/FDATab';
import ClinicalTrialsTab from './tabs/ClinicalTrialsTab';
import NCBITab from './tabs/NCBITab';
import NewsTab from './tabs/NewsTab';
import SECTab from './tabs/SECTab';
import SNOMEDTab from './tabs/SNOMEDTab';

const ResultsDashboard = ({ results, summary, query, searchType }) => {
  // Default to summary tab
  const [activeTab, setActiveTab] = useState('summary');
  
  // Very simple tab configuration
  const tabConfig = [
    { id: 'summary', label: 'Summary' },
    { id: 'fda', label: 'FDA' },
    { id: 'clinical_trials', label: 'Clinical Trials' },
    { id: 'ncbi', label: 'NCBI Publications' },
    { id: 'news', label: 'News' },
    { id: 'sec', label: 'SEC Company Info' },
    { id: 'snomed', label: 'Medical Terms' }
  ];

  // If no results, show wait message
  if (!results) {
    return (
      <div className="results-dashboard">
        <div className="card results-card">
          <div className="card-header">
            <h2 className="card-title">Waiting for results...</h2>
          </div>
          <div className="no-results">
            <p>Enter a search query and select data sources to see results.</p>
          </div>
        </div>
      </div>
    );
  }

  // Helper function to render tab content safely
  const renderTabContent = () => {
    // Make sure all data passed to components has safe fallbacks
    const safeResults = results || {};
    const safeSummary = summary || {};
    const safeQuery = query || '';
    const safeSearchType = searchType || 'drug';

    switch (activeTab) {
      case 'summary':
        return <SummaryTab summary={safeSummary} query={safeQuery} searchType={safeSearchType} />;
      case 'fda':
        return <FDATab data={safeResults.fda || []} searchType={safeSearchType} />;
      case 'clinical_trials':
        return <ClinicalTrialsTab data={safeResults.clinical_trials || []} />;
      case 'ncbi':
        return <NCBITab data={safeResults.ncbi || []} />;
      case 'news':
        return <NewsTab data={safeResults.news || {}} />;
      case 'sec':
        return <SECTab data={safeResults.sec || []} />;
      case 'snomed':
        return <SNOMEDTab data={safeResults.snomed || []} query={safeQuery} />;
      default:
        return <div>Select a tab to view results</div>;
    }
  };

  return (
    <div className="results-dashboard">
      <div className="card results-card">
        <div className="card-header">
          <h2 className="card-title">Results for: {query || 'Your search'}</h2>
          <span className="search-type-badge">
            {searchType === 'drug' ? 'Drug' : 'Disease'}
          </span>
        </div>

        <div className="tabs">
          {tabConfig.map(tab => (
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
      </div>
    </div>
  );
};

export default ResultsDashboard;
