"""
Animation state management for the Ethiopia ABM dashboard.

Handles:
- Frame timing and progression
- Particle animation phases
- Smooth playback control
"""

import streamlit as st
import time
from typing import Optional, Callable


def advance_animation(speed: float = 1.0, max_months: int = 60) -> bool:
    """
    Advance the animation by one frame.

    Args:
        speed: Speed multiplier (1.0 = 1 month per second)
        max_months: Maximum month value

    Returns:
        True if animation should continue, False if ended
    """
    current = st.session_state.get('current_month', 1)
    is_playing = st.session_state.get('is_playing', False)

    if not is_playing:
        return False

    # Check if we've reached the end
    if current >= max_months:
        st.session_state.is_playing = False
        return False

    # Advance month
    st.session_state.current_month = current + 1

    # Update particle phase (cycles 0-1)
    phase = st.session_state.get('particle_phase', 0.0)
    st.session_state.particle_phase = (phase + 0.1 * speed) % 1.0

    return True


def get_frame_delay(speed: float = 1.0) -> float:
    """
    Calculate delay between frames based on speed.

    Args:
        speed: Speed multiplier

    Returns:
        Delay in seconds
    """
    # Base rate: 1 month per second at speed=1.0
    base_delay = 1.0
    return base_delay / speed


def animate_with_fragment(update_callback: Callable, speed: float = 1.0, max_months: int = 60):
    """
    Run animation loop using Streamlit's fragment mechanism.

    This is called from within a st.fragment decorated function.

    Args:
        update_callback: Function to call on each frame update
        speed: Speed multiplier
        max_months: Maximum month value
    """
    if st.session_state.get('is_playing', False):
        if advance_animation(speed, max_months):
            update_callback()
            time.sleep(get_frame_delay(speed))
            st.rerun(scope='fragment')


class AnimationController:
    """
    Controller class for managing animation state.

    Provides a cleaner interface for animation management.
    """

    def __init__(self, max_months: int = 60, default_speed: float = 1.0):
        self.max_months = max_months
        self.default_speed = default_speed

    @property
    def current_month(self) -> int:
        return st.session_state.get('current_month', 1)

    @current_month.setter
    def current_month(self, value: int):
        st.session_state.current_month = max(1, min(value, self.max_months))

    @property
    def is_playing(self) -> bool:
        return st.session_state.get('is_playing', False)

    @is_playing.setter
    def is_playing(self, value: bool):
        st.session_state.is_playing = value

    @property
    def speed(self) -> float:
        return st.session_state.get('speed', self.default_speed)

    @speed.setter
    def speed(self, value: float):
        st.session_state.speed = max(0.5, min(3.0, value))

    @property
    def particle_phase(self) -> float:
        return st.session_state.get('particle_phase', 0.0)

    def play(self):
        """Start playback."""
        self.is_playing = True

    def pause(self):
        """Pause playback."""
        self.is_playing = False

    def reset(self):
        """Reset to beginning."""
        self.current_month = 1
        self.is_playing = False
        st.session_state.particle_phase = 0.0

    def toggle(self):
        """Toggle play/pause."""
        self.is_playing = not self.is_playing

    def step_forward(self):
        """Advance one month."""
        if self.current_month < self.max_months:
            self.current_month += 1
            self._update_particle_phase()

    def step_backward(self):
        """Go back one month."""
        if self.current_month > 1:
            self.current_month -= 1

    def seek(self, month: int):
        """Jump to specific month."""
        self.current_month = month
        self.pause()

    def _update_particle_phase(self):
        """Update particle animation phase."""
        phase = self.particle_phase
        st.session_state.particle_phase = (phase + 0.1 * self.speed) % 1.0

    def tick(self) -> bool:
        """
        Advance animation by one tick if playing.

        Returns:
            True if animation is still running
        """
        if not self.is_playing:
            return False

        if self.current_month >= self.max_months:
            self.pause()
            return False

        self.step_forward()
        return True

    def get_frame_delay(self) -> float:
        """Get delay in seconds for current speed."""
        return 1.0 / self.speed
