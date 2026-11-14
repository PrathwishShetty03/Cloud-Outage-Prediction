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

# Auto-recovery delay after outage (seconds)
AUTO_RECOVERY_DELAY_SEC = 15.0

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
    "last_failover_time": None,
    "auto_recovery_pending": False,
    "auto_recovery_at": 0.0,
    "outage_triggered_at": 0.0,
}


def _auto_recover_server_a():
    """
    Background thread: waits AUTO_RECOVERY_DELAY_SEC after outage,
    then automatically calls /simulate/recover on Server A.
    """
    time.sleep(AUTO_RECOVERY_DELAY_SEC)
    if not demo_state["auto_recovery_pending"]:
        return
    ist_time = get_ist_now_str()
    try:
        r = requests.post(f"{SERVER_A_URL}/simulate/recover", timeout=5.0)
        success = (r.status_code == 200)
        msg = (
            "AUTO-RECOVERY: Server A automatically initiated recovery after "
            f"{int(AUTO_RECOVERY_DELAY_SEC)}s outage window."
        )
    except Exception as e:
        success = False
        msg = f"AUTO-RECOVERY attempt failed: {e}"

    demo_state["auto_recovery_pending"] = False
    demo_state["events"].insert(0, {
        "timestamp_ist": ist_time,
        "event_type": "AUTO_RECOVERY_INITIATED",
        "server": "SERVER_A",
        "success": success,
        "message": msg,
    })

@app.route("/")
def index():
    return render_template("index.html")

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
            status_a = {
                "server_id": "SERVER_A",
                "port": 5001,
                "status": da.get("status", "HEALTHY"),
                "reachable": True,
                "total_requests": da.get("total_requests", 0),
                "health_score": da.get("health_score", 100.0),
                "cpu": da.get("cpu_percent", da.get("cpu", 0.0)),
                "memory": da.get("memory_percent", da.get("memory", 0.0)),
                "error_rate": da.get("error_rate", 0.0),
                "is_outage": da.get("active_simulations", {}).get("is_outage", False),
                "is_recovering": da.get("status") == "RECOVERING" or da.get("active_simulations", {}).get("is_recovering", False),
                "recovery_remaining_sec": da.get("recovery_remaining_sec", 0.0)
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
                "total_requests": dc.get("total_requests", 0)
            }
    except Exception:
        pass

    # Query HAProxy Entrypoint
    try:
        rh = requests.get(f"{HAPROXY_URL}/health", timeout=1.5)
        haproxy_status = {
            "status": "UP" if rh.status_code < 500 else "DEGRADED",
            "reachable": True,
            "status_code": rh.status_code,
            "routed_to": rh.headers.get("X-Served-By", "UNKNOWN")
        }
    except Exception as e:
        haproxy_status = {"status": "UNREACHABLE", "reachable": False, "error": str(e)}

    # Determine currently active ingress server.
    # RECOVERING = Server A is coming back but NOT ready to serve yet → Server B still active.
    a_truly_ready = (
        status_a.get("reachable") and
        status_a.get("status") == "HEALTHY" and
        not status_a.get("is_recovering", False)
    )
    if a_truly_ready:
        active_server = "SERVER_A"
    elif status_b.get("status") == "HEALTHY" and status_b.get("reachable"):
        active_server = "SERVER_B"
    elif status_c.get("status") == "HEALTHY" and status_c.get("reachable"):
        active_server = "SERVER_C"
    else:
        active_server = "NONE"

    # Include auto-recovery countdown in response
    auto_recovery_remaining = 0.0
    if demo_state["auto_recovery_pending"] and demo_state["auto_recovery_at"] > 0:
        auto_recovery_remaining = round(max(0.0, demo_state["auto_recovery_at"] - time.time()), 1)

    return jsonify({
        "timestamp_ist": get_ist_now_str(),
        "active_ingress_server": active_server,
        "server_a": status_a,
        "server_b": status_b,
        "server_c": status_c,
        "haproxy": haproxy_status,
        "auto_recovery_pending": demo_state["auto_recovery_pending"],
        "auto_recovery_remaining_sec": auto_recovery_remaining,
        "metrics_summary": {
            "total_sent": demo_state["total_requests_sent"],
            "successful": demo_state["successful_requests"],
            "failed": demo_state["failed_requests"],
            "server_a_hits": demo_state["server_a_hits"],
            "server_b_hits": demo_state["server_b_hits"],
            "failover_count": demo_state["failover_count"],
            "last_failover_time": demo_state["last_failover_time"]
        }
    })

@app.route("/api/demo/send-request", methods=["POST"])
def send_request():
    """
    Sends a REAL HTTP request through the HAProxy ingress port (:80).
    Captures X-Served-By, latency, status code, and payload.
    """
    data = request.get_json(silent=True) or {}
    action = data.get("action", "LOAD_PRODUCTS")
    
    # Map interactive button actions to real backend routes through HAProxy
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

    url = f"{HAPROXY_URL}{target_path}"
    start_time = time.time()
    ist_time = get_ist_now_str()

    try:
        if method == "POST":
            resp = requests.post(url, json=body, timeout=5.0, headers={"Accept": "application/json"})
        else:
            resp = requests.get(url, timeout=5.0, headers={"Accept": "application/json"})

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

        is_success = (status_code < 400)

    except requests.exceptions.RequestException as e:
        duration_ms = round((time.time() - start_time) * 1000.0, 1)
        status_code = 503
        served_by = "ERROR"
        served_port = "N/A"
        req_number = "N/A"
        payload = {"error": str(e), "message": "Failed to connect to HAProxy ingress port 80"}
        is_success = False

    # Track metrics in demo state
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
    if served_by in ["SERVER_A", "SERVER_B"] and served_by != demo_state["last_active_server"]:
        prev = demo_state["last_active_server"]
        demo_state["last_active_server"] = served_by
        demo_state["failover_count"] += 1
        demo_state["last_failover_time"] = ist_time

        event_type = "FAILOVER_ACTIVATED" if served_by == "SERVER_B" else "FAILBACK_RESTORED"
        msg = f"Traffic routed to {served_by} (switched from {prev})"
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
        "action": action,
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

    return jsonify({
        "status": "OK",
        "result": log_entry,
        "failover_event": failover_event,
        "active_server": served_by
    })

@app.route("/api/demo/simulate-outage", methods=["POST"])
def simulate_outage():
    """Triggers a controlled HTTP 503 Outage on Server A, then schedules auto-recovery."""
    ist_time = get_ist_now_str()
    try:
        r = requests.post(f"{SERVER_A_URL}/simulate/outage", timeout=3.0)
        success = (r.status_code == 200)
        msg = "Outage successfully injected on Server A (HTTP 503). Server A is now DOWN. Auto-recovery will begin in 15 seconds."
    except Exception as e:
        success = False
        msg = f"Error triggering outage on Server A: {e}"

    if success:
        # Cancel any previous pending recovery
        demo_state["auto_recovery_pending"] = True
        demo_state["auto_recovery_at"] = time.time() + AUTO_RECOVERY_DELAY_SEC
        demo_state["outage_triggered_at"] = time.time()
        # Launch background auto-recovery thread
        t = threading.Thread(target=_auto_recover_server_a, daemon=True)
        t.start()

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
        "auto_recovery_in_sec": AUTO_RECOVERY_DELAY_SEC if success else 0,
    })

@app.route("/api/demo/restore-server", methods=["POST"])
def restore_server():
    """Triggers controlled node recovery on Server A. Cancels pending auto-recovery if any."""
    ist_time = get_ist_now_str()
    # Cancel auto-recovery since user triggered it manually
    demo_state["auto_recovery_pending"] = False
    try:
        r = requests.post(f"{SERVER_A_URL}/simulate/recover", timeout=3.0)
        success = (r.status_code == 200)
        msg = "Recovery initiated for Server A. Server A is entering health remediation (20s cooldown). Server B continues handling traffic during recovery."
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
