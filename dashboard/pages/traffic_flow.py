import streamlit as st
from dashboard.shared.state import init_session_state, get_telemetry_evaluation
from dashboard.shared.data_fetch import trigger_shared_live_demo, fetch_haproxy_stats_raw
from dashboard.components.traffic_flow import render_traffic_flow_animation

controller = init_session_state()

st.title("Traffic Topology")
st.caption("Real-Time Request Routing & Layer 7 Ingress Control Loop (HAProxy :80)")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
    <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">
        Evaluates real-time HTTP ingress routes across Server A (Primary), Server B (Backup Twin), and Server C (Emergency).
    </div>
    """, unsafe_allow_html=True)
with col2:
    if st.button("Run Failover Simulation", type="primary", use_container_width=True, key="traffic_flow_live_demo_btn"):
        trigger_shared_live_demo(controller)
        st.rerun()

st.markdown("---")

@st.fragment(run_every="1.5s")
def render_live_traffic_flow():
    eval_res = get_telemetry_evaluation(controller)
    snapshot = eval_res["snapshot"]
    prediction = eval_res["prediction"]
    active_server = eval_res["active_server"]
    render_traffic_flow_animation(active_server, snapshot, prediction)

render_live_traffic_flow()

st.markdown("---")

st.markdown("### HAProxy Engine Statistics (Raw Telemetry)")
st.caption(f"Unfiltered ground truth stats exported from HAProxy engine on port 8404.")

stats_df = fetch_haproxy_stats_raw()
if not stats_df.empty:
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
else:
    st.info(f"HAProxy stats dashboard accessible at: [{controller.haproxy_url.replace(':80', ':8404')}/stats]({controller.haproxy_url.replace(':80', ':8404')}/stats)")
