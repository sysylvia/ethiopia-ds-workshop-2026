"""
Time-series chart components for the Ethiopia ABM dashboard.

Four charts in 2x2 grid:
1. Shortages by medicine type (stacked area)
2. Deaths by age group (line chart)
3. Stock levels across supply chain (stacked bar)
4. Treatment rate over time (line with fill)
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
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
}

# Medicine type colors
MEDICINE_COLORS = {
    'Penicillins': COLORS['primary'],
    'Macrolides': COLORS['info'],
    'Fluoroquinolones': COLORS['warning']
}

# Age group colors
AGE_COLORS = {
    'child': '#4169E1',  # Royal blue
    'adult': '#228B22',  # Forest green
    'elderly': '#CD5C5C'  # Indian red
}


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert hex color to rgba string."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r},{g},{b},{alpha})'


def create_shortages_chart(
    months_data: List[Dict],
    current_month: int,
    max_months: int = 60
) -> go.Figure:
    """Create stacked area chart of shortages by medicine type."""
    fig = go.Figure()

    # Extract data up to current month
    months = list(range(1, current_month + 1))
    medicine_types = ['Penicillins', 'Macrolides', 'Fluoroquinolones']

    for med_type in medicine_types:
        values = [
            months_data[i - 1]['shortages'].get(med_type, 0)
            for i in months
        ]
        fig.add_trace(go.Scatter(
            x=months,
            y=values,
            mode='lines',
            name=med_type,
            line=dict(width=0),
            fill='tonexty' if med_type != 'Penicillins' else 'tozeroy',
            fillcolor=hex_to_rgba(MEDICINE_COLORS[med_type], 0.5),
            hovertemplate=f'{med_type}: %{{y:,.0f}}<extra></extra>'
        ))

    # Add current month marker
    fig.add_vline(x=current_month, line_dash='dash', line_color=COLORS['dark'], line_width=1)

    fig.update_layout(
        title=dict(text='Shortages by Medicine Type', font=dict(size=14)),
        xaxis=dict(
            title='Month',
            range=[1, max_months],
            tickmode='linear',
            dtick=12,
            showgrid=True,
            gridcolor=COLORS['light']
        ),
        yaxis=dict(
            title='Shortage Events',
            showgrid=True,
            gridcolor=COLORS['light']
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=10)
        ),
        margin=dict(l=50, r=20, t=50, b=40),
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250
    )

    return fig


def create_deaths_chart(
    months_data: List[Dict],
    current_month: int,
    max_months: int = 60
) -> go.Figure:
    """Create line chart of deaths by age group."""
    fig = go.Figure()

    months = list(range(1, current_month + 1))
    age_groups = ['child', 'adult', 'elderly']
    age_labels = {'child': 'Children', 'adult': 'Adults', 'elderly': 'Elderly'}

    for age in age_groups:
        values = [
            months_data[i - 1]['deaths'].get(age, 0)
            for i in months
        ]
        fig.add_trace(go.Scatter(
            x=months,
            y=values,
            mode='lines',
            name=age_labels[age],
            line=dict(width=2, color=AGE_COLORS[age]),
            hovertemplate=f'{age_labels[age]}: %{{y:,.0f}}<extra></extra>'
        ))

    # Add current month marker
    fig.add_vline(x=current_month, line_dash='dash', line_color=COLORS['dark'], line_width=1)

    fig.update_layout(
        title=dict(text='Deaths by Age Group', font=dict(size=14)),
        xaxis=dict(
            title='Month',
            range=[1, max_months],
            tickmode='linear',
            dtick=12,
            showgrid=True,
            gridcolor=COLORS['light']
        ),
        yaxis=dict(
            title='Deaths',
            showgrid=True,
            gridcolor=COLORS['light']
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=10)
        ),
        margin=dict(l=50, r=20, t=50, b=40),
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250
    )

    return fig


def create_stock_chart(
    months_data: List[Dict],
    current_month: int,
    max_months: int = 60
) -> go.Figure:
    """Create grouped bar chart of stock levels across supply chain tiers."""
    fig = go.Figure()

    # Get current month data
    if current_month > 0 and current_month <= len(months_data):
        stock_levels = months_data[current_month - 1]['stock_levels']
    else:
        stock_levels = {'manufacturers': [], 'central_stores': [], 'hospitals': [], 'chc_regions': []}

    # Calculate totals by tier
    tiers = ['Manufacturers', 'Central Store', 'Hospitals', 'CHC Regions']
    tier_stocks = []
    tier_capacities = []

    # Manufacturers
    mfr_stock = sum(m['stock'] for m in stock_levels.get('manufacturers', []))
    mfr_cap = sum(m['capacity'] for m in stock_levels.get('manufacturers', []))
    tier_stocks.append(mfr_stock)
    tier_capacities.append(mfr_cap)

    # Central Store
    cms_stock = sum(c['stock'] for c in stock_levels.get('central_stores', []))
    cms_cap = sum(c['capacity'] for c in stock_levels.get('central_stores', []))
    tier_stocks.append(cms_stock)
    tier_capacities.append(cms_cap)

    # Hospitals
    hosp_stock = sum(h['stock'] for h in stock_levels.get('hospitals', []))
    hosp_cap = sum(h['capacity'] for h in stock_levels.get('hospitals', []))
    tier_stocks.append(hosp_stock)
    tier_capacities.append(hosp_cap)

    # CHC Regions
    chc_stock = sum(r['stock'] for r in stock_levels.get('chc_regions', []))
    chc_cap = sum(r['capacity'] for r in stock_levels.get('chc_regions', []))
    tier_stocks.append(chc_stock)
    tier_capacities.append(chc_cap)

    # Color based on fill percentage
    colors = []
    for stock, cap in zip(tier_stocks, tier_capacities):
        if cap == 0:
            colors.append(COLORS['light'])
        else:
            ratio = stock / cap
            if ratio < 0.2:
                colors.append(COLORS['danger'])
            elif ratio < 0.4:
                colors.append(COLORS['warning'])
            else:
                colors.append(COLORS['success'])

    fig.add_trace(go.Bar(
        x=tiers,
        y=tier_stocks,
        marker_color=colors,
        text=[f'{s:,.0f}' for s in tier_stocks],
        textposition='outside',
        hovertemplate='%{x}<br>Stock: %{y:,.0f}<extra></extra>'
    ))

    # Add capacity reference line
    fig.add_trace(go.Scatter(
        x=tiers,
        y=tier_capacities,
        mode='markers',
        marker=dict(symbol='line-ew', size=20, color=COLORS['dark'], line_width=2),
        name='Capacity',
        hovertemplate='%{x}<br>Capacity: %{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text=f'Stock Levels (Month {current_month})', font=dict(size=14)),
        xaxis=dict(title=None),
        yaxis=dict(
            title='Units',
            showgrid=True,
            gridcolor=COLORS['light']
        ),
        showlegend=False,
        margin=dict(l=50, r=20, t=50, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250
    )

    return fig


def create_treatment_rate_chart(
    months_data: List[Dict],
    current_month: int,
    max_months: int = 60
) -> go.Figure:
    """Create line chart of treatment rate over time."""
    fig = go.Figure()

    months = list(range(1, current_month + 1))
    treatment_rates = [
        months_data[i - 1]['treatment_rate'] * 100
        for i in months
    ]

    fig.add_trace(go.Scatter(
        x=months,
        y=treatment_rates,
        mode='lines',
        name='Treatment Rate',
        line=dict(width=2, color=COLORS['primary']),
        fill='tozeroy',
        fillcolor=hex_to_rgba(COLORS['primary'], 0.2),
        hovertemplate='Treatment Rate: %{y:.1f}%<extra></extra>'
    ))

    # Add 100% reference line
    fig.add_hline(y=100, line_dash='dot', line_color=COLORS['success'], line_width=1)

    # Add current month marker
    fig.add_vline(x=current_month, line_dash='dash', line_color=COLORS['dark'], line_width=1)

    fig.update_layout(
        title=dict(text='Treatment Rate', font=dict(size=14)),
        xaxis=dict(
            title='Month',
            range=[1, max_months],
            tickmode='linear',
            dtick=12,
            showgrid=True,
            gridcolor=COLORS['light']
        ),
        yaxis=dict(
            title='% Patients Treated',
            range=[0, 105],
            showgrid=True,
            gridcolor=COLORS['light']
        ),
        showlegend=False,
        margin=dict(l=50, r=20, t=50, b=40),
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250
    )

    return fig


def create_combined_charts(
    months_data: List[Dict],
    current_month: int,
    max_months: int = 60
) -> go.Figure:
    """Create combined 2x2 subplot figure with all four charts."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Shortages by Medicine Type', 'Deaths by Age Group',
                       f'Stock Levels (Month {current_month})', 'Treatment Rate'),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    months = list(range(1, current_month + 1))

    # Chart 1: Shortages (row 1, col 1)
    medicine_types = ['Penicillins', 'Macrolides', 'Fluoroquinolones']
    for med_type in medicine_types:
        values = [months_data[i - 1]['shortages'].get(med_type, 0) for i in months]
        fig.add_trace(go.Scatter(
            x=months, y=values, mode='lines', name=med_type,
            line=dict(width=0),
            fill='tonexty' if med_type != 'Penicillins' else 'tozeroy',
            fillcolor=hex_to_rgba(MEDICINE_COLORS[med_type], 0.5),
            legendgroup='shortages',
            showlegend=True
        ), row=1, col=1)

    # Chart 2: Deaths (row 1, col 2)
    age_labels = {'child': 'Children', 'adult': 'Adults', 'elderly': 'Elderly'}
    for age in ['child', 'adult', 'elderly']:
        values = [months_data[i - 1]['deaths'].get(age, 0) for i in months]
        fig.add_trace(go.Scatter(
            x=months, y=values, mode='lines', name=age_labels[age],
            line=dict(width=2, color=AGE_COLORS[age]),
            legendgroup='deaths',
            showlegend=True
        ), row=1, col=2)

    # Chart 3: Stock levels (row 2, col 1)
    if current_month > 0 and current_month <= len(months_data):
        stock_levels = months_data[current_month - 1]['stock_levels']
        tiers = ['MFR', 'CMS', 'HOSP', 'CHC']
        tier_stocks = [
            sum(m['stock'] for m in stock_levels.get('manufacturers', [])),
            sum(c['stock'] for c in stock_levels.get('central_stores', [])),
            sum(h['stock'] for h in stock_levels.get('hospitals', [])),
            sum(r['stock'] for r in stock_levels.get('chc_regions', []))
        ]
        tier_caps = [
            sum(m['capacity'] for m in stock_levels.get('manufacturers', [])),
            sum(c['capacity'] for c in stock_levels.get('central_stores', [])),
            sum(h['capacity'] for h in stock_levels.get('hospitals', [])),
            sum(r['capacity'] for r in stock_levels.get('chc_regions', []))
        ]
        colors = []
        for s, c in zip(tier_stocks, tier_caps):
            r = s / c if c > 0 else 0
            colors.append(COLORS['danger'] if r < 0.2 else COLORS['warning'] if r < 0.4 else COLORS['success'])

        fig.add_trace(go.Bar(
            x=tiers, y=tier_stocks, marker_color=colors,
            showlegend=False
        ), row=2, col=1)

    # Chart 4: Treatment rate (row 2, col 2)
    treatment_rates = [months_data[i - 1]['treatment_rate'] * 100 for i in months]
    fig.add_trace(go.Scatter(
        x=months, y=treatment_rates, mode='lines',
        line=dict(width=2, color=COLORS['primary']),
        fill='tozeroy', fillcolor=hex_to_rgba(COLORS['primary'], 0.2),
        showlegend=False
    ), row=2, col=2)

    # Add current month markers
    for row in [1, 1, 2]:
        for col in [1, 2, 2]:
            if not (row == 2 and col == 1):  # Skip bar chart
                fig.add_vline(x=current_month, line_dash='dash', line_color=COLORS['dark'],
                             line_width=1, row=row, col=col)

    fig.update_xaxes(range=[1, max_months], row=1, col=1)
    fig.update_xaxes(range=[1, max_months], row=1, col=2)
    fig.update_xaxes(range=[1, max_months], row=2, col=2)
    fig.update_yaxes(range=[0, 105], row=2, col=2)

    fig.update_layout(
        height=500,
        margin=dict(l=50, r=20, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.08,
            xanchor='center',
            x=0.5,
            font=dict(size=9)
        ),
        hovermode='x unified'
    )

    return fig
