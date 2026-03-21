#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 3.5.1: Similar Case Matching (Argentina Murder Case)
Dark theme with neon colors
"""

import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')

# Data
cases = ['Madrid Shooting\n(Spain)', 'Mexico City Murder\n(Mexico)', 'Chicago Shooting\n(USA)']
similarity = [78, 72, 68]
colors = ['#00d9ff', '#b24bf3', '#00ff88']

# Create figure
fig, ax = plt.subplots(figsize=(12, 7), facecolor='#0a0e27')
ax.set_facecolor('#0a0e27')

# Create horizontal bars with glow effect
y_pos = np.arange(len(cases))
for alpha, offset in [(0.3, 0.4), (0.6, 0.2), (1.0, 0)]:
    bars = ax.barh(y_pos, similarity, height=0.6,
                   color=colors, alpha=alpha, zorder=2)

# Add value labels
for i, (case, sim, color) in enumerate(zip(cases, similarity, colors)):
    ax.text(sim + 2, i, f'{sim}%',
            va='center', fontsize=14, color=color, fontweight='bold')

# Add reference line at 70%
ax.axvline(x=70, color='#ff6b6b', linestyle='--', linewidth=2, alpha=0.5, zorder=1)
ax.text(70, -0.6, 'High Similarity Threshold (70%)',
        ha='center', fontsize=10, color='#ff6b6b', style='italic')

# Styling
ax.set_yticks(y_pos)
ax.set_yticklabels(cases, fontsize=12, color='#e0e0e0')
ax.set_xlabel('Similarity Score (%)', fontsize=14, color='#e0e0e0', fontweight='bold')
ax.set_title('Similar Case Recommendations\nArgentina Murder Case (Keyword Matching)',
             fontsize=16, color='#00d9ff', fontweight='bold', pad=20)

ax.set_xlim(0, 100)
ax.grid(True, axis='x', alpha=0.2, color='#404040', linestyle='--', linewidth=0.5)
ax.tick_params(colors='#e0e0e0', labelsize=11)

for spine in ax.spines.values():
    spine.set_edgecolor('#404040')
    spine.set_linewidth(1.5)

plt.tight_layout()
plt.savefig('3_5_1_similar_cases_dark.png', dpi=300, facecolor='#0a0e27', bbox_inches='tight')
print("Chart 3.5.1 generated: 3_5_1_similar_cases_dark.png")
