#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDELT Crime Data Collector V2
优化版：使用组合查询减少请求次数，增加延迟避免限流
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime
import os

class GDELTCollectorV2:
    """GDELT API 数据采集器 V2"""

    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(self, output_dir="D:/Projects/CrimeJournal/data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def fetch_articles(self, query, max_records=250, timespan="3months",
                      mode="artlist", retry=3):
        """调用 GDELT API 获取文章数据（带重试机制）"""
        params = {
            "query": query,
            "mode": mode,
            "maxrecords": max_records,
            "timespan": timespan,
            "format": "json"
        }

        for attempt in range(retry):
            try:
                print(f"正在请求: {query[:50]}...")
                response = requests.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                count = len(data.get('articles', []))
                print(f"[OK] 获取 {count} 条记录")
                return data

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = 30 * (attempt + 1)
                    print(f"[WARN] 限流，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"[ERROR] HTTP错误: {e}")
                    return None
            except Exception as e:
                print(f"[ERROR] 请求失败: {e}")
                return None

        print("[ERROR] 重试次数用尽")
        return None
