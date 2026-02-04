# Ethiopia ABM Animated Dashboard

Animated Streamlit dashboard for visualizing the Ethiopia Antibiotic Supply Chain Agent-Based Model.

**WISE Workshop | Addis Ababa, Feb 2026**

## Features

- **Animated Network Graph**: Visualizes medicine flow through the supply chain hierarchy
  - Manufacturers → Central Medical Store → Hospitals → CHC Regions
  - Node colors indicate stock levels (green=healthy, yellow=low, red=critical)
  - Animated particles show active shipment flows

- **Synchronized Time-Series Charts**:
  - Shortages by medicine type (stacked area)
  - Deaths by age group (line chart)
  - Stock levels by supply chain tier (bar chart)
  - Treatment rate over time (filled line)

- **Interactive Controls**:
  - 8 pre-computed scenarios
  - Play/Pause animation
  - Speed control (0.5x - 3x)
  - Month scrubber for manual navigation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

## Scenarios

| Scenario | Description |
|----------|-------------|
| Base Case | Default parameters |
| Weather Delays | 4-month transit time (doubled) |
| Disease Outbreak | 25 CHCs with 3x demand |
| Advance Ordering | 4-month order lead time |
| Manufacturer Failure | One manufacturer offline months 12-24 |
| Optimized Policy | Balanced ordering and transit |
| AMR Substitution | 30% Penicillin resistance from month 24 |
| Private Sector | 25% demand diverted to private sector |

## Pre-computing Scenario Data

If you need to regenerate scenario data:

```bash
python data/precompute.py
```

This exports ABM results for all 8 scenarios to JSON files (~2.8MB each).

## Deployment

### Hugging Face Spaces (Recommended)

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space)
2. Select **Streamlit** as the SDK
3. Upload all files from this `dashboard/` directory
4. The app will automatically deploy

Or via CLI:
```bash
pip install huggingface_hub
huggingface-cli login
huggingface-cli repo create ethiopia-abm-dashboard --type space --space_sdk streamlit
cd dashboard
git init
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/ethiopia-abm-dashboard
git add .
git commit -m "Initial dashboard deployment"
git push space main
```

### Streamlit Cloud (Alternative)

1. Push the `dashboard/` folder to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Set main file path: `dashboard/app.py`
4. Deploy

### Local Development

```bash
streamlit run app.py --server.runOnSave true
```

## File Structure

```
dashboard/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Dependencies
├── components/
│   ├── network_graph.py    # Supply chain network visualization
│   ├── time_charts.py      # Time-series chart components
│   ├── controls.py         # UI controls (scenario, playback)
│   └── animation.py        # Animation state management
├── data/
│   ├── precompute.py       # Script to generate scenario data
│   └── scenarios/          # Pre-computed JSON files
└── .streamlit/
    └── config.toml         # Theme configuration
```

## License

WISE Workshop educational materials.
