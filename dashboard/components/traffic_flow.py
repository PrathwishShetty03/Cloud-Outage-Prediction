import streamlit as st

def render_traffic_flow_animation(active_server, snapshot, prediction):
    st.markdown("## Traffic Topology & Routing Diagram")
    st.caption("Live HTTP ingress routing through HAProxy L7 proxy engine to backend target nodes.")

    ma = snapshot.get("server_a", {})
    mb = snapshot.get("server_b", {})
    mc = snapshot.get("server_c", {})

    req_a = ma.get("total_requests", 0)
    req_b = mb.get("total_requests", 0)
    req_c = mc.get("total_requests", 0)

    prob = prediction.get("outage_probability", 0.05)
    is_risk = (prob >= 0.80 or ma.get("status") in ["WARNING", "UNHEALTHY", "AT_RISK"])

    if active_server == "SERVER_A":
        route_a_color = "#F59E0B" if is_risk else "#22C55E"
        route_b_color = "#64748B"
        route_c_color = "#64748B"
    elif active_server == "SERVER_B":
        route_a_color = "#F59E0B" if is_risk else "#64748B"
        route_b_color = "#22C55E"
        route_c_color = "#64748B"
    else:
        route_a_color = "#EF4444"
        route_b_color = "#EF4444"
        route_c_color = "#22C55E"

    srv_a_label = "Server A (AT RISK)" if is_risk else "Server A (PRIMARY)"
    srv_b_label = "Server B (ACTIVE)" if active_server == "SERVER_B" else "Server B (TWIN STANDBY)"

    svg_html = f'<div style="background: #151F32; border-radius: 8px; padding: 20px; border: 1px solid #29364A; text-anchor: middle; margin-bottom: 14px;"><svg width="100%" height="160" viewBox="0 0 800 160" xmlns="http://www.w3.org/2000/svg"><rect x="20" y="55" width="120" height="50" rx="6" fill="#0B1220" stroke="#4F7CFF" stroke-width="2"/><text x="80" y="85" fill="#F1F5F9" font-weight="600" font-size="13" text-anchor="middle">CLIENT TRAFFIC</text><line x1="140" y1="80" x2="250" y2="80" stroke="#4F7CFF" stroke-width="2" stroke-dasharray="5,5"/><rect x="250" y="45" width="160" height="70" rx="6" fill="#0B1220" stroke="#10B981" stroke-width="2"/><text x="330" y="78" fill="#F1F5F9" font-weight="700" font-size="13" text-anchor="middle">HAProxy :80</text><text x="330" y="98" fill="#94A3B8" font-size="11" text-anchor="middle">L7 Reverse Proxy</text><line x1="410" y1="65" x2="580" y2="30" stroke="{route_a_color}" stroke-width="2" stroke-dasharray="4,4"/><line x1="410" y1="80" x2="580" y2="80" stroke="{route_b_color}" stroke-width="2" stroke-dasharray="4,4"/><line x1="410" y1="95" x2="580" y2="130" stroke="{route_c_color}" stroke-width="2" stroke-dasharray="4,4"/><rect x="580" y="10" width="200" height="40" rx="4" fill="#0B1220" stroke="{route_a_color}" stroke-width="2"/><text x="680" y="35" fill="#F1F5F9" font-weight="600" font-size="11.5" text-anchor="middle">{srv_a_label} [{req_a:,} reqs]</text><rect x="580" y="60" width="200" height="40" rx="4" fill="#0B1220" stroke="{route_b_color}" stroke-width="2"/><text x="680" y="85" fill="#F1F5F9" font-weight="600" font-size="11.5" text-anchor="middle">{srv_b_label} [{req_b:,} reqs]</text><rect x="580" y="110" width="200" height="40" rx="4" fill="#0B1220" stroke="{route_c_color}" stroke-width="2"/><text x="680" y="135" fill="#F1F5F9" font-weight="600" font-size="11.5" text-anchor="middle">Server C (5003) [{req_c:,} reqs]</text></svg></div>'
    st.markdown(svg_html, unsafe_allow_html=True)

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        p1_html = '<div style="background: #151F32; border: 1px solid #29364A; border-radius: 6px; padding: 14px;"><div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; margin-bottom: 8px; text-transform: uppercase;">PRE-FAILOVER BASELINE ROUTING</div><div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.6;">• Primary Route Target: <strong style="color: #F1F5F9;" class="tech-id">Server A (Port 5001)</strong><br>• Backup Route Target: <span style="color: #94A3B8;" class="tech-id">Server B (Port 5002 - Standby)</span><br>• Baseline Risk Level: <strong>15.0% (Normal)</strong><br>• Routing Strategy: <strong>HAProxy Layer 7 Direct Ingress</strong></div></div>'
        st.markdown(p1_html, unsafe_allow_html=True)

    with col_p2:
        srv_a_status = f"Frozen at {req_a:,} reqs" if active_server != "SERVER_A" and req_a > 0 else "Active Ingress"
        srv_b_status = f"Active at {req_b:,} reqs" if active_server == "SERVER_B" else "Standby"
        risk_color = "#F59E0B" if prob >= 0.80 else "#22C55E"
        risk_score_str = f"{round(prob * 100, 1)}%"
        p2_html = f'<div style="background: #151F32; border: 1px solid #4F7CFF; border-radius: 6px; padding: 14px;"><div style="font-size: 0.8rem; font-weight: 700; color: #4F7CFF; margin-bottom: 8px; text-transform: uppercase;">LIVE ACTIVE INGRESS ROUTE</div><div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.6;">• Current Ingress Target: <strong style="color: #22C55E;" class="tech-id">{active_server}</strong><br>• Server A Status: <strong>{req_a:,} reqs ({srv_a_status})</strong><br>• Server B Status: <strong>{req_b:,} reqs ({srv_b_status})</strong><br>• Outage Risk Score: <strong style="color:{risk_color}">{risk_score_str}</strong></div></div>'
        st.markdown(p2_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    banner_html = '<div style="background: #0B1220; border: 1px solid #29364A; border-radius: 6px; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center;"><div><div style="font-size: 0.85rem; font-weight: 600; color: #F1F5F9;">HAProxy Engine Telemetry</div><div style="font-size: 0.8rem; color: #94A3B8;">Inspect live route table stats directly on HAProxy engine port 8404.</div></div><div><a href="http://localhost:8404/stats" target="_blank" style="background: #4F7CFF; color: #ffffff; padding: 6px 14px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; text-decoration: none;">Open HAProxy Stats (:8404)</a></div></div>'
    st.markdown(banner_html, unsafe_allow_html=True)
