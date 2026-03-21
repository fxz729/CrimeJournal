#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 07: TAM/SAM/SOM Analysis
Dark theme with neon colors - Funnel visualization
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.style.use('dark_background')

fig, ax = plt.subplots(figsize=(10, 10), facecolor='#0a0e27')
ax.set_facecolor('#0a0e27')

# Funnel data
levels = ['TAM\n$1,105B', 'SAM\n$35.1B', 'SOM (Y3)\n$0.52B', 'SOM (Y5)\n$1.75B']
values = [1105, 35.1, 0.52, 1.75]
colors = ['#00d9ff', '#4dd0e1', '#b24bf3', '#e91e63']

# Draw funnel
y_positions = [0.8, 0.55, 0.3, 0.05]
widths = [0.9, 0.6, 0.35, 0.45]

for i, (level, value, color, y_pos, width) in enumerate(zip(levels, values, colors, y_positions, widths)):
    # Rectangle with glow
    for alpha, lw in [(0.2, 8), (0.5, 4), (1.0, 2)]:
        rect = mpatches.FancyBboxPatch((0.5 - width/2, y_pos - 0.1), width, 0.2,
                                       boxstyle="round,pad=0.01",
                                       edgecolor=color, facecolor=color,
                                       alpha=alpha, linewidth=lw)
        ax.add_patch(rect)

    # Text
    ax.text(0.5, y_pos, level, ha='center', va='center',
            fontsize=16, color='white', fontweight='bold')

# Descriptions
descriptions = [
    'Total Addressable Market\nGlobal Legal Services',
    'Serviceable Available Market\nChina Legal Services (8.7% CAGR)',
    'Serviceable Obtainable Market\nYear 3 Target (1.5% share)',
    'Year 5 Target (5% share)'
]

for i, (desc, y_pos) in enumerate(zip(descriptions, y_positions)):
    ax.text(1.05, y_pos, desc, ha='left', va='center',
            fontsize=28, color='#e0e0e0', style='italic')

ax.set_xlim(0, 1.8)
ax.set_ylim(-0.1, 1.0)
ax.axis('off')

ax.set_title('TAM / SAM / SOM Analysis - Market Opportunity Funnel',
             fontsize=18, color='#00d9ff', fontweight='bold', pad=20, y=0.98)

plt.tight_layout()
plt.savefig('07_tam_sam_som_dark.png', dpi=300, facecolor='#0a0e27', bbox_inches='tight')
print("Chart 07 generated: 07_tam_sam_som_dark.png")
