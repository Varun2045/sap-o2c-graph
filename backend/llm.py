import os
from groq import Groq
from typing import Dict, Any, List
from database import db_manager

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        
    def natural_language_to_sql(self, query: str) -> str:
        """Convert natural language query to SQL using Groq"""
        
        # Get available tables and their schemas
        tables = db_manager.get_available_tables()
        schema_info = []
        
        for table in tables:
            schema = db_manager.get_table_schema(table)
            columns = [f"{col['column']} ({col['type']})" for col in schema]
            schema_info.append(f"Table {table}: {', '.join(columns)}")
        
        schema_text = "\n".join(schema_info)
        
        system_prompt = f"""
You are a SQL expert for SAP Order-to-Cash data. Convert natural language questions to SQL queries.

Available tables and schemas:
{schema_text}

Key relationships:
- billing_documents.accountingDocument → journal_entries.accountingDocument
- journal_entries.referenceDocument → billing_documents.billingDocument  
- journal_entries.clearingAccountingDocument → payments.accountingDocument
- billing_documents.soldToParty → customer ID
- sales_orders.soldToParty → customer ID

Rules:
1. Return ONLY the SQL query, no explanations
2. Use proper table and column names from the schema
3. Include JOINs when needed to connect related tables
4. Use appropriate WHERE clauses for filtering
5. Limit results to 100 rows unless specifically asked for more
6. Handle NULL values properly with IS NULL or IS NOT NULL

Example:
Question: "Show me all billing documents for customer 1000"
SQL: SELECT * FROM billing_documents WHERE soldToParty = '1000' LIMIT 100;
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {query}\nSQL:"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the response - remove any formatting
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            sql_query = sql_query.strip()
            
            return sql_query
            
        except Exception as e:
            raise Exception(f"Failed to convert natural language to SQL: {str(e)}")
    
    def execute_query_and_format_response(self, query: str) -> Dict[str, Any]:
        """Execute natural language query and format the response"""
        try:
            # Convert to SQL
            sql_query = self.natural_language_to_sql(query)
            
            # Execute the query
            results = db_manager.execute_query(sql_query)
            
            # Format response
            if not results:
                return {
                    "query": query,
                    "sql": sql_query,
                    "response": "No results found for your query.",
                    "data": [],
                    "count": 0
                }
            
            # Create a natural language summary
            summary = self._generate_summary(query, results)
            
            return {
                "query": query,
                "sql": sql_query,
                "response": summary,
                "data": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {
                "query": query,
                "sql": sql_query if 'sql_query' in locals() else "N/A",
                "response": f"Error: {str(e)}",
                "data": [],
                "count": 0
            }
    
    def _generate_summary(self, original_query: str, results: List[Dict[str, Any]]) -> str:
        """Generate a natural language summary of the results"""
        
        if not results:
            return "No results found."
        
        # Create a summary based on the results
        count = len(results)
        
        # Get column names
        columns = list(results[0].keys()) if results else []
        
        # Create a brief summary
        summary = f"Found {count} result"
        if count != 1:
            summary += "s"
            
        # Add some sample data if available
        if count > 0 and count <= 5:
            summary += ": "
            examples = []
            for result in results[:3]:
                # Create a readable representation of the first few columns
                example_parts = []
                for col in columns[:3]:
                    if col in result and result[col] is not None:
                        example_parts.append(f"{col}: {result[col]}")
                examples.append("(" + ", ".join(example_parts) + ")")
            summary += "; ".join(examples)
        elif count > 5:
            summary += f". Showing first {columns[0]} values: "
            first_values = [str(r.get(columns[0], 'N/A')) for r in results[:5]]
            summary += ", ".join(first_values)
            
        return summary

# Global LLM service instance
llm_service = LLMService()
