import os
import sys
import streamlit as st

# Add parent directory to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dashboard.components.styles import apply_custom_css
from dashboard.shared.state import init_session_state

# Page Configuration
st.set_page_config(
    page_title="Predictive Failover Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Enterprise Dark Theme Styles
apply_custom_css()

# Initialize Global Controller & Session State
controller = init_session_state()

# Native Streamlit Multi-Page Definitions (Clean Text Titles, Zero Emojis)
overview_page = st.Page("pages/overview.py", title="Overview", default=True)
servers_page = st.Page("pages/servers.py", title="Infrastructure")
traffic_flow_page = st.Page("pages/traffic_flow.py", title="Traffic Topology")
incidents_page = st.Page("pages/incidents.py", title="Incidents")

prediction_page = st.Page("pages/prediction.py", title="ML Risk & SHAP")
digital_twin_page = st.Page("pages/digital_twin.py", title="Digital Twin Analytics")
analytics_page = st.Page("pages/analytics.py", title="Historical Trends")

monitoring_page = st.Page("pages/monitoring.py", title="Predictive Failover")
autoscaling_page = st.Page("pages/autoscaling.py", title="Horizontal Autoscaling")
chaos_page = st.Page("pages/chaos_lab.py", title="Chaos Lab")
logs_page = st.Page("pages/logs.py", title="Audit Logs")

settings_page = st.Page("pages/settings.py", title="Configuration")

pg = st.navigation({
    "OVERVIEW": [overview_page, servers_page, traffic_flow_page, incidents_page],
    "INTELLIGENCE": [prediction_page, digital_twin_page, analytics_page],
    "OPERATIONS": [monitoring_page, autoscaling_page, chaos_page, logs_page],
    "SYSTEM": [settings_page]
})

pg.run()
