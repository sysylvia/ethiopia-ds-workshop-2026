# Ethiopia ABM Dashboard - Improvement Roadmap

**Evaluation Date:** 2026-02-04
**Evaluated URL:** https://huggingface.co/spaces/sysylvia/ethiopia-abm-dashboard
**Evaluator:** Helix (Claude Opus 4.5)

---

## Executive Summary

The Ethiopia ABM Dashboard successfully deploys to HuggingFace Spaces and provides a functional visualization of the antibiotic supply chain simulation. Core functionality (scenario switching, manual month navigation, network visualization, time-series charts) works well. However, **critical bugs in the animation system** prevent the Play/Reset buttons from working as intended.

### Overall Assessment
- **Functionality:** 70% - Core features work, animation broken
- **Performance:** 85% - Fast load time, responsive interactions
- **Usability:** 75% - Clear layout, some UX improvements needed
- **Visual Design:** 85% - Professional appearance, good color coding

---

## Priority 1: Critical (Blocking Issues)

### C1. Play Button Animation Not Working
**Description:** Clicking Play changes button to "Pause" but the month slider never advances. Animation loop doesn't execute.

**Impact:** Users cannot watch the simulation unfold over time - the primary feature of an animated dashboard.

**Root Cause Analysis:**
In `components/controls.py:95-120`, the `render_month_scrubber()` function contains logic that sets `is_playing = False` when the slider widget value differs from `current_month` (line 117). This creates a race condition:
1. Play button sets `is_playing = True`
2. `st.rerun()` is called
3. On rerun, the slider widget may not immediately reflect the new `current_month`
4. The check `if month != current` triggers, setting `is_playing = False`

**Recommended Fix:**
```python
# In render_month_scrubber(), only pause if user EXPLICITLY moved the slider
# Add a flag to distinguish user interaction from programmatic updates
def render_month_scrubber(max_months: int = 60) -> int:
    current = st.session_state.get('current_month', 1)

    month = st.slider(
        'Month',
        min_value=1,
        max_value=max_months,
        value=min(current, max_months),
        key='month_scrubber'
    )

    # Only pause if user manually dragged AND we're playing
    # Use on_change callback instead of value comparison
    return month

# Alternative: Use st.slider's on_change parameter
```

**Complexity:** Medium (requires careful state management testing)

---

### C2. Reset Button Not Resetting Month
**Description:** Clicking Reset does not return the month slider to 1. The slider visually shows the old value even though `st.session_state.current_month` is set to 1.

**Impact:** Users cannot restart the simulation from the beginning without refreshing the page.

**Root Cause Analysis:**
The Reset button (line 69-72 in controls.py) correctly sets `current_month = 1` in session state, but the slider widget has its own state via `key='month_scrubber'`. Streamlit widgets with keys maintain their own state that may not sync immediately.

**Recommended Fix:**
```python
# Option 1: Clear the widget key to force fresh render
if st.button('Reset', key='reset_btn', use_container_width=True):
    st.session_state.current_month = 1
    st.session_state.is_playing = False
    # Clear the slider's internal state
    if 'month_scrubber' in st.session_state:
        del st.session_state['month_scrubber']
    st.rerun()

# Option 2: Use value parameter more carefully
# Ensure the slider's value= parameter is bound to session state
```

**Complexity:** Low

---

## Priority 2: High (Significant UX Issues)

### H1. Scenario Switch Should Reset Month to 1
**Description:** When changing scenarios, the month slider retains its current position. Users expect switching scenarios to start from month 1.

**Impact:** Confusing UX - users may see mid-simulation state for a new scenario without context.

**Recommended Fix:**
```python
# In app.py, when scenario changes:
if selected_scenario != st.session_state.get('scenario'):
    st.session_state.scenario = selected_scenario
    st.session_state.current_month = 1  # Add this line
    anim.reset()
    st.rerun()
```

**Complexity:** Low

---

### H2. Stock Levels Chart Shows Wrong Month Label
**Description:** After Reset or scenario change, the Stock Levels chart title shows "Month 1" even when the slider shows a different month. State inconsistency between UI elements.

**Impact:** Visual confusion about which month is being displayed.

**Root Cause:** The chart title is computed from `current_month` while the slider widget may have stale state.

**Recommended Fix:** Ensure single source of truth for month state before rendering charts.

**Complexity:** Low

---

### H3. Speed Slider Labels Appear/Disappear
**Description:** The "0.5x" and "3.0x" labels on the speed slider appear inconsistently - sometimes visible, sometimes not.

**Impact:** Minor visual inconsistency.

**Root Cause:** Likely Streamlit's slider rendering behavior or CSS overflow.

**Recommended Fix:** Add explicit CSS to ensure labels are always visible, or use explicit labeling.

**Complexity:** Low

---

## Priority 3: Medium (Nice-to-Have Improvements)

### M1. Add Loading State Indicator
**Description:** When switching scenarios, there's no visual feedback that data is loading.

**Recommended Fix:** Add `st.spinner()` context manager around scenario loading.

**Complexity:** Low

---

### M2. Add Keyboard Shortcuts
**Description:** Allow spacebar to toggle Play/Pause, arrow keys to step through months.

**Recommended Fix:** Use Streamlit's key handling or custom JavaScript component.

**Complexity:** Medium

---

### M3. Particle Animation on Network Graph
**Description:** The network graph has particle animation code (`particle_phase` in session state) but particles aren't visibly animating.

**Root Cause:** Since the main animation loop isn't running (C1), particles also don't animate.

**Recommended Fix:** Fix C1 first, then verify particle animation works.

**Complexity:** Dependent on C1

---

### M4. Add Scenario Description Tooltip
**Description:** Users may not understand what each scenario represents. Add hover tooltips or expandable descriptions.

**Recommended Fix:**
```python
st.selectbox(
    'Scenario',
    options=display_options,
    help='Select a supply chain disruption scenario to explore'
)
# Or add st.markdown with scenario description below dropdown
```

**Complexity:** Low

---

### M5. Mobile/Tablet Responsiveness
**Description:** Dashboard layout may not work well on smaller screens.

**Recommended Fix:** Test on mobile viewports, consider adding responsive breakpoints via CSS.

**Complexity:** Medium

---

## Priority 4: Low (Polish)

### L1. Add Year Markers to Time Charts
**Description:** Charts only show month numbers. Adding year markers (Year 1, Year 2...) at months 12, 24, etc. would improve readability.

**Complexity:** Low

---

### L2. Improve Color Contrast for Accessibility
**Description:** Some chart colors (especially light yellow for Macrolides) may be hard to see.

**Recommended Fix:** Run through WCAG contrast checker, adjust palette.

**Complexity:** Low

---

### L3. Add Export/Download Functionality
**Description:** Users may want to download charts or data for presentations.

**Recommended Fix:** Add download buttons for PNG/SVG export.

**Complexity:** Medium

---

### L4. Progressive Chart Reveal Animation
**Description:** When advancing months, charts update instantly. A smooth transition/animation would look more polished.

**Complexity:** Medium (requires Plotly animation configuration)

---

## Implementation Sequence

### Phase 1: Critical Fixes (Required before workshop)
1. Fix C1 (Animation bug) - **MUST FIX**
2. Fix C2 (Reset bug) - **MUST FIX**

### Phase 2: High Priority (Recommended before workshop)
3. Fix H1 (Scenario reset)
4. Fix H2 (Month label sync)
5. Fix H3 (Speed slider labels)

### Phase 3: Enhancements (Time permitting)
6. M1 (Loading state)
7. M4 (Scenario descriptions)
8. L1 (Year markers)

---

## Testing Checklist

After implementing fixes, verify:

- [ ] Play button advances month slider automatically
- [ ] Pause button stops animation
- [ ] Reset button returns to Month 1
- [ ] Scenario switching resets to Month 1
- [ ] All 8 scenarios load correctly
- [ ] Network graph node colors change appropriately
- [ ] All 4 time-series charts update progressively
- [ ] Bottom metrics bar shows cumulative values
- [ ] 60-Month Totals accordion displays correct summary
- [ ] No JavaScript console errors

---

## Files to Modify

| File | Changes |
|------|---------|
| `components/controls.py` | Fix C1, C2 - animation and reset state management |
| `app.py` | Fix H1 - scenario change reset |
| `components/time_charts.py` | Fix H2 - month label consistency |

---

*Generated by Helix evaluation system*
