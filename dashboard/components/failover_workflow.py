import streamlit as st

def render_failover_workflow_section(active_server, failover_logs):
    st.markdown("## 🔄 Dynamic Failover Workflow Engine & Audit Trail")

    if not failover_logs:
        st.info("No failover execution events recorded in current session.")
        return

    latest_failover = next((l for l in failover_logs if "FAILOVER" in l.get("event_type", "")), None)

    if latest_failover:
        st.markdown(f"""
        <div style="background: #1e1b4b; border: 2px solid #6366f1; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #a78bfa;">⚡ LATEST FAILOVER EVENT DETECTED</h3>
            <div style="margin-top: 10px; font-size: 0.95rem; color: #cbd5e1; line-height: 1.7;">
                • <b>Event Timestamp</b>: {latest_failover.get('timestamp', '')}<br>
                • <b>Target Server Activated</b>: <b style="color: #34d399;">{latest_failover.get('server', '')}</b><br>
                • <b>HAProxy Decision</b>: Disabled failed node; routed traffic to standby backup<br>
                • <b>Trigger Reason</b>: {latest_failover.get('description', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)
