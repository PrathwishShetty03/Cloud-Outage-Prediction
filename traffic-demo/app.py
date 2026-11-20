"""
Live Traffic Demo Application - Backend Server
================================================
Separate web application demonstrating real-time traffic routing,
dynamic HAProxy failover from Server A to Server B, and recovery.

Port: 5050 (default)
URL:  http://localhost:5050
"""

import os
import time
import threading
import requests
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# IST Timezone Helper (UTC +05:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now_str():
    return datetime.now(IST).strftime("%H:%M:%S.%f")[:-3] + " IST"

def get_ist_date_time_str():
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")

# Target Service URLs
HAPROXY_URL = os.environ.get("HAPROXY_URL", "http://localhost:80").rstrip("/")
SERVER_A_URL = os.environ.get("SERVER_A_URL", "http://localhost:5001").rstrip("/")
SERVER_B_URL = os.environ.get("SERVER_B_URL", "http://localhost:5002").rstrip("/")
SERVER_C_URL = os.environ.get("SERVER_C_URL", "http://localhost:5003").rstrip("/")

# In-memory session state for demo logs & failover tracking
demo_state = {
    "logs": [],
    "events": [],
    "last_active_server": "SERVER_A",
    "total_requests_sent": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "server_a_hits": 0,
    "server_b_hits": 0,
    "server_c_hits": 0,
    "failover_count": 0,
    "last_failover_time": None
}

def detect_live_ingress_target():
    """
    Identifies the active load balancer entry point:
    1. Primary HAProxy on port 80
    2. Alternate HAProxy on port 8080 (local reverse proxy)
    3. Direct cluster fallback: Server A (5001) or Server B (5002)
    """
    for candidate in [HAPROXY_URL, "http://localhost:80", "http://localhost:8080"]:
        try:
            r = requests.get(f"{candidate}/health", timeout=0.6)
            if r.status_code < 500:
                return candidate, "HAPROXY"
        except Exception:
            pass

    # Direct fallback based on Server A's real health check
    try:
        ra = requests.get(f"{SERVER_A_URL}/health", timeout=0.8)
        if ra.status_code == 200:
            return SERVER_A_URL, "DIRECT_SERVER_A"
    except Exception:
        pass

    return SERVER_B_URL, "DIRECT_SERVER_B"

def execute_dispatched_request(target_path, method="GET", json_body=None, action_name="API_REQUEST"):
    """
    Core Traffic Dispatcher for Port 5050:
    Routes incoming HTTP requests genuinely to Server A or Server B via HAProxy or active backend.
    Logs every transaction in IST and returns real response with proof headers.
    """
    start_time = time.time()
    ist_time = get_ist_now_str()

    target_lb, route_type = detect_live_ingress_target()
    
    # Determine the actual HTTP request URL
    if route_type == "HAPROXY":
        url = f"{target_lb}{target_path}"
    else:
        # Direct cluster fallback: verify Server A's health
        try:
            ra = requests.get(f"{SERVER_A_URL}/health", timeout=0.8)
            a_is_up = (ra.status_code == 200)
        except Exception:
            a_is_up = False

        if a_is_up:
            active_url = SERVER_A_URL
        else:
            try:
                rb = requests.get(f"{SERVER_B_URL}/health", timeout=0.8)
                b_is_up = (rb.status_code == 200)
            except Exception:
                b_is_up = False
            active_url = SERVER_B_URL if b_is_up else SERVER_C_URL
        url = f"{active_url}{target_path}"

    try:
        req_headers = {"Accept": "application/json"}
        if method == "POST":
            resp = requests.post(url, json=json_body, timeout=5.0, headers=req_headers)
        else:
            resp = requests.get(url, timeout=5.0, headers=req_headers)

        duration_ms = round((time.time() - start_time) * 1000.0, 1)
        status_code = resp.status_code
        served_by = resp.headers.get("X-Served-By", "UNKNOWN")
        served_port = resp.headers.get("X-Server-Port", "80")
        req_number = resp.headers.get("X-Request-Number", "N/A")

        try:
            payload = resp.json()
            if served_by == "UNKNOWN" and isinstance(payload, dict):
                served_by = payload.get("server_id", served_by)
        except Exception:
            payload = {"raw_text": resp.text[:200]}

        # If HAProxy forwarded but didn't set X-Served-By header, detect from payload/URL
        if served_by == "UNKNOWN":
            if "5001" in str(resp.content) or SERVER_A_URL in url:
                served_by = "SERVER_A"
                served_port = "5001"
            elif "5002" in str(resp.content) or SERVER_B_URL in url:
                served_by = "SERVER_B"
                served_port = "5002"
            elif "5003" in str(resp.content) or SERVER_C_URL in url:
                served_by = "SERVER_C"
                served_port = "5003"

        is_success = (status_code < 400)

    except requests.exceptions.RequestException as e:
        duration_ms = round((time.time() - start_time) * 1000.0, 1)
        status_code = 503
        served_by = "ERROR"
        served_port = "N/A"
        req_number = "N/A"
        payload = {"error": str(e), "message": "Failed connecting to active server"}
        is_success = False

    # Monotonic tracking in session state
    demo_state["total_requests_sent"] += 1
    if is_success:
        demo_state["successful_requests"] += 1
        if served_by == "SERVER_A":
            demo_state["server_a_hits"] += 1
        elif served_by == "SERVER_B":
            demo_state["server_b_hits"] += 1
        elif served_by == "SERVER_C":
            demo_state["server_c_hits"] += 1
    else:
        demo_state["failed_requests"] += 1

    # Detect failover transition
    failover_event = None
    if served_by in ["SERVER_A", "SERVER_B", "SERVER_C"] and served_by != demo_state["last_active_server"]:
        prev = demo_state["last_active_server"]
        demo_state["last_active_server"] = served_by
        demo_state["failover_count"] += 1
        demo_state["last_failover_time"] = ist_time

        if served_by == "SERVER_B":
            event_type = "FAILOVER_ACTIVATED"
            msg = f"Traffic switched from {prev} to Backup Server B"
        elif served_by == "SERVER_C":
            event_type = "EMERGENCY_FAILOVER"
            msg = f"Traffic switched from {prev} to Emergency Server C"
        else:
            event_type = "FAILBACK_RESTORED"
            msg = f"Traffic restored from {prev} to Primary Server A"

        failover_event = {
            "timestamp_ist": ist_time,
            "event_type": event_type,
            "previous_server": prev,
            "active_server": served_by,
            "message": msg
        }
        demo_state["events"].insert(0, failover_event)

    log_entry = {
        "id": demo_state["total_requests_sent"],
        "timestamp_ist": ist_time,
        "action": action_name,
        "endpoint": target_path,
        "method": method,
        "served_by": served_by,
        "port": served_port,
        "request_number": req_number,
        "status_code": status_code,
        "latency_ms": duration_ms,
        "success": is_success,
        "payload": payload,
        "verified_by_header": ("X-Served-By" in resp.headers if 'resp' in locals() else False)
    }

    demo_state["logs"].insert(0, log_entry)
    if len(demo_state["logs"]) > 200:
        demo_state["logs"].pop()

    return log_entry, failover_event, served_by, status_code, payload

@app.route("/")
def index():
    return render_template("index.html")

# ==============================================================================
# PASS-THROUGH BUSINESS API ENDPOINTS ON PORT 5050
# Incoming requests to port 5050 are forwarded to the active server (Server A / B)
# with real response bodies, status codes, and proof headers.
# ==============================================================================

@app.route("/api/products", methods=["GET"])
def handle_api_products():
    entry, _, _, code, payload = execute_dispatched_request("/api/products", "GET", None, "LOAD_PRODUCTS")
    resp = jsonify(payload) if isinstance(payload, (dict, list)) else app.response_class(str(payload), mimetype="application/json")
    resp.headers["X-Served-By"] = entry["served_by"]
    resp.headers["X-Server-Port"] = str(entry["port"])
    resp.headers["X-Request-Number"] = str(entry["request_number"])
    resp.headers["X-Handled-Port"] = "5050"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp, code

@app.route("/api/dashboard-data", methods=["GET"])
def handle_api_dashboard_data():
    entry, _, _, code, payload = execute_dispatched_request("/api/dashboard-data", "GET", None, "FETCH_DASHBOARD")
    resp = jsonify(payload) if isinstance(payload, (dict, list)) else app.response_class(str(payload), mimetype="application/json")
    resp.headers["X-Served-By"] = entry["served_by"]
    resp.headers["X-Server-Port"] = str(entry["port"])
    resp.headers["X-Request-Number"] = str(entry["request_number"])
    resp.headers["X-Handled-Port"] = "5050"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp, code

@app.route("/api/orders", methods=["GET", "POST"])
def handle_api_orders():
    body = request.get_json(silent=True) or {"item": "Production Compute Node (Failover Safe)", "quantity": 1}
    entry, _, _, code, payload = execute_dispatched_request("/api/orders", "POST", body, "PLACE_ORDER")
    resp = jsonify(payload) if isinstance(payload, (dict, list)) else app.response_class(str(payload), mimetype="application/json")
    resp.headers["X-Served-By"] = entry["served_by"]
    resp.headers["X-Server-Port"] = str(entry["port"])
    resp.headers["X-Request-Number"] = str(entry["request_number"])
    resp.headers["X-Handled-Port"] = "5050"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp, code

@app.route("/api/demo/health-status", methods=["GET"])
def get_health_status():
    """Polls real health and metrics from Server A, Server B, Server C, and HAProxy."""
    status_a = {"status": "UNKNOWN", "reachable": False, "total_requests": 0, "health_score": 0.0}
    status_b = {"status": "UNKNOWN", "reachable": False, "total_requests": 0, "health_score": 0.0}
    status_c = {"status": "UNKNOWN", "reachable": False, "total_requests": 0, "health_score": 0.0}
    haproxy_status = {"status": "UNKNOWN", "reachable": False}

    # Query Server A
    try:
        ra = requests.get(f"{SERVER_A_URL}/api/metrics", timeout=1.5)
        if ra.status_code == 200:
            da = ra.json()
            is_rec = (da.get("status") == "RECOVERING" or da.get("active_simulations", {}).get("is_recovering", False))
            status_a = {
                "server_id": "SERVER_A",
                "port": 5001,
                "status": "RECOVERING" if is_rec else da.get("status", "HEALTHY"),
                "reachable": True,
                "total_requests": da.get("total_requests", 0),
                "health_score": da.get("health_score", 100.0),
                "cpu": da.get("cpu_percent", da.get("cpu", 0.0)),
                "memory": da.get("memory_percent", da.get("memory", 0.0)),
                "error_rate": da.get("error_rate", 0.0),
                "is_outage": da.get("active_simulations", {}).get("is_outage", False),
                "is_recovering": is_rec,
                "recovery_stage": da.get("recovery_stage") or da.get("active_simulations", {}).get("recovery_stage"),
                "recovery_stage_index": da.get("recovery_stage_index") or da.get("active_simulations", {}).get("recovery_stage_index", 0),
                "recovery_stage_name": da.get("recovery_stage_name") or da.get("active_simulations", {}).get("recovery_stage_name", ""),
                "recovery_stage_description": da.get("description", ""),
                "recovery_progress_pct": da.get("recovery_progress_pct") or da.get("active_simulations", {}).get("recovery_progress_pct", 0.0),
                "recovery_remaining_sec": da.get("recovery_remaining_sec") or da.get("active_simulations", {}).get("recovery_remaining_sec", 0.0)
            }
        else:
            status_a["status"] = "UNHEALTHY"
            status_a["reachable"] = True
    except Exception as e:
        status_a["status"] = "DOWN"
        status_a["reachable"] = False
        status_a["error"] = str(e)

    # Query Server B
    try:
        rb = requests.get(f"{SERVER_B_URL}/api/metrics", timeout=1.5)
        if rb.status_code == 200:
            db = rb.json()
            status_b = {
                "server_id": "SERVER_B",
                "port": 5002,
                "status": db.get("status", "HEALTHY"),
                "reachable": True,
                "total_requests": db.get("total_requests", 0),
                "health_score": db.get("health_score", 100.0),
                "cpu": db.get("cpu_percent", db.get("cpu", 0.0)),
                "memory": db.get("memory_percent", db.get("memory", 0.0)),
                "error_rate": db.get("error_rate", 0.0)
            }
    except Exception as e:
        status_b["status"] = "DOWN"
        status_b["reachable"] = False
        status_b["error"] = str(e)

    # Query Server C
    try:
        rc = requests.get(f"{SERVER_C_URL}/api/metrics", timeout=1.5)
        if rc.status_code == 200:
            dc = rc.json()
            status_c = {
                "server_id": "SERVER_C",
                "port": 5003,
                "status": dc.get("status", "HEALTHY"),
                "reachable": True,
                "total_requests": dc.get("total_requests", 0),
                "health_score": dc.get("health_score", 100.0),
                "cpu": dc.get("cpu_percent", dc.get("cpu", 0.0)),
                "memory": dc.get("memory_percent", dc.get("memory", 0.0)),
                "error_rate": dc.get("error_rate", 0.0)
            }
    except Exception as e:
        status_c["status"] = "DOWN"
        status_c["reachable"] = False
        status_c["error"] = str(e)

    # Query HAProxy Entrypoint
    active_lb_url, route_type = detect_live_ingress_target()
    haproxy_status = {"status": "UNKNOWN", "reachable": False, "url": active_lb_url, "type": route_type}
    try:
        rh = requests.get(f"{active_lb_url}/health", timeout=1.2)
        haproxy_status = {
            "status": "UP" if rh.status_code < 500 else "DEGRADED",
            "reachable": True,
            "status_code": rh.status_code,
            "url": active_lb_url,
            "type": route_type,
            "routed_to": rh.headers.get("X-Served-By", "SERVER_A" if rh.status_code == 200 else "SERVER_B")
        }
    except Exception as e:
        haproxy_status = {"status": "STANDALONE_GATEWAY", "reachable": True, "url": "PORT_5050_INGRESS", "type": "INTERNAL_LB", "error": str(e)}

    # Determine currently active ingress server.
    # RECOVERING = Server A is not ready to serve yet -> Server B handles traffic!
    a_truly_ready = (
        status_a.get("reachable") and
        status_a.get("status") == "HEALTHY" and
        not status_a.get("is_recovering", False) and
        not status_a.get("is_outage", False)
    )
    if a_truly_ready:
        active_server = "SERVER_A"
    elif status_b.get("status") == "HEALTHY" and status_b.get("reachable"):
        active_server = "SERVER_B"
    elif status_c.get("status") == "HEALTHY" and status_c.get("reachable"):
        active_server = "SERVER_C"
    else:
        active_server = "NONE"

    return jsonify({
        "timestamp_ist": get_ist_now_str(),
        "active_ingress_server": active_server,
        "server_a": status_a,
        "server_b": status_b,
        "server_c": status_c,
        "haproxy": haproxy_status,
        "metrics_summary": {
            "total_sent": demo_state["total_requests_sent"],
            "successful": demo_state["successful_requests"],
            "failed": demo_state["failed_requests"],
            "server_a_hits": demo_state["server_a_hits"],
            "server_b_hits": demo_state["server_b_hits"],
            "server_c_hits": demo_state.get("server_c_hits", 0),
            "failover_count": demo_state["failover_count"],
            "last_failover_time": demo_state["last_failover_time"]
        }
    })

@app.route("/api/demo/send-request", methods=["POST"])
def send_request():
    """
    Handles interactive button clicks from the web application.
    Executes real HTTP call through HAProxy or direct active server.
    """
    data = request.get_json(silent=True) or {}
    action = data.get("action", "LOAD_PRODUCTS")

    if action == "LOAD_PRODUCTS":
        target_path = "/api/products"
        method = "GET"
        body = None
    elif action == "FETCH_DASHBOARD":
        target_path = "/api/dashboard-data"
        method = "GET"
        body = None
    elif action == "PLACE_ORDER":
        target_path = "/api/orders"
        method = "POST"
        body = {"item": "Production Compute Node (Failover Safe)", "quantity": 1}
    elif action == "REFRESH_STATUS":
        target_path = "/"
        method = "GET"
        body = None
    else:
        target_path = "/"
        method = "GET"
        body = None

    log_entry, failover_event, served_by, _, _ = execute_dispatched_request(target_path, method, body, action)

    return jsonify({
        "status": "OK",
        "result": log_entry,
        "failover_event": failover_event,
        "active_server": served_by
    })

@app.route("/api/demo/simulate-outage", methods=["POST"])
def simulate_outage():
    """
    Triggers real simulated outage on Server A (HTTP 503).
    Server A's automated 4-stage self-healing recovery pipeline begins automatically.
    """
    ist_time = get_ist_now_str()
    try:
        r = requests.post(f"{SERVER_A_URL}/simulate/outage", json={"auto_recover": True, "delay": 2.0, "duration": 20.0}, timeout=3.0)
        success = (r.status_code == 200)
        msg = "Outage successfully injected on Server A (HTTP 503). Server A is now DOWN. Automated 4-stage self-healing recovery initiated!"
    except Exception as e:
        success = False
        msg = f"Error triggering outage on Server A: {e}"

    event = {
        "timestamp_ist": ist_time,
        "event_type": "OUTAGE_TRIGGERED",
        "server": "SERVER_A",
        "success": success,
        "message": msg,
    }
    demo_state["events"].insert(0, event)

    return jsonify({
        "success": success,
        "timestamp_ist": ist_time,
        "message": msg,
        "auto_recovery_enabled": True
    })

@app.route("/api/demo/restore-server", methods=["POST"])
def restore_server():
    """Explicitly triggers or accelerates node recovery on Server A."""
    ist_time = get_ist_now_str()
    try:
        r = requests.post(f"{SERVER_A_URL}/simulate/recover", json={"duration": 20.0}, timeout=3.0)
        success = (r.status_code == 200)
        msg = "Recovery initiated for Server A. Beginning 4-stage self-healing recovery sequence."
    except Exception as e:
        success = False
        msg = f"Error triggering recovery on Server A: {e}"

    event = {
        "timestamp_ist": ist_time,
        "event_type": "RECOVERY_INITIATED",
        "server": "SERVER_A",
        "success": success,
        "message": msg,
    }
    demo_state["events"].insert(0, event)

    return jsonify({
        "success": success,
        "timestamp_ist": ist_time,
        "message": msg,
    })

@app.route("/api/demo/logs", methods=["GET"])
def get_logs():
    return jsonify({
        "logs": demo_state["logs"][:50],
        "events": demo_state["events"][:20],
        "total_requests": demo_state["total_requests_sent"]
    })

@app.route("/api/demo/clear-logs", methods=["POST"])
def clear_logs():
    demo_state["logs"].clear()
    demo_state["events"].clear()
    demo_state["total_requests_sent"] = 0
    demo_state["successful_requests"] = 0
    demo_state["failed_requests"] = 0
    demo_state["server_a_hits"] = 0
    demo_state["server_b_hits"] = 0
    demo_state["server_c_hits"] = 0
    demo_state["failover_count"] = 0
    demo_state["auto_recovery_pending"] = False
    demo_state["auto_recovery_at"] = 0.0
    demo_state["outage_triggered_at"] = 0.0
    return jsonify({"status": "CLEARED"})

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Live Traffic Demo Web Application")
    parser.add_argument("--port", type=int, default=5050, help="Port to run web app (default: 5050)")
    parser.add_argument("--host", default="0.0.0.0", help="Host binding (default: 0.0.0.0)")
    args = parser.parse_args()

    print(f"\n=======================================================")
    print(f"  LIVE TRAFFIC & FAILOVER DEMO APPLICATION")
    print(f"=======================================================")
    print(f"  Web Dashboard:  http://localhost:{args.port}")
    print(f"  HAProxy Target: {HAPROXY_URL}")
    print(f"  Server A Node:  {SERVER_A_URL}")
    print(f"  Server B Node:  {SERVER_B_URL}")
    print(f"  Local Time:     {get_ist_now_str()}")
    print(f"=======================================================\n")
    app.run(host=args.host, port=args.port, debug=False)
