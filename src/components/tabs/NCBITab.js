import React, { useState } from 'react';

const NCBITab = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPub, setSelectedPub] = useState(null);

  // Handle empty or error data
  if (!data || (Array.isArray(data) && data.length === 0)) {
    return (
      <div className="no-data">
        <p>No publications found.</p>
      </div>
    );
  }

  // Convert to array if it's not already
  const dataArray = Array.isArray(data) ? data : [data];

  // Filter publications by search term
  const filteredPubs = searchTerm.trim() 
    ? dataArray.filter(pub => {
        const searchLower = searchTerm.toLowerCase();
        return (
          (pub.title && pub.title.toLowerCase().includes(searchLower)) ||
          (pub.abstract && pub.abstract.toLowerCase().includes(searchLower)) ||
          (pub.authors && pub.authors.toLowerCase().includes(searchLower)) ||
          (pub.journal && pub.journal.toLowerCase().includes(searchLower))
        );
      })
    : dataArray;

  // Format date
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    
    try {
      const parts = dateStr.split('/');
      if (parts.length >= 2) {
        const year = parts[0];
        const month = parts[1];
        const months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${months[parseInt(month)]} ${year}`;
      }
      return dateStr;
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="ncbi-tab">
      <div className="ncbi-header">
        <h3 className="ncbi-title">NCBI Publications ({dataArray.length})</h3>
        
        <div className="ncbi-search">
          <input
            type="text"
            className="form-control"
            placeholder="Search publications..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
      
      <div className="ncbi-content">
        <div className="pub-list">
          {filteredPubs.length === 0 ? (
            <div className="no-pubs">
              <p>No publications found matching your search.</p>
            </div>
          ) : (
            <div className="pubs-container">
              {filteredPubs.map((pub, idx) => (
                <div 
                  key={pub.pmid || idx}
                  className={`pub-item ${selectedPub === pub ? 'active' : ''}`}
                  onClick={() => setSelectedPub(pub)}
                >
                  <h4 className="pub-title">
                    {pub.title || 'Untitled Publication'}
                  </h4>
                  <div className="pub-meta">
                    {pub.authors && (
                      <span className="pub-authors">
                        {pub.authors.split(',').slice(0, 3).join(', ')}
                        {pub.authors.split(',').length > 3 ? ', et al.' : ''}
                      </span>
                    )}
                    {pub.journal && (
                      <span className="pub-journal">
                        {pub.journal}
                      </span>
                    )}
                    {pub.publication_date && (
                      <span className="pub-date">
                        {formatDate(pub.publication_date)}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="pub-details">
          {selectedPub ? (
            <div className="details-content">
              <h3 className="details-title">
                {selectedPub.title}
              </h3>
              
              <div className="details-meta">
                {selectedPub.authors && (
                  <div className="meta-item">
                    <span className="meta-label">Authors:</span>
                    <span className="meta-value">{selectedPub.authors}</span>
                  </div>
                )}
                {selectedPub.journal && (
                  <div className="meta-item">
                    <span className="meta-label">Journal:</span>
                    <span className="meta-value">{selectedPub.journal}</span>
                  </div>
                )}
                {selectedPub.publication_date && (
                  <div className="meta-item">
                    <span className="meta-label">Publication Date:</span>
                    <span className="meta-value">{formatDate(selectedPub.publication_date)}</span>
                  </div>
                )}
                {selectedPub.pmid && (
                  <div className="meta-item">
                    <span className="meta-label">PMID:</span>
                    <span className="meta-value">
                      <a 
                        href={`https://pubmed.ncbi.nlm.nih.gov/${selectedPub.pmid}`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {selectedPub.pmid}
                      </a>
                    </span>
                  </div>
                )}
              </div>
              
              {selectedPub.abstract && (
                <div className="abstract-section">
                  <h4 className="section-title">Abstract</h4>
                  <div className="abstract-content">
                    {selectedPub.abstract}
                  </div>
                </div>
              )}
              
              {selectedPub.keywords && (
                <div className="keywords-section">
                  <h4 className="section-title">Keywords</h4>
                  <div className="keywords-list">
                    {selectedPub.keywords.split(',').map((keyword, idx) => (
                      <span key={idx} className="keyword-item">
                        {keyword.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedPub.mesh_terms && selectedPub.mesh_terms.length > 0 && (
                <div className="mesh-section">
                  <h4 className="section-title">MeSH Terms</h4>
                  <div className="mesh-list">
                    {selectedPub.mesh_terms.map((term, idx) => (
                      <span key={idx} className="mesh-item">
                        {term}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="no-selection">
              <p>Select a publication to view details</p>
            </div>
          )}
        </div>
      </div>
      
      <style jsx>{`
        .ncbi-tab {
          padding: 0.5rem;
        }
        
        .ncbi-header {
          margin-bottom: 1.5rem;
        }
        
        .ncbi-title {
          font-size: 1.25rem;
          margin-bottom: 1rem;
          color: var(--primary-color);
        }
        
        .ncbi-search {
          margin-bottom: 1.5rem;
        }
        
        .ncbi-content {
          display: grid;
          grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr);
          gap: 1.5rem;
        }
        
        .pub-list {
          border-right: 1px solid var(--border-color);
          max-height: 600px;
        }
        
        .pubs-container {
          overflow-y: auto;
          max-height: 600px;
          padding-right: 1rem;
        }
        
        .pub-item {
          padding: 1rem;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          margin-bottom: 1rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .pub-item:hover {
          border-color: var(--secondary-color);
        }
        
        .pub-item.active {
          border-color: var(--secondary-color);
          background-color: rgba(52, 152, 219, 0.05);
        }
        
        .pub-title {
          font-size: 1rem;
          margin-bottom: 0.5rem;
          color: var(--primary-color);
          line-height: 1.4;
        }
        
        .pub-meta {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          font-size: 0.85rem;
          color: var(--light-text);
        }
        
        .pub-details {
          overflow-y: auto;
          max-height: 600px;
        }
        
        .details-title {
          font-size: 1.25rem;
          margin-bottom: 1rem;
          color: var(--primary-color);
          line-height: 1.4;
        }
        
        .details-meta {
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid var(--border-color);
        }
        
        .meta-item {
          margin-bottom: 0.5rem;
        }
        
        .meta-label {
          font-size: 0.85rem;
          font-weight: 500;
          color: var(--primary-color);
          margin-right: 0.5rem;
        }
        
        .meta-value {
          font-size: 0.95rem;
        }
        
        .meta-value a {
          color: var(--secondary-color);
          text-decoration: none;
        }
        
        .meta-value a:hover {
          text-decoration: underline;
        }
        
        .abstract-section {
          margin-bottom: 1.5rem;
        }
        
        .section-title {
          font-size: 1.1rem;
          color: var(--primary-color);
          margin-bottom: 0.75rem;
          padding-bottom: 0.35rem;
          border-bottom: 1px dashed var(--border-color);
        }
        
        .abstract-content {
          font-size: 0.95rem;
          line-height: 1.6;
          text-align: justify;
        }
        
        .keywords-list, .mesh-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }
        
        .keyword-item {
          background-color: rgba(52, 152, 219, 0.1);
          padding: 0.35rem 0.75rem;
          border-radius: 20px;
          font-size: 0.85rem;
          color: var(--secondary-color);
        }
        
        .mesh-item {
          background-color: rgba(46, 204, 113, 0.1);
          padding: 0.35rem 0.75rem;
          border-radius: 20px;
          font-size: 0.85rem;
          color: var(--success-color);
        }
        
        .no-pubs, .no-selection, .no-data {
          display: flex;
          height: 200px;
          justify-content: center;
          align-items: center;
          color: var(--light-text);
          border: 1px dashed var(--border-color);
          border-radius: 6px;
        }
        
        @media (max-width: 992px) {
          .ncbi-content {
            grid-template-columns: 1fr;
          }
          
          .pub-list {
            border-right: none;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 1.5rem;
            padding-bottom: 1.5rem;
          }
          
          .pubs-container {
            max-height: 300px;
          }
        }
      `}</style>
    </div>
  );
};

export default NCBITab;
