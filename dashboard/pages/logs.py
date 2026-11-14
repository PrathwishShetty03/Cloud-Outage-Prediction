import time
import pandas as pd
import streamlit as st
from dashboard.shared.state import init_session_state
from dashboard.shared.data_fetch import export_proof_csv, export_proof_pdf

controller = init_session_state()

st.title("Audit Logs")
st.caption("Event Audit History, Telemetry Evidence & CSV/PDF Export Capability")

logs = controller.failover_logs

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    csv_bytes = export_proof_csv(logs)
    st.download_button(
        label="Download Audit Log (CSV)",
        data=csv_bytes,
        file_name=f"audit_event_log_{int(time.time())}.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True
    )

with col_exp2:
    pdf_bytes = export_proof_pdf(logs)
    st.download_button(
        label="Download Audit Log (PDF)",
        data=pdf_bytes,
        file_name=f"audit_event_log_{int(time.time())}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )

st.markdown("---")

st.markdown("### 📋 Audit Log Stream")
if logs:
    df_logs = pd.DataFrame(logs)
    cols = ["timestamp", "event_type", "server", "severity", "description", "failover_type", "outage_probability", "cpu", "memory", "latency"]
    df_show = df_logs[[c for c in cols if c in df_logs.columns]]
    st.dataframe(df_show, use_container_width=True, hide_index=True)
else:
    st.info("● No audit log entries recorded in current session.")
