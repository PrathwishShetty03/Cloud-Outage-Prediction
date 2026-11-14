import streamlit as st
from dashboard.shared.state import init_session_state, get_telemetry_evaluation
from dashboard.components.resource_graphs import render_live_resource_graphs

controller = init_session_state()
eval_res = get_telemetry_evaluation(controller)

st.title("Predictive Failover & Telemetry")
st.caption("Real-Time Telemetry Stream Analytics & Primary vs Twin Performance Evaluation")

render_live_resource_graphs(controller.history_a, controller.history_b)
