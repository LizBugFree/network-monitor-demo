import React from 'react';
import './Layout.css';

const Layout = ({ children }) => {
  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <h1 className="app-title">Network Monitor</h1>
          <div className="header-status">
            <span className="status-indicator active"></span>
            <span>Connected</span>
          </div>
        </div>
      </header>
      
      <nav className="sidebar">
        <div className="nav-menu">
          <a href="/" className="nav-item active">
            <span className="nav-icon">🏠</span>
            Overview
          </a>
          <a href="/topology" className="nav-item">
            <span className="nav-icon">🗺️</span>
            Topology
          </a>
          <a href="/metrics" className="nav-item">
            <span className="nav-icon">📊</span>
            Metrics
          </a>
          <a href="/costs" className="nav-item">
            <span className="nav-icon">💰</span>
            Costs
          </a>
        </div>
      </nav>
      
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout;