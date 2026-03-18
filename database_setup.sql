-- Run this in Azure Portal -> SQL Database -> Query editor
-- Make sure you are connected to the 'my-sql-r' database
-- This script creates the target table for the sentiment analysis data

CREATE TABLE stock_news_sentiment (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(MAX),
    published_at DATETIME,
    sentiment NVARCHAR(50),
    score FLOAT
);

-- After running the Databricks notebook, you can verify data insertion with:
-- SELECT TOP 100 * FROM stock_news_sentiment ORDER BY published_at DESC;
