#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart 3.5.2: Cross-Border Case Association Network (Bolivia Drug Case)
Dark theme with neon colors
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

plt.style.use('dark_background')

# Create figure
fig, ax = plt.subplots(figsize=(14, 10), facecolor='#0a0e27')
ax.set_facecolor('#0a0e27')

# Create directed graph
G = nx.DiGraph()

# Add nodes with attributes
nodes = {
    'Uruguay': {'pos': (0, 0), 'color': '#b24bf3', 'size': 3000},
    'Bolivia': {'pos': (2, -1), 'color': '#00d9ff', 'size': 4000},
    'Paraguay': {'pos': (4, -1), 'color': '#00ff88', 'size': 2500},
    'USA': {'pos': (2, -3), 'color': '#ff6b6b', 'size': 3500},
    'Banks': {'pos': (4, -3), 'color': '#ffd93d', 'size': 2800}
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
                              width=weight * 8 * width_mult,
                              alpha=alpha * 0.5,
                              edge_color='#ffffff',
                              arrows=True,
                              arrowsize=20,
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
                              ax=ax)

# Draw labels
labels = {node: node for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels,
                       font_size=13,
                       font_color='#ffffff',
                       font_weight='bold',
                       ax=ax)

# Add edge labels (connection strength)
edge_labels = {}
for u, v, d in G.edges(data=True):
    mid_x = (pos[u][0] + pos[v][0]) / 2
    mid_y = (pos[u][1] + pos[v][1]) / 2
    weight_pct = int(d['weight'] * 100)
    ax.text(mid_x, mid_y + 0.2, f"{weight_pct}%",
           fontsize=10, color='#ffd93d', ha='center',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0e27',
                    edgecolor='#ffd93d', alpha=0.8))

# Add annotations
annotations = [
    (0, 0.5, 'Drug Lord Origin', '#b24bf3'),
    (2, -0.5, '2022 Arrest', '#00d9ff'),
    (2, -3.5, '2026 Indictment', '#ff6b6b'),
    (4, -3.5, 'Money Laundering', '#ffd93d')
]

for x, y, text, color in annotations:
    ax.text(x, y, text, fontsize=10, color=color,
           style='italic', ha='center',
           bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1d2e',
                    edgecolor=color, alpha=0.7, linewidth=1.5))

# Title
ax.set_title('Cross-Border Case Association Network\nBolivia Drug Trafficking Case (Sebastián Marset)',
            fontsize=16, color='#00d9ff', fontweight='bold', pad=20)

# Legend
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#b24bf3',
              markersize=12, label='Origin Country', linestyle='None'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#00d9ff',
              markersize=12, label='Arrest Location', linestyle='None'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff6b6b',
              markersize=12, label='Indictment Country', linestyle='None'),
    plt.Line2D([0], [0], color='#ffffff', linewidth=3, label='Connection Strength')
]
legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=11,
                  framealpha=0.8, facecolor='#1a1d2e', edgecolor='#00d9ff',
                  labelcolor='#e0e0e0')
legend.get_frame().set_linewidth(2)

ax.axis('off')
ax.set_xlim(-1, 5)
ax.set_ylim(-4.5, 1)

plt.tight_layout()
plt.savefig('3_5_2_cross_border_network_dark.png', dpi=300, facecolor='#0a0e27', bbox_inches='tight')
print("Chart 3.5.2 generated: 3_5_2_cross_border_network_dark.png")
