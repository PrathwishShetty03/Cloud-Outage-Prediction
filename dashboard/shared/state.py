import os
import time
import threading
import streamlit as st
from failover.failover_controller import AutomatedFailoverController

def normalize_url(val, default):
    url = val if val else default
    url = url.strip().rstrip("/")
    if "10.38.110.19" in url:
        url = url.replace("10.38.110.19", "localhost")
    return url

def reload_env_into_state():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    for env_filename in [".env", "config/.env"]:
        env_path = os.path.join(root_dir, env_filename)
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line_str = line.strip()
                    if "=" in line_str and not line_str.startswith("#"):
                        k, v = line_str.split("=", 1)
                        key = k.strip()
                        val = v.strip()
                        if key not in os.environ:
                            os.environ[key] = val

    in_docker = os.path.exists('/.dockerenv') or os.environ.get('IS_DOCKER') == 'true' or os.environ.get('HOSTNAME') == 'streamlit_command_center'

    default_a = "http://server_a:5001" if in_docker else "http://localhost:5001"
    default_b = "http://server_b:5002" if in_docker else "http://localhost:5002"
    default_c = "http://server_c:5003" if in_docker else "http://localhost:5003"
    default_haproxy = "http://haproxy:80" if in_docker else "http://localhost:80"
    default_stats = "http://haproxy:8404/stats" if in_docker else "http://localhost:8404/stats"

    st.session_state["endpoint_a"] = normalize_url(os.environ.get("SERVER_A_URL"), default_a)
    st.session_state["endpoint_b"] = normalize_url(os.environ.get("SERVER_B_URL"), default_b)
    st.session_state["endpoint_c"] = normalize_url(os.environ.get("SERVER_C_URL"), default_c)
    st.session_state["haproxy_url"] = normalize_url(os.environ.get("HAPROXY_URL"), default_haproxy)
    st.session_state["haproxy_stats_url"] = normalize_url(os.environ.get("HAPROXY_STATS_URL"), default_stats)

    if "controller" in st.session_state:
        st.session_state.controller.update_endpoints(
            st.session_state["endpoint_a"],
            st.session_state["endpoint_b"],
            st.session_state["endpoint_c"]
        )

reload_env_into_state()

GLOBAL_EVAL_CACHE = {}
GLOBAL_CACHE_LOCK = threading.Lock()

def bg_telemetry_worker(controller):
    global GLOBAL_EVAL_CACHE
    while True:
        try:
            res = controller.evaluate_cycle()
            with GLOBAL_CACHE_LOCK:
                GLOBAL_EVAL_CACHE = res
        except Exception:
            pass
        time.sleep(1.2)

def init_session_state():
    in_docker = os.path.exists('/.dockerenv') or os.environ.get('IS_DOCKER') == 'true' or os.environ.get('HOSTNAME') == 'streamlit_command_center'

    default_a = "http://server_a:5001" if in_docker else "http://localhost:5001"
    default_b = "http://server_b:5002" if in_docker else "http://localhost:5002"
    default_c = "http://server_c:5003" if in_docker else "http://localhost:5003"
    default_haproxy = "http://haproxy:80" if in_docker else "http://localhost:80"
    default_stats = "http://haproxy:8404/stats" if in_docker else "http://localhost:8404/stats"

    if "endpoint_a" not in st.session_state:
        st.session_state["endpoint_a"] = normalize_url(os.environ.get("SERVER_A_URL"), default_a)
    if "endpoint_b" not in st.session_state:
        st.session_state["endpoint_b"] = normalize_url(os.environ.get("SERVER_B_URL"), default_b)
    if "endpoint_c" not in st.session_state:
        st.session_state["endpoint_c"] = normalize_url(os.environ.get("SERVER_C_URL"), default_c)
    if "haproxy_url" not in st.session_state:
        st.session_state["haproxy_url"] = normalize_url(os.environ.get("HAPROXY_URL"), default_haproxy)
    if "haproxy_stats_url" not in st.session_state:
        st.session_state["haproxy_stats_url"] = normalize_url(os.environ.get("HAPROXY_STATS_URL"), default_stats)
    if "auto_refresh" not in st.session_state:
        st.session_state["auto_refresh"] = True

    ep_a = st.session_state["endpoint_a"]
    ep_b = st.session_state["endpoint_b"]
    ep_c = st.session_state["endpoint_c"]
    haproxy_url = st.session_state["haproxy_url"]

    if "controller" not in st.session_state:
        st.session_state.controller = AutomatedFailoverController(
            endpoint_a=ep_a,
            endpoint_b=ep_b,
            endpoint_c=ep_c,
            haproxy_url=haproxy_url
        )

    controller = st.session_state.controller
    controller.update_endpoints(ep_a, ep_b, ep_c)
    controller.haproxy_url = haproxy_url

    if "bg_thread_started" not in st.session_state:
        t = threading.Thread(target=bg_telemetry_worker, args=(controller,), daemon=True)
        t.start()
        st.session_state["bg_thread_started"] = True

    return controller

def get_telemetry_evaluation(controller):
    global GLOBAL_EVAL_CACHE
    with GLOBAL_CACHE_LOCK:
        if GLOBAL_EVAL_CACHE:
            return GLOBAL_EVAL_CACHE
    
    res = controller.evaluate_cycle()
    with GLOBAL_CACHE_LOCK:
        GLOBAL_EVAL_CACHE = res
    return res
