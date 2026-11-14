import streamlit as st

def render_network_topology_section(active_server, ep_a, ep_b):
    st.markdown("## 🌐 Multi-Region Architecture & Network Topology")
    st.caption("Distributed load-balanced multi-server cluster with automatic failover fallback.")

    st.markdown(f"""
    <div style="background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155;">
        <div style="display: flex; justify-content: space-around; text-align: center;">
            <div style="background: #0f172a; padding: 16px; border-radius: 10px; width: 28%;">
                <h4 style="margin: 0; color: #38bdf8;">🌐 Node A (Primary)</h4>
                <p style="margin: 4px 0; color: #94a3b8; font-size: 0.85rem;">{ep_a}</p>
                <span style="font-weight: bold; color: {'#34d399' if active_server == 'SERVER_A' else '#f87171'};">
                    {'ACTIVE INGRESS' if active_server == 'SERVER_A' else 'FAILOVER / STANDBY'}
                </span>
            </div>
            <div style="background: #0f172a; padding: 16px; border-radius: 10px; width: 28%;">
                <h4 style="margin: 0; color: #34d399;">🔮 Node B (Digital Twin)</h4>
                <p style="margin: 4px 0; color: #94a3b8; font-size: 0.85rem;">{ep_b}</p>
                <span style="font-weight: bold; color: {'#34d399' if active_server == 'SERVER_B' else '#64748b'};">
                    {'ACTIVE INGRESS' if active_server == 'SERVER_B' else 'MIRRORING / STANDBY'}
                </span>
            </div>
            <div style="background: #0f172a; padding: 16px; border-radius: 10px; width: 28%;">
                <h4 style="margin: 0; color: #fbbf24;">🚨 Node C (Emergency)</h4>
                <p style="margin: 4px 0; color: #94a3b8; font-size: 0.85rem;">http://localhost:5003</p>
                <span style="font-weight: bold; color: {'#34d399' if active_server == 'SERVER_C' else '#64748b'};">
                    {'ACTIVE EMERGENCY' if active_server == 'SERVER_C' else 'STANDBY'}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
