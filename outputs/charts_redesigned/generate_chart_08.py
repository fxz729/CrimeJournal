#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 08: Target User Segments & Market Penetration
Dark theme with neon colors
"""

import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), facecolor='#0a0e27')
fig.patch.set_facecolor('#0a0e27')

# Left: User segments pie chart
segments = ['Lawyers\n830K', 'Police\n2,100K', 'Researchers\n141K']
sizes = [830, 2100, 141]
colors = ['#00d9ff', '#b24bf3', '#00ff88']
explode = (0.05, 0.05, 0.05)

ax1.set_facecolor('#0a0e27')
wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=segments, colors=colors,
                                     autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12, 'color': 'white', 'fontweight': 'bold'},
                                     wedgeprops={'edgecolor': 'white', 'linewidth': 2})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')

ax1.set_title('Target User Segments\n(Total: 3.07M)', fontsize=16, color='#00d9ff', fontweight='bold', pad=20)

# Right: Penetration rate over years
ax2.set_facecolor('#0a0e27')
years = [1, 2, 3, 4, 5]
penetration = [0.5, 2.0, 5.0, 10.0, 15.0]
users = [15, 61.4, 153.5, 307, 460.5]

color = '#b24bf3'
for alpha, lw in [(0.3, 8), (0.6, 4), (1.0, 3)]:
    ax2.plot(years, penetration, color=color, alpha=alpha, linewidth=lw)

ax2.scatter(years, penetration, color=color, s=150, zorder=3, edgecolors='white', linewidths=2)

for year, pen, user in zip(years, penetration, users):
    ax2.text(year, pen + 0.8, f'{pen}%\n({user:.1f}K users)', ha='center', va='bottom',
             color=color, fontsize=10, fontweight='bold')

ax2.fill_between(years, penetration, alpha=0.2, color=color)
ax2.grid(True, alpha=0.2, color='#404040', linestyle='--', linewidth=0.5)
ax2.set_xlabel('Year', fontsize=13, color='#e0e0e0', fontweight='bold')
ax2.set_ylabel('Market Penetration Rate (%)', fontsize=13, color='#e0e0e0', fontweight='bold')
ax2.set_title('Market Penetration Roadmap\n(Conservative Strategy)', fontsize=16, color='#b24bf3', fontweight='bold', pad=20)
ax2.set_xticks(years)
ax2.set_xticklabels([f'Y{y}' for y in years])
ax2.tick_params(colors='#e0e0e0', labelsize=11)

for spine in ax2.spines.values():
    spine.set_edgecolor('#404040')
    spine.set_linewidth(1.5)

plt.tight_layout()
plt.savefig('08_user_segments_dark.png', dpi=300, facecolor='#0a0e27', bbox_inches='tight')
print("Chart 08 generated: 08_user_segments_dark.png")
