<<<<<<< HEAD
# Stock-News-Sentiment
Stock News Sentiment (Azure Data Engineering Mini Project)
=======
# Stock News Sentiment (Azure Data Engineering Mini Project)

This project is an end-to-end **data engineering pipeline** that:

- pulls **financial/stock-related news** from an API (NewsAPI),
- lands the raw JSON into **Azure Blob Storage**,
- runs **sentiment analysis** on headlines (Hugging Face Transformers),
- loads curated results into **Azure SQL Database**,
- and is ready to visualize in **Power BI**.

It’s a great beginner-friendly project because it covers the real workflow: **ingest → land → transform/ML-enrich → load → consume**.

## Architecture diagram (high level)

```mermaid
flowchart LR
  A[NewsAPI\n(HTTP JSON)] -->|extract_news.py| B[Azure Blob Storage\nContainer: raw]
  B -->|databricks_process.py\n(or local Python)| C[Sentiment Analysis\nTransformers + Torch]
  C -->|SQLAlchemy + pyodbc| D[Azure SQL Database\nTable: stock_news_sentiment]
  D --> E[Power BI Dashboard]
```

## Repository contents

- `extract_news.py`: fetches news from NewsAPI and uploads JSON to Blob Storage (container `raw` by default).
- `databricks_process.py`: reads JSON from Blob Storage, performs sentiment analysis, inserts rows into Azure SQL.
- `database_setup.sql`: creates the `stock_news_sentiment` table in Azure SQL.
- `check_schema.py`: quick verification script (connects to Azure SQL and shows row count + last rows).
- `.env`: configuration (API keys, storage connection string, SQL connection parameters).
- `requirements.txt`: Python dependencies for local execution.

## What the student will learn

- **API ingestion** (REST, pagination basics)
- **Cloud landing zone** design (raw container, immutable JSON blobs)
- **Transformation & enrichment** (DataFrame shaping + ML inference)
- **Loading to relational storage** (Azure SQL, schema design, inserts)
- **Operational concerns** (secrets in `.env`, repeatable runs, verification)

## Prerequisites (Windows)

### Accounts / cloud resources

- **NewsAPI key**: create a free key at `https://newsapi.org`
- **Azure Storage Account** (Blob Storage)
- **Azure SQL Database**
- (Optional) **Azure Databricks** workspace/cluster
- (Optional) Power BI Desktop

### Software to install on Windows

- **Python 3.10+**
- **Git** (optional, but recommended)
- **Microsoft ODBC Driver for SQL Server (x64)**  
  Install **ODBC Driver 18 for SQL Server** (recommended). This is required for `pyodbc` to connect to Azure SQL.

## Step-by-step: run the whole pipeline on Windows (from scratch)

### 1) Get the code

- Download the project folder, or clone if it’s in a git repo.
- Open PowerShell in the project directory.

### 2) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 3) Install Python dependencies

```powershell
pip install -r requirements.txt
```

If `torch` installation is slow, that’s normal (it’s large). CPU-only is fine for this project.

### 4) Create `.env` (all configuration lives here)

Create a file named `.env` in the project root:

```bash
### NewsAPI
NEWS_API_KEY=your_newsapi_key
NEWS_QUERY="finance OR stock OR market"

### Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING="your_azure_blob_connection_string"
AZURE_STORAGE_CONTAINER_RAW=raw

### Azure SQL
AZURE_SQL_SERVER="your_server_name.database.windows.net"
AZURE_SQL_DATABASE="your_database_name"
AZURE_SQL_DRIVER="ODBC Driver 18 for SQL Server"
AZURE_SQL_USER="your_sql_username"
AZURE_SQL_PASSWORD="your_sql_password"
```

Where to find these values:

- **Blob connection string**: Azure Portal → Storage Account → **Access keys** → **Connection string**
- **SQL server + database**: Azure Portal → SQL Database (overview page shows both)
- **SQL username/password**: what you created for the SQL Server login

### 5) Create the SQL table in Azure SQL

Run `database_setup.sql`:

- Azure Portal → your **SQL Database** → **Query editor** (or SSMS/Azure Data Studio)
- Paste the SQL from `database_setup.sql` and run it.

This creates:

- **table**: `stock_news_sentiment`
- **columns**: `title`, `published_at`, `sentiment`, `score`

### 6) Ingest raw news to Blob Storage

```powershell
python extract_news.py
```

Expected result:
- a new blob like `news_YYYYMMDD_HHMMSS.json` uploaded into container `raw`

### 7) Transform + sentiment + load to Azure SQL

You can run this in two ways.

**Option A: Run locally (simple for learning)**

```powershell
python databricks_process.py
```

This will:
- read all `.json` blobs inside the `raw` container,
- run sentiment analysis on `title`,
- insert into Azure SQL table `stock_news_sentiment`.

**Option B: Run in Azure Databricks (more “real world”)**

- Create an **ML runtime** cluster (Databricks Runtime ML is recommended).
- Upload/copy `databricks_process.py` into a notebook.
- Install missing libs in a notebook cell if needed:

```python
%pip install -r requirements.txt
dbutils.library.restartPython()
```

- Set secrets as Databricks secrets / environment variables (recommended) or upload `.env` to the workspace.
- Run the notebook.

### 8) Validate results

```powershell
python check_schema.py
```

Expected:
- It prints the connected DB name
- It prints row count from `stock_news_sentiment`
- It prints top rows (title, sentiment, score)

### 9) Visualize in Power BI (optional)

Connect Power BI to Azure SQL and build visuals on:
- sentiment distribution
- sentiment over time
- top negative/positive headlines

## Troubleshooting (common)

- **Blob upload error / missing connection string**: confirm `AZURE_STORAGE_CONNECTION_STRING` is real and quoted in `.env`.
- **HF model download slow**: first run downloads the model; subsequent runs are faster.
- **`pyodbc` errors on Windows**: install **Microsoft ODBC Driver 18 for SQL Server** and ensure `.env` has `AZURE_SQL_DRIVER="ODBC Driver 18 for SQL Server"`.

## Notes for instructors

- This repo intentionally keeps the pipeline “small” and readable.
- Production-grade improvements would include: deduping articles, incremental loads, partitioned folders in blob, and a job scheduler.
>>>>>>> 2910e050 (Add Azure stock news sentiment pipeline docs and config)
