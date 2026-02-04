"""
Network graph visualization for the Ethiopia ABM supply chain.

Shows hierarchical layout with:
- Manufacturers at top
- Central Medical Store
- Regional Hospitals
- CHC Regions at bottom

Nodes colored by stock level, edges show shipment flows.
"""

import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Optional


# Workshop color scheme
COLORS = {
    'primary': '#4A7C59',
    'secondary': '#6B8E23',
    'success': '#228B22',
    'info': '#5F9EA0',
    'warning': '#DAA520',
    'danger': '#CD5C5C',
    'light': '#F5F5F5',
    'dark': '#333333',
    'white': '#FFFFFF',
}


def stock_to_color(stock: int, capacity: int) -> str:
    """Convert stock level to color (red=low, yellow=medium, green=healthy)."""
    if capacity == 0:
        return COLORS['light']
    ratio = stock / capacity
    if ratio < 0.2:
        return COLORS['danger']
    elif ratio < 0.4:
        return COLORS['warning']
    else:
        return COLORS['success']


def stock_to_opacity(stock: int, capacity: int) -> float:
    """Make low stock nodes more visually prominent."""
    if capacity == 0:
        return 0.5
    ratio = stock / capacity
    return max(0.4, min(1.0, 0.4 + ratio * 0.6))


def build_network_positions() -> Dict[str, tuple]:
    """
    Build fixed positions for network nodes in hierarchical layout.

    Returns dict of {node_id: (x, y)}
    """
    positions = {}

    # Manufacturers (top row)
    positions['MFR_0'] = (-0.3, 1.0)
    positions['MFR_1'] = (0.3, 1.0)

    # Central Medical Store
    positions['CMS_0'] = (0.0, 0.66)

    # Hospitals
    positions['HOSP_0'] = (-0.5, 0.33)
    positions['HOSP_1'] = (0.0, 0.33)
    positions['HOSP_2'] = (0.5, 0.33)

    # CHC Regions (aggregated)
    positions['CHC_Region_0'] = (-0.5, 0.0)
    positions['CHC_Region_1'] = (0.0, 0.0)
    positions['CHC_Region_2'] = (0.5, 0.0)

    return positions


def build_static_edges() -> List[tuple]:
    """
    Build static edge list for the supply chain.

    Returns list of (source, target) tuples.
    """
    edges = [
        # Manufacturers to CMS
        ('MFR_0', 'CMS_0'),
        ('MFR_1', 'CMS_0'),
        # CMS to Hospitals
        ('CMS_0', 'HOSP_0'),
        ('CMS_0', 'HOSP_1'),
        ('CMS_0', 'HOSP_2'),
        # Hospitals to CHC Regions
        ('HOSP_0', 'CHC_Region_0'),
        ('HOSP_1', 'CHC_Region_1'),
        ('HOSP_2', 'CHC_Region_2'),
    ]
    return edges


def create_network_figure(
    stock_levels: Dict,
    shipments: List[Dict],
    particle_phase: float = 0.0,
    show_particles: bool = True
) -> go.Figure:
    """
    Create the network visualization figure.

    Args:
        stock_levels: Dict with 'manufacturers', 'central_stores', 'hospitals', 'chc_regions'
        shipments: List of shipment dicts with 'from', 'to', 'quantity'
        particle_phase: Animation phase (0-1) for particle positions
        show_particles: Whether to show animated particles

    Returns:
        Plotly Figure object
    """
    positions = build_network_positions()
    edges = build_static_edges()

    fig = go.Figure()

    # Add edges (supply chain links)
    edge_x = []
    edge_y = []
    for src, tgt in edges:
        x0, y0 = positions[src]
        x1, y1 = positions[tgt]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    fig.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=2, color=COLORS['light']),
        hoverinfo='none',
        showlegend=False
    ))

    # Calculate shipment volumes for edge thickness
    edge_volumes = {}
    for shipment in shipments:
        key = (shipment['from'], shipment['to'])
        edge_volumes[key] = edge_volumes.get(key, 0) + shipment['quantity']

    # Add thicker edges for active shipments
    if edge_volumes:
        max_vol = max(edge_volumes.values()) if edge_volumes else 1
        for (src, tgt), vol in edge_volumes.items():
            # Map shipment source/target to network nodes
            src_node = src
            tgt_node = tgt
            # Handle CHC aggregation
            if tgt.startswith('CHC_') and not tgt.startswith('CHC_Region'):
                # Find which region this CHC belongs to
                chc_num = int(tgt.split('_')[1])
                region_idx = (chc_num - 1) % 3
                tgt_node = f'CHC_Region_{region_idx}'

            if src_node in positions and tgt_node in positions:
                x0, y0 = positions[src_node]
                x1, y1 = positions[tgt_node]
                width = 2 + 8 * (vol / max_vol)

                fig.add_trace(go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode='lines',
                    line=dict(width=width, color=COLORS['primary']),
                    opacity=0.5,
                    hoverinfo='none',
                    showlegend=False
                ))

    # Add particles on edges (animated flow indicators)
    if show_particles and edge_volumes:
        particle_x = []
        particle_y = []
        for (src, tgt), vol in edge_volumes.items():
            src_node = src
            tgt_node = tgt
            if tgt.startswith('CHC_') and not tgt.startswith('CHC_Region'):
                chc_num = int(tgt.split('_')[1])
                region_idx = (chc_num - 1) % 3
                tgt_node = f'CHC_Region_{region_idx}'

            if src_node in positions and tgt_node in positions:
                x0, y0 = positions[src_node]
                x1, y1 = positions[tgt_node]

                # Multiple particles per edge based on volume
                n_particles = max(1, int(3 * vol / max(edge_volumes.values())))
                for i in range(n_particles):
                    # Stagger particles along the edge
                    t = (particle_phase + i / n_particles) % 1.0
                    px = x0 + t * (x1 - x0)
                    py = y0 + t * (y1 - y0)
                    particle_x.append(px)
                    particle_y.append(py)

        if particle_x:
            fig.add_trace(go.Scatter(
                x=particle_x,
                y=particle_y,
                mode='markers',
                marker=dict(size=8, color=COLORS['warning'], symbol='circle'),
                hoverinfo='none',
                showlegend=False
            ))

    # Build node data
    node_data = []

    # Manufacturers
    for mfr in stock_levels.get('manufacturers', []):
        node_data.append({
            'id': mfr['id'],
            'label': f"MFR {mfr['id'].split('_')[1]}",
            'stock': mfr['stock'],
            'capacity': mfr['capacity'],
            'type': 'manufacturer',
            'operational': mfr.get('operational', True)
        })

    # Central Stores
    for cms in stock_levels.get('central_stores', []):
        node_data.append({
            'id': cms['id'],
            'label': 'EPSA',
            'stock': cms['stock'],
            'capacity': cms['capacity'],
            'type': 'central_store'
        })

    # Hospitals
    for hosp in stock_levels.get('hospitals', []):
        node_data.append({
            'id': hosp['id'],
            'label': f"Hospital {hosp['id'].split('_')[1]}",
            'stock': hosp['stock'],
            'capacity': hosp['capacity'],
            'type': 'hospital'
        })

    # CHC Regions
    for region in stock_levels.get('chc_regions', []):
        node_data.append({
            'id': region['id'],
            'label': f"CHCs ({region['num_chcs']})",
            'stock': region['stock'],
            'capacity': region['capacity'],
            'type': 'chc_region'
        })

    # Add nodes
    node_x = []
    node_y = []
    node_colors = []
    node_sizes = []
    node_text = []
    node_customdata = []

    for node in node_data:
        if node['id'] in positions:
            x, y = positions[node['id']]
            node_x.append(x)
            node_y.append(y)

            # Color based on stock level
            if node.get('type') == 'manufacturer' and not node.get('operational', True):
                node_colors.append(COLORS['danger'])
            else:
                node_colors.append(stock_to_color(node['stock'], node['capacity']))

            # Size based on capacity (normalized)
            base_size = 30
            if node['type'] == 'manufacturer':
                node_sizes.append(base_size + 15)
            elif node['type'] == 'central_store':
                node_sizes.append(base_size + 20)
            elif node['type'] == 'hospital':
                node_sizes.append(base_size + 10)
            else:
                node_sizes.append(base_size + 5)

            # Hover text
            pct = (node['stock'] / node['capacity'] * 100) if node['capacity'] > 0 else 0
            status = ''
            if node.get('type') == 'manufacturer' and not node.get('operational', True):
                status = ' (OFFLINE)'
            node_text.append(
                f"<b>{node['label']}{status}</b><br>"
                f"Stock: {node['stock']:,}<br>"
                f"Capacity: {node['capacity']:,}<br>"
                f"Fill: {pct:.0f}%"
            )
            node_customdata.append(node['label'])

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color=COLORS['dark']),
            opacity=0.9
        ),
        text=[n['label'] for n in node_data if n['id'] in positions],
        textposition='bottom center',
        textfont=dict(size=10, color=COLORS['dark']),
        hovertext=node_text,
        hoverinfo='text',
        showlegend=False
    ))

    # Layout
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1, 1]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.2, 1.2],
            scaleanchor='x',
            scaleratio=1
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )

    # Add layer labels
    fig.add_annotation(x=-0.9, y=1.0, text="Manufacturers", showarrow=False,
                       font=dict(size=10, color=COLORS['dark']), xanchor='left')
    fig.add_annotation(x=-0.9, y=0.66, text="Central Store", showarrow=False,
                       font=dict(size=10, color=COLORS['dark']), xanchor='left')
    fig.add_annotation(x=-0.9, y=0.33, text="Hospitals", showarrow=False,
                       font=dict(size=10, color=COLORS['dark']), xanchor='left')
    fig.add_annotation(x=-0.9, y=0.0, text="CHC Regions", showarrow=False,
                       font=dict(size=10, color=COLORS['dark']), xanchor='left')

    return fig
