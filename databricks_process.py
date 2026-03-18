# Databricks notebook source
# MAKE SURE TO ATTACH A CLUSTER RUNNING 13.x ML WITH 2 WORKERS
# Install required libraries if not already installed (you can use cluster libraries or this command):
 # %pip install transformers pyodbc sqlalchemy pandas

from transformers import pipeline
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import os
from dotenv import load_dotenv

# Load local .env file if running locally
load_dotenv()

# --- Step 2: Read Raw News Data ---
import glob
import json

# Instead of spark read, let's use standard Python to read from Blob Storage or Local if downloaded
container = os.getenv("AZURE_STORAGE_CONTAINER_RAW", "raw")
container_client = __import__('azure.storage.blob').storage.blob.ContainerClient.from_connection_string(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING"), container
)

print(f"Reading from Blob Storage Container: {container}...")
blobs = list(container_client.list_blobs())

all_news = []
for blob in blobs:
    if blob.name.endswith(".json"):
        blob_data = container_client.download_blob(blob.name).readall()
        all_news.extend(json.loads(blob_data))

df = pd.DataFrame(all_news)
print(df.head())

# --- Step 3: Sentiment Analysis using HuggingFace ---
print("Initializing sentiment analysis pipeline...")
# Using a specific model for sentiment analysis to ensure consistency
sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", revision="main")

pdf = df

# Drop rows where title is null
pdf = pdf.dropna(subset=['title'])

print("Running sentiment analysis on headlines...")
# Truncating strings to 512 chars as transformer models have a max token limit usually
pdf["result"] = pdf["title"].apply(lambda x: sentiment_model(str(x)[:512])[0])

pdf["sentiment"] = pdf["result"].apply(lambda x: x["label"])
pdf["score"] = pdf["result"].apply(lambda x: x["score"])

# Drop the raw result column
pdf = pdf.drop(columns=["result"])

# Display the processed data
print(pdf.head())

# --- Step 4: Load to Azure SQL Database ---
print("Loading data into Azure SQL Database...")

# Database credentials and connection string
db_user = os.getenv("AZURE_SQL_USER") or os.getenv("user")
db_password = os.getenv("AZURE_SQL_PASSWORD") or os.getenv("sql_pass")
db_server = os.getenv("AZURE_SQL_SERVER")
db_name = os.getenv("AZURE_SQL_DATABASE")
db_driver = os.getenv("AZURE_SQL_DRIVER", "ODBC Driver 18 for SQL Server")

if not db_user or not db_password or not db_server or not db_name:
    raise ValueError(
        "Missing one or more required env vars: AZURE_SQL_USER, AZURE_SQL_PASSWORD, AZURE_SQL_SERVER, AZURE_SQL_DATABASE"
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
params = urllib.parse.quote_plus(azure_conn_str)

# Create connection engine using the encoded connection string
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
table_name = "stock_news_sentiment"

# Select only desired columns to match the SQL table schema
columns_to_insert = ["title", "published_at", "sentiment", "score"]
pdf_to_sql = pdf[columns_to_insert].copy()

# Ensure published_at is a datetime object and strip timezone for SQL Server DATETIME compatibility
pdf_to_sql["published_at"] = pd.to_datetime(pdf_to_sql["published_at"]).dt.tz_localize(None)

print(f"Inserting {len(pdf_to_sql)} rows into {table_name}...")
pdf_to_sql.to_sql(table_name, engine, if_exists="append", index=False)
print("Data successfully loaded to Azure SQL Database.")
