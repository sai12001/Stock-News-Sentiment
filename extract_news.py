import os
import json
import requests
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"
QUERY = os.getenv("NEWS_QUERY", "finance OR stock OR market")

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_RAW", "raw")
BLOB_NAME = f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def fetch_news():
    print("Fetching news from API...")
    params = {
        "q": QUERY,
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY,
        "pageSize": 50
    }
    response = requests.get(NEWS_API_URL, params=params)
    response.raise_for_status()
    news_data = response.json()
    
    # Process news into a cleaner JSON list
    articles = []
    for article in news_data.get("articles", []):
        articles.append({
            "title": article.get("title"),
            "published_at": article.get("publishedAt"),
            "source": article.get("source", {}).get("name"),
            "url": article.get("url")
        })
    print(f"Fetched {len(articles)} articles.")
    return articles

def upload_to_blob(data):
    print("Uploading to Azure Blob Storage...")
    try:
        if not AZURE_CONNECTION_STRING:
            raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING")

        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        # Create container if it doesn't exist
        if not container_client.exists():
            container_client.create_container()
            
        blob_client = container_client.get_blob_client(blob=BLOB_NAME)
        
        json_data = json.dumps(data, indent=2)
        blob_client.upload_blob(json_data, overwrite=True)
        print(f"Successfully uploaded {BLOB_NAME} to container {CONTAINER_NAME}.")
    except Exception as e:
        print(f"Error uploading to Blob Storage: {e}")
        print("Please make sure you have set the AZURE_STORAGE_CONNECTION_STRING environment variable or updated it in the script.")

if __name__ == "__main__":
    if not NEWS_API_KEY:
        raise SystemExit(
            "Missing NEWS_API_KEY. Set it in your .env file (register at https://newsapi.org)."
        )
    
    news_data = fetch_news()
    if news_data:
        upload_to_blob(news_data)
