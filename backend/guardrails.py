import re
from typing import List, Tuple

class QueryGuardrails:
    def __init__(self):
        # Define allowed topics and keywords for SAP Order-to-Cash domain
        self.allowed_keywords = [
            # SAP entities
            'sales', 'order', 'orders', 'delivery', 'deliveries', 'billing', 'invoice', 
            'payment', 'payments', 'customer', 'customers', 'accounting', 'journal',
            'document', 'documents', 'transaction', 'transactions',
            
            # SAP specific terms
            'soldto', 'party', 'amount', 'currency', 'status', 'date', 'creation',
            'shipping', 'goods', 'movement', 'cancelled', 'clearing', 'posting',
            
            # General business terms
            'revenue', 'cash', 'receivable', 'credit', 'debit', 'balance', 'due',
            'overdue', 'pending', 'completed', 'processed', 'shipped', 'billed',
            
            # Data analysis terms
            'count', 'sum', 'total', 'average', 'max', 'min', 'list', 'show', 'find',
            'filter', 'search', 'top', 'bottom', 'highest', 'lowest', 'between'
        ]
        
        # Blocked topics (off-topic)
        self.blocked_topics = [
            'politics', 'religion', 'sports', 'entertainment', 'celebrity', 'weather',
            'personal', 'health', 'medical', 'legal', 'illegal', 'hacking', 'security',
            'password', 'login', 'authentication', 'admin', 'system', 'database',
            'configuration', 'settings', 'user', 'employee', 'hr', 'payroll'
        ]
        
        # SQL injection patterns to block
        self.sql_injection_patterns = [
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'TRUNCATE\s+TABLE',
            r'ALTER\s+TABLE',
            r'CREATE\s+TABLE',
            r'INSERT\s+INTO',
            r'UPDATE\s+.*\s+SET',
            r'EXEC\s*\(',
            r'EXECUTE\s*\(',
            r'UNION\s+SELECT',
            r'--',
            r'/\*',
            r'\*/',
            r'xp_',
            r'sp_',
            r'@@',
            r'CHAR\s*\(',
            r'ASCII\s*\(',
            r'CONCAT\s*\(',
            r'SUBSTRING\s*\(',
            r'LEN\s*\(',
            r'LENGTH\s*\('
        ]
    
    def validate_query(self, query: str) -> Tuple[bool, str]:
        """
        Validate if a query is appropriate for the SAP Order-to-Cash system.
        
        Returns:
            Tuple[bool, str]: (is_valid, reason_if_invalid)
        """
        query_lower = query.lower().strip()
        
        # Check for SQL injection attempts
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False, "Query contains potentially unsafe SQL patterns"
        
        # Check for blocked topics
        for topic in self.blocked_topics:
            if topic in query_lower:
                return False, f"Query contains off-topic content: {topic}"
        
        # Check if query contains at least one allowed keyword
        has_allowed_keyword = any(keyword in query_lower for keyword in self.allowed_keywords)
        
        if not has_allowed_keyword:
            return False, "Query appears to be outside the SAP Order-to-Cash domain"
        
        # Check query length (very short queries might be too vague)
        if len(query.strip()) < 3:
            return False, "Query is too short"
        
        # Check for very long queries (might indicate attempts to bypass filters)
        if len(query) > 500:
            return False, "Query is too long"
        
        return True, "Query is valid"
    
    def get_suggested_queries(self) -> List[str]:
        """Return suggested queries that are appropriate for the system"""
        return [
            "Show me all sales orders",
            "List billing documents for customer 1000",
            "What are the total amounts for all payments?",
            "Find all deliveries with status 'completed'",
            "Show journal entries created in the last 30 days",
            "List customers with billing documents",
            "What is the total net amount for all sales orders?",
            "Find cancelled billing documents",
            "Show payments that cleared journal entries",
            "List all sales orders with delivery status"
        ]
    
    def sanitize_query(self, query: str) -> str:
        """Sanitize the query by removing potentially harmful characters"""
        # Remove excessive whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Remove any non-printable characters except newlines and tabs
        query = re.sub(r'[^\x20-\x7E\n\t]', '', query)
        
        return query

# Global guardrails instance
query_guardrails = QueryGuardrails()
