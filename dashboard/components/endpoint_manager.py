import streamlit as st
import requests
from dashboard.shared.state import reload_env_into_state

def test_endpoint_health(url):
    try:
        clean_url = url.strip().rstrip("/") if url else ""
        r = requests.get(f"{clean_url}/health", timeout=0.5)
        return r.status_code == 200, r.json() if r.status_code == 200 else {}
    except Exception as e:
        return False, {"error": str(e)}

def render_endpoint_manager_section():
    st.markdown("## Cluster Configuration & Endpoint Inspector")
    st.caption("Active cluster endpoint resolution synchronized from environment configuration (`.env`).")

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        st.markdown('<div style="font-size: 0.85rem; color: #94A3B8;">Inspect target node health probes, reverse proxy binding, and autoscaling service endpoints.</div>', unsafe_allow_html=True)
    with col_btn2:
        if st.button("Reload Configuration (`.env`)", use_container_width=True):
            reload_env_into_state()
            st.rerun()

    st.markdown("---")

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        ep_a = st.text_input("Server A Target (Primary)", key="endpoint_a")
        ok_a, res_a = test_endpoint_health(ep_a)
        if ok_a:
            st.markdown(f'<span class="status-badge badge-healthy">● CONNECTED</span> <span style="font-size: 0.8rem; color: #94A3B8;" class="tech-id">Port {res_a.get("port", 5001)}</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge badge-critical">● UNREACHABLE</span>', unsafe_allow_html=True)

    with col_e2:
        ep_b = st.text_input("Server B Target (Backup)", key="endpoint_b")
        ok_b, res_b = test_endpoint_health(ep_b)
        if ok_b:
            st.markdown(f'<span class="status-badge badge-healthy">● CONNECTED</span> <span style="font-size: 0.8rem; color: #94A3B8;" class="tech-id">Port {res_b.get("port", 5002)}</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge badge-critical">● UNREACHABLE</span>', unsafe_allow_html=True)

    with col_e3:
        ep_c = st.text_input("Server C Target (Emergency)", key="endpoint_c")
        ok_c, res_c = test_endpoint_health(ep_c)
        if ok_c:
            st.markdown(f'<span class="status-badge badge-healthy">● CONNECTED</span> <span style="font-size: 0.8rem; color: #94A3B8;" class="tech-id">Port {res_c.get("port", 5003)}</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge badge-critical">● UNREACHABLE</span>', unsafe_allow_html=True)

    st.markdown("---")

    # Ingress & Service Endpoints Table (Single Line / Unindented String)
    st.markdown("### Load Balancer & Service Routing Inspection")
    table_html = '<table style="width: 100%; border-collapse: collapse;"><thead><tr><th>Service Name</th><th>Role</th><th>Resolved Endpoint</th><th>Binding Port</th><th>Health Probe</th></tr></thead><tbody><tr><td>HAProxy Load Balancer</td><td>L7 Ingress Router</td><td><code class="tech-id">http://localhost:80</code></td><td class="tech-id">Port 80</td><td><span class="status-badge badge-healthy">● ACTIVE</span></td></tr><tr><td>Rule-Based Autoscaler</td><td>Capacity Controller</td><td><code class="tech-id">http://localhost:9090</code></td><td class="tech-id">Port 9090</td><td><span class="status-badge badge-healthy">● ACTIVE</span></td></tr><tr><td>HAProxy Engine Stats</td><td>Telemetry Exporter</td><td><code class="tech-id">http://localhost:8404/stats</code></td><td class="tech-id">Port 8404</td><td><span class="status-badge badge-healthy">● ACTIVE</span></td></tr></tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)
