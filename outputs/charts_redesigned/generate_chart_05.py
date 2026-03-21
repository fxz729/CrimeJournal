#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 05: Competitive Analysis Radar Chart
Dark theme with neon colors
"""

import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')

categories = ['Data\nCoverage', 'AI\nFeatures', 'User\nExperience', 'Price', 'Update\nSpeed']
crime_journal = [8, 9, 8, 9, 10]
pkulaw = [9, 3, 5, 6, 8]
westlaw = [10, 7, 6, 3, 9]

angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
crime_journal += crime_journal[:1]
pkulaw += pkulaw[:1]
westlaw += westlaw[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'), facecolor='#0a0e27')
ax.set_facecolor('#0a0e27')

# Plot with glow
ax.plot(angles, crime_journal, 'o-', linewidth=3, color='#4dd0e1', label='Crime Journal', markersize=8)
ax.fill(angles, crime_journal, alpha=0.25, color='#4dd0e1')

ax.plot(angles, pkulaw, 'o-', linewidth=2, color='#808080', label='Pkulaw', alpha=0.6, markersize=6)
ax.fill(angles, pkulaw, alpha=0.1, color='#808080')

ax.plot(angles, westlaw, 'o-', linewidth=2, color='#606060', label='Westlaw', alpha=0.6, markersize=6)
ax.fill(angles, westlaw, alpha=0.1, color='#606060')

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=12, color='#e0e0e0', fontweight='bold')
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=10, color='#808080')
ax.grid(True, color='#404040', alpha=0.3, linewidth=1)

ax.set_title('Competitive Analysis Radar Chart',
             fontsize=18, color='#4dd0e1', fontweight='bold', pad=30, y=1.08)

legend = ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11,
                   framealpha=0.8, facecolor='#1a1d2e', edgecolor='#4dd0e1', labelcolor='#e0e0e0')
legend.get_frame().set_linewidth(2)

ax.tick_params(colors='#e0e0e0')
ax.spines['polar'].set_color('#404040')
ax.spines['polar'].set_linewidth(1.5)

plt.tight_layout()
plt.savefig('05_competitor_radar_dark.png', dpi=300, facecolor='#0a0e27', bbox_inches='tight')
print("Chart 05 generated: 05_competitor_radar_dark.png")
