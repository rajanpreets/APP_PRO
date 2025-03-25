import React from 'react';

const SummaryTab = ({ summary = {}, query = '', searchType = 'drug' }) => {
  // More defensive check for summary
  if (!summary || typeof summary !== 'object' || summary === null || Object.keys(summary || {}).length === 0) {
    return (
      <div className="no-summary">
        <p>No summary available.</p>
      </div>
    );
  }

  if (summary.error) {
    return (
      <div className="summary-error">
        <p>An error occurred while generating the summary: {summary.error}</p>
      </div>
    );
  }

  // Determine which sections to display based on search type
  const getSections = () => {
    if (searchType === 'drug') {
      return [
        { id: 'summary', label: 'Overview' },
        { id: 'clinical', label: 'Clinical Information' },
        { id: 'regulatory', label: 'Regulatory Status' },
        { id: 'safety', label: 'Safety Profile' },
        { id: 'research', label: 'Recent Research' }
      ];
    } else {
      return [
        { id: 'overview', label: 'Overview' },
        { id: 'symptoms', label: 'Symptoms & Clinical Presentation' },
        { id: 'treatment', label: 'Treatment Approaches' },
        { id: 'research', label: 'Recent Research' },
        { id: 'unmet_needs', label: 'Unmet Needs & Future Directions' }
      ];
    }
  };

  const sections = getSections();

  // Function to render the content of a section
  const renderSectionContent = (sectionId) => {
    // More defensive check for section content
    if (!summary || typeof summary !== 'object' || !summary[sectionId] || typeof summary[sectionId] !== 'string') {
      return <p>No information available.</p>;
    }

    const content = summary[sectionId];
    
    // Split content by line breaks and create paragraphs
    return content.split('\n\n').map((paragraph, index) => (
      <p key={index}>{paragraph}</p>
    ));
  };

  return (
    <div className="summary-section">
      <h2 className="summary-title">
        {searchType === 'drug' ? `${query} Summary` : `${query} Summary`}
      </h2>
      
      <div className="summary-grid">
        {sections.map(section => (
          <div key={section.id} className="summary-card">
            <h3 className="summary-card-title">{section.label}</h3>
            <div className="summary-card-content">
              {renderSectionContent(section.id)}
            </div>
          </div>
        ))}
      </div>
      
      <div className="summary-footer">
        <p>This summary was generated based on data from multiple medical sources and may not be comprehensive. Always consult healthcare professionals for medical advice.</p>
      </div>
      
      <style jsx>{`
        .summary-section {
          padding: 0.5rem;
        }
        
        .summary-title {
          font-size: 1.5rem;
          margin-bottom: 1.5rem;
          color: var(--primary-color);
        }
        
        .summary-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1.5rem;
        }
        
        .summary-card {
          background-color: var(--card-background);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          padding: 1.25rem;
          height: 100%;
          transition: box-shadow 0.3s ease, transform 0.3s ease;
        }
        
        .summary-card:hover {
          box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
          transform: translateY(-2px);
        }
        
        .summary-card-title {
          font-size: 1.1rem;
          color: var(--primary-color);
          margin-bottom: 0.75rem;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid var(--border-color);
        }
        
        .summary-card-content {
          font-size: 0.95rem;
          line-height: 1.6;
        }
        
        .summary-card-content p {
          margin-bottom: 0.75rem;
        }
        
        .summary-card-content p:last-child {
          margin-bottom: 0;
        }
        
        .summary-footer {
          margin-top: 2rem;
          padding-top: 1rem;
          border-top: 1px solid var(--border-color);
          font-size: 0.85rem;
          color: var(--light-text);
          font-style: italic;
          text-align: center;
        }
        
        .no-summary, .summary-error {
          padding: 3rem 1rem;
          text-align: center;
          color: var(--light-text);
        }
        
        .summary-error {
          color: var(--accent-color);
        }
        
        @media (max-width: 768px) {
          .summary-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default SummaryTab;
