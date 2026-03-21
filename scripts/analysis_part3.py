#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crime Journal - 补充图表 6-8
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

DATA_DIR = Path("D:/Projects/CrimeJournal/data")
OUTPUT_DIR = Path("D:/Projects/CrimeJournal/outputs")

def plot_market_growth_rate():
    """图6: 市场增长率对比"""
    market_df = pd.read_csv(DATA_DIR / "processed/market_size_panel.csv")

    fig, ax = plt.subplots(figsize=(12, 6))

    for country in ['China', 'USA', 'Global']:
        data = market_df[market_df['country'] == country]
        ax.plot(data['year'], data['growth_rate_percent'],
               marker='o', linewidth=2.5, label=country)

    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Growth Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Legal Services Market Growth Rate (2015-2025)',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "06_market_growth_rate.png", dpi=300, bbox_inches='tight')
    plt.close()

    return {
        'cn': "中国市场增长率波动较大，2018年达峰值15.3%后逐年回落至2025年的1.7%，反映市场从高速扩张转向成熟稳定。美国和全球市场增速相对平稳，2020年疫情导致全球市场短暂负增长(-1.9%)。",
        'en': "China's growth rate peaked at 15.3% in 2018, then declined to 1.7% in 2025, indicating market maturation. US and global markets show stable growth, with brief COVID-19 contraction (-1.9%) in 2020."
    }

def plot_tam_sam_som():
    """图7: TAM/SAM/SOM 分析"""
    fig, ax = plt.subplots(figsize=(10, 8))

    # 市场规模数据（单位：亿美元）
    tam = 11050  # 全球法律服务市场
    sam = 351    # 中国法律服务市场
    som_3y = 5.2  # 3年目标市场份额（1.5%）
    som_5y = 17.5 # 5年目标市场份额（5%）

    sizes = [tam, sam, som_5y, som_3y]
    labels = ['TAM\nGlobal Legal\nServices\n$1,105B',
             'SAM\nChina Legal\nServices\n$35.1B',
             'SOM (5Y)\nTarget Market\n$1.75B (5%)',
             'SOM (3Y)\nInitial Target\n$0.52B (1.5%)']
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']

    # 创建嵌套圆形
    for i, (size, label, color) in enumerate(zip(sizes, labels, colors)):
        radius = np.sqrt(size)
        circle = plt.Circle((0, 0), radius, color=color, alpha=0.3, linewidth=3,
                          edgecolor=color, fill=True)
        ax.add_patch(circle)

        # 添加标签
        angle = 45 + i * 30
        x = radius * 0.7 * np.cos(np.radians(angle))
        y = radius * 0.7 * np.sin(np.radians(angle))
        ax.text(x, y, label, fontsize=10, fontweight='bold',
               ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    ax.set_xlim(-120, 120)
    ax.set_ylim(-120, 120)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('TAM/SAM/SOM Analysis - Crime Journal Market Opportunity',
                fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "07_tam_sam_som.png", dpi=300, bbox_inches='tight')
    plt.close()

    return {
        'cn': "TAM（总可达市场）为全球法律服务市场11050亿美元，SAM（可服务市场）聚焦中国市场351亿美元，SOM（可获得市场）设定3年目标5.2亿美元（占SAM的1.5%），5年目标17.5亿美元（占SAM的5%）。",
        'en': "TAM (Total Addressable Market) is $1,105B global legal services, SAM (Serviceable Available Market) focuses on China's $35.1B market, SOM (Serviceable Obtainable Market) targets $0.52B in 3 years (1.5% of SAM) and $1.75B in 5 years (5% of SAM)."
    }

def plot_user_segments():
    """图8: 目标用户群体规模"""
    legal_df = pd.read_csv(DATA_DIR / "processed/legal_professionals_panel.csv")

    # 2025年数据
    china_2025 = legal_df[(legal_df['country'] == 'China') & (legal_df['year'] == 2025)].iloc[0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 左图：用户群体规模
    categories = ['Lawyers', 'Police', 'Researchers']
    values = [china_2025['lawyer_count']/1000,
             china_2025['police_count']/1000,
             china_2025['legal_researchers']/1000]
    colors = ['#3498db', '#e74c3c', '#2ecc71']

    bars = ax1.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('Population (Thousands)', fontsize=12, fontweight='bold')
    ax1.set_title('Target User Segments in China (2025)', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')

    # 添加数值标签
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.0f}K', ha='center', va='bottom', fontweight='bold')

    # 右图：市场渗透率预测
    years = [1, 2, 3, 4, 5]
    penetration = [0.5, 2.0, 5.0, 10.0, 15.0]  # 渗透率%

    ax2.plot(years, penetration, marker='o', linewidth=3, markersize=10, color='#e74c3c')
    ax2.fill_between(years, penetration, alpha=0.2, color='#e74c3c')
    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Market Penetration (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Projected Market Penetration (5-Year)', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(years)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "08_user_segments.png", dpi=300, bbox_inches='tight')
    plt.close()

    return {
        'cn': "中国目标用户群体庞大：律师83万、警察210万、法律研究人员14.1万，合计307万潜在用户。市场渗透率预测：第1年0.5%，第3年5%，第5年15%，对应用户规模从1.5万增至46万。",
        'en': "China's target user base is substantial: 830K lawyers, 2.1M police, 141K researchers, totaling 3.07M potential users. Projected penetration: Year 1 at 0.5%, Year 3 at 5%, Year 5 at 15%, corresponding to 15K-460K users."
    }

if __name__ == "__main__":
    print("Chart 6...")
    plot_market_growth_rate()
    print("Chart 6 done")

    print("Chart 7...")
    plot_tam_sam_som()
    print("Chart 7 done")

    print("Chart 8...")
    plot_user_segments()
    print("Chart 8 done")

    print("All charts completed!")
