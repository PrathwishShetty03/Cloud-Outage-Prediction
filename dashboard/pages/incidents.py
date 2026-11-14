import streamlit as st
import pandas as pd
from dashboard.shared.state import init_session_state, get_telemetry_evaluation
from dashboard.components.alert_center import render_alert_center_section

controller = init_session_state()
eval_res = get_telemetry_evaluation(controller)
snapshot = eval_res["snapshot"]
prediction = eval_res["prediction"]

st.title("Incidents")
st.caption("Incident Management Timeline & Self-Healing Remediation History")

# Automated Self-Healing Trigger Button
col_sh1, col_sh2 = st.columns([3, 1])
with col_sh1:
    st.markdown("""
    <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">
        Automated Self-Healing Workflow: Drains traffic → executes process recovery → polls health verification → restores standby state.
    </div>
    """, unsafe_allow_html=True)
with col_sh2:
    if st.button("Execute Self-Healing", type="primary", use_container_width=True, key="trigger_self_healing_btn"):
        rec_res = controller.remediation_engine.execute_remediation("SERVER_A", controller.endpoint_a, problem_reason="MANUAL_OPERATOR_TRIGGER")
        st.success(f"● Self-Healing completed in {rec_res['duration_seconds']}s. Status: {rec_res['status']}")
        st.rerun()

st.markdown("---")

render_alert_center_section(snapshot, prediction, eval_res)

st.markdown("---")

# Self-Healing Remediation History Section
st.markdown("### Self-Healing Remediation Records")
remediations = controller.remediation_engine.get_remediation_history()
if remediations:
    for r in remediations:
        with st.expander(f"Record {r['remediation_id']} — Target: {r['target_server']} ({r['status']}) — {r['timestamp']}", expanded=True):
            st.markdown(f"**Problem Reason**: `{r['problem']}` | **Duration**: `{r['duration_seconds']}s` | **Verified**: `{r['verified_healthy']}`")
            st.markdown("**Workflow Execution Steps:**")
            for s in r.get("steps", []):
                step_badge = '● COMPLETED' if s["status"] == "COMPLETED" else f'● {s["status"]}'
                st.markdown(f"- **{s['step']}** ({step_badge}): {s['details']}")
else:
    st.info("● No self-healing remediation records in current session.")

st.markdown("---")
st.markdown("### Event Audit Table")

filter_option = st.selectbox(
    "Filter Logs by Severity",
    ["ALL", "INFO", "WARNING", "CRITICAL", "FAILOVER", "RECOVERY"]
)

logs = controller.failover_logs
if logs:
    df = pd.DataFrame(logs)
    if filter_option != "ALL":
        df = df[df["severity"].str.upper() == filter_option]
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("● No incident logs recorded in current session.")
