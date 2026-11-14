import streamlit as st
from dashboard.shared.state import init_session_state, get_telemetry_evaluation
from dashboard.components.outage_prediction import render_outage_prediction_section

controller = init_session_state()
eval_res = get_telemetry_evaluation(controller)
prediction = eval_res["prediction"]

st.title("ML Risk Analysis")
st.caption("Predictive Outage Probability & SHAP Shapley Feature Attribution Engine")

render_outage_prediction_section(prediction, controller.history_a, controller.ml_predictor)
