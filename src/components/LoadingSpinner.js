import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="spinner-container">
      <div className="spinner"></div>
      <p className="spinner-text">Searching across multiple databases...</p>
      <p className="spinner-subtext">This may take a moment as we gather comprehensive information</p>
      
      <style jsx>{`
        .spinner-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 3rem 0;
          background-color: rgba(255, 255, 255, 0.7);
          border-radius: 8px;
        }
        
        .spinner {
          border: 4px solid rgba(0, 0, 0, 0.1);
          width: 48px;
          height: 48px;
          border-radius: 50%;
          border-left-color: var(--secondary-color);
          animation: spin 1s linear infinite;
          margin-bottom: 1.5rem;
        }
        
        .spinner-text {
          color: var(--primary-color);
          font-size: 1.1rem;
          font-weight: 500;
          margin-bottom: 0.5rem;
        }
        
        .spinner-subtext {
          color: var(--light-text);
          font-size: 0.9rem;
        }
        
        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
