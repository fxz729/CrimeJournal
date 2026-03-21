#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 03: Pain Points Quantified - Case Search Time & Cost
Dark theme with neon colors
"""

import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')

categories = ['Lawyer\n(China)', 'Lawyer\n(US)', 'Police\n(China)', 'Police\n(US)']
time_hours = [1890, 3276, 2688, 3325]
cost_thousands = [151.2, 819.0, 94.08, 182.875]

x = np.arange(len(categories))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 8), facecolor='#0a0e27')
ax.set_facecolor('#0a0e27')

# Bars with gradient effect
bars1 = ax.bar(x - width/2, time_hours, width, label='Annual Time Cost (Hours)',
               color='#ff0055', edgecolor='white', linewidth=1.5, alpha=0.9)
bars2 = ax.bar(x + width/2, [c*10 for c in cost_thousands], width, label='Annual Cost ($K × 10)',
               color='#00d9ff', edgecolor='white', linewidth=1.5, alpha=0.9)

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}h', ha='center', va='bottom', color='#ff0055', fontsize=10, fontweight='bold')

for i, bar in enumerate(bars2):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'${cost_thousands[i]:.1f}K', ha='center', va='bottom', color='#00d9ff', fontsize=10, fontweight='bold')

ax.set_xlabel('User Type', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_ylabel('Annual Cost', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_title('User Pain Points - Annual Time & Cost Waste',
             fontsize=18, color='#ff0055', fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=12, color='#e0e0e0')

legend = ax.legend(loc='upper left', fontsize=11, framealpha=0.8,
                   facecolor='#1a1d2e', edgecolor='#ff0055', labelcolor='#e0e0e0')
legend.get_frame().set_linewidth(2)

ax.grid(True, alpha=0.2, color='#404040', linestyle='--', linewidth=0.5, axis='y')
ax.tick_params(colors='#e0e0e0', labelsize=11)
for spine in ax.spines.values():
    spine.set_edgecolor('#404040')
    spine.set_linewidth(1.5)

plt.tight_layout()
plt.savefig('03_pain_points_quantified_dark.png', dpi=300, facecolor='#0a0e27', bbox_inches='tight')
print("Chart 03 generated: 03_pain_points_quantified_dark.png")
