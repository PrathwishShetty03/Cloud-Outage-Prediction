import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render_live_resource_graphs(history_a, history_b):
    st.markdown("## Live Telemetry Stream Analytics")
    st.caption("Real-time metric sequence tracking comparing Primary Server A vs Digital Twin Server B.")

    if not history_a:
        st.info("● Gathering initial telemetry frames...")
        return

    df_a = pd.DataFrame(history_a)
    df_b = pd.DataFrame(history_b) if history_b else pd.DataFrame()

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_cpu = go.Figure()
        fig_cpu.add_trace(go.Scatter(y=df_a.get("cpu_percent", df_a.get("cpu", [])), name="Server A CPU %", line=dict(color="#4F7CFF", width=2)))
        if not df_b.empty and "cpu_percent" in df_b:
            fig_cpu.add_trace(go.Scatter(y=df_b.get("cpu_percent", df_b.get("cpu", [])), name="Server B CPU %", line=dict(color="#22C55E", width=2, dash="dash")))
        
        fig_cpu.update_layout(
            title=dict(text="CPU Utilization (%)", font=dict(size=14, color="#F1F5F9")),
            paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
            font=dict(color="#F1F5F9", family="Inter"),
            yaxis=dict(gridcolor="#29364A"), xaxis=dict(gridcolor="#29364A"),
            margin=dict(l=20, r=20, t=40, b=20), height=240
        )
        st.plotly_chart(fig_cpu, use_container_width=True)

    with col_g2:
        fig_lat = go.Figure()
        fig_lat.add_trace(go.Scatter(y=df_a.get("latency_ms", df_a.get("latency", [])), name="Server A Latency (ms)", line=dict(color="#F59E0B", width=2)))
        if not df_b.empty and "latency_ms" in df_b:
            fig_lat.add_trace(go.Scatter(y=df_b.get("latency_ms", df_b.get("latency", [])), name="Server B Latency (ms)", line=dict(color="#A78BFA", width=2, dash="dash")))
        
        fig_lat.update_layout(
            title=dict(text="Network Latency Surges (ms)", font=dict(size=14, color="#F1F5F9")),
            paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
            font=dict(color="#F1F5F9", family="Inter"),
            yaxis=dict(gridcolor="#29364A"), xaxis=dict(gridcolor="#29364A"),
            margin=dict(l=20, r=20, t=40, b=20), height=240
        )
        st.plotly_chart(fig_lat, use_container_width=True)

    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        fig_err = go.Figure()
        fig_err.add_trace(go.Scatter(y=df_a.get("error_rate", []) * 100, name="Server A Error Rate %", line=dict(color="#EF4444", width=2)))
        if not df_b.empty and "error_rate" in df_b:
            fig_err.add_trace(go.Scatter(y=df_b.get("error_rate", []) * 100, name="Server B Error Rate %", line=dict(color="#F472B6", width=2, dash="dash")))
        
        fig_err.update_layout(
            title=dict(text="Error Rate Ratio (%)", font=dict(size=14, color="#F1F5F9")),
            paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
            font=dict(color="#F1F5F9", family="Inter"),
            yaxis=dict(gridcolor="#29364A"), xaxis=dict(gridcolor="#29364A"),
            margin=dict(l=20, r=20, t=40, b=20), height=240
        )
        st.plotly_chart(fig_err, use_container_width=True)

    with col_g4:
        fig_req = go.Figure()
        fig_req.add_trace(go.Scatter(y=df_a.get("total_requests", []), name="Server A Requests", line=dict(color="#4F7CFF", width=2)))
        if not df_b.empty and "total_requests" in df_b:
            fig_req.add_trace(go.Scatter(y=df_b.get("total_requests", []), name="Server B Requests", line=dict(color="#22C55E", width=2)))
        
        fig_req.update_layout(
            title=dict(text="Cumulative Requests Ingress", font=dict(size=14, color="#F1F5F9")),
            paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
            font=dict(color="#F1F5F9", family="Inter"),
            yaxis=dict(gridcolor="#29364A"), xaxis=dict(gridcolor="#29364A"),
            margin=dict(l=20, r=20, t=40, b=20), height=240
        )
        st.plotly_chart(fig_req, use_container_width=True)
