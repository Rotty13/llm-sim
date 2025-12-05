"""
Streamlit Dashboard for llm-sim Visualization

Features:
- World map visualization (using Plotly)
- Event timeline (using Plotly)
- Agent view (select agent, show stats, relationships, actions)
- Loads simulation data from metrics and world files

Run with: streamlit run scripts/visualization/llm_sim_dashboard.py
"""
import streamlit as st
import plotly.express as px
import json
import os

# Load metrics data
METRICS_PATH = 'outputs/llm_logs/World_0_metrics.json'
WORLD_PATH = 'worlds/World_0/world.yaml'
AGENTS_PATH = 'worlds/World_0/personas.yaml'

st.set_page_config(page_title="llm-sim Dashboard", layout="wide")
st.title("llm-sim Simulation Dashboard")

# Load metrics
metrics = {}
if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH, 'r', encoding='utf-8') as f:
        metrics = json.load(f)

# Load world config
world = {}
if os.path.exists(WORLD_PATH):
    with open(WORLD_PATH, 'r', encoding='utf-8') as f:
        import yaml
        world = yaml.safe_load(f)

# Load agents
agents = []
if os.path.exists(AGENTS_PATH):
    with open(AGENTS_PATH, 'r', encoding='utf-8') as f:
        import yaml
        personas = yaml.safe_load(f)
        agents = personas.get('people', [])

# Sidebar: Agent selection
agent_names = [a.get('name', f'Agent_{i}') for i, a in enumerate(agents)]
selected_agent = st.sidebar.selectbox("Select Agent", agent_names)
selected_agent_data = next((a for a in agents if a.get('name') == selected_agent), None)

# World Map (stub: random locations)
st.header("World Map")
if agents:
    import pandas as pd
    df = pd.DataFrame({
        'Agent': agent_names,
        'lat': [40.0 + i*0.01 for i in range(len(agent_names))],
        'lon': [-74.0 + i*0.01 for i in range(len(agent_names))]
    })
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_name="Agent", zoom=10)
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No agent location data available.")

# Event Timeline (stub: tick-based events)
st.header("Event Timeline")
if metrics and 'tick_history' in metrics:
    df = pd.DataFrame(metrics['tick_history'])
    fig = px.line(df, x="tick", y=["agent_actions", "resource_flows", "world_events"], labels={"value": "Count", "variable": "Metric"})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No event timeline data available.")

# Agent View
st.header("Agent View")
if selected_agent_data:
    st.subheader(f"Stats for {selected_agent}")
    st.json(selected_agent_data)
else:
    st.info("Select an agent to view details.")
