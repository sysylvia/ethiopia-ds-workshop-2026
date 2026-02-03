#!/usr/bin/env python3
"""
Generate figures for ML-ABM Integration slides (Day 3)

This script creates publication-quality figures for the ML-ABM integration
presentation using matplotlib with consistent styling.

Usage:
    python generate_figures.py

Output:
    All figures saved to ../images/ directory
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np
from pathlib import Path

# ============================================================================
# STYLE CONFIGURATION
# ============================================================================

# Colors matching workshop.scss theme
COLORS = {
    'primary': '#4A7C59',      # Green - main theme
    'secondary': '#6B8E23',    # Olive green
    'success': '#228B22',      # Forest green
    'info': '#5F9EA0',         # Cadet blue
    'warning': '#DAA520',      # Goldenrod
    'danger': '#CD5C5C',       # Indian red
    'light': '#F5F5F5',        # Light gray background
    'dark': '#333333',         # Dark text
    'white': '#FFFFFF',
    'gray': '#888888',
}

# Quadrant colors for taxonomy diagram
QUAD_COLORS = {
    'calibration': '#4A7C59',     # Primary green
    'behavior': '#5F9EA0',        # Info blue
    'surrogate': '#6B8E23',       # Secondary olive
    'hybrid': '#DAA520',          # Warning gold
}

# Configure matplotlib
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Source Sans Pro', 'DejaVu Sans', 'Arial'],
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 16,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / 'images'
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# FIGURE 1: Integration Taxonomy (Four Quadrants)
# ============================================================================

def create_integration_taxonomy():
    """Create four-quadrant diagram showing ML-ABM integration approaches."""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Draw quadrant boxes
    quadrants = [
        # (x, y, width, height, label, description, color)
        (0, 0.5, 0.48, 0.48, 'Calibration',
         'ML estimates ABM\nparameters from data\n\n• Neural calibration\n• ML-ABC\n• Simulation-based inference',
         QUAD_COLORS['calibration']),
        (0.52, 0.5, 0.48, 0.48, 'Prediction-Driven\nBehaviors',
         'ML models drive\nagent decisions\n\n• RL for adaptive behavior\n• Neural decision rules',
         QUAD_COLORS['behavior']),
        (0, 0, 0.48, 0.48, 'Surrogate\nModels',
         'ML approximates ABM\nfor speed\n\n• Neural networks\n• Gaussian processes\n• 1000x+ speedup',
         QUAD_COLORS['surrogate']),
        (0.52, 0, 0.48, 0.48, 'Hybrid /\nDifferentiable',
         'End-to-end gradient\noptimization\n\n• GradABM\n• Differentiable simulation',
         QUAD_COLORS['hybrid']),
    ]

    for x, y, w, h, title, desc, color in quadrants:
        # Background box
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02",
                              facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.add_patch(box)

        # Title
        ax.text(x + w/2, y + h - 0.08, title, fontsize=14, fontweight='bold',
               ha='center', va='top', color=color)

        # Description
        ax.text(x + w/2, y + h - 0.18, desc, fontsize=10,
               ha='center', va='top', color=COLORS['dark'])

    # Axis labels
    ax.annotate('', xy=(1.05, 0.5), xytext=(-0.05, 0.5),
                arrowprops=dict(arrowstyle='->', color=COLORS['gray'], lw=1.5))
    ax.text(0.5, -0.08, 'Integration Depth →', ha='center', fontsize=12, style='italic')
    ax.text(0.5, -0.12, '(Loose coupling → Tight coupling)', ha='center', fontsize=9,
            color=COLORS['gray'])

    ax.annotate('', xy=(0.5, 1.05), xytext=(0.5, -0.02),
                arrowprops=dict(arrowstyle='->', color=COLORS['gray'], lw=1.5))
    ax.text(-0.08, 0.5, 'ML Role →', ha='center', va='center', fontsize=12,
            style='italic', rotation=90)
    ax.text(-0.12, 0.5, '(Support → Core)', ha='center', va='center', fontsize=9,
            color=COLORS['gray'], rotation=90)

    # Title
    ax.set_title('ML-ABM Integration Approaches', fontsize=16, fontweight='bold', pad=20)

    ax.set_xlim(-0.15, 1.1)
    ax.set_ylim(-0.18, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'integration-taxonomy.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✓ Created integration-taxonomy.png")


# ============================================================================
# FIGURE 2: ML-ABM Workflows
# ============================================================================

def create_ml_abm_workflows():
    """Create diagram showing data flow for each integration approach."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    def draw_box(ax, x, y, text, color, width=0.25, height=0.12):
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                             boxstyle="round,pad=0.01,rounding_size=0.02",
                             facecolor=color, alpha=0.3, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')

    def draw_arrow(ax, start, end, label=None):
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=1.5))
        if label:
            mid = ((start[0] + end[0])/2, (start[1] + end[1])/2 + 0.05)
            ax.text(mid[0], mid[1], label, fontsize=8, ha='center', color=COLORS['gray'])

    # Workflow 1: Calibration
    ax1 = axes[0, 0]
    ax1.set_title('1. ML for Calibration', fontweight='bold', fontsize=12,
                  color=QUAD_COLORS['calibration'])

    draw_box(ax1, 0.2, 0.7, 'Real-World\nData', COLORS['info'])
    draw_box(ax1, 0.5, 0.7, 'ABM\nSimulation', COLORS['primary'])
    draw_box(ax1, 0.8, 0.7, 'Simulated\nData', COLORS['secondary'])
    draw_box(ax1, 0.5, 0.35, 'ML Model\n(Inverse)', COLORS['warning'])
    draw_box(ax1, 0.5, 0.1, 'Calibrated\nParameters', COLORS['success'])

    draw_arrow(ax1, (0.2, 0.64), (0.2, 0.41))
    draw_arrow(ax1, (0.5, 0.64), (0.5, 0.41))
    draw_arrow(ax1, (0.8, 0.64), (0.8, 0.41))
    draw_arrow(ax1, (0.3, 0.35), (0.35, 0.35))
    draw_arrow(ax1, (0.65, 0.35), (0.7, 0.35))
    draw_arrow(ax1, (0.5, 0.29), (0.5, 0.16))
    ax1.text(0.25, 0.53, 'Compare', fontsize=8, ha='center', color=COLORS['gray'])

    # Workflow 2: Prediction-Driven Behaviors
    ax2 = axes[0, 1]
    ax2.set_title('2. ML-Driven Agent Behaviors', fontweight='bold', fontsize=12,
                  color=QUAD_COLORS['behavior'])

    draw_box(ax2, 0.3, 0.7, 'Environment\nState', COLORS['info'])
    draw_box(ax2, 0.7, 0.7, 'ML/RL\nModel', COLORS['warning'])
    draw_box(ax2, 0.7, 0.35, 'Agent\nDecision', COLORS['primary'])
    draw_box(ax2, 0.3, 0.35, 'ABM\nSimulation', COLORS['success'])
    draw_box(ax2, 0.3, 0.1, 'Updated\nState', COLORS['secondary'])

    draw_arrow(ax2, (0.42, 0.7), (0.55, 0.7))
    draw_arrow(ax2, (0.7, 0.64), (0.7, 0.41))
    draw_arrow(ax2, (0.58, 0.35), (0.43, 0.35))
    draw_arrow(ax2, (0.3, 0.29), (0.3, 0.16))

    # Draw feedback loop
    ax2.annotate('', xy=(0.22, 0.5), xytext=(0.22, 0.15),
                arrowprops=dict(arrowstyle='->', color=COLORS['gray'], lw=1,
                               connectionstyle='arc3,rad=0.3'))
    ax2.annotate('', xy=(0.3, 0.64), xytext=(0.22, 0.5),
                arrowprops=dict(arrowstyle='->', color=COLORS['gray'], lw=1))
    ax2.text(0.12, 0.4, 'Feedback', fontsize=7, color=COLORS['gray'], rotation=90)

    # Workflow 3: Surrogate Models
    ax3 = axes[1, 0]
    ax3.set_title('3. Surrogate Models', fontweight='bold', fontsize=12,
                  color=QUAD_COLORS['surrogate'])

    draw_box(ax3, 0.2, 0.7, 'ABM\n(Slow)', COLORS['primary'])
    draw_box(ax3, 0.5, 0.7, 'Training\nData', COLORS['info'])
    draw_box(ax3, 0.8, 0.7, 'ML\nSurrogate', COLORS['warning'])
    draw_box(ax3, 0.5, 0.35, 'New\nInputs', COLORS['secondary'])
    draw_box(ax3, 0.8, 0.35, 'Fast\nPredictions', COLORS['success'])

    draw_arrow(ax3, (0.32, 0.7), (0.37, 0.7), 'Generate')
    draw_arrow(ax3, (0.62, 0.7), (0.67, 0.7), 'Train')
    draw_arrow(ax3, (0.62, 0.35), (0.67, 0.35), 'Query')
    ax3.text(0.8, 0.2, '1000x+ faster', fontsize=9, ha='center',
             color=COLORS['success'], fontweight='bold')

    # Workflow 4: Hybrid/Differentiable
    ax4 = axes[1, 1]
    ax4.set_title('4. Hybrid / Differentiable ABM', fontweight='bold', fontsize=12,
                  color=QUAD_COLORS['hybrid'])

    draw_box(ax4, 0.3, 0.75, 'Input\nParameters', COLORS['info'])
    draw_box(ax4, 0.5, 0.55, 'Differentiable\nABM', COLORS['warning'], width=0.3)
    draw_box(ax4, 0.7, 0.75, 'Loss\nFunction', COLORS['danger'])
    draw_box(ax4, 0.5, 0.25, 'Gradient\nDescent', COLORS['success'])
    draw_box(ax4, 0.5, 0.05, 'Optimized\nPolicy', COLORS['primary'])

    draw_arrow(ax4, (0.3, 0.69), (0.4, 0.61))
    draw_arrow(ax4, (0.6, 0.61), (0.7, 0.69))
    draw_arrow(ax4, (0.7, 0.69), (0.62, 0.55), '∂L/∂θ')
    draw_arrow(ax4, (0.5, 0.49), (0.5, 0.31))
    draw_arrow(ax4, (0.5, 0.19), (0.5, 0.11))

    # Draw backprop arrow
    ax4.annotate('', xy=(0.38, 0.55), xytext=(0.38, 0.25),
                arrowprops=dict(arrowstyle='->', color=COLORS['danger'], lw=1.5,
                               connectionstyle='arc3,rad=-0.3', linestyle='--'))
    ax4.text(0.25, 0.4, 'Backprop', fontsize=8, color=COLORS['danger'])

    for ax in axes.flat:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 0.85)
        ax.axis('off')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'ml-abm-workflows.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✓ Created ml-abm-workflows.png")


# ============================================================================
# FIGURE 3: RL-ABM Interaction Loop
# ============================================================================

def create_rl_abm_loop():
    """Create circular diagram showing RL-ABM interaction cycle."""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Center of the diagram
    cx, cy = 0.5, 0.5
    radius = 0.3

    # Draw main components at compass points
    components = [
        (0, 'State\n(Environment)', COLORS['info']),        # Top
        (1, 'RL Agent\n(Policy)', COLORS['warning']),       # Right
        (2, 'Action\n(Decision)', COLORS['primary']),       # Bottom
        (3, 'ABM\n(Simulation)', COLORS['success']),        # Left
    ]

    positions = []
    for i, (idx, label, color) in enumerate(components):
        angle = np.pi/2 - idx * np.pi/2  # Start from top, go clockwise
        x = cx + radius * np.cos(angle)
        y = cy + radius * np.sin(angle)
        positions.append((x, y))

        # Draw component box
        box = FancyBboxPatch((x - 0.1, y - 0.07), 0.2, 0.14,
                             boxstyle="round,pad=0.01,rounding_size=0.02",
                             facecolor=color, alpha=0.3, edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold')

    # Draw circular arrows between components
    arrow_labels = ['Observe', 'Select', 'Execute', 'Update']
    for i in range(4):
        start = positions[i]
        end = positions[(i + 1) % 4]

        # Calculate control point for curved arrow
        mid_angle = np.pi/2 - (i + 0.5) * np.pi/2
        ctrl_radius = radius * 0.6
        ctrl_x = cx + ctrl_radius * np.cos(mid_angle)
        ctrl_y = cy + ctrl_radius * np.sin(mid_angle)

        # Adjust start/end to be on box edges
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = np.sqrt(dx**2 + dy**2)

        start_adj = (start[0] + 0.12 * dx/dist, start[1] + 0.1 * dy/dist)
        end_adj = (end[0] - 0.12 * dx/dist, end[1] - 0.1 * dy/dist)

        ax.annotate('', xy=end_adj, xytext=start_adj,
                   arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2,
                                  connectionstyle=f'arc3,rad=0.3'))

        # Label
        label_x = cx + (radius - 0.12) * np.cos(mid_angle)
        label_y = cy + (radius - 0.12) * np.sin(mid_angle)
        ax.text(label_x, label_y, arrow_labels[i], fontsize=9, ha='center', va='center',
               color=COLORS['gray'], style='italic')

    # Add reward signal (going back from ABM to Agent)
    ax.annotate('', xy=(positions[1][0] - 0.1, positions[1][1] - 0.08),
               xytext=(positions[3][0] + 0.1, positions[3][1] - 0.08),
               arrowprops=dict(arrowstyle='->', color=COLORS['danger'], lw=2,
                              connectionstyle='arc3,rad=-0.5', linestyle='--'))
    ax.text(cx, cy - 0.08, 'Reward', fontsize=10, ha='center', va='center',
           color=COLORS['danger'], fontweight='bold')

    # Title
    ax.set_title('Reinforcement Learning + ABM Interaction Loop',
                fontsize=14, fontweight='bold', y=0.95)

    # Annotations
    ax.text(0.5, 0.08, 'Agent learns optimal policy through trial and error in ABM environment',
           ha='center', fontsize=10, style='italic', color=COLORS['gray'])

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'rl-abm-loop.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✓ Created rl-abm-loop.png")


# ============================================================================
# FIGURE 4: WISE Integration Pipeline
# ============================================================================

def create_wise_pipeline():
    """Create flowchart showing WISE project ML-ABM integration workflow."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Define pipeline stages
    stages = [
        ('Historical\nData', 0.1, COLORS['info'], 'Facility records\nDemand history\nStock levels'),
        ('ML Model\n(Days 1-2)', 0.3, COLORS['warning'], 'Feature engineering\nRandom Forest\nCross-validation'),
        ('Demand\nForecasts', 0.5, COLORS['secondary'], 'By facility\nBy medication\nConfidence bounds'),
        ('ABM\n(Day 4)', 0.7, COLORS['primary'], 'Agent behaviors\nSupply chain sim\nPolicy testing'),
        ('Policy\nInsights', 0.9, COLORS['success'], 'Intervention effects\nResource allocation\nDecision support'),
    ]

    y_center = 0.5
    box_width = 0.14
    box_height = 0.25

    for label, x, color, details in stages:
        # Main box
        box = FancyBboxPatch((x - box_width/2, y_center - box_height/2),
                             box_width, box_height,
                             boxstyle="round,pad=0.01,rounding_size=0.02",
                             facecolor=color, alpha=0.25, edgecolor=color, linewidth=2)
        ax.add_patch(box)

        # Label
        ax.text(x, y_center + 0.03, label, ha='center', va='center',
               fontsize=11, fontweight='bold')

        # Details below
        ax.text(x, y_center - 0.22, details, ha='center', va='top',
               fontsize=8, color=COLORS['gray'])

    # Draw arrows between stages
    for i in range(len(stages) - 1):
        x1 = stages[i][1] + box_width/2 + 0.01
        x2 = stages[i+1][1] - box_width/2 - 0.01
        ax.annotate('', xy=(x2, y_center), xytext=(x1, y_center),
                   arrowprops=dict(arrowstyle='->', color=COLORS['dark'], lw=2))

    # Add day labels at top
    day_labels = [
        ('Days 1-2: Data & ML', 0.2),
        ('Day 3: Integration', 0.5),
        ('Day 4: Simulation', 0.8),
    ]

    for label, x in day_labels:
        ax.text(x, 0.88, label, ha='center', fontsize=10, fontweight='bold',
               color=COLORS['primary'],
               bbox=dict(boxstyle='round', facecolor=COLORS['light'], edgecolor=COLORS['primary']))

    # Add feedback arrow (optional policy refinement)
    ax.annotate('', xy=(0.3, y_center - 0.18), xytext=(0.7, y_center - 0.18),
               arrowprops=dict(arrowstyle='<-', color=COLORS['gray'], lw=1.5,
                              linestyle='--'))
    ax.text(0.5, y_center - 0.26, 'Feedback: Refine forecasts based on simulation results',
           ha='center', fontsize=8, style='italic', color=COLORS['gray'])

    # Title
    ax.set_title('WISE Project Integration Pipeline', fontsize=14, fontweight='bold', y=0.98)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'wise-pipeline.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✓ Created wise-pipeline.png")


# ============================================================================
# FIGURE 5: Bullwhip Effect Comparison
# ============================================================================

def create_bullwhip_effect():
    """Create visualization of bullwhip effect before/after RL intervention."""
    np.random.seed(42)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Simulate demand signal and orders at each echelon
    weeks = np.arange(1, 53)
    base_demand = 100 + 20 * np.sin(2 * np.pi * weeks / 26)  # Seasonal pattern
    noise = np.random.normal(0, 5, len(weeks))
    consumer_demand = base_demand + noise

    # Without RL: Traditional ordering (amplification factor increases up chain)
    amplification_no_rl = [1.0, 1.8, 2.8, 4.0]  # Retailer, Distributor, Wholesaler, Manufacturer
    echelons = ['Consumer\nDemand', 'Retailer\nOrders', 'Distributor\nOrders', 'Manufacturer\nOrders']

    # With RL: Reduced amplification
    amplification_with_rl = [1.0, 1.2, 1.4, 1.6]

    colors_echelon = [COLORS['info'], COLORS['secondary'], COLORS['warning'], COLORS['danger']]

    # Plot 1: Without RL
    ax1 = axes[0]
    ax1.set_title('Traditional Ordering Policy', fontsize=12, fontweight='bold',
                  color=COLORS['danger'])

    for i, (label, amp, color) in enumerate(zip(echelons, amplification_no_rl, colors_echelon)):
        orders = base_demand * amp + noise * amp * 1.5
        ax1.plot(weeks, orders, label=label, color=color, linewidth=2, alpha=0.8)

    ax1.set_xlabel('Week', fontsize=11)
    ax1.set_ylabel('Order Quantity', fontsize=11)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.set_ylim(0, 500)
    ax1.grid(True, alpha=0.3)

    # Add variance annotation
    ax1.annotate('High variance\namplification', xy=(35, 420), fontsize=10,
                ha='center', color=COLORS['danger'], fontweight='bold')

    # Plot 2: With RL
    ax2 = axes[1]
    ax2.set_title('DQN-Learned Ordering Policy', fontsize=12, fontweight='bold',
                  color=COLORS['success'])

    for i, (label, amp, color) in enumerate(zip(echelons, amplification_with_rl, colors_echelon)):
        orders = base_demand * amp + noise * amp * 0.8
        ax2.plot(weeks, orders, label=label, color=color, linewidth=2, alpha=0.8)

    ax2.set_xlabel('Week', fontsize=11)
    ax2.set_ylabel('Order Quantity', fontsize=11)
    ax2.legend(loc='upper right', fontsize=9)
    ax2.set_ylim(0, 500)
    ax2.grid(True, alpha=0.3)

    # Add variance annotation
    ax2.annotate('Bullwhip effect\nmitigated', xy=(35, 200), fontsize=10,
                ha='center', color=COLORS['success'], fontweight='bold')

    # Add overall annotation
    fig.suptitle('Bullwhip Effect: Order Variance Amplification in Supply Chain',
                fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'bullwhip-effect.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✓ Created bullwhip-effect.png")


# ============================================================================
# FIGURE 6: Surrogate Model Speedup Comparison
# ============================================================================

def create_surrogate_speedup():
    """Create bar chart comparing ABM vs surrogate model runtime."""
    fig, ax = plt.subplots(figsize=(10, 6))

    tasks = ['Single Run\n(1 scenario)', 'Sensitivity\nAnalysis\n(1000 scenarios)',
             'Policy\nOptimization\n(10000 scenarios)', 'Real-time\nDecision\nSupport']

    # Runtime in seconds (log scale)
    abm_times = [120, 120000, 1200000, 120]  # 2 min per run
    surrogate_times = [0.1, 100, 1000, 0.1]

    x = np.arange(len(tasks))
    width = 0.35

    bars1 = ax.bar(x - width/2, abm_times, width, label='Full ABM',
                   color=COLORS['primary'], alpha=0.8)
    bars2 = ax.bar(x + width/2, surrogate_times, width, label='ML Surrogate',
                   color=COLORS['warning'], alpha=0.8)

    ax.set_ylabel('Runtime (seconds, log scale)', fontsize=11)
    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, fontsize=10)
    ax.legend(fontsize=11)

    # Add speedup annotations
    speedups = [f'{int(a/s)}x' for a, s in zip(abm_times, surrogate_times)]
    for i, (bar1, bar2, speedup) in enumerate(zip(bars1, bars2, speedups)):
        height = bar1.get_height()
        ax.annotate(f'{speedup} faster',
                   xy=(bar2.get_x() + bar2.get_width()/2, bar2.get_height()),
                   xytext=(0, 5), textcoords='offset points',
                   ha='center', va='bottom', fontsize=10, fontweight='bold',
                   color=COLORS['success'])

    # Add time labels on bars
    def format_time(seconds):
        if seconds >= 86400:
            return f'{seconds/86400:.0f} days'
        elif seconds >= 3600:
            return f'{seconds/3600:.0f} hrs'
        elif seconds >= 60:
            return f'{seconds/60:.0f} min'
        else:
            return f'{seconds:.1f} sec'

    for bar, time in zip(bars1, abm_times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 0.5,
               format_time(time), ha='center', va='center', fontsize=8,
               color='white', fontweight='bold', rotation=90)

    for bar, time in zip(bars2, surrogate_times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 0.5,
               format_time(time), ha='center', va='center', fontsize=8,
               color='white', fontweight='bold', rotation=90)

    ax.set_title('Surrogate Model Speedup: ABM vs Neural Network Approximation',
                fontsize=13, fontweight='bold')

    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0.01, 10000000)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'surrogate-speedup.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✓ Created surrogate-speedup.png")


# ============================================================================
# FIGURE 7: RL Learning Curve
# ============================================================================

def create_rl_learning_curve():
    """Create plot showing RL agent performance improvement over training."""
    np.random.seed(42)

    fig, ax = plt.subplots(figsize=(10, 6))

    episodes = np.arange(0, 5001, 50)

    # Simulated learning curves
    # Reward starts negative (poor policy), improves and plateaus
    def learning_curve(episodes, final_reward, learning_rate, noise_scale):
        base = final_reward * (1 - np.exp(-learning_rate * episodes / 1000))
        noise = np.random.normal(0, noise_scale * (1 - episodes/5000), len(episodes))
        return base + noise

    # RL agent reward
    rl_reward = learning_curve(episodes, 850, 1.5, 80)
    rl_reward = np.clip(rl_reward, -200, 900)

    # Baseline policies
    base_stock = np.full_like(episodes, 400.0) + np.random.normal(0, 20, len(episodes))
    optimal_bound = np.full_like(episodes, 880.0)

    # Plot
    ax.fill_between(episodes, rl_reward - 50, rl_reward + 50, alpha=0.2,
                    color=COLORS['primary'], label='RL Agent (±1 std)')
    ax.plot(episodes, rl_reward, color=COLORS['primary'], linewidth=2.5, label='RL Agent')
    ax.axhline(y=400, color=COLORS['warning'], linestyle='--', linewidth=2,
               label='Base-Stock Policy')
    ax.axhline(y=880, color=COLORS['success'], linestyle=':', linewidth=2,
               label='Theoretical Optimum')

    # Annotations
    ax.annotate('Exploration\nphase', xy=(500, 200), fontsize=9, ha='center',
               color=COLORS['gray'])
    ax.annotate('Learning\nimprovement', xy=(1500, 550), fontsize=9, ha='center',
               color=COLORS['primary'])
    ax.annotate('Converged', xy=(4000, 820), fontsize=9, ha='center',
               color=COLORS['success'])

    ax.set_xlabel('Training Episodes', fontsize=11)
    ax.set_ylabel('Cumulative Reward (higher = better)', fontsize=11)
    ax.set_title('RL Agent Learning: Inventory Management Policy Optimization',
                fontsize=13, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 5000)
    ax.set_ylim(-250, 1000)

    # Add performance improvement annotation
    ax.annotate('', xy=(4500, 850), xytext=(4500, 400),
               arrowprops=dict(arrowstyle='<->', color=COLORS['danger'], lw=2))
    ax.text(4700, 625, '+112%\nvs baseline', fontsize=10, ha='left',
           fontweight='bold', color=COLORS['danger'])

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'rl-learning-curve.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✓ Created rl-learning-curve.png")


# ============================================================================
# FIGURE 8: Demand Forecast to Inventory Policy
# ============================================================================

def create_demand_inventory():
    """Create dual-axis plot showing ML predictions feeding inventory decisions."""
    np.random.seed(42)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Time axis
    months = np.arange(1, 25)
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] * 2

    # Historical demand (first 12 months)
    historical_demand = 1000 + 200 * np.sin(2 * np.pi * months[:12] / 12) + \
                        np.random.normal(0, 50, 12)

    # Forecasted demand (next 12 months)
    forecast_demand = 1000 + 200 * np.sin(2 * np.pi * months[12:] / 12) + 50  # Slight trend
    forecast_lower = forecast_demand - 100 - 10 * np.arange(12)  # Widening CI
    forecast_upper = forecast_demand + 100 + 10 * np.arange(12)

    # Plot demand
    ax1.plot(months[:12], historical_demand, 'o-', color=COLORS['primary'],
            linewidth=2, markersize=6, label='Historical Demand')
    ax1.plot(months[12:], forecast_demand, 's--', color=COLORS['warning'],
            linewidth=2, markersize=6, label='ML Forecast')
    ax1.fill_between(months[12:], forecast_lower, forecast_upper,
                    alpha=0.2, color=COLORS['warning'], label='95% Prediction Interval')

    ax1.axvline(x=12.5, color=COLORS['gray'], linestyle=':', linewidth=2)
    ax1.text(12.5, 1300, 'Forecast\nHorizon', ha='center', fontsize=9, color=COLORS['gray'])

    ax1.set_xlabel('Month', fontsize=11)
    ax1.set_ylabel('Demand (units)', fontsize=11, color=COLORS['primary'])
    ax1.tick_params(axis='y', labelcolor=COLORS['primary'])
    ax1.set_ylim(600, 1400)

    # Second y-axis for inventory/reorder
    ax2 = ax1.twinx()

    # Reorder point (based on forecast + safety stock)
    safety_stock_factor = 1.5  # z-score for service level
    reorder_point = forecast_demand + safety_stock_factor * (forecast_upper - forecast_demand) / 2

    # Order quantity
    order_qty = np.where(months[12:] % 3 == 0, reorder_point * 1.2, np.nan)

    ax2.plot(months[12:], reorder_point, 'v-', color=COLORS['success'],
            linewidth=2, markersize=8, label='Reorder Point')
    ax2.scatter(months[12:][~np.isnan(order_qty)], order_qty[~np.isnan(order_qty)],
               s=150, marker='D', color=COLORS['danger'], zorder=5, label='Order Placed')

    ax2.set_ylabel('Reorder Point (units)', fontsize=11, color=COLORS['success'])
    ax2.tick_params(axis='y', labelcolor=COLORS['success'])
    ax2.set_ylim(800, 1600)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

    # Annotations
    ax1.annotate('ML Model Training', xy=(6, 750), fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor=COLORS['light'], edgecolor=COLORS['primary']),
                color=COLORS['primary'])
    ax1.annotate('Forecast → Inventory Policy', xy=(18, 750), fontsize=10, ha='center',
                bbox=dict(boxstyle='round', facecolor=COLORS['light'], edgecolor=COLORS['success']),
                color=COLORS['success'])

    ax1.set_xticks(months)
    ax1.set_xticklabels(month_labels, fontsize=8, rotation=45, ha='right')

    ax1.set_title('ML Demand Forecast Driving Inventory Reorder Policy',
                 fontsize=13, fontweight='bold')

    ax1.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'demand-inventory.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("✓ Created demand-inventory.png")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Generate all figures."""
    print(f"\nGenerating figures to: {OUTPUT_DIR}\n")

    create_integration_taxonomy()
    create_ml_abm_workflows()
    create_rl_abm_loop()
    create_wise_pipeline()
    create_bullwhip_effect()
    create_surrogate_speedup()
    create_rl_learning_curve()
    create_demand_inventory()

    print(f"\n✓ All figures generated successfully!")
    print(f"  Output directory: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
