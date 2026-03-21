#!/ 批量爬取脚本
# 从 CSV 读取 URL 并批量爬取

import pandas as pd
import os
import time

# 读取 CSV
df = pd.read_csv("D:/Projects/CrimeJournal/data/raw/gdelt_crime_articles.csv", encoding='utf-8')
print(f"Total URLs: {len(df)}")

# 选择前100 条 URL 进行测试
urls_to_crawl = df['url'].head(100).tolist()

print(f"Selected {len(urls_to_crawl)} URLs for batch crawling")
print("Please use Firecrawl MCP tool to crawl these URLs")
print("\nURLs to crawl:")
for i, enumerate(urls_to_crawl[:10]):
    print(f"{i+1}. {urls_to_cibble[i]}")
