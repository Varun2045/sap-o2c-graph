import React, { useState, useEffect } from 'react';
import GraphViewer from './components/GraphViewer';
import ChatPanel from './components/ChatPanel';

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [suggestedQueries, setSuggestedQueries] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Fetch graph data on component mount
  useEffect(() => {
    fetchGraphData();
    fetchSuggestedQueries();
  }, []);

  const fetchGraphData = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_URL}/graph`);
      if (response.ok) {
        const data = await response.json();
        // Convert edges to links for react-force-graph-2d
        const graphData = {
          nodes: data.nodes || [],
          links: (data.edges || []).map(edge => ({
            ...edge,
            source: edge.source,
            target: edge.target
          }))
        };
        setGraphData(graphData);
      } else {
        console.error('Failed to fetch graph data');
      }
    } catch (error) {
      console.error('Error fetching graph data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSuggestedQueries = async () => {
    try {
      const response = await fetch(`${API_URL}/suggested-queries`);
      if (response.ok) {
        const queries = await response.json();
        setSuggestedQueries(queries);
      }
    } catch (error) {
      console.error('Error fetching suggested queries:', error);
      // Fallback suggested queries
      setSuggestedQueries([
        "Show me all sales orders",
        "List billing documents for customer 1000",
        "What are the total amounts for all payments?",
        "Find all deliveries with status 'completed'"
      ]);
    }
  };

  const handleSendMessage = async (message) => {
    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: message }),
      });

      if (!response.ok) {
        throw new Error('Failed to send query');
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    console.log('Node clicked:', node);
  };

  const handleNodeHover = (node) => {
    // Optional: Add hover effects
  };

  return (
    <div style={{ 
      width: '100vw', 
      height: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <header style={{
        background: '#0d1117',
        color: 'white',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 1px 0 0 #21262d',
        zIndex: 1000,
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Graph Icon */}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="8" cy="8" r="3" fill="#58a6ff"/>
            <circle cx="16" cy="8" r="3" fill="#58a6ff"/>
            <circle cx="12" cy="16" r="3" fill="#58a6ff"/>
            <path d="M8 8L16 8M16 8L12 16M8 8L12 16" stroke="#58a6ff" strokeWidth="1.5"/>
          </svg>
          <div>
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>Order-to-Cash Intelligence</h1>
            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#8b949e' }}>
              SAP Data Graph Explorer
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {/* Live Indicator */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '8px',
              height: '8px',
              backgroundColor: '#238636',
              borderRadius: '50%',
              animation: 'pulse 2s infinite'
            }}></div>
            <span style={{ fontSize: '14px', color: '#8b949e', fontWeight: '500' }}>Live</span>
          </div>
          <button
            onClick={fetchGraphData}
            disabled={isLoading}
            style={{
              padding: '8px 16px',
              backgroundColor: isLoading ? '#21262d' : '#238636',
              color: 'white',
              border: '1px solid #30363d',
              borderRadius: '8px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => !isLoading && (e.target.style.backgroundColor = '#2ea043')}
            onMouseOut={(e) => !isLoading && (e.target.style.backgroundColor = '#238636')}
          >
            {isLoading ? 'Loading...' : 'Refresh Graph'}
          </button>
        </div>
      </header>

      {/* Add pulse animation */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>

      {/* Main Content - Full Height Flex Row */}
      <div style={{ 
        flex: 1, 
        display: 'flex', 
        overflow: 'hidden',
        minHeight: 0
      }}>
        {/* Graph Viewer - 65% width */}
        <div style={{ 
          width: '65%', 
          position: 'relative',
          backgroundColor: '#0d1117',
          overflow: 'hidden',
          borderRight: '1px solid #21262d'
        }}>
          <GraphViewer 
            data={graphData}
            onNodeClick={handleNodeClick}
            onNodeHover={handleNodeHover}
          />
          
          {/* Professional Color Legend */}
          <div style={{
            position: 'absolute',
            bottom: '20px',
            left: '20px',
            background: '#161b22',
            padding: '16px',
            border: '1px solid #21262d',
            borderRadius: '8px',
            fontSize: '12px',
            color: 'white',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)'
          }}>
            <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: '600' }}>Node Types</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ 
                  width: '14px', 
                  height: '14px', 
                  backgroundColor: '#FF6B6B', 
                  borderRadius: '50%',
                  boxShadow: '0 0 4px rgba(255, 107, 107, 0.5)'
                }}></div>
                <span>Customer</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ 
                  width: '14px', 
                  height: '14px', 
                  backgroundColor: '#4ECDC4', 
                  borderRadius: '50%',
                  boxShadow: '0 0 4px rgba(78, 205, 196, 0.5)'
                }}></div>
                <span>Sales Order</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ 
                  width: '14px', 
                  height: '14px', 
                  backgroundColor: '#45B7D1', 
                  borderRadius: '50%',
                  boxShadow: '0 0 4px rgba(69, 183, 209, 0.5)'
                }}></div>
                <span>Billing Document</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ 
                  width: '14px', 
                  height: '14px', 
                  backgroundColor: '#96CEB4', 
                  borderRadius: '50%',
                  boxShadow: '0 0 4px rgba(150, 206, 180, 0.5)'
                }}></div>
                <span>Delivery</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ 
                  width: '14px', 
                  height: '14px', 
                  backgroundColor: '#FFEAA7', 
                  borderRadius: '50%',
                  boxShadow: '0 0 4px rgba(255, 234, 167, 0.5)'
                }}></div>
                <span>Journal Entry</span>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Panel - 35% width */}
        <div style={{ 
          width: '35%', 
          backgroundColor: '#161b22',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          <ChatPanel 
            onSendMessage={handleSendMessage}
            suggestedQueries={suggestedQueries}
          />
        </div>
      </div>

      {/* Selected Node Details Modal */}
      {selectedNode && (
        <div style={{
          position: 'fixed',
          top: '0',
          left: '0',
          right: '0',
          bottom: '0',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 2000
        }}>
          <div style={{
            background: 'white',
            padding: '24px',
            borderRadius: '12px',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            maxWidth: '500px',
            maxHeight: '80vh',
            overflow: 'auto',
            margin: '20px'
          }}>
            <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#1a202c' }}>{selectedNode.label}</h3>
            <p style={{ marginBottom: '16px', color: '#4a5568' }}>
              <strong>Type:</strong> {selectedNode.type}
            </p>
            {selectedNode.data && (
              <div>
                <strong style={{ color: '#2d3748' }}>Details:</strong>
                <div style={{ 
                  marginTop: '12px', 
                  padding: '12px', 
                  backgroundColor: '#f7fafc', 
                  borderRadius: '6px',
                  fontSize: '14px'
                }}>
                  {Object.entries(selectedNode.data).map(([key, value]) => (
                    <div key={key} style={{ marginBottom: '8px' }}>
                      <strong style={{ color: '#2d3748' }}>{key}:</strong>{' '}
                      <span style={{ color: '#4a5568' }}>
                        {value !== null && value !== undefined ? String(value) : 'N/A'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <button
              onClick={() => setSelectedNode(null)}
              style={{
                marginTop: '20px',
                padding: '10px 20px',
                backgroundColor: '#e53e3e',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                width: '100%'
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
