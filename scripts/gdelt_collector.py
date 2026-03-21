#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDELT Crime Data Collector
采集全球犯罪新闻数据
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime
import os

class GDELTCollector:
    """GDELT API 数据采集器"""

    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(self, output_dir="D:/Projects/CrimeJournal/data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def fetch_articles(self, query, max_records=250, timespan="3months",
                      source_country=None, mode="artlist"):
        """
        调用 GDELT API 获取文章数据

        Args:
            query: 搜索关键词
            max_records: 最大返回记录数（最多250）
            timespan: 时间范围
            source_country: 来源国家（可选）
            mode: 输出模式
        """
        params = {
            "query": query,
            "mode": mode,
            "maxrecords": max_records,
            "timespan": timespan,
            "format": "json"
        }

        if source_country:
            params["query"] = f"{query} sourcecountry:{source_country}"

        try:
            print(f"正在请求: {query} (country: {source_country or 'all'})")
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            print(f"[OK] 获取 {len(data.get('articles', []))} 条记录")
            return data

        except Exception as e:
            print(f"[ERROR] 请求失败: {e}")
            return None

    def collect_crime_data(self):
        """采集犯罪数据 - 多关键词、多国家"""

        # 犯罪类型关键词
        crime_keywords = [
            "crime", "murder", "theft", "robbery", "fraud",
            "assault", "terrorism", "cybercrime", "corruption",
            "trafficking", "kidnapping", "arson", "burglary"
        ]

        # 重点国家
        countries = ["china", "us", "uk", "france", "germany", "japan", "india"]

        all_articles = []

        # 1. 全球数据采集（不限国家）
        print("\n=== 阶段1: 全球犯罪数据采集 ===")
        for keyword in crime_keywords:
            data = self.fetch_articles(keyword, max_records=250)
            if data and "articles" in data:
                all_articles.extend(data["articles"])
            time.sleep(2)  # 避免请求过快

        # 2. 重点国家数据采集
        print("\n=== 阶段2: 重点国家数据采集 ===")
        for country in countries:
            query = "(crime OR murder OR theft OR fraud)"
            data = self.fetch_articles(query, max_records=250, source_country=country)
            if data and "articles" in data:
                all_articles.extend(data["articles"])
            time.sleep(2)

        return all_articles

    def save_to_json(self, articles, filename="gdelt_crime_raw.json"):
        """保存原始 JSON 数据"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] 已保存 {len(articles)} 条记录到: {filepath}")

    def save_to_csv(self, articles, filename="gdelt_crime_articles.csv"):
        """转换为 CSV 格式"""
        if not articles:
            print("没有数据可保存")
            return

        df = pd.DataFrame(articles)
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"[OK] 已保存 CSV 到: {filepath}")

    def get_statistics(self, articles):
        """统计数据概览"""
        if not articles:
            return

        df = pd.DataFrame(articles)
        print("\n=== 数据统计 ===")
        print(f"总记录数: {len(df)}")

        if 'sourcelang' in df.columns:
            print(f"\n语言分布 (Top 10):")
            print(df['sourcelang'].value_counts().head(10))

        if 'sourcecountry' in df.columns:
            print(f"\n国家分布 (Top 10):")
            print(df['sourcecountry'].value_counts().head(10))


def main():
    """主函数"""
    print("=" * 60)
    print("GDELT Crime Data Collector")
    print("目标: 采集 20,000+ 条全球犯罪新闻数据")
    print("=" * 60)

    collector = GDELTCollector()

    # 采集数据
    articles = collector.collect_crime_data()

    # 去重
    unique_articles = []
    seen_urls = set()
    for article in articles:
        url = article.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)

    print(f"\n去重后: {len(unique_articles)} 条唯一记录")

    # 保存数据
    collector.save_to_json(unique_articles)
    collector.save_to_csv(unique_articles)

    # 统计信息
    collector.get_statistics(unique_articles)

    print("\n[OK] 数据采集完成!")


if __name__ == "__main__":
    main()

