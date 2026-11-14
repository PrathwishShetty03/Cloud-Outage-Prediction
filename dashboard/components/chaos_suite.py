import streamlit as st
import requests
from scripts.run_live_demo import run_automated_demo_scenario

def render_chaos_suite_section(controller, snapshot, active_server):
    st.markdown("## Chaos Lab & Resilience Testing Suite")
    st.caption("Controlled fault injection environment for evaluating platform resilience, ML detection lead times, and HAProxy failover execution.")

    # Environment Restriction Warning Banner
    st.markdown("""
    <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid #F59E0B; border-radius: 6px; padding: 14px 18px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span class="status-badge badge-warning">● RESILIENCE LAB TESTING</span>
                <strong style="color: #F1F5F9; font-size: 0.95rem; margin-left: 8px;">Automated Chaos & Fault Injection Suite</strong>
                <div style="color: #CBD5E1; font-size: 0.82rem; margin-top: 4px;">
                    Execute controlled workload escalation on Primary Server A to verify real-time ML risk scoring and HAProxy route migration.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Run Failover Simulation", type="primary", use_container_width=True):
        with st.spinner("Executing Automated Failover Test Scenario..."):
            df_proof, filepath = run_automated_demo_scenario(
                server_a_url=st.session_state.get("endpoint_a", "http://localhost:5001"),
                server_b_url=st.session_state.get("endpoint_b", "http://localhost:5002"),
                server_c_url=st.session_state.get("endpoint_c", "http://localhost:5003"),
                haproxy_url="http://localhost:80"
            )
            st.session_state["latest_proof_df"] = df_proof
            st.success(f"● Demo scenario completed. Timestamped proof log saved: `{filepath}`.")
            st.rerun()

    st.markdown("---")
    st.markdown("### Targeted Fault Injection Controls (Server A)")

    col_c1, col_c2, col_c3, col_c4 = st.columns(4)

    ep_a = st.session_state.get("endpoint_a", "http://localhost:5001")

    with col_c1:
        if st.button("Inject CPU Stress (100%)", use_container_width=True, key="chaos_cpu"):
            try:
                requests.post(f"{ep_a}/stress/cpu", json={"enable": True}, timeout=2.0)
                st.toast("CPU stress workload injected on Server A.")
            except Exception as e:
                st.error(f"Execution error: {e}")

    with col_c2:
        if st.button("Inject Latency (5.5s)", use_container_width=True, key="chaos_lat"):
            try:
                requests.post(f"{ep_a}/stress/latency", json={"seconds": 5.5}, timeout=2.0)
                st.toast("5.5s Latency injected on Server A.")
            except Exception as e:
                st.error(f"Execution error: {e}")

    with col_c3:
        if st.button("Inject Error Rate (35%)", use_container_width=True, key="chaos_err"):
            try:
                requests.post(f"{ep_a}/stress/error", json={"rate": 0.35}, timeout=2.0)
                st.toast("35% Error rate injected on Server A.")
            except Exception as e:
                st.error(f"Execution error: {e}")

    with col_c4:
        if st.button("Reset / Recover Server A", type="secondary", use_container_width=True, key="chaos_recover"):
            try:
                requests.post(f"{ep_a}/simulate/recover", timeout=2.0)
                st.toast("Server A recovery signal dispatched.")
            except Exception as e:
                st.error(f"Execution error: {e}")
