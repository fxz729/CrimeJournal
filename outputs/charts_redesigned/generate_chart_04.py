#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 04: Homicide Rate Trends (2015-2023)
Dark theme with neon colors
"""

import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')

years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
china = [0.62, 0.58, 0.55, 0.52, 0.49, 0.46, 0.44, 0.43, 0.42]
us = [5.3, 5.4, 5.4, 5.0, 5.0, 6.5, 6.8, 6.3, 5.72]
india = [3.21, 3.15, 3.08, 3.01, 2.95, 2.88, 2.82, 2.75, 2.68]

fig, ax = plt.subplots(figsize=(14, 8), facecolor='#0a0e27')
ax.set_facecolor('#0a0e27')

# Glow effect
for alpha, lw in [(0.3, 8), (0.6, 4), (1.0, 2.5)]:
    ax.plot(years, us, color='#ff0055', alpha=alpha, linewidth=lw)
    ax.plot(years, china, color='#00d9ff', alpha=alpha, linewidth=lw)
    ax.plot(years, india, color='#00ff88', alpha=alpha, linewidth=lw)

ax.scatter(years, us, color='#ff0055', s=100, zorder=3, edgecolors='white', linewidths=1.5)
ax.scatter(years, china, color='#00d9ff', s=100, zorder=3, edgecolors='white', linewidths=1.5)
ax.scatter(years, india, color='#00ff88', s=100, zorder=3, edgecolors='white', linewidths=1.5)

# Fill area
ax.fill_between(years, us, alpha=0.15, color='#ff0055')
ax.fill_between(years, china, alpha=0.15, color='#00d9ff')
ax.fill_between(years, india, alpha=0.15, color='#00ff88')

# Annotations
ax.text(2023, 5.72, '5.72', color='#ff0055', fontsize=11, ha='left', fontweight='bold')
ax.text(2023, 0.42, '0.42 (-32%)', color='#00d9ff', fontsize=11, ha='left', fontweight='bold')
ax.text(2023, 2.68, '2.68', color='#00ff88', fontsize=11, ha='left', fontweight='bold')

ax.grid(True, alpha=0.2, color='#404040', linestyle='--', linewidth=0.5)
ax.set_xlabel('Year', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_ylabel('Homicide Rate (per 100,000)', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_title('Homicide Rate Trends (2015-2023)',
             fontsize=18, color='#ff0055', fontweight='bold', pad=20)

legend = ax.legend(['United States', 'China', 'India'],
                   loc='upper right', fontsize=12, framealpha=0.8,
                   facecolor='#1a1d2e', edgecolor='#ff0055', labelcolor='#e0e0e0')
legend.get_frame().set_linewidth(2)

ax.tick_params(colors='#e0e0e0', labelsize=11)
for spine in ax.spines.values():
    spine.set_edgecolor('#404040')
    spine.set_linewidth(1.5)

plt.tight_layout()
plt.savefig('04_crime_trends_dark.png', dpi=300, facecolor='#0a0e27', bbox_inches='tight')
print("Chart 04 generated: 04_crime_trends_dark.png")
