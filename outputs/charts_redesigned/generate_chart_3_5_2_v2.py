#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 3.5.2 V2: Cross-Border Case Association Network (Enhanced)
Larger fonts and clearer labels
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

plt.style.use('dark_background')

# Create figure
fig, ax = plt.subplots(figsize=(16, 12), facecolor='none')
ax.set_facecolor('none')

# Create directed graph
G = nx.DiGraph()

# Add nodes with attributes
nodes = {
    'Uruguay': {'pos': (0, 0), 'color': '#b24bf3', 'size': 4000},
    'Bolivia': {'pos': (2, -1), 'color': '#00d9ff', 'size': 5000},
    'Paraguay': {'pos': (4, -1), 'color': '#00ff88', 'size': 3500},
    'USA': {'pos': (2, -3), 'color': '#ff6b6b', 'size': 4500},
    'Banks': {'pos': (4, -3), 'color': '#ffd93d', 'size': 3800}
}

for node, attrs in nodes.items():
    G.add_node(node, **attrs)

# Add edges with weights
edges = [
    ('Uruguay', 'Bolivia', 0.9),
    ('Bolivia', 'Paraguay', 0.7),
    ('Bolivia', 'USA', 0.85),
    ('USA', 'Banks', 0.8),
    ('Paraguay', 'Banks', 0.6)
]

for src, dst, weight in edges:
    G.add_edge(src, dst, weight=weight)

# Get positions
pos = {node: attrs['pos'] for node, attrs in nodes.items()}

# Draw edges with glow effect
for alpha, width_mult in [(0.3, 3), (0.6, 2), (1.0, 1)]:
    for (u, v, d) in G.edges(data=True):
        weight = d['weight']
        nx.draw_networkx_edges(G, pos, [(u, v)],
                              width=weight * 10 * width_mult,
                              alpha=alpha * 0.5,
                              edge_color='#ffffff',
                              arrows=True,
                              arrowsize=30,
                              arrowstyle='-|>',
                              connectionstyle='arc3,rad=0.1',
                              ax=ax)

# Draw nodes with glow effect
for node, attrs in nodes.items():
    for alpha, size_mult in [(0.3, 1.5), (0.6, 1.2), (1.0, 1.0)]:
        nx.draw_networkx_nodes(G, pos, [node],
                              node_size=attrs['size'] * size_mult,
                              node_color=attrs['color'],
                              alpha=alpha,
                              edgecolors='white',
                              linewidths=3,
                              ax=ax)

# Draw labels with larger font
labels = {node: node for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels,
                       font_size=40,
                       font_color='#ffffff',
                       font_weight='bold',
                       ax=ax)

# Add edge labels (connection strength)
for u, v, d in G.edges(data=True):
    mid_x = (pos[u][0] + pos[v][0]) / 2
    mid_y = (pos[u][1] + pos[v][1]) / 2
    weight_pct = int(d['weight'] * 100)
    ax.text(mid_x, mid_y + 0.25, f"{weight_pct}%",
           fontsize=36, color='#ffd93d', ha='center', fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#0a0e27',
                    edgecolor='#ffd93d', alpha=0.9, linewidth=2))

# Add annotations with larger font
annotations = [
    (0, 0.6, 'Drug Lord Origin', '#b24bf3'),
    (2, -0.4, '2022 Arrest', '#00d9ff'),
    (2, -3.6, '2026 Indictment', '#ff6b6b'),
    (4, -3.6, 'Money Laundering', '#ffd93d')
]

for x, y, text, color in annotations:
    ax.text(x, y, text, fontsize=32, color=color,
           style='italic', ha='center', fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.6', facecolor='#1a1d2e',
                    edgecolor=color, alpha=0.8, linewidth=2.5))

# Title
ax.set_title('Cross-Border Case Association Network\nBolivia Drug Trafficking Case (Sebastián Marset)',
            fontsize=56, color='#00d9ff', fontweight='bold', pad=30)

# Legend with larger font
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#b24bf3',
              markersize=16, label='Origin Country', linestyle='None', markeredgewidth=2, markeredgecolor='white'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#00d9ff',
              markersize=16, label='Arrest Location', linestyle='None', markeredgewidth=2, markeredgecolor='white'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff6b6b',
              markersize=16, label='Indictment Country', linestyle='None', markeredgewidth=2, markeredgecolor='white'),
    plt.Line2D([0], [0], color='#ffffff', linewidth=4, label='Connection Strength')
]
legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=32,
                  framealpha=0.9, facecolor='#1a1d2e', edgecolor='#00d9ff',
                  labelcolor='#e0e0e0')
legend.get_frame().set_linewidth(2.5)

ax.axis('off')
ax.set_xlim(-1, 5)
ax.set_ylim(-4.5, 1.2)

plt.tight_layout()
plt.savefig('3_5_2_cross_border_network_v2.png', dpi=600, transparent=True, bbox_inches='tight')
print("Chart 3.5.2 V2 generated: 3_5_2_cross_border_network_v2.png")
