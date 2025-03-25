import React, { useState } from 'react';

const NCBITab = ({ data }) => {
  const [selectedPublication, setSelectedPublication] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [view, setView] = useState('list');
  
  // Handle empty data
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className="no-results">
        <p>No NCBI publications found.</p>
      </div>
    );
  }
  
  // Filter publications based on search term
  const filteredPublications = searchTerm.trim() 
    ? data.filter(pub => {
        const searchLower = searchTerm.toLowerCase();
        return (
          (pub.title && pub.title.toLowerCase().includes(searchLower)) ||
          (pub.abstract && pub.abstract.toLowerCase().includes(searchLower)) ||
          (pub.authors && pub.authors.toLowerCase().includes(searchLower)) ||
          (pub.journal && pub.journal.toLowerCase().includes(searchLower))
        );
      })
    : data;
  
  // Handle publication selection
  const handleSelectPublication = (pub) => {
    setSelectedPublication(pub);
    setView('detail');
  };
  
  // Format date string
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) {
        return dateStr;
      }
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long'
      });
    } catch {
      return dateStr;
    }
  };

  // Render publication list view
  const renderPublicationList = () => {
    return (
      <>
        <div className="search-container">
          <input
            type="text"
            className="form-control"
            placeholder="Search publications by title, author, or journal..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        <div className="publication-count">
          Showing {filteredPublications.length} of {data.length} publications
        </div>
        
        <div className="publication-list">
          {filteredPublications.length === 0 ? (
            <div className="no-publications">
              <p>No publications found matching your search.</p>
            </div>
          ) : (
            filteredPublications.map((pub, idx) => (
              <div 
                key={pub.pmid || idx}
                className="publication-item"
                onClick={() => handleSelectPublication(pub)}
              >
                <h4 className="publication-title">
                  {pub.title || 'Untitled Publication'}
                </h4>
                <div className="publication-meta">
                  {pub.authors && (
                    <span className="publication-authors">
                      {pub.authors.split(',').slice(0, 3).join(', ')}
                      {pub.authors.split(',').length > 3 ? ', et al.' : ''}
                    </span>
                  )}
                  {pub.journal && (
                    <span className="publication-journal">
                      {pub.journal}
                    </span>
                  )}
                  {pub.publication_date && (
                    <span className="publication-date">
                      {formatDate(pub.publication_date)}
                    </span>
                  )}
                </div>
                <p className="publication-snippet">
                  {pub.abstract ? (pub.abstract.substring(0, 200) + '...') : 'No abstract available'}
                </p>
                {pub.pmid && (
                  <div className="publication-pmid">PMID: {pub.pmid}</div>
                )}
              </div>
            ))
          )}
        </div>
      </>
    );
  };
  
  // Render publication detail view
  const renderPublicationDetail = () => {
    if (!selectedPublication) return null;
    
    return (
      <div className="publication-detail">
        <button className="back-button" onClick={() => setView('list')}>
          ← Back to publications
        </button>
        
        <h3 className="detail-title">
          {selectedPublication.title}
        </h3>
        
        <div className="detail-meta">
          {selectedPublication.authors && (
            <div className="meta-item">
              <span className="meta-label">Authors:</span>
              <span className="meta-value">{selectedPublication.authors}</span>
            </div>
          )}
          {selectedPublication.journal && (
            <div className="meta-item">
              <span className="meta-label">Journal:</span>
              <span className="meta-value">{selectedPublication.journal}</span>
            </div>
          )}
          {selectedPublication.publication_date && (
            <div className="meta-item">
              <span className="meta-label">Publication Date:</span>
              <span className="meta-value">{formatDate(selectedPublication.publication_date)}</span>
            </div>
          )}
          {selectedPublication.pmid && (
            <div className="meta-item">
              <span className="meta-label">PMID:</span>
              <span className="meta-value">
                <a 
                  href={`https://pubmed.ncbi.nlm.nih.gov/${selectedPublication.pmid}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {selectedPublication.pmid}
                </a>
              </span>
            </div>
          )}
        </div>
        
        {selectedPublication.abstract && (
          <div className="abstract-section">
            <h4 className="section-title">Abstract</h4>
            <div className="abstract-content">
              {selectedPublication.abstract}
            </div>
          </div>
        )}
        
        {selectedPublication.keywords && (
          <div className="keywords-section">
            <h4 className="section-title">Keywords</h4>
            <div className="keywords-list">
              {selectedPublication.keywords.split(',').map((keyword, idx) => (
                <span key={idx} className="keyword-item">
                  {keyword.trim()}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {selectedPublication.mesh_terms && selectedPublication.mesh_terms.length > 0 && (
          <div className="mesh-section">
            <h4 className="section-title">MeSH Terms</h4>
            <div className="mesh-list">
              {selectedPublication.mesh_terms.map((term, idx) => (
                <span key={idx} className="mesh-item">
                  {term}
                </span>
              ))}
            </div>
          </div>
        )}
        
        <div className="detail-footer">
          <a
            href={`https://pubmed.ncbi.nlm.nih.gov/${selectedPublication.pmid}`}
            target="_blank"
            rel="noopener noreferrer"
            className="pubmed-link"
          >
            View on PubMed
          </a>
        </div>
      </div>
    );
  };

  return (
    <div className="ncbi-results">
      <div className="ncbi-header">
        <h3 className="ncbi-title">NCBI Publications ({data.length})</h3>
        <p className="ncbi-description">
          Scientific publications from the National Center for Biotechnology Information database.
        </p>
      </div>
      
      {view === 'list' ? renderPublicationList() : renderPublicationDetail()}
      
      <style jsx>{`
        .ncbi-results {
          padding: 0.5rem;
        }
        
        .ncbi-header {
          margin-bottom: 1.5rem;
        }
        
        .ncbi-title {
          font-size: 1.25rem;
          margin-bottom: 0.5rem;
          color: var(--primary-color);
        }
        
        .ncbi-description {
          color: var(--light-text);
          font-size: 0.95rem;
        }
        
        .search-container {
          margin-bottom: 1.5rem;
        }
        
        .publication-count {
          font-size: 0.9rem;
          color: var(--light-text);
          margin-bottom: 1rem;
        }
        
        .publication-list {
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }
        
        .publication-item {
          padding: 1.25rem;
          border: 1px solid var(--border-color);
          border-radius: 8px;
          transition: transform 0.2s, box-shadow 0.2s;
          cursor: pointer;
        }
        
        .publication-item:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        .publication-title {
          font-size: 1.1rem;
          margin-bottom: 0.75rem;
          color: var(--primary-color);
          line-height: 1.4;
        }
        
        .publication-meta {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          margin-bottom: 0.75rem;
          font-size: 0.9rem;
          color: var(--light-text);
        }
        
        .publication-authors {
          font-weight: 500;
        }
        
        .publication-snippet {
          font-size: 0.95rem;
          line-height: 1.6;
          margin-bottom: 0.75rem;
          color: var(--text-color);
        }
        
        .publication-pmid {
          font-size: 0.85rem;
          color: var(--secondary-color);
        }
        
        .no-results, .no-publications {
          display: flex;
          height: 200px;
          justify-content: center;
          align-items: center;
          color: var(--light-text);
          border: 1px dashed var(--border-color);
          border-radius: 8px;
        }
        
        /* Detail view styles */
        .publication-detail {
          padding: 0 0.5rem;
        }
        
        .back-button {
          background: none;
          border: none;
          color: var(--secondary-color);
          cursor: pointer;
          padding: 0.5rem 0;
          margin-bottom: 1rem;
          font-size: 0.95rem;
          display: inline-flex;
          align-items: center;
        }
        
        .back-button:hover {
          text-decoration: underline;
        }
        
        .detail-title {
          font-size: 1.5rem;
          margin-bottom: 1.5rem;
          color: var(--primary-color);
          line-height: 1.4;
        }
        
        .detail-meta {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 1rem;
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid var(--border-color);
        }
        
        .meta-item {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        
        .meta-label {
          font-size: 0.85rem;
          color: var(--light-text);
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
        
        .abstract-section,
        .keywords-section,
        .mesh-section {
          margin-bottom: 1.5rem;
          padding: 1.25rem;
          border: 1px solid var(--border-color);
          border-radius: 8px;
          background-color: rgba(52, 152, 219, 0.03);
        }
        
        .section-title {
          font-size: 1.1rem;
          color: var(--primary-color);
          margin-bottom: 1rem;
        }
        
        .abstract-content {
          font-size: 0.95rem;
          line-height: 1.7;
          text-align: justify;
        }
        
        .keywords-list,
        .mesh-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        
        .keyword-item {
          background-color: rgba(52, 152, 219, 0.1);
          color: var(--secondary-color);
          padding: 0.35rem 0.75rem;
          border-radius: 20px;
          font-size: 0.85rem;
        }
        
        .mesh-item {
          background-color: rgba(46, 204, 113, 0.1);
          color: var(--success-color);
          padding: 0.35rem 0.75rem;
          border-radius: 20px;
          font-size: 0.85rem;
        }
        
        .detail-footer {
          margin-top: 2rem;
          padding-top: 1rem;
          border-top: 1px solid var(--border-color);
          text-align: center;
        }
        
        .pubmed-link {
          display: inline-block;
          padding: 0.75rem 1.5rem;
          background-color: var(--secondary-color);
          color: white;
          text-decoration: none;
          border-radius: 4px;
          transition: background-color 0.2s;
        }
        
        .pubmed-link:hover {
          background-color: #2980b9;
        }
        
        @media (max-width: 768px) {
          .detail-meta {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default NCBITab;
