#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDELT 数据分析脚本
分析采集到的犯罪新闻数据
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class GDELTAnalyzer:
    def __init__(self, data_file="D:/Projects/CrimeJournal/data/raw/gdelt_crime_articles.csv"):
        self.data_file = data_file
        self.df = None
        self.output_dir = "D:/Projects/CrimeJournal/outputs"

    def load_data(self):
        """加载数据"""
        self.df = pd.read_csv(self.data_file, encoding='utf-8')
        print(f"Loaded {len(self.df)} articles")

    def analyze_language_distribution(self):
        """分析语言分布"""
        lang_dist = self.df['language'].value_counts()

        # 计算非英语占比
        total = len(self.df)
        english_count = lang_dist.get('English', 0)
        non_english_pct = (total - english_count) / total * 100

        print(f"\nLanguage Distribution:")
        print(f"Total articles: {total}")
        print(f"English: {english_count} ({english_count/total*100:.1f}%)")
        print(f"Non-English: {total-english_count} ({non_english_pct:.1f}%)")
        print(f"\nTop 10 languages:")
        print(lang_dist.head(10))

        return lang_dist

    def analyze_country_distribution(self):
        """分析国家分布"""
        country_dist = self.df['sourcecountry'].value_counts()

        print(f"\nCountry Distribution:")
        print(f"Total countries: {len(country_dist)}")
        print(f"\nTop 10 countries:")
        print(country_dist.head(10))

        return country_dist

    def analyze_time_distribution(self):
        """分析时间分布"""
        self.df['seendate'] = pd.to_datetime(self.df['seendate'], format='%Y%m%dT%H%M%SZ')
        self.df['date'] = self.df['seendate'].dt.date

        time_dist = self.df['date'].value_counts().sort_index()

        print(f"\nTime Distribution:")
        print(f"Date range: {time_dist.index.min()} to {time_dist.index.max()}")
        print(f"Articles per day (avg): {len(self.df)/len(time_dist):.1f}")

        return time_dist

    def generate_summary_report(self):
        """生成汇总报告"""
        lang_dist = self.analyze_language_distribution()
        country_dist = self.analyze_country_distribution()
        time_dist = self.analyze_time_distribution()

        # 保存统计数据
        summary = {
            'total_articles': len(self.df),
            'languages': len(lang_dist),
            'countries': len(country_dist),
            'date_range': f"{time_dist.index.min()} to {time_dist.index.max()}",
            'top_language': lang_dist.index[0],
            'top_country': country_dist.index[0]
        }

        # 保存为 JSON
        import json
        output_file = os.path.join(self.output_dir, 'gdelt_data_summary.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

        print(f"\nSummary saved to: {output_file}")

        return summary

if __name__ == "__main__":
    analyzer = GDELTAnalyzer()
    analyzer.load_data()
    summary = analyzer.generate_summary_report()

    print("\n[DONE] Analysis complete")
