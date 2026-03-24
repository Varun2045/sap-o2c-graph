from typing import Dict, List, Any, Tuple
from database import db_manager

class GraphBuilder:
    def __init__(self):
        self.nodes = []
        self.edges = []
        
    def build_graph_from_data(self) -> Dict[str, Any]:
        """Build graph structure from SAP Order-to-Cash data"""
        self.nodes = []
        self.edges = []
        
        # Add customer nodes (from business_partners if available, or from documents)
        self._add_customer_nodes()
        
        # Add document nodes
        self._add_sales_order_nodes()
        self._add_delivery_nodes() 
        self._add_billing_nodes()
        self._add_journal_entry_nodes()
        self._add_payment_nodes()
        
        # Add relationships
        self._add_document_relationships()
        
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }
    
    def _add_customer_nodes(self):
        """Add customer nodes to the graph"""
        try:
            # Get unique customers from billing documents
            customers = db_manager.execute_query("""
                SELECT DISTINCT soldToParty as customer_id, soldToParty as customer_name
                FROM billing_documents
                WHERE soldToParty IS NOT NULL
            """)
            
            for customer in customers:
                self.nodes.append({
                    "id": f"customer_{customer['customer_id']}",
                    "label": f"Customer: {customer['customer_id']}",
                    "type": "customer",
                    "data": customer
                })
        except Exception as e:
            print(f"Error adding customer nodes: {e}")
    
    def _add_sales_order_nodes(self):
        """Add sales order nodes"""
        try:
            orders = db_manager.execute_query("""
                SELECT salesOrder, soldToParty, totalNetAmount, overallDeliveryStatus, 
                       transactionCurrency, creationDate
                FROM sales_orders
            """)
            
            for order in orders:
                self.nodes.append({
                    "id": f"sales_order_{order['salesOrder']}",
                    "label": f"Sales Order: {order['salesOrder']}",
                    "type": "sales_order",
                    "data": order
                })
        except Exception as e:
            print(f"Error adding sales order nodes: {e}")
    
    def _add_delivery_nodes(self):
        """Add outbound delivery nodes"""
        try:
            deliveries = db_manager.execute_query("""
                SELECT deliveryDocument, shippingPoint, overallGoodsMovementStatus, creationDate
                FROM outbound_deliveries
            """)
            
            for delivery in deliveries:
                self.nodes.append({
                    "id": f"delivery_{delivery['deliveryDocument']}",
                    "label": f"Delivery: {delivery['deliveryDocument']}",
                    "type": "delivery",
                    "data": delivery
                })
        except Exception as e:
            print(f"Error adding delivery nodes: {e}")
    
    def _add_billing_nodes(self):
        """Add billing document nodes"""
        try:
            bills = db_manager.execute_query("""
                SELECT billingDocument, accountingDocument, soldToParty, totalNetAmount,
                       billingDocumentIsCancelled, cancelledBillingDocument
                FROM billing_documents
            """)
            
            for bill in bills:
                self.nodes.append({
                    "id": f"billing_{bill['billingDocument']}",
                    "label": f"Billing: {bill['billingDocument']}",
                    "type": "billing",
                    "data": bill
                })
        except Exception as e:
            print(f"Error adding billing nodes: {e}")
    
    def _add_journal_entry_nodes(self):
        """Add journal entry nodes"""
        try:
            entries = db_manager.execute_query("""
                SELECT accountingDocument, referenceDocument, customer, 
                       amountInTransactionCurrency, clearingAccountingDocument, postingDate
                FROM journal_entries
            """)
            
            for entry in entries:
                self.nodes.append({
                    "id": f"journal_{entry['accountingDocument']}",
                    "label": f"Journal: {entry['accountingDocument']}",
                    "type": "journal_entry",
                    "data": entry
                })
        except Exception as e:
            print(f"Error adding journal entry nodes: {e}")
    
    def _add_payment_nodes(self):
        """Add payment nodes"""
        try:
            payments = db_manager.execute_query("""
                SELECT accountingDocument, customer, amountInTransactionCurrency,
                       clearingAccountingDocument
                FROM payments
            """)
            
            for payment in payments:
                self.nodes.append({
                    "id": f"payment_{payment['accountingDocument']}",
                    "label": f"Payment: {payment['accountingDocument']}",
                    "type": "payment",
                    "data": payment
                })
        except Exception as e:
            print(f"Error adding payment nodes: {e}")
    
    def _add_document_relationships(self):
        """Add edges between related documents"""
        try:
            # Billing to Journal Entry (accountingDocument)
            billing_journal = db_manager.execute_query("""
                SELECT b.billingDocument, b.accountingDocument
                FROM billing_documents b
                WHERE b.accountingDocument IS NOT NULL
            """)
            
            for row in billing_journal:
                self.edges.append({
                    "source": f"billing_{row['billingDocument']}",
                    "target": f"journal_{row['accountingDocument']}",
                    "label": "creates",
                    "type": "billing_to_journal"
                })
            
            # Journal Entry to Billing (referenceDocument)
            journal_billing = db_manager.execute_query("""
                SELECT j.accountingDocument, j.referenceDocument
                FROM journal_entries j
                WHERE j.referenceDocument IS NOT NULL
            """)
            
            for row in journal_billing:
                self.edges.append({
                    "source": f"journal_{row['accountingDocument']}",
                    "target": f"billing_{row['referenceDocument']}",
                    "label": "references",
                    "type": "journal_to_billing"
                })
            
            # Journal Entry to Payment (clearingAccountingDocument)
            journal_payment = db_manager.execute_query("""
                SELECT j.accountingDocument, j.clearingAccountingDocument
                FROM journal_entries j
                WHERE j.clearingAccountingDocument IS NOT NULL
            """)
            
            for row in journal_payment:
                self.edges.append({
                    "source": f"journal_{row['accountingDocument']}",
                    "target": f"payment_{row['clearingAccountingDocument']}",
                    "label": "cleared_by",
                    "type": "journal_to_payment"
                })
            
            # Customer relationships
            # Sales Order to Customer
            so_customer = db_manager.execute_query("""
                SELECT salesOrder, soldToParty
                FROM sales_orders
                WHERE soldToParty IS NOT NULL
            """)
            
            for row in so_customer:
                self.edges.append({
                    "source": f"sales_order_{row['salesOrder']}",
                    "target": f"customer_{row['soldToParty']}",
                    "label": "sold_to",
                    "type": "order_to_customer"
                })
            
            # Billing to Customer
            bill_customer = db_manager.execute_query("""
                SELECT billingDocument, soldToParty
                FROM billing_documents
                WHERE soldToParty IS NOT NULL
            """)
            
            for row in bill_customer:
                self.edges.append({
                    "source": f"billing_{row['billingDocument']}",
                    "target": f"customer_{row['soldToParty']}",
                    "label": "billed_to",
                    "type": "billing_to_customer"
                })
                
        except Exception as e:
            print(f"Error adding relationships: {e}")

# Global graph builder instance
graph_builder = GraphBuilder()
