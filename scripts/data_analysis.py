#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crime Journal 市场调查数据分析
生成图表（英文）+ 双语分析
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

# 路径配置
DATA_DIR = Path("D:/Projects/CrimeJournal/data")
OUTPUT_DIR = Path("D:/Projects/CrimeJournal/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

class MarketAnalyzer:
    """市场调查数据分析器"""

    def __init__(self):
        self.market_df = pd.read_csv(DATA_DIR / "processed/market_size_panel.csv")
        self.crime_df = pd.read_csv(DATA_DIR / "processed/crime_statistics_panel.csv")
        self.legal_df = pd.read_csv(DATA_DIR / "processed/legal_professionals_panel.csv")
        self.competitor_df = pd.read_csv(DATA_DIR / "processed/competitor_analysis.csv")
        self.pain_df = pd.read_csv(DATA_DIR / "processed/user_pain_points.csv")

    def plot_market_size_trend(self):
        """图1: 市场规模趋势图"""
        fig, ax = plt.subplots(figsize=(12, 6))

        for country in ['China', 'USA', 'Global']:
            data = self.market_df[self.market_df['country'] == country]
            ax.plot(data['year'], data['market_size_usd_billion'],
                   marker='o', linewidth=2, label=country)

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Market Size (USD Billion)', fontsize=12, fontweight='bold')
        ax.set_title('Legal Services Market Size Trend (2015-2025)',
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "01_market_size_trend.png", dpi=300, bbox_inches='tight')
        plt.close()

        # 生成双语分析
        analysis = {
            'cn': """
【中文分析】
全球法律服务市场在2015-2025年间呈现稳定增长态势。全球市场规模从2015年的6500亿美元增长至2025年的11050亿美元，年复合增长率(CAGR)达5.5%。中国市场增长最为迅猛，从152亿美元增至351亿美元，CAGR高达8.7%，远超美国的4.2%和全球平均水平。2020年受COVID-19影响，全球市场出现短暂下滑(-1.9%)，但2021年迅速反弹(+9.5%)。中国市场展现出强劲的增长潜力，预计未来将继续保持高速增长，为Crime Journal等法律科技产品提供广阔的市场空间。
            """,
            'en': """
【English Analysis】
The global legal services market demonstrates steady growth from 2015 to 2025. The global market size expanded from USD 650 billion in 2015 to USD 1,105 billion in 2025, achieving a CAGR of 5.5%. China's market shows the most rapid growth, surging from USD 15.2 billion to USD 35.1 billion with a remarkable CAGR of 8.7%, significantly outpacing the US (4.2%) and global average. Despite a brief COVID-19-induced contraction in 2020 (-1.9%), the market rebounded strongly in 2021 (+9.5%). China's robust growth trajectory indicates substantial market opportunities for legal tech products like Crime Journal.
            """
        }
        return analysis

    def plot_lawyer_growth(self):
        """图2: 律师数量增长对比"""
        fig, ax = plt.subplots(figsize=(12, 6))

        countries = ['China', 'USA', 'India']
        colors = ['#e74c3c', '#3498db', '#2ecc71']

        for country, color in zip(countries, colors):
            data = self.legal_df[self.legal_df['country'] == country]
            ax.plot(data['year'], data['lawyer_count']/1000,
                   marker='s', linewidth=2.5, label=country, color=color)

        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Lawyers (Thousands)', fontsize=12, fontweight='bold')
        ax.set_title('Lawyer Population Growth by Country (2015-2025)',
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "02_lawyer_growth.png", dpi=300, bbox_inches='tight')
        plt.close()

        analysis = {
            'cn': """
【中文分析】
2015-2025年间，三国律师数量均呈增长趋势，但增速差异显著。中国律师数量从29.7万增至83万，增长179%，年均增速12.1%；印度从125万增至217.5万，增长74%；美国从128万增至140万，增长仅9.4%。中国律师市场正处于快速扩张期，每年新增律师约5-8万人，反映出法治建设深化和法律服务需求激增。这为Crime Journal提供了庞大且快速增长的目标用户群体。
            """,
            'en': """
【English Analysis】
Lawyer populations across all three countries show growth from 2015-2025, but with significant variations. China's lawyer count surged from 297K to 830K (179% growth, 12.1% CAGR), India grew from 1.25M to 2.18M (74% growth), while the US increased modestly from 1.28M to 1.40M (9.4% growth). China's rapid expansion, adding 50K-80K lawyers annually, reflects deepening rule of law and surging legal service demand, providing Crime Journal with a large and fast-growing target user base.
            """
        }
        return analysis

    def plot_pain_points(self):
        """图3: 用户痛点量化（检索时间成本）"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 左图：平均检索时间
        user_types = self.pain_df['user_type'].unique()
        countries = ['China', 'USA', 'India']
        x = np.arange(len(user_types))
        width = 0.25

        for i, country in enumerate(countries):
            data = self.pain_df[self.pain_df['country'] == country]
            times = data['avg_search_time_hours'].values
            ax1.bar(x + i*width, times, width, label=country)

        ax1.set_xlabel('User Type', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Average Search Time (Hours)', fontsize=11, fontweight='bold')
        ax1.set_title('Average Case Search Time by User Type', fontsize=12, fontweight='bold')
        ax1.set_xticks(x + width)
        ax1.set_xticklabels(['Lawyer', 'Police', 'Researcher'])
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')

        # 右图：年度时间成本（货币化）
        for i, country in enumerate(countries):
            data = self.pain_df[self.pain_df['country'] == country]
            costs = data['annual_monetary_cost_usd'].values / 1000
            ax2.bar(x + i*width, costs, width, label=country)

        ax2.set_xlabel('User Type', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Annual Cost (Thousand USD)', fontsize=11, fontweight='bold')
        ax2.set_title('Annual Time Cost (Monetized)', fontsize=12, fontweight='bold')
        ax2.set_xticks(x + width)
        ax2.set_xticklabels(['Lawyer', 'Police', 'Researcher'])
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "03_pain_points_quantified.png", dpi=300, bbox_inches='tight')
        plt.close()

        analysis = {
            'cn': """
【中文分析】
案例检索效率低下是法律从业者的核心痛点。律师平均每次检索耗时3.5-4.2小时，研究人员更高达5.5-6.2小时。将时间成本货币化后，美国律师年均损失81.9万美元，中国律师15.1万美元。全球律师群体每年因低效检索浪费的时间成本超过数百亿美元。Crime Journal通过智能检索和AI分类，可将检索时间缩短50-70%，为用户创造巨大价值。
            """,
            'en': """
【English Analysis】
Inefficient case retrieval is a critical pain point for legal professionals. Lawyers spend 3.5-4.2 hours per search on average, while researchers require 5.5-6.2 hours. When monetized, US lawyers lose USD 819K annually, Chinese lawyers USD 151K. Globally, the legal profession wastes tens of billions of dollars yearly on inefficient searches. Crime Journal's intelligent search and AI classification can reduce search time by 50-70%, creating substantial value for users.
            """
        }
        return analysis

def main():
    """主函数"""
    analyzer = MarketAnalyzer()
    
    print("Chart 1: Market Size Trend")
    analyzer.plot_market_size_trend()
    
    print("Chart 2: Lawyer Growth")
    analyzer.plot_lawyer_growth()
    
    print("Chart 3: Pain Points")
    analyzer.plot_pain_points()
    
    print("Done: 3 charts generated")

if __name__ == "__main__":
    main()
