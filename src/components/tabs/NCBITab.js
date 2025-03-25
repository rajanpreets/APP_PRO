import React, { useState } from 'react';

const NewsTab = ({ data }) => {
  const [activeCategory, setActiveCategory] = useState('regulatory');
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [view, setView] = useState('list');
  
  // Check if we have valid news data
  if (!data || typeof data !== 'object') {
    return (
      <div className="no-results">
        <p>No news articles found.</p>
      </div>
    );
  }

  // Get available categories from data
  const categories = ['regulatory', 'commercial', 'clinical', 'other'].filter(
    cat => Array.isArray(data[cat]) && data[cat].length > 0
  );
  
  // If no categories have articles, show empty state
  if (categories.length === 0) {
    return (
      <div className="no-results">
        <p>No news articles found.</p>
      </div>
    );
  }
  
  // Set active category to the first available one if current selection has no articles
  if (!categories.includes(activeCategory) && categories.length > 0) {
    setActiveCategory(categories[0]);
  }
  
  // Format date
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    
    try {
      const date = new Date(dateStr);
      
      // Check if the date is valid
      if (isNaN(date.getTime())) {
        return dateStr;
      }
      
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) {
        return 'Today';
      } else if (diffDays === 1) {
        return 'Yesterday';
      } else if (diffDays < 7) {
        return `${diffDays} days ago`;
      } else if (diffDays < 30) {
        const weeks = Math.floor(diffDays / 7);
        return `${weeks} ${weeks === 1 ? 'week' : 'weeks'} ago`;
      } else {
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      }
    } catch {
      return dateStr;
    }
  };
  
  // Get the summary for the current category
  const getCategorySummary = () => {
    if (data.summaries && data.summaries[activeCategory]) {
      return data.summaries[activeCategory];
    }
    return `No summary available for ${activeCategory} news.`;
  };
  
  // Get the articles for the current category
  const getCategoryArticles = () => {
    if (Array.isArray(data[activeCategory])) {
      return data[activeCategory];
    }
    return [];
  };
  
  // Format category label
  const formatCategoryLabel = (category) => {
    return category.charAt(0).toUpperCase() + category.slice(1);
  };
  
  const categoryArticles = getCategoryArticles();

  // Handle viewing article details
  const handleViewArticle = (article) => {
    setSelectedArticle(article);
    setView('detail');
  };

  // Handle going back to list view
  const handleBackToList = () => {
    setSelectedArticle(null);
    setView('list');
  };

  // Render article list view
  const renderArticleList = () => {
    return (
      <>
        <div className="news-summary">
          <p>{getCategorySummary()}</p>
        </div>
        
        <div className="news-list">
          {categoryArticles.length === 0 ? (
            <div className="no-articles">
              <p>No articles found in this category.</p>
            </div>
          ) : (
            categoryArticles.map((article, idx) => (
              <div key={idx} className="news-article" onClick={() => handleViewArticle(article)}>
                {article.url_to_image || article.thumbnail ? (
                  <div className="article-image">
                    <img 
                      src={article.url_to_image || article.thumbnail} 
                      alt={article.title}
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.style.display = 'none';
                      }}
                    />
                  </div>
                ) : null}
                
                <div className="article-content">
                  <h4 className="article-title">
                    <a 
                      href={article.url || article.link} 
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {article.title}
                    </a>
                  </h4>
                  
                  <div className="article-meta">
                    {article.source && (
                      <span className="article-source">{article.source}</span>
                    )}
                    {article.published_at || article.date ? (
                      <span className="article-date">
                        {formatDate(article.published_at || article.date)}
                      </span>
                    ) : null}
                  </div>
                  
                  {article.description || article.snippet ? (
                    <p className="article-description">{article.description || article.snippet}</p>
                  ) : null}
                  
                  {article.author && (
                    <div className="article-author">By: {article.author}</div>
                  )}

                  {article.content && (
                    <div className="has-content">
                      <span>Additional content available - click to view</span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </>
    );
  };

  // Render article detail view
  const renderArticleDetail = () => {
    if (!selectedArticle) return null;

    return (
      <div className="article-detail">
        <button className="back-button" onClick={handleBackToList}>
          ← Back to news list
        </button>
        
        <h3 className="detail-title">
          <a 
            href={selectedArticle.url || selectedArticle.link} 
            target="_blank" 
            rel="noopener noreferrer"
          >
            {selectedArticle.title}
          </a>
        </h3>
        
        <div className="detail-meta">
          {selectedArticle.source && (
            <span className="detail-source">{selectedArticle.source}</span>
          )}
          {selectedArticle.published_at || selectedArticle.date ? (
            <span className="detail-date">
              {formatDate(selectedArticle.published_at || selectedArticle.date)}
            </span>
          ) : null}
          {selectedArticle.author && (
            <span className="detail-author">By: {selectedArticle.author}</span>
          )}
        </div>
        
        {(selectedArticle.url_to_image || selectedArticle.thumbnail) && (
          <div className="detail-image">
            <img 
              src={selectedArticle.url_to_image || selectedArticle.thumbnail} 
              alt={selectedArticle.title}
              onError={(e) => {
                e.target.onerror = null;
                e.target.style.display = 'none';
              }}
            />
          </div>
        )}
        
        {selectedArticle.description || selectedArticle.snippet ? (
          <div className="detail-section">
            <h4>Summary</h4>
            <p>{selectedArticle.description || selectedArticle.snippet}</p>
          </div>
        ) : null}
        
        {selectedArticle.content ? (
          <div className="detail-section">
            <h4>Full Content</h4>
            <div className="detail-content">
              {selectedArticle.content.split('\n').map((para, idx) => (
                para.trim() ? <p key={idx}>{para}</p> : null
              ))}
            </div>
          </div>
        ) : null}
        
        {selectedArticle.full_text ? (
          <div className="detail-section">
            <h4>Additional Content</h4>
            <div className="detail-content">
              {selectedArticle.full_text.split('\n').map((para, idx) => (
                para.trim() ? <p key={idx}>{para}</p> : null
              ))}
            </div>
          </div>
        ) : null}
        
        <div className="detail-footer">
          <a 
            href={selectedArticle.url || selectedArticle.link} 
            target="_blank" 
            rel="noopener noreferrer"
            className="source-link"
          >
            Read full article on original source
          </a>
        </div>
      </div>
    );
  };

  return (
    <div className="news-results">
      <div className="news-header">
        <h3 className="news-title">Latest News</h3>
        
        {view === 'list' && (
          <div className="news-tabs">
            {categories.map(category => (
              <div 
                key={category}
                className={`news-tab ${activeCategory === category ? 'active' : ''}`}
                onClick={() => setActiveCategory(category)}
              >
                {formatCategoryLabel(category)} ({data[category].length})
              </div>
            ))}
          </div>
        )}
      </div>
      
      {view === 'list' ? renderArticleList() : renderArticleDetail()}
      
      <style jsx>{`
        .news-results {
          padding: 0.5rem;
        }
        
        .news-header {
          margin-bottom: 1.5rem;
        }
        
        .news-title {
          font-size: 1.25rem;
          margin-bottom: 1rem;
          color: var(--primary-color);
        }
        
        .news-tabs {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        
        .news-tab {
          padding: 0.5rem 1rem;
          background-color: #f5f5f5;
          border-radius: 20px;
          cursor: pointer;
          font-size: 0.9rem;
          transition: all 0.2s;
        }
        
        .news-tab:hover {
          background-color: #e0e0e0;
        }
        
        .news-tab.active {
          background-color: var(--secondary-color);
          color: white;
        }
        
        .news-summary {
          background-color: rgba(52, 152, 219, 0.1);
          border-left: 4px solid var(--secondary-color);
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 1.5rem;
          line-height: 1.6;
        }
        
        .news-list {
          display: grid;
          gap: 1.5rem;
        }
        
        .news-article {
          display: grid;
          grid-template-columns: minmax(0, 3fr) minmax(0, 7fr);
          gap: 1rem;
          padding: 1rem;
          border: 1px solid var(--border-color);
          border-radius: 8px;
          transition: transform 0.2s, box-shadow 0.2s;
          cursor: pointer;
        }
        
        .news-article:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        @media (max-width: 768px) {
          .news-article {
            grid-template-columns: 1fr;
          }
        }
        
        .article-image {
          width: 100%;
          height: 160px;
          overflow: hidden;
          border-radius: 6px;
        }
        
        .article-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        
        .article-title {
          font-size: 1.1rem;
          margin-bottom: 0.75rem;
          line-height: 1.4;
        }
        
        .article-title a {
          color: var(--primary-color);
          text-decoration: none;
          transition: color 0.2s;
        }
        
        .article-title a:hover {
          color: var(--secondary-color);
        }
        
        .article-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          margin-bottom: 0.75rem;
          font-size: 0.85rem;
          color: var(--light-text);
        }
        
        .article-source {
          font-weight: 500;
        }
        
        .article-description {
          font-size: 0.95rem;
          line-height: 1.6;
          margin-bottom: 0.75rem;
          color: var(--text-color);
        }
        
        .article-author {
          font-size: 0.85rem;
          color: var(--light-text);
          font-style: italic;
        }
        
        .has-content {
          color: var(--secondary-color);
          font-size: 0.85rem;
          font-style: italic;
          margin-top: 0.5rem;
        }
        
        .no-results, .no-articles {
          display: flex;
          height: 200px;
          justify-content: center;
          align-items: center;
          color: var(--light-text);
          border: 1px dashed var(--border-color);
          border-radius: 6px;
        }
        
        /* Detail view styles */
        .article-detail {
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
          margin-bottom: 1rem;
          color: var(--primary-color);
          line-height: 1.4;
        }
        
        .detail-title a {
          color: inherit;
          text-decoration: none;
        }
        
        .detail-title a:hover {
          text-decoration: underline;
        }
        
        .detail-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          margin-bottom: 1.5rem;
          font-size: 0.9rem;
          color: var(--light-text);
        }
        
        .detail-image {
          width: 100%;
          max-height: 400px;
          overflow: hidden;
          border-radius: 8px;
          margin-bottom: 1.5rem;
        }
        
        .detail-image img {
          width: 100%;
          height: 100%;
          object-fit: contain;
        }
        
        .detail-section {
          margin-bottom: 1.5rem;
          padding: 1.25rem;
          border: 1px solid var(--border-color);
          border-radius: 8px;
          background-color: rgba(52, 152, 219, 0.03);
        }
        
        .detail-section h4 {
          margin-bottom: 1rem;
          color: var(--primary-color);
          font-size: 1.1rem;
        }
        
        .detail-content {
          line-height: 1.7;
        }
        
        .detail-content p {
          margin-bottom: 1rem;
        }
        
        .detail-footer {
          margin-top: 2rem;
          padding-top: 1rem;
          border-top: 1px solid var(--border-color);
          text-align: center;
        }
        
        .source-link {
          display: inline-block;
          padding: 0.75rem 1.5rem;
          background-color: var(--secondary-color);
          color: white;
          text-decoration: none;
          border-radius: 4px;
          transition: background-color 0.2s;
        }
        
        .source-link:hover {
          background-color: #2980b9;
        }
      `}</style>
    </div>
  );
};

export default NewsTab;
