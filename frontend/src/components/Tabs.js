import React, { useState } from 'react';

const Tabs = ({ children, defaultTab = 0 }) => {
  const [activeTab, setActiveTab] = useState(defaultTab);

  const tabs = React.Children.toArray(children);

  return (
    <div className="tabs-container">
      {/* Tab Headers */}
      <div className="tabs-header">
        {tabs.map((tab, index) => (
          <button
            key={index}
            className={`tab ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
            type="button"
          >
            {tab.props.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="tabs-content">
        {tabs[activeTab]}
      </div>

      <style jsx>{`
        .tabs-container {
          width: 100%;
        }

        .tabs-header {
          display: flex;
          border-bottom: 2px solid #e5e7eb;
          margin-bottom: 2rem;
          background: #f8f9fa;
          border-radius: 8px 8px 0 0;
          padding: 0;
          overflow-x: auto;
        }

        .tab {
          padding: 1rem 1.5rem;
          border: none;
          background: transparent;
          cursor: pointer;
          font-size: 1rem;
          font-weight: 500;
          color: #6b7280;
          border-bottom: 3px solid transparent;
          transition: all 0.2s ease;
          white-space: nowrap;
          min-width: fit-content;
        }

        .tab:hover {
          background: rgba(255, 255, 255, 0.5);
          color: #374151;
        }

        .tab.active {
          color: var(--primary-color, #667eea);
          border-bottom-color: var(--primary-color, #667eea);
          background: white;
          position: relative;
        }

        .tab.active::after {
          content: '';
          position: absolute;
          bottom: -2px;
          left: 0;
          right: 0;
          height: 2px;
          background: var(--primary-color, #667eea);
        }

        .tabs-content {
          padding: 0;
        }

        /* Responsive design for mobile */
        @media (max-width: 768px) {
          .tabs-header {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
          }
          
          .tab {
            padding: 0.75rem 1rem;
            font-size: 0.9rem;
          }
        }
      `}</style>
    </div>
  );
};

const TabPanel = ({ children, label }) => {
  return <div className="tab-panel">{children}</div>;
};

export { Tabs, TabPanel };