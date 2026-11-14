import streamlit as st
from dashboard.shared.state import init_session_state, get_telemetry_evaluation
from dashboard.shared.data_fetch import trigger_shared_live_demo
from dashboard.components.header import render_top_header
from dashboard.components.server_monitoring import render_server_monitoring_section
from dashboard.components.alert_center import render_alert_center_section
from dashboard.components.traffic_flow import render_traffic_flow_animation
from dashboard.components.outage_prediction import render_outage_prediction_section
from dashboard.components.digital_twin import render_digital_twin_section

controller = init_session_state()

st.title("System Overview")
st.caption("Production Cluster Reliability & Infrastructure Observability Console")

col_demo1, col_demo2 = st.columns([3, 1])
with col_demo1:
    st.markdown('<div style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">Workload Escalation Scenario: Evaluates telemetry sequence → triggers ML risk score >= 80% → HAProxy proactive route transfer to Server B.</div>', unsafe_allow_html=True)
with col_demo2:
    if st.button("Run Failover Simulation", type="primary", use_container_width=True, key="overview_live_demo_btn"):
        trigger_shared_live_demo(controller)
        st.rerun()

st.markdown("---")

@st.fragment(run_every="1.5s")
def render_live_overview_dashboard():
    eval_res = get_telemetry_evaluation(controller)
    snapshot = eval_res["snapshot"]
    prediction = eval_res["prediction"]
    active_server = eval_res["active_server"]

    # Top Header KPI Bar
    render_top_header(active_server, eval_res, snapshot, prediction)

    # Operational Predictive Failover Control Panel
    prob = prediction.get("outage_probability", 0.05)
    prob_pct = round(prob * 100.0, 1)
    f_type = eval_res.get("failover_type", getattr(controller, "failover_type", "NORMAL"))
    ma = snapshot.get("server_a", {})
    mb = snapshot.get("server_b", {})
    status_a = ma.get("status", "HEALTHY")
    status_b = mb.get("status", "HEALTHY")

    if f_type == "EMERGENCY" or status_a == "UNHEALTHY" or not ma.get("is_reachable", True):
        border_color = "#EF4444"
        badge_html = '<span class="status-badge badge-critical">● EMERGENCY FAILOVER ACTIVE</span>'
        primary_label = f"DOWN / OUTAGE ({status_a})"
        color_a = "#EF4444"
    elif prob >= 0.80 or f_type == "PREDICTIVE":
        border_color = "#F59E0B"
        badge_html = '<span class="status-badge badge-warning">● PREDICTIVE FAILOVER TRIGGERED</span>'
        primary_label = f"AT RISK ({prob_pct}% Risk)"
        color_a = "#F59E0B"
    elif status_a == "RECOVERING":
        border_color = "#F59E0B"
        badge_html = '<span class="status-badge badge-warning">● NODE RECOVERING</span>'
        primary_label = "RECOVERING..."
        color_a = "#F59E0B"
    else:
        border_color = "#29364A"
        badge_html = '<span class="status-badge badge-healthy">● NORMAL MONITORING</span>'
        primary_label = f"HEALTHY ({prob_pct}% Risk)"
        color_a = "#22C55E"

    color_b = "#22C55E" if active_server == "SERVER_B" else "#94A3B8"
    status_b_label = "ACTIVE INGRESS" if active_server == "SERVER_B" else status_b

    ctrl_panel_html = f'<div style="background: #151F32; border: 1px solid {border_color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;"><div style="font-weight: 700; font-size: 0.95rem; color: #F1F5F9; text-transform: uppercase; letter-spacing: 0.04em;">Predictive Failover Controller</div>{badge_html}</div><div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; font-size: 0.85rem;"><div>Active Target: <br><strong style="color: #4F7CFF; font-size: 1rem;" class="tech-id">{active_server}</strong></div><div>Primary Server A: <br><strong style="color:{color_a};">{primary_label}</strong></div><div>Backup Server B: <br><strong style="color:{color_b};">{status_b_label}</strong></div><div>Failover Mode: <br><strong style="color: #CBD5E1;">{f_type}</strong></div></div></div>'
    st.markdown(ctrl_panel_html, unsafe_allow_html=True)

    st.markdown("### Infrastructure Telemetry")
    render_server_monitoring_section(snapshot, active_server)

    st.markdown("---")

    st.markdown("### Operational Incidents Timeline")
    render_alert_center_section(snapshot, prediction, eval_res)

    st.markdown("---")

    st.markdown("### Active Traffic Ingress Topology")
    render_traffic_flow_animation(active_server, snapshot, prediction)

    st.markdown("---")

    col_left, col_right = st.columns(2)
    with col_left:
        render_outage_prediction_section(prediction, controller.history_a, controller.ml_predictor)

    with col_right:
        render_digital_twin_section(snapshot, eval_res, controller)

render_live_overview_dashboard()
