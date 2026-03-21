#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 06: Market Growth Rate (2015-2025)
Dark theme with neon colors
"""

import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')

years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
china_growth = [12.5, 14.0, 15.3, 12.0, 8.3, 10.3, 6.3, 4.7, 3.9, 1.7]
global_growth = [4.6, 4.4, 4.9, 4.0, 1.9, 9.5, 7.5, 7.5, 7.0, 3.3]
us_growth = [3.9, 3.8, 4.4, 4.0, 1.1, 8.9, 6.1, 5.8, 4.5, 3.5]

fig, ax = plt.subplots(figsize=(14, 8), facecolor='#0a0e27')
ax.set_facecolor('#0a0e27')

for alpha, lw in [(0.3, 8), (0.6, 4), (1.0, 2.5)]:
    ax.plot(years, china_growth, color='#b24bf3', alpha=alpha, linewidth=lw)
    ax.plot(years, global_growth, color='#00d9ff', alpha=alpha, linewidth=lw)
    ax.plot(years, us_growth, color='#00ff88', alpha=alpha, linewidth=lw)

ax.scatter(years, china_growth, color='#b24bf3', s=100, zorder=3, edgecolors='white', linewidths=1.5)
ax.scatter(years, global_growth, color='#00d9ff', s=100, zorder=3, edgecolors='white', linewidths=1.5)
ax.scatter(years, us_growth, color='#00ff88', s=100, zorder=3, edgecolors='white', linewidths=1.5)

# Highlight peak
ax.annotate('Peak: 15.3%', xy=(2018, 15.3), xytext=(2018, 17),
            color='#b24bf3', fontsize=11, ha='center', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#b24bf3', lw=2))

ax.grid(True, alpha=0.2, color='#404040', linestyle='--', linewidth=0.5)
ax.set_xlabel('Year', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_ylabel('Annual Growth Rate (%)', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_title('Legal Services Market Growth Rate (2016-2025)',
             fontsize=18, color='#b24bf3', fontweight='bold', pad=20)

legend = ax.legend(['China', 'Global', 'United States'],
                   loc='upper right', fontsize=12, framealpha=0.8,
                   facecolor='#1a1d2e', edgecolor='#b24bf3', labelcolor='#e0e0e0')
legend.get_frame().set_linewidth(2)

ax.tick_params(colors='#e0e0e0', labelsize=11)
for spine in ax.spines.values():
    spine.set_edgecolor('#404040')
    spine.set_linewidth(1.5)

plt.tight_layout()
plt.savefig('06_market_growth_rate_dark.png', dpi=300, facecolor='#0a0e27', bbox_inches='tight')
print("Chart 06 generated: 06_market_growth_rate_dark.png")
