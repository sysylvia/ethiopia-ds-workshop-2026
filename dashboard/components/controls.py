"""
Control panel components for the Ethiopia ABM dashboard.

Provides:
- Scenario selection dropdown
- Play/Pause button
- Reset button
- Speed slider
- Month scrubber
"""

import streamlit as st
from typing import Dict, List, Optional


def render_scenario_selector(scenarios: Dict[str, Dict], current_scenario: str) -> str:
    """
    Render scenario selection dropdown.

    Args:
        scenarios: Dict of {scenario_id: {'name': str, 'totals': dict}}
        current_scenario: Currently selected scenario ID

    Returns:
        Selected scenario ID
    """
    scenario_options = {
        sid: data['name'] for sid, data in scenarios.items()
    }

    # Create reverse mapping for display
    display_options = list(scenario_options.values())
    current_display = scenario_options.get(current_scenario, display_options[0])

    selected_display = st.selectbox(
        'Scenario',
        options=display_options,
        index=display_options.index(current_display) if current_display in display_options else 0,
        key='scenario_selector'
    )

    # Map back to scenario ID
    for sid, name in scenario_options.items():
        if name == selected_display:
            return sid

    return current_scenario


def render_playback_controls():
    """
    Render playback control buttons (Play/Pause, Reset).

    Uses session state for is_playing and current_month.
    """
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.get('is_playing', False):
            if st.button('Pause', key='pause_btn', use_container_width=True):
                st.session_state.is_playing = False
                st.rerun()
        else:
            if st.button('Play', key='play_btn', use_container_width=True, type='primary'):
                st.session_state.is_playing = True
                st.rerun()

    with col2:
        if st.button('Reset', key='reset_btn', use_container_width=True):
            st.session_state.current_month = 1
            st.session_state.is_playing = False
            # Clear slider widget state so it syncs with session state
            if 'month_scrubber' in st.session_state:
                del st.session_state['month_scrubber']
            st.rerun()


def render_speed_slider() -> float:
    """
    Render speed control slider with explicit labels.

    Returns:
        Speed multiplier (0.5 - 3.0)
    """
    st.caption('Speed: 0.5x (slow) — 3.0x (fast)')
    speed = st.slider(
        'Speed',
        min_value=0.5,
        max_value=3.0,
        value=st.session_state.get('speed', 1.0),
        step=0.5,
        format='%.1fx',
        key='speed_slider',
        label_visibility='collapsed'
    )
    st.session_state.speed = speed
    return speed


def _on_month_change():
    """Callback for user-initiated month changes via slider."""
    st.session_state.is_playing = False
    st.session_state.current_month = st.session_state.month_scrubber


def render_month_scrubber(max_months: int = 60) -> int:
    """
    Render month scrubber slider.

    Args:
        max_months: Maximum month value

    Returns:
        Selected month (from session state, not widget)
    """
    current = st.session_state.get('current_month', 1)

    st.slider(
        'Month',
        min_value=1,
        max_value=max_months,
        value=min(current, max_months),
        key='month_scrubber',
        on_change=_on_month_change  # Only fires on USER interaction
    )

    # Return session state value (updated by animation or callback)
    return st.session_state.get('current_month', 1)


def render_metrics_bar(months_data: List[Dict], current_month: int):
    """
    Render key metrics bar at bottom of dashboard.

    Args:
        months_data: List of monthly data dicts
        current_month: Current month being displayed
    """
    if current_month < 1 or current_month > len(months_data):
        return

    current_data = months_data[current_month - 1]

    # Calculate cumulative metrics
    cum_shortages = sum(
        sum(m['shortages'].values())
        for m in months_data[:current_month]
    )
    cum_deaths = sum(
        sum(m['deaths'].values())
        for m in months_data[:current_month]
    )
    cum_wastage = sum(
        sum(m['wastage'].values())
        for m in months_data[:current_month]
    )
    treatment_rate = current_data['treatment_rate'] * 100

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label='Month',
            value=f'{current_month}/60',
            delta=f'Year {(current_month - 1) // 12 + 1}'
        )

    with col2:
        # Show delta from previous month
        prev_short = cum_shortages - sum(current_data['shortages'].values())
        delta = sum(current_data['shortages'].values())
        st.metric(
            label='Total Shortages',
            value=f'{cum_shortages:,}',
            delta=f'+{delta:,}' if delta > 0 else '0',
            delta_color='inverse'
        )

    with col3:
        delta = sum(current_data['deaths'].values())
        st.metric(
            label='Total Deaths',
            value=f'{cum_deaths:,}',
            delta=f'+{delta:,}' if delta > 0 else '0',
            delta_color='inverse'
        )

    with col4:
        st.metric(
            label='Treatment Rate',
            value=f'{treatment_rate:.1f}%',
            delta=None
        )


def render_scenario_summary(scenario_data: Dict):
    """
    Render scenario summary information.

    Args:
        scenario_data: Loaded scenario data dict
    """
    totals = scenario_data.get('totals', {})

    st.markdown(f"**{scenario_data.get('scenario_name', 'Unknown')}**")

    with st.expander('Final Outcomes (60 months)'):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Shortages', f"{totals.get('shortages', 0):,}")
        with col2:
            st.metric('Deaths', f"{totals.get('deaths', 0):,}")
        with col3:
            st.metric('Wastage', f"{totals.get('wastage', 0):,}")


def init_session_state():
    """Initialize session state variables if not present."""
    defaults = {
        'current_month': 1,
        'is_playing': False,
        'speed': 1.0,
        'particle_phase': 0.0,
        'scenario': 'base'
    }

    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default
