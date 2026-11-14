import time
import streamlit as st
import pandas as pd
from dashboard.shared.state import init_session_state
from dashboard.shared.data_fetch import fetch_autoscaler_status

controller = init_session_state()

st.title("Horizontal Autoscaling")
st.caption("Telemetry Watermark Monitoring, Multi-Signal Hysteresis & Dynamic Replica Management")

@st.fragment(run_every="2s")
def render_autoscaling_dashboard():
    autoscaler_url = st.session_state.get("autoscaler_url", "http://localhost:9090")
    data = fetch_autoscaler_status(autoscaler_url)
    
    is_reachable = data.get("is_reachable", False)
    status_str = data.get("status", "OFFLINE")
    cfg = data.get("config", {})
    signals = data.get("signals", {})
    discovered = data.get("discovered_instances", [])
    history = data.get("history", [])
    watermarks = cfg.get("watermarks", {})

    current_reps = data.get("current_instances", len(discovered))
    desired_reps = data.get("desired_instances", current_reps)
    healthy_count = data.get("healthy_instances", len([d for d in discovered if d.get("healthy")]))
    min_inst = cfg.get("min_instances", 1)
    max_inst = cfg.get("max_instances", 5)
    in_cooldown = data.get("in_cooldown", False)
    last_action = data.get("last_action", "hold").upper()
    last_reason = data.get("last_reason", "Awaiting evaluation")

    # Top KPI Metric Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(
            label="Active Replicas",
            value=f"{current_reps} / {max_inst}",
            delta=f"Desired: {desired_reps}" if desired_reps != current_reps else "Stable"
        )

    with kpi2:
        st.metric(
            label="Autoscaler Daemon",
            value=status_str,
            delta="CONNECTED" if is_reachable else "OFFLINE",
            delta_color="normal" if is_reachable else "inverse"
        )

    with kpi3:
        st.metric(
            label="Last Action",
            value=last_action,
            delta="In Cooldown" if in_cooldown else "Ready"
        )

    with kpi4:
        st.metric(
            label="Healthy Workers",
            value=f"{healthy_count} / {max(1, len(discovered))}",
            delta="All Healthy" if healthy_count == len(discovered) and len(discovered) > 0 else "Degraded"
        )

    st.markdown("---")

    # Decision Status Banner
    st.markdown(f"""
    <div style="background: #1E293B; border-left: 4px solid #38BDF8; border-radius: 4px; padding: 12px 16px; margin-bottom: 16px;">
        <div style="font-size: 0.78rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Autoscaling Decision & Reason</div>
        <div style="font-size: 0.9rem; font-weight: 600; color: #F8FAFC; margin-top: 4px; font-family: monospace;">
            {last_reason}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Multi-Signal Watermarks
    st.markdown("### 🎯 Multi-Signal Telemetry Watermarks")
    s1, s2, s3, s4 = st.columns(4)

    avg_cpu = float(signals.get("avg_cpu", 0.0))
    cpu_high = float(watermarks.get("cpu_high", 75.0))
    cpu_low = float(watermarks.get("cpu_low", 52.5))

    avg_mem = float(signals.get("avg_memory", 0.0))
    mem_high = float(watermarks.get("memory_high", 75.0))
    mem_low = float(watermarks.get("memory_low", 52.5))

    avg_lat = float(signals.get("avg_latency_ms", 0.0))
    lat_high = float(watermarks.get("latency_high_ms", 800.0))
    lat_low = float(watermarks.get("latency_low_ms", 560.0))

    avg_rps = float(signals.get("request_rate_per_instance", 0.0))
    rps_high = float(watermarks.get("request_rate_high", 25.0))
    rps_low = float(watermarks.get("request_rate_low", 17.5))

    with s1:
        st.markdown(f"""
        <div style="background: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 12px;">
            <div style="color: #94A3B8; font-size: 0.78rem; font-weight: 600;">CPU Utilization</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #F8FAFC;">{avg_cpu}%</div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">Low: <b>{cpu_low}%</b> | High: <b>{cpu_high}%</b></div>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown(f"""
        <div style="background: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 12px;">
            <div style="color: #94A3B8; font-size: 0.78rem; font-weight: 600;">Memory Allocation</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #F8FAFC;">{avg_mem}%</div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">Low: <b>{mem_low}%</b> | High: <b>{mem_high}%</b></div>
        </div>
        """, unsafe_allow_html=True)

    with s3:
        st.markdown(f"""
        <div style="background: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 12px;">
            <div style="color: #94A3B8; font-size: 0.78rem; font-weight: 600;">Average Latency</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #F8FAFC;">{avg_lat} ms</div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">Low: <b>{lat_low}ms</b> | High: <b>{lat_high}ms</b></div>
        </div>
        """, unsafe_allow_html=True)

    with s4:
        st.markdown(f"""
        <div style="background: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 12px;">
            <div style="color: #94A3B8; font-size: 0.78rem; font-weight: 600;">Request Rate / Worker</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #F8FAFC;">{avg_rps} RPS</div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">Low: <b>{rps_low}</b> | High: <b>{rps_high}</b></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Scaling Decision Audit Timeline
    st.markdown("### 📜 Scaling Decision Audit History")
    if history:
        history_rows = []
        for h in history[:15]:
            ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(h.get("timestamp", time.time())))
            history_rows.append({
                "Timestamp": ts_str,
                "Action": str(h.get("action", "hold")).upper(),
                "Replicas": f"{h.get('current', 1)} → {h.get('desired', 1)}",
                "Healthy": h.get("healthy", 0),
                "Cooldown": "Yes" if h.get("in_cooldown") else "No",
                "Reason": h.get("reason", "HOLD")
            })
        df_hist = pd.DataFrame(history_rows)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.caption("● No scale transitions recorded in current session.")

render_autoscaling_dashboard()
