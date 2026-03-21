#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 02: Lawyer Population Growth by Country (2015-2025)
Dark theme with neon colors
"""

import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')

# Data (in thousands)
years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
china = [297, 336, 380, 430, 487, 551, 623, 705, 753, 790, 830]
india = [1250, 1350, 1450, 1550, 1650, 1750, 1850, 1950, 2050, 2120, 2175]
us = [1281, 1300, 1315, 1328, 1340, 1350, 1360, 1370, 1380, 1390, 1400]

fig, ax = plt.subplots(figsize=(14, 8), facecolor='#0a0e27')
ax.set_facecolor('#0a0e27')

# Plot with glow
for alpha, lw in [(0.3, 8), (0.6, 4), (1.0, 2.5)]:
    ax.plot(years, china, color='#4dd0e1', alpha=alpha, linewidth=lw)
    ax.plot(years, india, color='#e91e63', alpha=alpha, linewidth=lw)
    ax.plot(years, us, color='#ffd60a', alpha=alpha, linewidth=lw)

ax.scatter(years, china, color='#4dd0e1', s=120, zorder=3, edgecolors='white', linewidths=2)
ax.scatter(years, india, color='#e91e63', s=120, zorder=3, edgecolors='white', linewidths=2)
ax.scatter(years, us, color='#ffd60a', s=120, zorder=3, edgecolors='white', linewidths=2)

# Annotations
ax.text(2025, 830, '830K\n(+179%)', color='#4dd0e1', fontsize=11, ha='left', va='center', fontweight='bold')
ax.text(2025, 2175, '2,175K\n(+74%)', color='#e91e63', fontsize=11, ha='left', va='center', fontweight='bold')
ax.text(2025, 1400, '1,400K\n(+9%)', color='#ffd60a', fontsize=11, ha='left', va='center', fontweight='bold')

ax.grid(True, alpha=0.2, color='#404040', linestyle='--', linewidth=0.5)
ax.set_xlabel('Year', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_ylabel('Number of Lawyers (Thousands)', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_title('Lawyer Population Growth by Country (2015-2025)',
             fontsize=18, color='#00d9ff', fontweight='bold', pad=20)

legend = ax.legend(['China', 'India', 'United States'],
                   loc='upper left', fontsize=12, framealpha=0.8,
                   facecolor='#1a1d2e', edgecolor='#00d9ff', labelcolor='#e0e0e0')
legend.get_frame().set_linewidth(2)

ax.tick_params(colors='#e0e0e0', labelsize=11)
for spine in ax.spines.values():
    spine.set_edgecolor('#404040')
    spine.set_linewidth(1.5)

plt.tight_layout()
plt.savefig('02_lawyer_growth_dark.png', dpi=300, facecolor='#0a0e27', bbox_inches='tight')
print("Chart 02 generated: 02_lawyer_growth_dark.png")
