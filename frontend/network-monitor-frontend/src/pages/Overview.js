import React, { useState, useEffect } from 'react';
import { metricsAPI } from '../services/api';

const Overview = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        const response = await metricsAPI.getSummary();
        if (response.success) {
          setSummary(response.data);
        } else {
          setError('Failed to load summary data');
        }
      } catch (err) {
        setError(err.error || 'Network error occurred');
        console.error('Error fetching summary:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error Loading Dashboard</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="overview-dashboard">
      <h1>Network Overview</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <h3>Total VPCs</h3>
            <span className="stat-icon">🏗️</span>
          </div>
          <div className="stat-value">
            {summary?.total_vpcs || 0}
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <h3>NAT Gateways</h3>
            <span className="stat-icon">🚪</span>
          </div>
          <div className="stat-value">
            {summary?.total_nat_gateways || 0}
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <h3>Load Balancers</h3>
            <span className="stat-icon">⚖️</span>
          </div>
          <div className="stat-value">
            {summary?.total_load_balancers || 0}
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <h3>Avg Utilization</h3>
            <span className="stat-icon">📈</span>
          </div>
          <div className="stat-value">
            {summary?.avg_utilization ? 
              `${summary.avg_utilization.toFixed(1)}%` : 
              'N/A'
            }
          </div>
        </div>
      </div>
      
      <div className="charts-section">
        <h2>Quick Metrics</h2>
        <div className="chart-placeholder">
          <p>Time-series charts will be implemented tomorrow</p>
          <div className="mock-chart">
            📊 Network Traffic Trends
          </div>
        </div>
      </div>
    </div>
  );
};

export default Overview;