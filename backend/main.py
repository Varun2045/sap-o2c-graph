from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import duckdb
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB setup ──────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
con = duckdb.connect()

TABLES = {
    "sales_order_headers":                      "salesOrder",
    "billing_document_headers":                 "billingDocument",
    "outbound_delivery_headers":                "deliveryDocument",
    "journal_entry_items_accounts_receivable":  "accountingDocument",
    "payments_accounts_receivable":             "accountingDocument",
    "business_partners":                        "businessPartner",
    "products":                                 "product",
    "plants":                                   "plant",
}

def load_tables():
    for folder, _ in TABLES.items():
        folder_path = DATA_DIR / folder
        if not folder_path.exists():
            print(f"[WARN] folder not found: {folder_path}")
            continue
        jsonl_files = list(folder_path.glob("*.jsonl"))
        if not jsonl_files:
            print(f"[WARN] no jsonl files in {folder_path}")
            continue
        # read all jsonl files into a list
        rows = []
        for f in jsonl_files:
            with open(f) as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        rows.append(json.loads(line))
        if not rows:
            continue
        # create table from JSON
        con.execute(f"DROP TABLE IF EXISTS {folder}")
        con.execute(f"CREATE TABLE {folder} AS SELECT * FROM read_json_auto(?)", [str(jsonl_files[0])])
        # if multiple files, union them
        if len(jsonl_files) > 1:
            for extra in jsonl_files[1:]:
                try:
                    con.execute(f"INSERT INTO {folder} SELECT * FROM read_json_auto(?)", [str(extra)])
                except Exception as e:
                    print(f"[WARN] insert failed for {extra}: {e}")
        count = con.execute(f"SELECT COUNT(*) FROM {folder}").fetchone()[0]
        print(f"[OK] loaded {folder}: {count} rows")

load_tables()

# Fix VARCHAR numeric columns
try:
    con.execute("ALTER TABLE sales_order_headers ADD COLUMN totalNetAmountNum DECIMAL AS (CAST(totalNetAmount AS DECIMAL))")
except:
    pass
try:
    con.execute("ALTER TABLE billing_document_headers ADD COLUMN totalNetAmountNum DECIMAL AS (CAST(totalNetAmount AS DECIMAL))")
except:
    pass

# ── Graph endpoint ─────────────────────────────────────────────────────────────
@app.get("/graph")
def get_graph():
    nodes = []
    edges = []
    seen_nodes = set()

    def add_node(id_, label, type_, props={}):
        if id_ not in seen_nodes:
            seen_nodes.add(id_)
            nodes.append({"id": id_, "label": label, "type": type_, "properties": props})

    # Sales orders
    try:
        rows = con.execute("SELECT salesOrder, soldToParty, totalNetAmount, overallDeliveryStatus FROM sales_order_headers LIMIT 100").fetchall()
        for r in rows:
            add_node(f"SO_{r[0]}", f"SO {r[0]}", "SalesOrder", {"id": r[0], "customer": r[1], "amount": r[2], "deliveryStatus": r[3]})
            add_node(f"CU_{r[1]}", f"Customer {r[1]}", "Customer", {"id": r[1]})
            edges.append({"source": f"CU_{r[1]}", "target": f"SO_{r[0]}", "label": "PLACED"})
    except Exception as e:
        print(f"sales_order_headers error: {e}")

    # Billing documents
    try:
        rows = con.execute("SELECT billingDocument, accountingDocument, soldToParty, totalNetAmount FROM billing_document_headers LIMIT 100").fetchall()
        for r in rows:
            add_node(f"BD_{r[0]}", f"Invoice {r[0]}", "BillingDocument", {"id": r[0], "accountingDoc": r[1], "customer": r[2], "amount": r[3]})
            add_node(f"CU_{r[2]}", f"Customer {r[2]}", "Customer", {"id": r[2]})
            edges.append({"source": f"CU_{r[2]}", "target": f"BD_{r[0]}", "label": "BILLED"})
            if r[1]:
                add_node(f"JE_{r[1]}", f"Journal {r[1]}", "JournalEntry", {"id": r[1]})
                edges.append({"source": f"BD_{r[0]}", "target": f"JE_{r[1]}", "label": "POSTED_TO"})
    except Exception as e:
        print(f"billing_document_headers error: {e}")

    # Deliveries
    try:
        rows = con.execute("SELECT deliveryDocument, shippingPoint FROM outbound_delivery_headers LIMIT 100").fetchall()
        for r in rows:
            add_node(f"DL_{r[0]}", f"Delivery {r[0]}", "Delivery", {"id": r[0], "shippingPoint": r[1]})
    except Exception as e:
        print(f"outbound_delivery_headers error: {e}")

    return {"nodes": nodes, "edges": edges}


# ── Suggested queries ──────────────────────────────────────────────────────────
@app.get("/suggested-queries")
def suggested_queries():
    return {"queries": [
        "Which customers have the most billing documents?",
        "Show me the top 5 sales orders by amount",
        "Which billing documents are cancelled?",
        "What is the total revenue across all invoices?",
        "Show sales orders with delivery status C",
    ]}


# ── Chat / query endpoint ──────────────────────────────────────────────────────
DOMAIN_KEYWORDS = [
    "sales", "order", "delivery", "billing", "invoice", "payment",
    "customer", "journal", "amount", "revenue", "document", "sap",
    "ship", "product", "partner", "plant", "cancel", "status", "date",
    "total", "account", "fiscal", "currency", "entry"
]

SCHEMA_CONTEXT = """
Tables available:
- sales_order_headers: salesOrder, soldToParty, CAST(totalNetAmount AS DOUBLE) AS totalNetAmount, overallDeliveryStatus, transactionCurrency, creationDate, salesOrderType
  NOTE: always write SUM(CAST(totalNetAmount AS DOUBLE)) for any sum
  NOTE: billingDocumentIsCancelled does NOT exist in sales_order_headers, use billing_document_headers table for cancellation status
- billing_document_headers: billingDocument, accountingDocument, soldToParty, totalNetAmount, billingDocumentIsCancelled, cancelledBillingDocument, billingDocumentDate
- outbound_delivery_headers: deliveryDocument, shippingPoint, overallGoodsMovementStatus, creationDate
- journal_entry_items_accounts_receivable: accountingDocument, referenceDocument, customer, amountInTransactionCurrency, clearingAccountingDocument, postingDate, glAccount
- payments_accounts_receivable: accountingDocument, customer, amountInTransactionCurrency, clearingAccountingDocument, postingDate

Key relationships:
- billing_document_headers.accountingDocument = journal_entry_items_accounts_receivable.accountingDocument
- journal_entry_items_accounts_receivable.referenceDocument = billing_document_headers.billingDocument
- billing_document_headers.soldToParty = sales_order_headers.soldToParty (same customer)

IMPORTANT: billingDocumentIsCancelled column only exists in billing_document_headers table, not in sales_order_headers.
To filter sales orders by billing cancellation status, you must JOIN with billing_document_headers table.
"""

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def run_query(req: QueryRequest):
    q = req.query.lower()

    # Guardrail
    if not any(kw in q for kw in DOMAIN_KEYWORDS):
        return {
            "answer": "This system is designed to answer questions related to the SAP Order-to-Cash dataset only. Please ask about sales orders, deliveries, billing documents, payments, or customers.",
            "sql": None,
            "data": []
        }

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"answer": "GROQ_API_KEY not set in .env file.", "sql": None, "data": []}

    client = Groq(api_key=api_key)

    # Step 1: Generate SQL
    sql_prompt = f"""You are a SQL expert. Given this database schema:

{SCHEMA_CONTEXT}

Write a single DuckDB SQL query to answer this question: "{req.query}"

Rules:
- Return ONLY the SQL query, nothing else
- No markdown, no explanation, no backticks
- Use LIMIT 20 unless asking for totals/counts
- Only use tables listed in the schema above
- billingDocumentIsCancelled is a BOOLEAN column that ONLY exists in billing_document_headers table, use TRUE or FALSE not 'X'
- For boolean comparisons always use: WHERE billingDocumentIsCancelled = TRUE
- totalNetAmount and amountInTransactionCurrency are stored as VARCHAR, always cast them: CAST(totalNetAmount AS DECIMAL)
- ALWAYS use SUM(CAST(totalNetAmount AS DOUBLE)) never SUM(totalNetAmount)
- ALWAYS use SUM(CAST(amountInTransactionCurrency AS DOUBLE)) for amounts
- CRITICAL: If the question asks about billing cancellation status for sales orders, you MUST JOIN sales_order_headers with billing_document_headers
- Example join pattern: FROM sales_order_headers soh JOIN billing_document_headers bdh ON soh.soldToParty = bdh.soldToParty
"""

    sql_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": sql_prompt}],
        max_tokens=300,
    )
    sql = sql_response.choices[0].message.content.strip()

    # Step 2: Execute SQL
    try:
        result = con.execute(sql).fetchdf()
        data = result.to_dict(orient="records")
    except Exception as e:
        return {"answer": f"SQL execution error: {e}", "sql": sql, "data": []}

    # Step 3: Natural language answer
    answer_prompt = f"""You are a business analyst. The user asked: "{req.query}"

The SQL query returned this data:
{data[:10]}

Give a concise, helpful answer in 2-3 sentences based on the data.
Do not mention SQL. Be direct and business-focused.
"""
    answer_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": answer_prompt}],
        max_tokens=200,
    )
    answer = answer_response.choices[0].message.content.strip()

    return {"answer": answer, "sql": sql, "data": data}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)