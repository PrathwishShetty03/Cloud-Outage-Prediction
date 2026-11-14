import os
import time
import requests
import pandas as pd
import streamlit as st
from fpdf import FPDF
from scripts.run_predictive_demo import run_predictive_demo_scenario, generate_pdf_proof

def fetch_haproxy_stats_raw(stats_url="http://localhost:8404/stats;csv"):
    try:
        r = requests.get(stats_url, timeout=2.0)
        if r.status_code == 200:
            lines = r.text.strip().split('\n')
            if len(lines) > 1:
                # Remove leading '#' from header line
                header = lines[0].lstrip('# ').split(',')
                data = [line.split(',') for line in lines[1:] if line]
                df = pd.DataFrame(data, columns=header[:len(data[0])])
                return df
    except Exception:
        pass
    return pd.DataFrame()

def trigger_shared_live_demo(controller):
    with st.spinner("🚀 Running Predictive Failover Live Demo (Prevention Before Failure)... Please wait 6-8 seconds..."):
        try:
            df, csv_path, pdf_path = run_predictive_demo_scenario(
                server_a_url=controller.endpoint_a,
                server_b_url=controller.endpoint_b,
                server_c_url=controller.endpoint_c,
                haproxy_url=controller.haproxy_url
            )
            st.success("✅ Predictive Failover Live Demo completed successfully! Timestamped proof logs generated.")
            st.session_state["last_demo_run"] = time.time()
            return df, csv_path, pdf_path
        except Exception as e:
            st.error(f"❌ Demo execution error: {e}")
            return None, None, None

def export_proof_csv(logs_list):
    if not logs_list:
        return b""
    df = pd.DataFrame(logs_list)
    return df.to_csv(index=False).encode('utf-8')

def export_proof_pdf(logs_list):
    if not logs_list:
        return b""
    df = pd.DataFrame(logs_list)
    temp_path = f"/tmp/proof_{int(time.time())}.pdf" if os.name != 'nt' else os.path.join(os.environ.get("TEMP", "C:\\Temp"), f"proof_{int(time.time())}.pdf")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    try:
        generate_pdf_proof(df, temp_path)
        with open(temp_path, "rb") as f:
            pdf_bytes = f.read()
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return pdf_bytes
    except Exception as e:
        st.error(f"Error building PDF: {e}")
        return b""

def fetch_autoscaler_status(autoscaler_url="http://localhost:9090"):
    try:
        r = requests.get(f"{autoscaler_url}/status", timeout=1.5)
        if r.status_code == 200:
            data = r.json()
            data["is_reachable"] = True
            return data
    except Exception:
        pass
    return {"status": "OFFLINE", "is_reachable": False, "current_instances": 1, "desired_instances": 1, "healthy_instances": 1, "signals": {}}

def fetch_autoscaler_history(autoscaler_url="http://localhost:9090"):
    try:
        r = requests.get(f"{autoscaler_url}/history", timeout=1.5)
        if r.status_code == 200:
            return r.json().get("history", [])
    except Exception:
        pass
    return []
