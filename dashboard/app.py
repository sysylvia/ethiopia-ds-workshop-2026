"""
Ethiopia Antibiotic Supply Chain ABM - Animated Dashboard

WISE Workshop | Addis Ababa, Feb 2026

This Streamlit dashboard provides an animated visualization of the
Ethiopia antibiotic supply chain ABM. Features include:
- Animated network graph showing medicine flow through supply chain
- Synchronized time-series charts for key metrics
- Interactive scenario selection and playback controls

Usage:
    streamlit run app.py

For development:
    streamlit run app.py --server.runOnSave true
"""

import json
import time
from pathlib import Path

import streamlit as st

from components.network_graph import create_network_figure
from components.time_charts import (
    create_shortages_chart,
    create_deaths_chart,
    create_stock_chart,
    create_treatment_rate_chart
)
from components.controls import (
    init_session_state,
    render_scenario_selector,
    render_playback_controls,
    render_speed_slider,
    render_month_scrubber,
    render_metrics_bar
)
from components.animation import AnimationController

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title='Ethiopia ABM Dashboard',
    page_icon='🏥',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS for clean appearance
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Reduce padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }

    /* Style metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }

    /* Style headers */
    .main-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #4A7C59;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 1rem;
    }

    /* Reduce chart container spacing */
    .element-container {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Data Loading
# ============================================================================

@st.cache_data
def load_scenario_index():
    """Load scenario index file."""
    index_path = Path(__file__).parent / 'data' / 'scenarios' / 'index.json'
    if index_path.exists():
        with open(index_path) as f:
            return json.load(f)
    return {}


@st.cache_data
def load_scenario_data(scenario_id: str):
    """Load pre-computed scenario data."""
    data_path = Path(__file__).parent / 'data' / 'scenarios' / f'{scenario_id}.json'
    if data_path.exists():
        with open(data_path) as f:
            return json.load(f)
    return None


# ============================================================================
# Main Application
# ============================================================================

def main():
    # Initialize session state
    init_session_state()

    # Create animation controller
    anim = AnimationController(max_months=60)

    # Load scenario index
    scenarios = load_scenario_index()

    if not scenarios:
        st.error('No scenario data found. Please run `python data/precompute.py` first.')
        return

    # Header
    st.markdown('<div class="main-header">Ethiopia Antibiotic Supply Chain Simulation</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">WISE Workshop | Addis Ababa, Feb 2026</div>',
                unsafe_allow_html=True)

    # Sidebar controls
    with st.sidebar:
        st.header('Controls')

        # Scenario selector
        selected_scenario = render_scenario_selector(scenarios, st.session_state.get('scenario', 'base'))

        # Update scenario in state if changed
        if selected_scenario != st.session_state.get('scenario'):
            st.session_state.scenario = selected_scenario
            st.session_state.current_month = 1
            st.session_state.is_playing = False
            # Clear slider widget state so it syncs with session state
            if 'month_scrubber' in st.session_state:
                del st.session_state['month_scrubber']
            anim.reset()
            st.rerun()

        st.divider()

        # Playback controls
        render_playback_controls()

        st.divider()

        # Speed control
        speed = render_speed_slider()

        # Month scrubber
        month = render_month_scrubber(max_months=60)

        st.divider()

        # Scenario info
        scenario_data = load_scenario_data(st.session_state.get('scenario', 'base'))
        if scenario_data:
            st.markdown(f"**{scenario_data.get('scenario_name', 'Unknown')}**")
            totals = scenario_data.get('totals', {})
            with st.expander('60-Month Totals'):
                st.metric('Shortages', f"{totals.get('shortages', 0):,}")
                st.metric('Deaths', f"{totals.get('deaths', 0):,}")
                st.metric('Wastage', f"{totals.get('wastage', 0):,}")

    # Load current scenario data
    scenario_data = load_scenario_data(st.session_state.get('scenario', 'base'))

    if not scenario_data:
        st.error(f"Could not load scenario: {st.session_state.get('scenario')}")
        return

    months_data = scenario_data.get('months', [])
    current_month = st.session_state.get('current_month', 1)

    if current_month < 1:
        current_month = 1
    if current_month > len(months_data):
        current_month = len(months_data)

    current_data = months_data[current_month - 1] if months_data else {}

    # Main content area - split layout
    col_network, col_charts = st.columns([1, 1.2])

    with col_network:
        st.subheader('Supply Chain Network')

        # Create network graph
        network_fig = create_network_figure(
            stock_levels=current_data.get('stock_levels', {}),
            shipments=current_data.get('shipments', []),
            particle_phase=st.session_state.get('particle_phase', 0.0),
            show_particles=True
        )

        st.plotly_chart(network_fig, use_container_width=True, config={'displayModeBar': False})

        # Legend
        st.markdown("""
        <div style="font-size: 0.8rem; color: #666;">
        <b>Node colors:</b>
        🟢 Healthy stock (>40%) |
        🟡 Low stock (20-40%) |
        🔴 Critical (<20%)
        </div>
        """, unsafe_allow_html=True)

    with col_charts:
        st.subheader('Key Metrics Over Time')

        # 2x2 grid of charts
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # Shortages chart
            shortages_fig = create_shortages_chart(months_data, current_month)
            st.plotly_chart(shortages_fig, use_container_width=True, config={'displayModeBar': False})

            # Stock levels chart
            stock_fig = create_stock_chart(months_data, current_month)
            st.plotly_chart(stock_fig, use_container_width=True, config={'displayModeBar': False})

        with chart_col2:
            # Deaths chart
            deaths_fig = create_deaths_chart(months_data, current_month)
            st.plotly_chart(deaths_fig, use_container_width=True, config={'displayModeBar': False})

            # Treatment rate chart
            treatment_fig = create_treatment_rate_chart(months_data, current_month)
            st.plotly_chart(treatment_fig, use_container_width=True, config={'displayModeBar': False})

    # Metrics bar at bottom
    st.divider()
    render_metrics_bar(months_data, current_month)

    # Animation: auto-rerun when playing
    if st.session_state.get('is_playing', False):
        current = st.session_state.get('current_month', 1)
        speed = st.session_state.get('speed', 1.0)

        if current < 60:
            # Calculate delay based on speed
            delay = 1.0 / speed
            time.sleep(delay)

            # Advance animation state
            st.session_state.current_month = current + 1
            st.session_state.particle_phase = (st.session_state.get('particle_phase', 0.0) + 0.15) % 1.0

            st.rerun()
        else:
            st.session_state.is_playing = False
            st.rerun()


if __name__ == '__main__':
    main()
