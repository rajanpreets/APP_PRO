import React from 'react';

const ErrorMessage = ({ message }) => {
  return (
    <div className="error-message">
      <div className="error-icon">⚠️</div>
      <div className="error-content">
        <h3 className="error-title">Error</h3>
        <p className="error-text">{message}</p>
      </div>
      
      <style jsx>{`
        .error-message {
          display: flex;
          background-color: rgba(231, 76, 60, 0.1);
          border-left: 4px solid var(--accent-color);
          border-radius: 4px;
          padding: 1.25rem;
          margin-bottom: 1.5rem;
        }
        
        .error-icon {
          font-size: 1.5rem;
          margin-right: 1rem;
          display: flex;
          align-items: center;
        }
        
        .error-content {
          flex-grow: 1;
        }
        
        .error-title {
          font-size: 1.1rem;
          margin-bottom: 0.5rem;
          color: var(--accent-color);
        }
        
        .error-text {
          font-size: 0.95rem;
          color: var(--text-color);
          line-height: 1.5;
        }
      `}</style>
    </div>
  );
};

export default ErrorMessage;
