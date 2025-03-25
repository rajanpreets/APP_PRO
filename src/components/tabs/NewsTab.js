import React, { useState } from 'react';

const NewsTab = ({ data }) => {
  const [activeCategory, setActiveCategory] = useState('all');
  
  // Handle empty or error data
  if (!data || !Object.keys(data).length) {
    return (
      <div className="no-data">
        <p>No news articles found.</p>
      </div>
    );
  }
  
  // Prepare data structure
  const categories = ['regulatory', 'commercial', 'clinical', 'other'];
  const allArticles = [
    ...getArticlesFromCategory('regulatory'),
    ...getArticlesFromCategory('commercial'),
    ...getArticlesFromCategory('clinical'),
    ...getArticlesFromCategory('other')
  ];
  
  // Helper function to get articles from a category
  function getArticlesFromCategory(category) {
    if (!data[category] || !Array.isArray(data[category])) return [];
    return data[category].map(article => ({...article, category}));
  }
  
  // Get current articles to display
  const currentArticles = activeCategory === 'all' 
    ? allArticles 
    : getArticlesFromCategory(activeCategory);
    
  // Format date
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return dateStr;
      
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
    <div className="news-tab">
      <div className="news-header">
        <h3 className="news-title">Latest News</h3>
        
        <div className="news-categories">
          <button 
            className={`category-btn ${activeCategory === 'all' ? 'active' : ''}`}
            onClick={() => setActiveCategory('all')}
          >
            All ({allArticles.length})
          </button>
          
          {categories.map(category => {
            const count = getArticlesFromCategory(category).length;
            if (count === 0) return null;
            
            return (
              <button 
                key={category}
                className={`category-btn ${activeCategory === category ? 'active' : ''}`}
                onClick={() => setActiveCategory(category)}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)} ({count})
              </button>
            );
          })}
        </div>
      </div>
      
      {data.summaries && data.summaries[activeCategory === 'all' ? 'regulatory' : activeCategory] && (
        <div className="news-summary">
          <p>{data.summaries[activeCategory === 'all' ? 'regulatory' : activeCategory]}</p>
        </div>
      )}
      
      <div className="news-articles">
        {currentArticles.length === 0 ? (
          <div className="no-articles">
            <p>No articles found in this category.</p>
          </div>
        ) : (
          currentArticles.map((article, idx) => (
            <div key={idx} className="news-article">
              {article.thumbnail && (
                <div className="article-image">
                  <img src={article.thumbnail} alt={article.title} />
                </div>
              )}
              
              <div className="article-content">
                <div className={`article-category ${article.category}`}>
                  {article.category.charAt(0).toUpperCase() + article.category.slice(1)}
                </div>
                
                <h4 className="article-title">
                  <a 
                    href={article.link} 
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {article.title}
                  </a>
                </h4>
                
                <div className="article-meta">
                  {article.source && (
                    <span className="article-source">{article.source}</span>
                  )}
                  {article.date && (
                    <span className="article-date">{formatDate(article.date)}</span>
                  )}
                </div>
                
                {article.snippet && (
                  <p className="article-description">{article.snippet}</p>
                )}
                
                {article.content && (
                  <p className="article-content-preview">
                    {article.content.length > 200 
                      ? article.content.substring(0, 200) + '...' 
                      : article.content}
                  </p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
      
      <style jsx>{`
        .news-tab {
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
        
        .news-categories {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        
        .category-btn {
          background-color: #f5f5f5;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .category-btn:hover {
          background-color: #e0e0e0;
        }
        
        .category-btn.active {
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
        
        .news-articles {
          display: grid;
          gap: 1.5rem;
        }
        
        .news-article {
          display: grid;
          grid-template-columns: minmax(0, 1fr) minmax(0, 3fr);
          gap: 1rem;
          padding: 1rem;
          border: 1px solid var(--border-color);
          border-radius: 8px;
          transition: all 0.2s ease;
        }
        
        .news-article:hover {
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
          transform: translateY(-2px);
        }
        
        .article-image {
          width: 100%;
          height: 120px;
          overflow: hidden;
          border-radius: 6px;
        }
        
        .article-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        
        .article-content {
          display: flex;
          flex-direction: column;
        }
        
        .article-category {
          display: inline-block;
          font-size: 0.8rem;
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
        
        .article-category.regulatory {
          background-color: rgba(231, 76, 60, 0.1);
          color: #e74c3c;
        }
        
        .article-category.commercial {
          background-color: rgba(46, 204, 113, 0.1);
          color: #2ecc71;
        }
        
        .article-category.clinical {
          background-color: rgba(52, 152, 219, 0.1);
          color: #3498db;
        }
        
        .article-category.other {
          background-color: rgba(155, 89, 182, 0.1);
          color: #9b59b6;
        }
        
        .article-title {
          font-size: 1.1rem;
          margin-bottom: 0.5rem;
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
        
        .article-description, .article-content-preview {
          font-size: 0.95rem;
          line-height: 1.6;
          margin-bottom: 0.5rem;
          color: var(--text-color);
        }
        
        .no-articles, .no-data {
          display: flex;
          height: 200px;
          justify-content: center;
          align-items: center;
          color: var(--light-text);
          border: 1px dashed var(--border-color);
          border-radius: 6px;
        }
        
        @media (max-width: 768px) {
          .news-article {
            grid-template-columns: 1fr;
          }
          
          .article-image {
            height: 180px;
          }
        }
      `}</style>
    </div>
  );
};

export default NewsTab;
