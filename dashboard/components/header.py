import time
from datetime import datetime, timezone, timedelta
import streamlit as st

def render_top_header(active_server, eval_res, snapshot, prediction):
    ma = snapshot.get("server_a", {})
    mb = snapshot.get("server_b", {})
    mc = snapshot.get("server_c", {})
    
    req_a = ma.get("total_requests", 0)
    req_b = mb.get("total_requests", 0)
    req_c = mc.get("total_requests", 0)
    total_reqs = req_a + req_b + req_c
    
    prob = prediction.get("outage_probability", 0.05)
    prob_pct = round(prob * 100.0, 1)
    
    twin_res = eval_res.get("digital_twin", {})
    div_score = twin_res.get("divergence_score", 0.0)
    sync_status = twin_res.get("sync_status", "SYNCHRONIZED")

    status_a = ma.get("status", "UNHEALTHY")
    status_b = mb.get("status", "UNHEALTHY")
    
    if status_a == "HEALTHY" and status_b == "HEALTHY":
        sys_status_badge = '<span class="status-badge badge-healthy">● HEALTHY</span>'
    elif status_a == "WARNING" or status_b == "WARNING":
        sys_status_badge = '<span class="status-badge badge-warning">● WARNING</span>'
    else:
        sys_status_badge = '<span class="status-badge badge-critical">● DEGRADED</span>'

    IST = timezone(timedelta(hours=5, minutes=30))
    current_time = datetime.now(IST).strftime("%H:%M:%S") + " IST"

    # Header Bar (Constructed without leading indentation to prevent markdown pre/code block formatting)
    header_html = f'<div style="background: #151F32; border: 1px solid #29364A; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;"><div><div style="font-size: 1.15rem; font-weight: 700; color: #F1F5F9; letter-spacing: -0.01em;">Predictive Failover Platform <span style="font-size: 0.72rem; font-weight: 600; color: #4F7CFF; background: #1B263A; border: 1px solid rgba(79, 124, 255, 0.3); padding: 2px 8px; border-radius: 4px; margin-left: 8px;">PRODUCTION</span></div><div style="font-size: 0.8rem; color: #94A3B8; margin-top: 2px;">Multi-Region Infrastructure Observability & Autonomous Failover Control Loop</div></div><div style="display: flex; align-items: center; gap: 16px; font-size: 0.8rem; color: #94A3B8;"><div>Status: {sys_status_badge}</div><div style="border-left: 1px solid #29364A; padding-left: 14px;">Ingress: <strong style="color: #4F7CFF;" class="tech-id">HAProxy :80 → {active_server}</strong></div><div style="border-left: 1px solid #29364A; padding-left: 14px;">Updated: <span style="color: #F1F5F9;" class="tech-id">{current_time}</span></div></div></div>'
    st.markdown(header_html, unsafe_allow_html=True)

    # Top Metric Summary Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.metric("Active Ingress", active_server, delta="HAProxy 100%" if active_server == "SERVER_A" else "FAILOVER ACTIVE")
    with c2:
        st.metric("Cluster Requests", f"{total_reqs:,}", delta=f"A:{req_a} B:{req_b} C:{req_c}")
    with c3:
        st.metric("Outage Risk", f"{prob_pct}%", delta="HIGH RISK" if prob >= 0.80 else "NORMAL", delta_color="inverse" if prob >= 0.80 else "normal")
    with c4:
        st.metric("Twin Divergence", f"{div_score}%", delta=sync_status)
    with c5:
        err_a = ma.get("error_rate", 0.0) * 100.0
        st.metric("Error Rate", f"{round(err_a, 2)}%", delta="SLO Compliant" if err_a < 1.0 else "Breach", delta_color="normal" if err_a < 1.0 else "inverse")
