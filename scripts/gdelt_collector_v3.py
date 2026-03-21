#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDELT Crime Data Collector V3
优化策略：
1. 大组合查询减少请求次数
2. 分时段采集避免重复
3. 重点国家单独采集
4. 更长延迟避免限流（10-30秒）
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import os

class GDELTCollectorV3:
    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(self, output_dir="D:/Projects/CrimeJournal/data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.all_articles = []

    def fetch_with_retry(self, params, delay=15, max_retry=3):
        """带重试和延迟的API调用"""
        for attempt in range(max_retry):
            try:
                print(f"  请求中... (尝试 {attempt+1}/{max_retry})")
                response = requests.get(self.BASE_URL, params=params, timeout=30)

                if response.status_code == 429:
                    wait = 60 * (attempt + 1)
                    print(f"  [限流] 等待 {wait}s")
                    time.sleep(wait)
                    continue

                response.raise_for_status()
                data = response.json()
                articles = data.get('articles', [])
                print(f"  [成功] 获取 {len(articles)} 条")
                time.sleep(delay)
                return articles

            except Exception as e:
                print(f"  [错误] {e}")
                if attempt < max_retry - 1:
                    time.sleep(30)
        return []

    def collect_by_timespan(self, query, start_date, end_date, max_records=250):
        """按时间段采集"""
        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": max_records,
            "startdatetime": start_date,
            "enddatetime": end_date,
            "format": "json"
        }
        print(f"\n[时段] {start_date} 至 {end_date}")
        print(f"[查询] {query}")
        return self.fetch_with_retry(params, delay=20)

    def collect_by_country(self, query, country, timespan="3months", max_records=250):
        """按国家采集"""
        params = {
            "query": f"{query} sourcecountry:{country}",
            "mode": "artlist",
            "maxrecords": max_records,
            "timespan": timespan,
            "format": "json"
        }
        print(f"\n[国家] {country}")
        print(f"[查询] {query}")
        return self.fetch_with_retry(params, delay=25)

    def run_collection(self):
        """执行完整采集流程"""
        print("="*60)
        print("GDELT 犯罪数据采集 V3")
        print("="*60)

        # 策略1: 大组合查询（全球数据）
        print("\n【阶段1】全球犯罪数据采集")
        global_queries = [
            "(crime OR murder OR theft OR fraud OR assault)",
            "(terrorism OR cybercrime OR corruption OR trafficking)",
            "(robbery OR kidnapping OR homicide OR violence)"
        ]

        for query in global_queries:
            articles = self.fetch_with_retry({
                "query": query,
                "mode": "artlist",
                "maxrecords": 250,
                "timespan": "3months",
                "format": "json"
            }, delay=20)
            self.all_articles.extend(articles)
            print(f"  累计: {len(self.all_articles)} 条\n")

        # 策略2: 重点国家单独采集
        print("\n【阶段2】重点国家数据采集")
        countries = ["China", "United States", "United Kingdom", "Germany", "India"]
        for country in countries:
            articles = self.collect_by_country(
                "(crime OR murder OR theft)",
                country,
                timespan="3months"
            )
            self.all_articles.extend(articles)
            print(f"  累计: {len(self.all_articles)} 条\n")

        # 策略3: 分时段采集（最近3个月分6段）
        print("\n【阶段3】分时段采集")
        end = datetime.now()
        for i in range(6):
            start = end - timedelta(days=15)
            articles = self.collect_by_timespan(
                "(crime OR criminal OR felony)",
                start.strftime("%Y%m%d%H%M%S"),
                end.strftime("%Y%m%d%H%M%S")
            )
            self.all_articles.extend(articles)
            print(f"  累计: {len(self.all_articles)} 条\n")
            end = start

        # 去重并保存
        print("\n【保存数据】")
        df = pd.DataFrame(self.all_articles)
        df_unique = df.drop_duplicates(subset=['url'], keep='first')

        output_file = os.path.join(self.output_dir, "gdelt_crime_articles_v3.csv")
        df_unique.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"原始数据: {len(self.all_articles)} 条")
        print(f"去重后: {len(df_unique)} 条")
        print(f"保存至: {output_file}")

        return df_unique

if __name__ == "__main__":
    collector = GDELTCollectorV3()
    df = collector.run_collection()
    print("\n✅ 采集完成")
