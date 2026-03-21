#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDELT 增量采集脚本 - 保守策略
每次采集少量数据，避免API限流
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime
import os

class IncrementalCollector:
    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(self, output_file="D:/Projects/CrimeJournal/data/raw/gdelt_crime_articles.csv"):
        self.output_file = output_file

    def fetch_batch(self, query, max_records=50, timespan="7days"):
        """采集单批数据"""
        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": max_records,
            "timespan": timespan,
            "format": "json"
        }

        try:
            print(f"Fetching: {query[:50]}...")
            response = requests.get(self.BASE_URL, params=params, timeout=30)

            if response.status_code == 429:
                print("[WARN] Rate limited, waiting 60s...")
                time.sleep(60)
                return []

            response.raise_for_status()
            data = response.json()
            articles = data.get('articles', [])
            print(f"[OK] Got {len(articles)} articles")
            return articles

        except Exception as e:
            print(f"[ERROR] {e}")
            return []

    def collect_to_target(self, target_count=1100):
        """采集到目标数量"""
        # 读取现有数据
        if os.path.exists(self.output_file):
            existing_df = pd.read_csv(self.output_file)
            current_count = len(existing_df)
            print(f"Current: {current_count} articles")
        else:
            existing_df = pd.DataFrame()
            current_count = 0

        if current_count >= target_count:
            print(f"Already have {current_count} articles, target reached!")
            return

        needed = target_count - current_count
        print(f"Need {needed} more articles")

        # 查询列表（多样化）
        queries = [
            "crime murder",
            "theft robbery",
            "fraud scam",
            "assault violence",
            "cybercrime hacking",
            "terrorism attack",
            "corruption bribery",
            "kidnapping abduction"
        ]

        all_new = []
        batch_size = 50

        for i, query in enumerate(queries):
            if len(all_new) >= needed:
                break

            print(f"\n[Batch {i+1}/{len(queries)}] Query: {query}")
            articles = self.fetch_batch(query, max_records=batch_size)
            all_new.extend(articles)

            print(f"Total collected: {len(all_new)}")
            time.sleep(30)  # 30秒延迟

        # 合并去重
        if all_new:
            new_df = pd.DataFrame(all_new)
            combined = pd.concat([existing_df, new_df], ignore_index=True)
            combined_unique = combined.drop_duplicates(subset=['url'], keep='first')

            combined_unique.to_csv(self.output_file, index=False, encoding='utf-8-sig')

            print(f"\n[DONE]")
            print(f"Original: {current_count}")
            print(f"New: {len(all_new)}")
            print(f"After dedup: {len(combined_unique)}")
            print(f"Saved to: {self.output_file}")

if __name__ == "__main__":
    collector = IncrementalCollector()
    collector.collect_to_target(target_count=1000)
