import duckdb
import os
import json
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = ":memory:"):
        self.db = duckdb.connect(db_path)
        self.data_directory = "data"
        
    def load_jsonl_folder(self, folder_name: str, table_name: str):
        """Load JSONL files from a folder into a DuckDB table"""
        folder_path = os.path.join(self.data_directory, folder_name)
        
        if not os.path.exists(folder_path):
            print(f"Warning: Data folder {folder_path} not found")
            return
            
        # Get all JSONL files in the folder
        jsonl_files = [f for f in os.listdir(folder_path) if f.endswith('.jsonl')]
        
        if not jsonl_files:
            print(f"Warning: No JSONL files found in {folder_path}")
            return
            
        # Load each JSONL file
        for jsonl_file in jsonl_files:
            file_path = os.path.join(folder_path, jsonl_file)
            self.db.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} AS 
                SELECT * FROM read_json_auto('{file_path}')
            """)
            print(f"Loaded {jsonl_file} into table {table_name}")
    
    def load_all_data(self):
        """Load all SAP Order-to-Cash data"""
        # Define the data schema mapping
        data_mappings = {
            "sales_order_headers": "sales_orders",
            "outbound_delivery_headers": "outbound_deliveries", 
            "billing_document_headers": "billing_documents",
            "journal_entry_items_accounts_receivable": "journal_entries",
            "payments_accounts_receivable": "payments"
        }
        
        for folder_name, table_name in data_mappings.items():
            self.load_jsonl_folder(folder_name, table_name)
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results"""
        try:
            result = self.db.execute(query).fetchall()
            columns = [desc[0] for desc in self.db.description]
            return [dict(zip(columns, row)) for row in result]
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """Get schema information for a table"""
        try:
            result = self.db.execute(f"DESCRIBE {table_name}").fetchall()
            return [{"column": row[0], "type": row[1]} for row in result]
        except Exception as e:
            raise Exception(f"Failed to get schema for {table_name}: {str(e)}")
    
    def get_available_tables(self) -> List[str]:
        """Get list of available tables"""
        try:
            result = self.db.execute("SHOW TABLES").fetchall()
            return [row[0] for row in result]
        except Exception as e:
            raise Exception(f"Failed to get tables: {str(e)}")

# Global database instance
db_manager = DatabaseManager()
