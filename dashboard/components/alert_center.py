import streamlit as st

def render_alert_center_section(snapshot, prediction, eval_res):
    st.markdown("## Incident Management & Event Feed")
    st.caption("Live incident timeline generated from infrastructure health probes, failover triggers, and self-healing actions.")

    controller = st.session_state.get("controller")
    logs = controller.failover_logs if controller else []

    # KPI Summary Row
    crit_count = sum(1 for l in logs if l.get("severity") == "CRITICAL")
    warn_count = sum(1 for l in logs if l.get("severity") == "WARNING")
    info_count = sum(1 for l in logs if l.get("severity") == "INFO")
    total_count = len(logs)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Events", total_count)
    with k2:
        st.metric("Critical Alerts", crit_count, delta="Action Required" if crit_count > 0 else "Clear", delta_color="inverse" if crit_count > 0 else "normal")
    with k3:
        st.metric("Warning Alerts", warn_count, delta="Monitoring" if warn_count > 0 else "Clear", delta_color="inverse" if warn_count > 0 else "normal")
    with k4:
        st.metric("System Logs", info_count)

    st.markdown("---")

    # Severity Filter Selector
    filter_col1, _ = st.columns([2, 3])
    with filter_col1:
        category = st.selectbox(
            "Filter Incident Severity",
            ["ALL", "CRITICAL", "WARNING", "INFO", "FAILOVER"],
            index=0
        )

    filtered_logs = logs
    if category != "ALL":
        if category == "FAILOVER":
            filtered_logs = [l for l in logs if "FAILOVER" in l.get("event_type", "") or "FAILBACK" in l.get("event_type", "")]
        else:
            filtered_logs = [l for l in logs if l.get("severity") == category]

    if not filtered_logs:
        st.info("● Infrastructure operating within normal parameters. No active incidents recorded.")
        return

    # Render Incident Timeline
    for log in filtered_logs[:12]:
        severity = log.get("severity", "INFO")
        event_type = log.get("event_type", "EVENT")
        server = log.get("server", "SYSTEM")
        ts = log.get("timestamp", log.get("iso_time", ""))
        desc = log.get("description", "")

        if severity == "CRITICAL":
            badge_html = '<span class="status-badge badge-critical">● CRITICAL</span>'
            border_color = "#EF4444"
        elif severity == "WARNING":
            badge_html = '<span class="status-badge badge-warning">● WARNING</span>'
            border_color = "#F59E0B"
        else:
            badge_html = '<span class="status-badge badge-healthy">● INFO</span>'
            border_color = "#4F7CFF"

        st.markdown(f"""
        <div style="background: #151F32; border-left: 4px solid {border_color}; border-radius: 4px; padding: 12px 16px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    {badge_html}
                    <strong style="color: #F1F5F9; font-size: 0.9rem;">{event_type}</strong>
                    <span style="color: #94A3B8; font-size: 0.8rem;">| Target Node: <code style="color: #4F7CFF;" class="tech-id">{server}</code></span>
                </div>
                <div style="font-size: 0.78rem; color: #94A3B8;" class="tech-id">{ts}</div>
            </div>
            <div style="margin-top: 6px; color: #CBD5E1; font-size: 0.85rem;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
