# SAP Order-to-Cash Graph-Based Data Modeling and Query System

A comprehensive graph-based data visualization and natural language query system for SAP Order-to-Cash datasets, built with FastAPI, DuckDB, Groq LLM, and React.

## � **Live Demo**
**🚀 Production URL**: https://sap-o2c-graph-production-c7ad.up.railway.app/

Explore the interactive SAP Order-to-Cash dashboard with:
- 📊 **Graph Visualization**: Interactive node-based data exploration
- 💬 **Natural Language Queries**: Ask questions about your SAP data in plain English
- 🎨 **Enterprise UI**: GitHub-inspired dark theme dashboard
- ⚡ **Real-time Analysis**: Instant SQL generation and results

## �️ Architecture

### Backend Stack
- **FastAPI**: REST API with CORS support
- **DuckDB**: High-performance analytical database for JSONL data
- **Groq API**: Llama-3.3-70B for natural language to SQL conversion
- **Python**: Core backend language

### Frontend Stack
- **React**: Modern UI framework
- **Vite**: Fast development build tool
- **react-force-graph-2d**: Interactive graph visualization
- **HTML5/CSS3**: Responsive design

## 📁 Project Structure

```
project/
├── backend/
│   ├── main.py              # FastAPI application with CORS
│   ├── database.py          # DuckDB setup and JSONL loading
│   ├── graph.py             # Graph building from database
│   ├── llm.py               # Groq LLM integration
│   ├── guardrails.py        # Query validation and safety
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── GraphViewer.jsx    # Graph visualization component
│   │   │   └── ChatPanel.jsx      # Chat interface component
│   │   └── App.jsx          # Main React application
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Groq API key

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Start the backend server**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:3000`

## 📊 Data Schema

The system processes SAP Order-to-Cash data from JSONL files organized by entity:

### Entity Tables
- **sales_order_headers**: Sales orders with customer and amount information
- **outbound_delivery_headers**: Delivery documents and shipping status
- **billing_document_headers**: Invoices and billing information
- **journal_entry_items_accounts_receivable**: Financial postings
- **payments_accounts_receivable**: Payment transactions

### Key Relationships
- `BillingDocument.accountingDocument` → `JournalEntry.accountingDocument`
- `JournalEntry.referenceDocument` → `BillingDocument.billingDocument`
- `JournalEntry.clearingAccountingDocument` → `Payment.accountingDocument`
- `BillingDocument.soldToParty` → Customer
- `SalesOrder.soldToParty` → Customer

## 🔧 API Endpoints

### Core Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /graph` - Retrieve graph data (nodes and edges)
- `POST /query` - Natural language query processing
- `GET /suggested-queries` - Get suggested queries

### Query Endpoint
```json
POST /query
{
  "query": "Show me all sales orders for customer 1000"
}
```

Response:
```json
{
  "query": "Show me all sales orders for customer 1000",
  "sql": "SELECT * FROM sales_orders WHERE soldToParty = '1000' LIMIT 100",
  "response": "Found 15 results showing sales orders for customer 1000",
  "data": [...],
  "count": 15
}
```

## 🎨 Features

### Graph Visualization
- **Interactive nodes**: Click to view detailed information
- **Color-coded entities**: Different colors for customers, orders, deliveries, etc.
- **Relationship mapping**: Visual connections between related documents
- **Hover effects**: Highlight connected nodes and edges
- **Zoom and pan**: Navigate large graphs easily

### Natural Language Queries
- **Intelligent SQL generation**: Converts natural language to optimized SQL
- **Context-aware responses**: Understands SAP business terminology
- **Safety guardrails**: Prevents SQL injection and off-topic queries
- **Result formatting**: Presents data in readable tables and summaries

### User Interface
- **Responsive design**: Works on desktop and tablet devices
- **Real-time updates**: Live graph updates and query results
- **Intuitive chat**: Suggested queries and conversation history
- **Professional styling**: Modern, clean interface

## 🔒 Security Features

### Query Guardrails
- **SQL injection prevention**: Blocks dangerous SQL patterns
- **Topic filtering**: Restricts to SAP Order-to-Cash domain
- **Input validation**: Sanitizes user inputs
- **Rate limiting**: Prevents abuse (can be implemented)

### Data Safety
- **Read-only operations**: No data modification through queries
- **Limited result sets**: Prevents excessive data exposure
- **Error handling**: Graceful failure without system exposure

## 🛠️ Development

### Adding New Data Sources
1. Place JSONL files in appropriate folders under `data/`
2. Update table mappings in `database.py`
3. Modify graph building logic in `graph.py` if needed
4. Update LLM schema information in `llm.py`

### Extending Query Capabilities
1. Add new keywords to `guardrails.py`
2. Update system prompts in `llm.py`
3. Add new API endpoints in `main.py`

### Customizing Graph Visualization
1. Modify node colors and shapes in `GraphViewer.jsx`
2. Update layout algorithms and physics parameters
3. Add new interaction patterns and animations

## 📈 Performance Considerations

### Database Optimization
- **DuckDB**: Uses columnar storage for analytical queries
- **In-memory processing**: Fast response times for typical datasets
- **Lazy loading**: Graph data loaded on demand

### Frontend Optimization
- **Virtual scrolling**: Handles large result sets efficiently
- **Debounced queries**: Prevents excessive API calls
- Component memoization: Reduces unnecessary re-renders

## 🚀 Deployment

### Railway (Production)
The application is deployed on Railway at: https://sap-o2c-graph-production-c7ad.up.railway.app/

**Deployment Setup**:
- **Backend**: FastAPI with Railway Procfile configuration
- **Environment Variables**: GROQ_API_KEY configured in Railway
- **Database**: DuckDB with JSONL data loading
- **Frontend**: React app served from backend static files

### Local Development
Follow the Quick Start guide above to run the application locally.

### Environment Configuration
- **Backend**: Set `GROQ_API_KEY` in `.env` file
- **Frontend**: Set `VITE_API_URL` in `.env` file (defaults to `http://localhost:8000`)

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Python version (3.8+ required)
   - Verify all dependencies installed
   - Ensure Groq API key is set correctly

2. **Frontend connection errors**
   - Ensure backend is running on port 8000
   - Check CORS configuration in main.py
   - Verify no firewall blocking the connection

3. **No graph data displayed**
   - Check if data files are in correct format
   - Verify JSONL file structure
   - Check backend logs for loading errors

4. **Query errors**
   - Verify Groq API key is valid
   - Check query guardrails for blocked content
   - Review SQL generation in backend logs

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section above
- Review the code comments for implementation details
- Verify all prerequisites are met
