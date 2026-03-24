import React, { useState, useRef, useEffect } from 'react';

const ChatPanel = ({ onSendMessage, suggestedQueries }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { type: 'user', content: inputValue };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await onSendMessage(inputValue);
      console.log('Full response from backend:', response); // Debug log
      
      const botMessage = {
        type: 'bot',
        content: response.answer || 'No response received',
        data: response.data || [],
        sql: response.sql || '',
        count: response.data ? response.data.length : 0
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: `Error: ${error.message}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuery = (query) => {
    setInputValue(query);
  };

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        background: '#161b22',
        borderBottom: '1px solid #21262d',
        fontWeight: '600',
        fontSize: '16px',
        color: 'white',
        flexShrink: 0
      }}>
        Chat with Graph
      </div>

      {/* Messages - Scrollable Middle */}
      <div style={{
        flex: 1,
        padding: '16px 20px',
        overflowY: 'auto',
        backgroundColor: '#161b22',
        minHeight: 0
      }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#8b949e', marginTop: '40px' }}>
            <p style={{ marginBottom: '12px', fontSize: '16px' }}>Ask questions about your SAP Order-to-Cash data:</p>
            <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
              <p>• Sales orders, deliveries, billing documents</p>
              <p>• Payments, journal entries, customers</p>
              <p>• Revenue, amounts, status information</p>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} style={{
            marginBottom: '16px',
            display: 'flex',
            justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start'
          }}>
            <div style={{
              maxWidth: '85%',
              padding: '12px 16px',
              borderRadius: '12px',
              backgroundColor: message.type === 'user' ? '#1f6feb' : 
                             message.type === 'error' ? '#da3633' : '#21262d',
              color: 'white',
              boxShadow: '0 1px 3px rgba(0,0,0,0.12)'
            }}>
              <div style={{ fontSize: '14px', lineHeight: '1.4' }}>{message.content}</div>
              
              {message.sql && (
                <details style={{
                  marginTop: '12px',
                  backgroundColor: '#0d1117',
                  border: '1px solid #30363d',
                  borderRadius: '6px',
                  padding: '8px 12px'
                }}>
                  <summary style={{
                    fontFamily: 'ui-monospace, Consolas, monospace',
                    fontSize: '12px',
                    cursor: 'pointer',
                    fontWeight: '600',
                    outline: 'none',
                    color: '#58a6ff'
                  }}>
                    SQL Query
                  </summary>
                  <pre style={{
                    fontFamily: 'ui-monospace, Consolas, monospace',
                    fontSize: '11px',
                    margin: '8px 0 0 0',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    color: '#3fb950'
                  }}>
                    {message.sql}
                  </pre>
                </details>
              )}
              
              {message.count > 0 && (
                <div style={{ marginTop: '8px', fontSize: '12px', color: '#8b949e' }}>
                  {message.count} result{message.count !== 1 ? 's' : ''} found
                </div>
              )}
              
              {message.data && message.data.length > 0 && (
                <div style={{
                  marginTop: '12px',
                  maxHeight: '200px',
                  overflow: 'auto',
                  backgroundColor: '#0d1117',
                  borderRadius: '6px',
                  padding: '8px',
                  border: '1px solid #30363d'
                }}>
                  <table style={{ width: '100%', fontSize: '12px', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid #30363d' }}>
                        {Object.keys(message.data[0]).map(key => (
                          <th key={key} style={{ 
                            padding: '6px 8px', 
                            textAlign: 'left', 
                            fontWeight: '600',
                            fontSize: '11px',
                            color: 'white'
                          }}>
                            {key}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {message.data.slice(0, 10).map((row, idx) => (
                        <tr key={idx} style={{ 
                          backgroundColor: idx % 2 === 0 ? '#1c2128' : '#161b22',
                          borderBottom: '1px solid #21262d'
                        }}>
                          {Object.values(row).map((value, i) => (
                            <td key={i} style={{ 
                              padding: '4px 8px',
                              fontSize: '11px',
                              color: 'white'
                            }}>
                              {value !== null && value !== undefined ? String(value) : ''}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {message.data.length > 10 && (
                    <div style={{ 
                      textAlign: 'center', 
                      marginTop: '6px', 
                      fontSize: '11px',
                      fontStyle: 'italic',
                      color: '#8b949e'
                    }}>
                      ... and {message.data.length - 10} more rows
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
            <div style={{
              maxWidth: '85%',
              padding: '12px 16px',
              borderRadius: '12px',
              backgroundColor: '#21262d',
              color: 'white',
              boxShadow: '0 1px 3px rgba(0,0,0,0.12)'
            }}>
              <div style={{ fontSize: '14px' }}>Thinking...</div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Queries */}
      {suggestedQueries && suggestedQueries.length > 0 && messages.length === 0 && (
        <div style={{
          padding: '12px 20px',
          backgroundColor: '#161b22',
          borderTop: '1px solid #21262d',
          flexShrink: 0
        }}>
          <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '8px' }}>Suggested queries:</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {suggestedQueries.slice(0, 3).map((query, index) => (
              <button
                key={index}
                onClick={() => handleSuggestedQuery(query)}
                style={{
                  padding: '6px 12px',
                  fontSize: '12px',
                  backgroundColor: '#21262d',
                  border: '1px solid #30363d',
                  borderRadius: '16px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s',
                  color: 'white'
                }}
                onMouseOver={(e) => e.target.style.backgroundColor = '#30363d'}
                onMouseOut={(e) => e.target.style.backgroundColor = '#21262d'}
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form - Pinned to Bottom */}
      <form onSubmit={handleSubmit} style={{
        padding: '16px 20px',
        borderTop: '1px solid #21262d',
        backgroundColor: '#161b22',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', gap: '12px' }}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about your SAP data..."
            disabled={isLoading}
            style={{
              flex: 1,
              padding: '10px 16px',
              border: '1px solid #30363d',
              borderRadius: '8px',
              fontSize: '14px',
              outline: 'none',
              transition: 'border-color 0.2s',
              backgroundColor: '#0d1117',
              color: 'white'
            }}
            onFocus={(e) => e.target.style.borderColor = '#58a6ff'}
            onBlur={(e) => e.target.style.borderColor = '#30363d'}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            style={{
              padding: '10px 20px',
              backgroundColor: isLoading || !inputValue.trim() ? '#21262d' : '#238636',
              color: 'white',
              border: '1px solid #30363d',
              borderRadius: '8px',
              cursor: isLoading || !inputValue.trim() ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => !isLoading && inputValue.trim() && (e.target.style.backgroundColor = '#2ea043')}
            onMouseOut={(e) => !isLoading && inputValue.trim() && (e.target.style.backgroundColor = '#238636')}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatPanel;
