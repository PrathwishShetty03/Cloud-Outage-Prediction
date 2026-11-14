import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.shared.state import init_session_state, get_telemetry_evaluation

controller = init_session_state()
eval_res = get_telemetry_evaluation(controller)

st.title("Historical Trends")
st.caption("Telemetry Correlation, Resource Utilization Trends, and Multi-Node Performance Comparison")

hist_a = controller.history_a
hist_b = controller.history_b

if hist_a and len(hist_a) > 1:
    df_a = pd.DataFrame(hist_a)
    df_b = pd.DataFrame(hist_b) if hist_b else pd.DataFrame()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### CPU & Memory Utilization (Server A)")
        fig_cpu = px.line(df_a, y=["cpu_percent", "memory_percent"],
                          labels={"value": "Percentage (%)", "index": "Sequence Window"},
                          color_discrete_sequence=["#EF4444", "#4F7CFF"])
        fig_cpu.update_layout(
            paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
            font=dict(color="#F1F5F9", family="Inter"),
            yaxis=dict(gridcolor="#29364A"), xaxis=dict(gridcolor="#29364A"),
            margin=dict(l=20, r=20, t=30, b=20), height=240
        )
        st.plotly_chart(fig_cpu, use_container_width=True)

    with c2:
        st.markdown("### Latency Trend (Server A)")
        fig_lat = px.area(df_a, y="latency_ms",
                          color_discrete_sequence=["#F59E0B"])
        fig_lat.update_layout(
            paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
            font=dict(color="#F1F5F9", family="Inter"),
            yaxis=dict(gridcolor="#29364A", title="Latency (ms)"), xaxis=dict(gridcolor="#29364A"),
            margin=dict(l=20, r=20, t=30, b=20), height=240
        )
        st.plotly_chart(fig_lat, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("### Request Throughput")
        fig_req = px.line(df_a, y="total_requests",
                          color_discrete_sequence=["#22C55E"])
        fig_req.update_layout(
            paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
            font=dict(color="#F1F5F9", family="Inter"),
            yaxis=dict(gridcolor="#29364A", title="Cumulative Requests"), xaxis=dict(gridcolor="#29364A"),
            margin=dict(l=20, r=20, t=30, b=20), height=240
        )
        st.plotly_chart(fig_req, use_container_width=True)

    with c4:
        st.markdown("### Error Rate Ratio")
        fig_err = px.line(df_a, y="error_rate",
                          color_discrete_sequence=["#EF4444"])
        fig_err.update_layout(
            paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
            font=dict(color="#F1F5F9", family="Inter"),
            yaxis=dict(gridcolor="#29364A", title="Error Rate Ratio"), xaxis=dict(gridcolor="#29364A"),
            margin=dict(l=20, r=20, t=30, b=20), height=240
        )
        st.plotly_chart(fig_err, use_container_width=True)
else:
    st.info("● Accumulating telemetry sequence snapshots... Graph trends will render in a few seconds.")
