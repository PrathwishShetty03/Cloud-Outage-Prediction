import streamlit as st
from dashboard.shared.state import init_session_state
from dashboard.components.endpoint_manager import render_endpoint_manager_section
from dashboard.components.chaos_suite import render_chaos_suite_section

controller = init_session_state()

st.title("Configuration")
st.caption("Cluster Settings, Failover Controller Mode & Endpoint Health Probes")

# Failover Operation Mode Toggle
st.markdown("### ⚙️ Failover Controller Operation Mode")
mode = st.radio("Select Operation Mode", ["AUTOMATIC", "MANUAL"], index=0 if controller.failover_mode == "AUTOMATIC" else 1, horizontal=True)
controller.failover_mode = mode

if mode == "MANUAL":
    st.markdown("""
    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #F59E0B; border-radius: 4px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.85rem; color: #FBBF24;">
        ● MANUAL OVERRIDE ACTIVE: Automated ML risk failover suspended. Operators can manually force ingress route targets.
    </div>
    """, unsafe_allow_html=True)
    c_m1, c_m2, c_m3 = st.columns(3)
    if c_m1.button("Force Route -> Server A", use_container_width=True):
        controller.execute_failback("SERVER_A", "Manual Operator Override to Server A")
        st.success("Ingress route forced to Server A")
        st.rerun()
    if c_m2.button("Force Route -> Server B", use_container_width=True):
        controller.execute_failover("SERVER_B", "Manual Operator Override to Server B")
        st.success("Ingress route forced to Server B")
        st.rerun()
    if c_m3.button("Force Route -> Server C", use_container_width=True):
        controller.execute_failover("SERVER_C", "Manual Operator Override to Server C")
        st.success("Ingress route forced to Server C")
        st.rerun()

st.markdown("---")

eval_res = controller.evaluate_cycle()
snapshot = eval_res["snapshot"]
active_server = eval_res["active_server"]

render_chaos_suite_section(controller, snapshot, active_server)

st.markdown("---")

render_endpoint_manager_section()
