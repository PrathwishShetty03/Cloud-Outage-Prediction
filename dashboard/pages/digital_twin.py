import streamlit as st
from dashboard.shared.state import init_session_state, get_telemetry_evaluation
from dashboard.components.digital_twin import render_digital_twin_section

controller = init_session_state()
eval_res = get_telemetry_evaluation(controller)
snapshot = eval_res["snapshot"]

st.title("Digital Twin Analytics")
st.caption("State Synchronization, Metric Divergence Evaluation & Scenario Simulation")

render_digital_twin_section(snapshot, eval_res, controller)
