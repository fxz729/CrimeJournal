#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 3.5.1 V2: Similar Case Matching (Enhanced)
Gradient colors + larger fonts
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

plt.style.use('dark_background')

# Data
cases = ['Madrid Shooting\n(Spain)', 'Mexico City Murder\n(Mexico)', 'Chicago Shooting\n(USA)']
similarity = [78, 72, 68]

# Gradient colors (from light to dark for each bar)
color_gradients = [
    ['#00d9ff', '#0088cc'],  # Cyan gradient
    ['#b24bf3', '#7a1fb8'],  # Purple gradient
    ['#00ff88', '#00cc66']   # Green gradient
]

# Create figure
fig, ax = plt.subplots(figsize=(14, 8), facecolor='#0a0e27')
ax.set_facecolor('#0a0e27')

# Create horizontal bars with gradient
y_pos = np.arange(len(cases))
bar_height = 0.6

for i, (case, sim) in enumerate(zip(cases, similarity)):
    # Glow effect layers
    for alpha, offset in [(0.2, 0.5), (0.4, 0.3)]:
        ax.barh(y_pos[i], sim, height=bar_height + offset,
               color=color_gradients[i][0], alpha=alpha, zorder=1)

    # Main gradient bar
    bar = ax.barh(y_pos[i], sim, height=bar_height,
                  color=color_gradients[i][0], zorder=2, edgecolor='white', linewidth=2)

    # Add inner gradient effect
    rect = Rectangle((0, y_pos[i] - bar_height/2), sim, bar_height,
                     facecolor=color_gradients[i][1], alpha=0.3, zorder=3)
    ax.add_patch(rect)

# Add value labels with larger font
for i, (sim, colors) in enumerate(zip(similarity, color_gradients)):
    ax.text(sim + 3, i, f'{sim}%',
            va='center', fontsize=28, color=colors[0], fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#0a0e27',
                     edgecolor=colors[0], linewidth=2, alpha=0.9))

# Reference line
ax.axvline(x=70, color='#ff6b6b', linestyle='--', linewidth=3, alpha=0.6, zorder=1)
ax.text(70, -0.7, 'High Similarity Threshold (70%)',
        ha='center', fontsize=20, color='#ff6b6b', style='italic',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1d2e',
                 edgecolor='#ff6b6b', alpha=0.8))

# Styling
ax.set_yticks(y_pos)
ax.set_yticklabels(cases, fontsize=24, color='#e0e0e0', fontweight='bold')
ax.set_xlabel('Similarity Score (%)', fontsize=28, color='#e0e0e0', fontweight='bold')
ax.set_title('Similar Case Recommendations\nArgentina Murder Case (Keyword Matching)',
             fontsize=32, color='#00d9ff', fontweight='bold', pad=30)

ax.set_xlim(0, 100)
ax.grid(True, axis='x', alpha=0.15, color='#404040', linestyle='--', linewidth=1)
ax.tick_params(colors='#e0e0e0', labelsize=22)

for spine in ax.spines.values():
    spine.set_edgecolor('#404040')
    spine.set_linewidth(2)

plt.tight_layout()
plt.savefig('3_5_1_similar_cases_v2.png', dpi=300, facecolor='#0a0e27', bbox_inches='tight')
print("Chart 3.5.1 V2 generated: 3_5_1_similar_cases_v2.png")
