import os
import pyodbc
from urllib.parse import unquote
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("AZURE_SQL_USER") or os.getenv("user")
db_password = os.getenv("AZURE_SQL_PASSWORD") or os.getenv("sql_pass")
db_server = os.getenv("AZURE_SQL_SERVER")
db_name = os.getenv("AZURE_SQL_DATABASE")
db_driver = os.getenv("AZURE_SQL_DRIVER", "ODBC Driver 18 for SQL Server")

if not db_user or not db_password or not db_server or not db_name:
    raise SystemExit(
        "Missing required env vars. Set AZURE_SQL_USER, AZURE_SQL_PASSWORD, AZURE_SQL_SERVER, AZURE_SQL_DATABASE in .env"
    )

azure_conn_str = (
    f"Driver={{{db_driver}}};"
    f"Server=tcp:{db_server},1433;"
    f"Database={db_name};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
    f"UID={db_user};"
    f"PWD={db_password};"
)

print("Connecting to DB to check schema...")
conn = pyodbc.connect(azure_conn_str)
cursor = conn.cursor()

cursor.execute("SELECT DB_NAME()")
print(f"Connected to database: {cursor.fetchone()[0]}")

print("Final verification: Counting rows in stock_news_sentiment...")
cursor.execute("SELECT COUNT(*) FROM stock_news_sentiment")
count = cursor.fetchone()[0]
print(f"Total rows in table: {count}")

print("Top 5 results:")
cursor.execute("SELECT TOP 5 title, sentiment, score FROM stock_news_sentiment ORDER BY id DESC")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
