import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_outage_prediction_section(prediction, history_a, ml_predictor):
    st.markdown("## ML Outage Risk & SHAP Feature Attribution")
    st.caption("Time-Series LSTM model inferring outage probability over 10-step sequence windows paired with SHAP Shapley value contributions.")

    prob = prediction.get("outage_probability", 0.05)
    prob_pct = prediction.get("outage_probability_pct", round(prob * 100.0, 1))
    risk_level = prediction.get("risk_level", "LOW")
    ttf_sec = prediction.get("estimated_ttf_seconds")
    model_used = prediction.get("model_used", "LSTM")
    shap_contribs = prediction.get("shap_contributions", {})
    top_feature = prediction.get("top_influential_feature", "CPU Usage")
    top_impact = prediction.get("top_impact_percent", 0.0)

    # Top Metric KPI Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Outage Risk Probability", f"{prob_pct}%", delta=f"{risk_level} RISK", delta_color="inverse" if prob >= 0.50 else "normal")
    with k2:
        st.metric("Inference Engine", model_used, delta="Time-Series Sequence")
    with k3:
        st.metric("Estimated Time-to-Failure", f"{ttf_sec}s" if ttf_sec else "Stable")
    with k4:
        st.metric("Primary Risk Factor", top_feature, delta=f"{top_impact}% SHAP Contribution")

    st.markdown("---")

    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        gauge_color = "#EF4444" if prob >= 0.80 else ("#F59E0B" if prob >= 0.50 else "#22C55E")
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob_pct,
            number={'suffix': "%", 'font': {'color': gauge_color, 'size': 38}},
            title={'text': f"Outage Risk ({risk_level} RISK)", 'font': {'size': 14, 'color': '#F1F5F9'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#64748B"},
                'bar': {'color': gauge_color},
                'steps': [
                    {'range': [0, 50], 'color': "#064E3B"},
                    {'range': [50, 80], 'color': "#78350F"},
                    {'range': [80, 100], 'color': "#7F1D1D"}
                ],
                'threshold': {
                    'line': {'color': "#F1F5F9", 'width': 3},
                    'thickness': 0.75,
                    'value': 80.0
                }
            }
        ))

        fig_gauge.update_layout(
            paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
            font=dict(color="#F1F5F9", family="Inter"),
            margin=dict(l=20, r=20, t=40, b=20),
            height=260
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_p2:
        df_shap = pd.DataFrame([
            {"Feature": k, "Contribution (%)": v}
            for k, v in shap_contribs.items()
        ])

        if not df_shap.empty:
            fig_shap = go.Figure(go.Bar(
                x=df_shap["Contribution (%)"],
                y=df_shap["Feature"],
                orientation='h',
                marker=dict(color='#4F7CFF')
            ))
            fig_shap.update_layout(
                title=dict(text=f"SHAP Feature Attribution (Top Factor: {top_feature})", font=dict(size=14, color="#F1F5F9")),
                paper_bgcolor="#151F32", plot_bgcolor="#0B1220",
                font=dict(color="#F1F5F9", family="Inter"),
                xaxis=dict(title="Contribution Percentage (%)", gridcolor="#29364A"),
                yaxis=dict(gridcolor="#29364A"),
                margin=dict(l=20, r=20, t=40, b=20),
                height=260
            )
            st.plotly_chart(fig_shap, use_container_width=True)

    # Model Performance Evaluation Table
    if ml_predictor:
        eval_metrics = ml_predictor.get_evaluation_metrics()
        if eval_metrics:
            st.markdown("### Model Performance Comparison")
            rf_m = eval_metrics.get("random_forest", {})
            lstm_m = eval_metrics.get("lstm", {})

            df_comp = pd.DataFrame([
                {"Model": "Random Forest Baseline", "Accuracy": rf_m.get("accuracy"), "Precision": rf_m.get("precision"), "Recall": rf_m.get("recall"), "F1 Score": rf_m.get("f1_score"), "ROC-AUC": rf_m.get("roc_auc")},
                {"Model": "PyTorch/Keras LSTM Time-Series", "Accuracy": lstm_m.get("accuracy"), "Precision": lstm_m.get("precision"), "Recall": lstm_m.get("recall"), "F1 Score": lstm_m.get("f1_score"), "ROC-AUC": lstm_m.get("roc_auc")}
            ])
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # Operational Alert Box (Risk >= 80%)
    if prob >= 0.80:
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 6px; padding: 14px; margin-top: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="status-badge badge-critical">● CRITICAL RISK EXCEEDED</span>
                <strong style="color: #F1F5F9; font-size: 0.95rem;">Outage Probability {prob_pct}% >= 80.0% Threshold</strong>
            </div>
            <div style="margin-top: 6px; color: #FCA5A5; font-size: 0.85rem;">
                Primary Contributing Metric: <strong>{top_feature}</strong> ({top_impact}% SHAP impact). Proactive failover route transfer executed. Estimated TTF: <strong>{ttf_sec}s</strong>.
            </div>
        </div>
        """, unsafe_allow_html=True)
