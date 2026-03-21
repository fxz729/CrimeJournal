#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 01: Legal Services Market Size Trend (2015-2025)
Dark theme with neon colors
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

# Set dark background style
plt.style.use('dark_background')

# Data
years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
global_market = [650, 680, 710, 745, 775, 790, 865, 930, 1000, 1070, 1105]  # Billion USD
china_market = [15.2, 17.1, 19.5, 22.5, 25.2, 27.3, 30.1, 32.0, 33.5, 34.8, 35.1]  # Billion USD
us_market = [380, 395, 410, 428, 445, 450, 490, 520, 550, 575, 595]  # Billion USD

# Create figure
fig, ax = plt.subplots(figsize=(14, 8), facecolor='#0a0e27')
ax.set_facecolor('#0a0e27')

# Plot lines with glow effect
for alpha, lw in [(0.3, 8), (0.6, 4), (1.0, 2)]:
    ax.plot(years, global_market, color='#00d9ff', alpha=alpha, linewidth=lw, zorder=2)
    ax.plot(years, china_market, color='#b24bf3', alpha=alpha, linewidth=lw, zorder=2)
    ax.plot(years, us_market, color='#00ff88', alpha=alpha, linewidth=lw, zorder=2)

# Add markers
ax.scatter(years, global_market, color='#00d9ff', s=100, zorder=3, edgecolors='white', linewidths=1.5)
ax.scatter(years, china_market, color='#b24bf3', s=100, zorder=3, edgecolors='white', linewidths=1.5)
ax.scatter(years, us_market, color='#00ff88', s=100, zorder=3, edgecolors='white', linewidths=1.5)

# Add value labels for key years
for year in [2015, 2020, 2025]:
    idx = years.index(year)
    ax.text(year, global_market[idx] + 30, f'${global_market[idx]}B',
            color='#00d9ff', fontsize=10, ha='center', fontweight='bold')
    ax.text(year, china_market[idx] + 2, f'${china_market[idx]}B',
            color='#b24bf3', fontsize=10, ha='center', fontweight='bold')

# Grid
ax.grid(True, alpha=0.2, color='#404040', linestyle='--', linewidth=0.5)

# Labels and title
ax.set_xlabel('Year', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_ylabel('Market Size (Billion USD)', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_title('Legal Services Market Size Trend (2015-2025)',
             fontsize=18, color='#00d9ff', fontweight='bold', pad=20)

# Legend
legend = ax.legend(['Global Market', 'China Market', 'US Market'],
                   loc='upper left', fontsize=12, framealpha=0.8,
                   facecolor='#1a1d2e', edgecolor='#00d9ff', labelcolor='#e0e0e0')
legend.get_frame().set_linewidth(2)

# Tick colors
ax.tick_params(colors='#e0e0e0', labelsize=11)

# Spine colors
for spine in ax.spines.values():
    spine.set_edgecolor('#404040')
    spine.set_linewidth(1.5)

plt.tight_layout()
plt.savefig('01_market_size_trend_dark.png', dpi=300, facecolor='#0a0e27', edgecolor='none', bbox_inches='tight')
print("Chart 01 generated: 01_market_size_trend_dark.png")
