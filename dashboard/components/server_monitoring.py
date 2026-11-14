import streamlit as st

def render_server_monitoring_section(snapshot, active_server, view_mode="table"):
    ma = snapshot.get("server_a", {})
    mb = snapshot.get("server_b", {})
    mc = snapshot.get("server_c", {})

    status_a = ma.get("status", "UNHEALTHY")
    status_b = mb.get("status", "UNHEALTHY")
    status_c = mc.get("status", "UNHEALTHY")

    active_m = snapshot.get(active_server.lower(), {})
    if active_m.get("status") == "UNHEALTHY" or not active_m.get("is_reachable", True):
        if status_a == "HEALTHY" and ma.get("is_reachable", True):
            effective_active = "SERVER_A"
        elif status_b == "HEALTHY" and mb.get("is_reachable", True):
            effective_active = "SERVER_B"
        elif status_c == "HEALTHY" and mc.get("is_reachable", True):
            effective_active = "SERVER_C"
        else:
            effective_active = "SERVER_A"
    else:
        effective_active = active_server

    nodes_data = [
        ("Server A", "PRIMARY", 5001, ma, effective_active == "SERVER_A"),
        ("Server B", "BACKUP / TWIN", 5002, mb, effective_active == "SERVER_B"),
        ("Server C", "EMERGENCY", 5003, mc, effective_active == "SERVER_C")
    ]

    # Compact Enterprise Telemetry Table View (Constructed without leading indentation to prevent markdown pre/code formatting)
    table_rows_html = ""
    for name, role, port, metrics, is_active in nodes_data:
        status = metrics.get("status", "UNHEALTHY")
        health_score = metrics.get("health_score", 0.0)
        cpu = metrics.get("cpu_percent", metrics.get("cpu", 0.0))
        mem = metrics.get("memory_percent", metrics.get("memory", 0.0))
        disk = metrics.get("disk_percent", metrics.get("disk", 0.0))
        lat = metrics.get("latency_ms", metrics.get("latency", 0.0))
        err = metrics.get("error_rate", 0.0) * 100.0
        reqs = metrics.get("total_requests", 0)

        if status == "HEALTHY":
            badge_html = '<span class="status-badge badge-healthy">● HEALTHY</span>'
        elif status in ["WARNING", "RECOVERING"]:
            badge_html = f'<span class="status-badge badge-warning">● {status}</span>'
        else:
            badge_html = '<span class="status-badge badge-critical">● UNHEALTHY</span>'

        if is_active:
            role_html = f'<b>{role}</b> <span class="status-badge badge-active">ACTIVE INGRESS</span>'
        else:
            role_html = f'<span style="color: #94A3B8;">{role}</span> <span class="status-badge badge-standby">STANDBY</span>'

        table_rows_html += f'<tr><td style="font-weight: 600; color: #F1F5F9;">{name}</td><td>{role_html}</td><td>{badge_html}</td><td class="tech-id">:{port}</td><td style="color: #4F7CFF; font-weight: 600;" class="tech-id">{health_score}%</td><td class="tech-id">{cpu}%</td><td class="tech-id">{mem}%</td><td class="tech-id">{disk}%</td><td class="tech-id">{lat} ms</td><td class="tech-id">{round(err, 2)}%</td><td style="font-weight: 600;" class="tech-id">{reqs:,}</td></tr>'

    full_table_html = f'<table style="width: 100%; border-collapse: collapse; margin-bottom: 14px;"><thead><tr><th>Node Name</th><th>Cluster Role</th><th>Status</th><th>Port</th><th>Health Score</th><th>CPU %</th><th>Memory %</th><th>Disk %</th><th>Latency</th><th>Error Rate</th><th>Requests Served</th></tr></thead><tbody>{table_rows_html}</tbody></table>'
    
    st.markdown(full_table_html, unsafe_allow_html=True)

    # Detailed Node Cards below table
    col_a, col_b, col_c = st.columns(3)
    cols = [col_a, col_b, col_c]

    for idx, (name, role, port, metrics, is_active) in enumerate(nodes_data):
        with cols[idx]:
            status = metrics.get("status", "UNHEALTHY")
            rem_sec = metrics.get("recovery_remaining_sec", 0.0)
            health_score = metrics.get("health_score", 0.0)
            cpu = metrics.get("cpu_percent", metrics.get("cpu", 0.0))
            mem = metrics.get("memory_percent", metrics.get("memory", 0.0))
            disk = metrics.get("disk_percent", metrics.get("disk", 0.0))
            lat = metrics.get("latency_ms", metrics.get("latency", 0.0))
            err = metrics.get("error_rate", 0.0) * 100.0
            reqs = metrics.get("total_requests", 0)
            active_reqs = metrics.get("active_requests", 0)
            uptime = metrics.get("uptime", 0)
            resp_time = metrics.get("response_time_ms", lat + 12.0)

            if status == "HEALTHY":
                badge_html = '<span class="status-badge badge-healthy">● HEALTHY</span>'
            elif status in ["WARNING", "RECOVERING"]:
                badge_html = f'<span class="status-badge badge-warning">● {status}</span>'
            else:
                badge_html = '<span class="status-badge badge-critical">● UNHEALTHY</span>'

            card_border = "border: 1px solid #4F7CFF;" if is_active else "border: 1px solid #29364A;"
            active_tag = '<span class="status-badge badge-active">ACTIVE INGRESS</span>' if is_active else '<span class="status-badge badge-standby">STANDBY</span>'

            recovering_msg = f'<div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 4px; padding: 6px 10px; margin-top: 8px; font-size: 0.78rem; color: #F59E0B; font-weight: 500;">Remediating node state... ({rem_sec}s remaining)</div>' if status == "RECOVERING" else ''

            card_html = f'<div style="background: #151F32; border-radius: 8px; padding: 14px; {card_border} margin-bottom: 10px;"><div style="display: flex; justify-content: space-between; align-items: center;"><div style="font-weight: 700; font-size: 0.95rem; color: #F1F5F9;">{name}</div>{badge_html}</div><div style="font-size: 0.78rem; color: #94A3B8; margin-top: 4px; display: flex; align-items: center; justify-content: space-between;"><span>Role: <strong style="color: #CBD5E1;">{role}</strong> | Port: <code style="color: #4F7CFF;" class="tech-id">{port}</code></span>{active_tag}</div>{recovering_msg}<hr style="border: none; border-top: 1px solid #29364A; margin: 10px 0;"><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.82rem;"><div>Health Score: <strong style="color: #4F7CFF;" class="tech-id">{health_score}%</strong></div><div>Requests: <strong class="tech-id">{reqs:,}</strong></div><div>CPU Usage: <strong class="tech-id">{cpu}%</strong></div><div>Memory Usage: <strong class="tech-id">{mem}%</strong></div><div>Disk Usage: <strong class="tech-id">{disk}%</strong></div><div>Latency: <strong class="tech-id">{lat} ms</strong></div><div>Avg Response: <strong class="tech-id">{resp_time} ms</strong></div><div>Error Rate: <strong class="tech-id">{round(err, 2)}%</strong></div><div>Active Reqs: <strong class="tech-id">{active_reqs}</strong></div><div>Uptime: <strong class="tech-id">{uptime}s</strong></div></div></div>'
            
            st.markdown(card_html, unsafe_allow_html=True)
