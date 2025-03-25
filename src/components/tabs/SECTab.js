import React, { useState } from 'react';

const SECTab = ({ data }) => {
  const [selectedCompany, setSelectedCompany] = useState(null);
  
  // Handle empty or error data
  if (!data || (Array.isArray(data) && data.length === 0)) {
    return (
      <div className="no-data">
        <p>No company information found.</p>
      </div>
    );
  }
  
  // Convert to array if it's not already
  const dataArray = Array.isArray(data) ? data : [data];
  
  // Default to first company if none selected
  if (!selectedCompany && dataArray.length > 0) {
    setSelectedCompany(dataArray[0]);
  }
  
  // Format currency
  const formatCurrency = (value) => {
    if (value === undefined || value === null) return 'N/A';
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 2
    }).format(value);
  };

  return (
    <div className="sec-tab">
      {dataArray.length > 1 && (
        <div className="company-selector">
          <div className="selector-label">Select Company:</div>
          <div className="company-tabs">
            {dataArray.map((company, idx) => (
              <div 
                key={idx}
                className={`company-tab ${selectedCompany === company ? 'active' : ''}`}
                onClick={() => setSelectedCompany(company)}
              >
                {company.name || company.ticker || `Company ${idx + 1}`}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {selectedCompany && (
        <div className="company-details">
          <div className="company-header">
            <div className="company-primary-info">
              <h3 className="company-name">
                {selectedCompany.name}
                {selectedCompany.ticker && (
                  <span className="company-ticker">{selectedCompany.ticker}</span>
                )}
              </h3>
              
              {(selectedCompany.city || selectedCompany.stateOrCountry) && (
                <p className="company-location">
                  {[
                    selectedCompany.city,
                    selectedCompany.stateOrCountry,
                    selectedCompany.zipCode
                  ].filter(Boolean).join(', ')}
                </p>
              )}
            </div>
            
            {selectedCompany.companyName && selectedCompany.companyName !== selectedCompany.name && (
              <div className="company-official-name">
                Official Name: {selectedCompany.companyName}
              </div>
            )}
          </div>
          
          <div className="company-section-grid">
            <div className="company-section financials-section">
              <h4 className="section-title">Financial Information</h4>
              
              <div className="financials-grid">
                {selectedCompany.revenue !== undefined && (
                  <div className="financial-item">
                    <div className="financial-label">Revenue</div>
                    <div className="financial-value">{formatCurrency(selectedCompany.revenue)}</div>
                    {selectedCompany.revenueFiscalYear && (
                      <div className="financial-period">
                        FY {selectedCompany.revenueFiscalYear}
                        {selectedCompany.revenueFiscalPeriod && ` (${selectedCompany.revenueFiscalPeriod})`}
                      </div>
                    )}
                  </div>
                )}
                
                {selectedCompany.netIncome !== undefined && (
                  <div className="financial-item">
                    <div className="financial-label">Net Income</div>
                    <div className="financial-value">{formatCurrency(selectedCompany.netIncome)}</div>
                    {selectedCompany.netIncomeFiscalYear && (
                      <div className="financial-period">
                        FY {selectedCompany.netIncomeFiscalYear}
                        {selectedCompany.netIncomeFiscalPeriod && ` (${selectedCompany.netIncomeFiscalPeriod})`}
                      </div>
                    )}
                  </div>
                )}
                
                {selectedCompany.rdExpense !== undefined && (
                  <div className="financial-item">
                    <div className="financial-label">R&D Expense</div>
                    <div className="financial-value">{formatCurrency(selectedCompany.rdExpense)}</div>
                    {selectedCompany.rdExpenseFiscalYear && (
                      <div className="financial-period">
                        FY {selectedCompany.rdExpenseFiscalYear}
                        {selectedCompany.rdExpenseFiscalPeriod && ` (${selectedCompany.rdExpenseFiscalPeriod})`}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
            
            <div className="company-section filings-section">
              <h4 className="section-title">Recent SEC Filings</h4>
              
              <div className="filings-grid">
                {selectedCompany.recent10K && (
                  <div className="filing-item">
                    <div className="filing-type">Annual Report (10-K)</div>
                    <div className="filing-date">{selectedCompany.recent10K}</div>
                    {selectedCompany.recent10KAccessionNumber && (
                      <a 
                        href={`https://www.sec.gov/Archives/edgar/data/0001${selectedCompany.recent10KAccessionNumber}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="filing-link"
                      >
                        View Filing
                      </a>
                    )}
                  </div>
                )}
                
                {selectedCompany.recent10Q && (
                  <div className="filing-item">
                    <div className="filing-type">Quarterly Report (10-Q)</div>
                    <div className="filing-date">{selectedCompany.recent10Q}</div>
                    {selectedCompany.recent10QAccessionNumber && (
                      <a 
                        href={`https://www.sec.gov/Archives/edgar/data/0001${selectedCompany.recent10QAccessionNumber}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="filing-link"
                      >
                        View Filing
                      </a>
                    )}
                  </div>
                )}
              </div>
            </div>
            
            <div className="company-section additional-section">
              <h4 className="section-title">Additional Information</h4>
              
              <div className="additional-grid">
                {selectedCompany.match_type && (
                  <div className="additional-item">
                    <div className="additional-label">Match Type</div>
                    <div className="additional-value match-type">
                      {selectedCompany.match_type === 'company_name' ? 'Direct Company Match' : 'Industry Match'}
                    </div>
                  </div>
                )}
                
                {selectedCompany.leadSponsorType && (
                  <div className="additional-item">
                    <div className="additional-label">Company Type</div>
                    <div className="additional-value">{selectedCompany.leadSponsorType}</div>
                  </div>
                )}
                
                {selectedCompany.street1 && (
                  <div className="additional-item full-width">
                    <div className="additional-label">Address</div>
                    <div className="additional-value">
                      {selectedCompany.street1}
                      {selectedCompany.street2 && <span>, {selectedCompany.street2}</span>}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .sec-tab {
          padding: 0.5rem;
        }
        
        .company-selector {
          margin-bottom: 1.5rem;
        }
        
        .selector-label {
          font-weight: 500;
          margin-bottom: 0.5rem;
        }
        
        .company-tabs {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          border-bottom: 1px solid var(--border-color);
          padding-bottom: 0.5rem;
        }
        
        .company-tab {
          padding: 0.5rem 1rem;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9rem;
          transition: all 0.2s ease;
        }
        
        .company-tab:hover {
          border-color: var(--secondary-color);
        }
        
        .company-tab.active {
          background-color: var(--secondary-color);
          color: white;
          border-color: var(--secondary-color);
        }
        
        .company-header {
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid var(--border-color);
        }
        
        .company-name {
          font-size: 1.5rem;
          color: var(--primary-color);
          margin-bottom: 0.5rem;
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }
        
        .company-ticker {
          font-size: 1rem;
          background-color: var(--primary-color);
          color: white;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }
        
        .company-location {
          color: var(--light-text);
          font-size: 0.95rem;
        }
        
        .company-official-name {
          margin-top: 0.5rem;
          font-size: 0.9rem;
          color: var(--light-text);
        }
        
        .company-section-grid {
          display: grid;
          gap: 1.5rem;
        }
        
        .company-section {
          border: 1px solid var(--border-color);
          border-radius: 8px;
          padding: 1.25rem;
          background-color: rgba(52, 152, 219, 0.02);
        }
        
        .section-title {
          font-size: 1.1rem;
          color: var(--primary-color);
          margin-bottom: 1rem;
          padding-bottom: 0.35rem;
          border-bottom: 1px dashed var(--border-color);
        }
        
        .financials-grid, .filings-grid, .additional-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 1rem;
        }
        
        .financial-item, .filing-item, .additional-item {
          padding: 1rem;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          background-color: #fff;
        }
        
        .additional-item.full-width {
          grid-column: 1 / -1;
        }
        
        .financial-label, .filing-type, .additional-label {
          font-size: 0.85rem;
          color: var(--light-text);
          margin-bottom: 0.5rem;
        }
        
        .financial-value {
          font-size: 1.5rem;
          font-weight: 600;
          color: var(--primary-color);
          margin-bottom: 0.25rem;
        }
        
        .financial-period {
          font-size: 0.85rem;
          color: var(--light-text);
        }
        
        .filing-date {
          font-size: 1rem;
          font-weight: 500;
          margin-bottom: 0.5rem;
        }
        
        .filing-link {
          display: inline-block;
          color: var(--secondary-color);
          text-decoration: none;
          font-size: 0.9rem;
        }
        
        .filing-link:hover {
          text-decoration: underline;
        }
        
        .additional-value {
          font-size: 1rem;
        }
        
        .match-type {
          color: var(--success-color);
          font-weight: 500;
        }
        
        .no-data {
          display: flex;
          height: 200px;
          justify-content: center;
          align-items: center;
          color: var(--light-text);
          border: 1px dashed var(--border-color);
          border-radius: 6px;
        }
      `}</style>
    </div>
  );
};

export default SECTab;
