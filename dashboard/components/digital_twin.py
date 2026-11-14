import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_digital_twin_section(snapshot, eval_res, controller):
    st.markdown("## Digital Twin State Sync & Metric Divergence")
    st.caption("Real-time telemetry comparison between Observed Server A and Digital Twin Server B + Predictive Trend Horizons (+10s, +20s, +30s).")

    twin_data = eval_res.get("digital_twin", {})
    trends_data = eval_res.get("projected_trends", {})
    div_score = twin_data.get("divergence_score", 0.0)
    sync_status = twin_data.get("sync_status", "SYNCHRONIZED")

    # KPI Header Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Divergence Score", f"{div_score}%", delta=sync_status, delta_color="normal" if sync_status == "SYNCHRONIZED" else "inverse")
    with k2:
        st.metric("Sync Status", sync_status)
    with k3:
        st.metric("State Match", "MATCHED" if twin_data.get("state_match", True) else "DIVERGENT")
    with k4:
        st.metric("Twin Target Node", "Server B (Port 5002)")

    st.markdown("---")

    col_t1, col_t2 = st.columns([1, 1])

    with col_t1:
        status_color = "#22C55E" if sync_status == "SYNCHRONIZED" else "#EF4444"
        fig_div = go.Figure(go.Indicator(
            mode="gauge+number",
            value=div_score,
            number={'suffix': "%", 'font': {'color': status_color, 'size': 38}},
            title={'text': f"Metric Divergence ({sync_status})", 'font': {'size': 14, 'color': '#F1F5F9'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#64748B"},
                'bar': {'color': status_color},
                'steps': [
                    {'range': [0, 15], 'color': "#064E3B"},
                    {'range': [15, 100], 'color': "#7F1D1D"}
                ],
                'threshold': {
                    'line': {'color': "#F1F5F9", 'width': 3},
                    'thickness': 0.75,
                    'value': 15.0
                }
            }
        ))

        fig_div.update_layout(
            paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
            font=dict(color="#F1F5F9", family="Inter"),
            margin=dict(l=20, r=20, t=40, b=20),
            height=250
        )
        st.plotly_chart(fig_div, use_container_width=True)

    with col_t2:
        st.markdown(f"""
        <div style="background: #151F32; border-radius: 6px; padding: 16px; border: 1px solid #29364A; height: 250px;">
            <div style="font-weight: 700; font-size: 0.85rem; color: #4F7CFF; margin-bottom: 12px; text-transform: uppercase;">Observed vs Twin Telemetry Deltas</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85rem; color: #CBD5E1;">
                <div>CPU Delta: <strong class="tech-id">{twin_data.get('cpu_delta', 0.0)}%</strong></div>
                <div>Memory Delta: <strong class="tech-id">{twin_data.get('memory_delta', 0.0)}%</strong></div>
                <div>Disk Delta: <strong class="tech-id">{twin_data.get('disk_delta', 0.0)}%</strong></div>
                <div>Latency Delta: <strong class="tech-id">{twin_data.get('latency_delta_ms', 0.0)} ms</strong></div>
                <div>Error Rate Delta: <strong class="tech-id">{twin_data.get('error_rate_delta', 0.0)}%</strong></div>
                <div>Request Delta: <strong class="tech-id">{twin_data.get('request_delta', 0)} reqs</strong></div>
                <div>State Alignment: <strong>{'VALID' if twin_data.get('state_match', True) else 'DIVERGENT'}</strong></div>
                <div>Sync Threshold: <strong>15.0% Limit</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Predictive Digital Twin Trend Forecasting Graph
    st.markdown("### Metric Velocity Trend Forecasting (+10s, +20s, +30s)")
    p_mem = trends_data.get("projected_memory", {10: 30, 20: 30, 30: 30})
    p_cpu = trends_data.get("projected_cpu", {10: 20, 20: 20, 30: 20})

    fig_trends = go.Figure()
    fig_trends.add_trace(go.Scatter(x=["+10s", "+20s", "+30s"], y=[p_mem[10], p_mem[20], p_mem[30]], mode='lines+markers', name='Projected Memory %', line=dict(color='#A78BFA', width=2)))
    fig_trends.add_trace(go.Scatter(x=["+10s", "+20s", "+30s"], y=[p_cpu[10], p_cpu[20], p_cpu[30]], mode='lines+markers', name='Projected CPU %', line=dict(color='#4F7CFF', width=2)))

    fig_trends.update_layout(
        paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
        font=dict(color="#F1F5F9", family="Inter"),
        yaxis=dict(range=[0, 100], title="Metric Target (%)", gridcolor="#29364A"),
        xaxis=dict(title="Future Time Horizon", gridcolor="#29364A"),
        margin=dict(l=20, r=20, t=30, b=20),
        height=230
    )
    st.plotly_chart(fig_trends, use_container_width=True)

    # Interactive What-If Simulation Engine
    st.markdown("### What-If Stress Scenario Simulator")
    with st.expander("Configure What-If Offset Parameters", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            cpu_sim = st.slider("Simulated CPU Delta (%)", -50.0, 50.0, 20.0)
        with c2:
            mem_sim = st.slider("Simulated Memory Delta (%)", -50.0, 50.0, 25.0)
        with c3:
            lat_sim = st.slider("Simulated Latency Offset (ms)", 0.0, 3000.0, 500.0)
        with c4:
            err_sim = st.slider("Simulated Error Offset (%)", 0.0, 50.0, 10.0) / 100.0

        base_a = snapshot.get("server_a", {})
        sim_res = controller.twin_engine.simulate_what_if(
            base_metrics=base_a,
            cpu_delta=cpu_sim,
            memory_delta=mem_sim,
            latency_delta=lat_sim,
            error_delta=err_sim,
            predictor=controller.ml_predictor.predictor
        )

        st.markdown(f"""
        <div style="background: #0B1220; border: 1px solid #4F7CFF; border-radius: 6px; padding: 14px; margin-top: 10px;">
            <div style="font-weight: 700; font-size: 0.85rem; color: #4F7CFF; margin-bottom: 8px; text-transform: uppercase;">Simulated Scenario Outcome</div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; font-size: 0.85rem; color: #CBD5E1;">
                <div>Simulated Risk: <strong style="color: #F59E0B;" class="tech-id">{sim_res['simulated_outage_probability_pct']}%</strong></div>
                <div>Simulated Risk Level: <strong>{sim_res['simulated_risk_level']}</strong></div>
                <div>Simulated Divergence: <strong class="tech-id">{sim_res['simulated_divergence_score']}%</strong></div>
                <div>Simulated Sync Status: <strong>{sim_res['simulated_sync_status']}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
