import React, { useState, useEffect } from 'react';
import SummaryTab from './tabs/SummaryTab';
import FDATab from './tabs/FDATab';
import ClinicalTrialsTab from './tabs/ClinicalTrialsTab';
import NCBITab from './tabs/NCBITab';
import NewsTab from './tabs/NewsTab';
import SECTab from './tabs/SECTab';
import SNOMEDTab from './tabs/SNOMEDTab';
import './ResultsDashboard.css'; // We'll create this CSS file

const ResultsDashboard = ({ results, summary, query, searchType }) => {
  const [activeTab, setActiveTab] = useState('summary');
  const [availableTabs, setAvailableTabs] = useState([]);

  // Determine which tabs should be available based on the results and searchType
  useEffect(() => {
    if (!results) {
      setAvailableTabs([]);
      return;
    }

    const tabs = [
      { id: 'summary', label: 'Summary', visible: !!summary && Object.keys(summary).length > 0 && !summary.error },
      { id: 'fda', label: 'FDA', visible: results.fda && Array.isArray(results.fda) && results.fda.length > 0 },
      { id: 'clinical_trials', label: 'Clinical Trials', visible: results.clinical_trials && Array.isArray(results.clinical_trials) && results.clinical_trials.length > 0 },
      { id: 'ncbi', label: 'NCBI Publications', visible: results.ncbi && Array.isArray(results.ncbi) && results.ncbi.length > 0 },
      { id: 'news', label: 'News', visible: results.news && Object.keys(results.news).length > 0 && !results.news.error },
      { id: 'sec', label: 'SEC Company Info', visible: searchType === 'drug' && results.sec && Array.isArray(results.sec) && results.sec.length > 0 },
      { id: 'snomed', label: 'Medical Terms', visible: results.snomed && Array.isArray(results.snomed) && results.snomed.length > 0 }
    ];

    const availableTabs = tabs.filter(tab => tab.visible);
    setAvailableTabs(availableTabs);

    // If the active tab is not available, set it to the first available tab
    if (availableTabs.length > 0 && !availableTabs.some(tab => tab.id === activeTab)) {
      setActiveTab(availableTabs[0].id);
    }
  }, [results, summary, searchType, activeTab]);

  const renderTabContent = () => {
    if (!results) return <div className="loading-placeholder">Loading results...</div>;

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

  // If no results yet, show a message
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
    </div>
  );
};

export default ResultsDashboard;
