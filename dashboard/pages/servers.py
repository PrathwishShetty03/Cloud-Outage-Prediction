import streamlit as st
from dashboard.shared.state import init_session_state, get_telemetry_evaluation
from dashboard.components.server_monitoring import render_server_monitoring_section

controller = init_session_state()

st.title("Infrastructure Telemetry")
st.caption("Real-Time Telemetry & Resource Utilization Metrics Across Cluster Nodes")

@st.fragment(run_every="1.5s")
def render_live_servers_page():
    eval_res = get_telemetry_evaluation(controller)
    snapshot = eval_res["snapshot"]
    active_server = eval_res["active_server"]

    render_server_monitoring_section(snapshot, active_server)

    st.markdown("---")
    st.markdown("### Node Telemetry Details & Specifications")

    cols = st.columns(3)
    servers = [
        ("SERVER_A", "Primary Server A", controller.endpoint_a, "5001", snapshot.get("server_a", {})),
        ("SERVER_B", "Digital Twin Server B", controller.endpoint_b, "5002", snapshot.get("server_b", {})),
        ("SERVER_C", "Emergency Server C", controller.endpoint_c, "5003", snapshot.get("server_c", {}))
    ]

    for idx, (srv_id, name, url, port, metrics) in enumerate(servers):
        with cols[idx]:
            status = metrics.get("status", "UNHEALTHY")
            is_active = (srv_id == active_server)

            if status == "HEALTHY":
                badge_html = '<span class="status-badge badge-healthy">● HEALTHY</span>'
            elif status in ["WARNING", "RECOVERING"]:
                badge_html = f'<span class="status-badge badge-warning">● {status}</span>'
            else:
                badge_html = '<span class="status-badge badge-critical">● UNHEALTHY</span>'

            active_tag = '<span class="status-badge badge-active">ACTIVE INGRESS</span>' if is_active else '<span class="status-badge badge-standby">STANDBY</span>'

            st.markdown(f"""
            <div style="background: #151F32; border: 1px solid #29364A; border-radius: 8px; padding: 14px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 700; color: #F1F5F9; font-size: 0.95rem;">{name}</div>
                    {badge_html}
                </div>
                <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 4px; display: flex; justify-content: space-between;">
                    <span>Endpoint: <code style="color: #4F7CFF;" class="tech-id">{url}</code></span>
                    {active_tag}
                </div>
                <hr style="border: none; border-top: 1px solid #29364A; margin: 10px 0;">
                <div style="font-size: 0.82rem; color: #CBD5E1; display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                    <div>Health Score: <strong style="color: #4F7CFF;" class="tech-id">{metrics.get('health_score', 0.0)}%</strong></div>
                    <div>Requests Served: <strong class="tech-id">{metrics.get('total_requests', 0):,}</strong></div>
                    <div>CPU Usage: <strong class="tech-id">{metrics.get('cpu_percent', metrics.get('cpu', 0.0))}%</strong></div>
                    <div>Memory Usage: <strong class="tech-id">{metrics.get('memory_percent', metrics.get('memory', 0.0))}%</strong></div>
                    <div>Disk Usage: <strong class="tech-id">{metrics.get('disk_percent', metrics.get('disk', 0.0))}%</strong></div>
                    <div>Latency: <strong class="tech-id">{metrics.get('latency_ms', metrics.get('latency', 0.0))} ms</strong></div>
                    <div>Avg Response: <strong class="tech-id">{metrics.get('average_response_time', metrics.get('response_time', 0.0))} ms</strong></div>
                    <div>Error Rate: <strong class="tech-id">{round(metrics.get('error_rate', 0.0) * 100, 2)}%</strong></div>
                    <div>Active Reqs: <strong class="tech-id">{metrics.get('active_requests', 0)}</strong></div>
                    <div>Uptime: <strong class="tech-id">{metrics.get('uptime', 0)}s</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

render_live_servers_page()
