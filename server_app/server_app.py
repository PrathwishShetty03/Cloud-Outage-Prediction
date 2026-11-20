import os
import time
import math
import socket
import json
import tempfile
import threading
from flask import Flask, jsonify, request, Response
import psutil
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge, Counter

app = Flask(__name__)

import argparse

parser = argparse.ArgumentParser(description="Cloud Outage Prediction Target Node Microservice")
parser.add_argument("--id", default=os.environ.get("SERVER_ID", "SERVER_A"), help="Server ID (e.g. SERVER_A, SERVER_B, SERVER_C)")
parser.add_argument("--port", type=int, default=int(os.environ.get("SERVER_PORT", 5001)), help="Server listener port")
parser.add_argument("--role", default=os.environ.get("SERVER_ROLE", None), help="Server role (PRIMARY, BACKUP, EMERGENCY)")
parser.add_argument("--primary", action="store_true", default=os.environ.get("IS_PRIMARY", "true").lower() == "true", help="Is primary node")
args, _ = parser.parse_known_args()

SERVER_ID = args.id
SERVER_PORT = args.port
IS_PRIMARY = args.primary
if args.role:
    SERVER_ROLE = args.role
else:
    SERVER_ROLE = "PRIMARY" if SERVER_ID == "SERVER_A" else ("BACKUP" if SERVER_ID == "SERVER_B" else "EMERGENCY")

# Determine default recovery duration based on SERVER_ID (Server A=20s, Server B=30s)
DEFAULT_RECOVERY_SEC = 20.0 if SERVER_ID == "SERVER_A" else (30.0 if SERVER_ID == "SERVER_B" else 20.0)

def get_recovery_stage_details(elapsed, total_dur):
    """
    Computes real-time recovery stages for autonomous self-healing:
    Stage 1: Outage Detection & Triage (0% to 25% of duration)
    Stage 2: Automated Root-Cause Diagnostics (25% to 50% of duration)
    Stage 3: Microservice Service/Container Restart (50% to 75% of duration)
    Stage 4: Self-Healing Health Verification & Warm-up (75% to 100% of duration)
    """
    total_dur = max(0.1, float(total_dur))
    ratio = min(1.0, max(0.0, float(elapsed) / total_dur))
    progress_pct = round(ratio * 100.0, 1)
    rem_sec = round(max(0.0, total_dur - elapsed), 1)

    if ratio < 0.25:
        stage_key = "OUTAGE_DETECTION"
        stage_idx = 1
        stage_name = "Outage Detection & Isolation"
        desc = "Outage signature confirmed. Isolating degraded node, draining lingering connections, and initializing diagnostic engine."
        health_score = round(15.0 + (ratio / 0.25) * 15.0, 1)
        cpu = round(max(20.0, 85.0 - (ratio / 0.25) * 20.0), 1)
        mem = round(max(25.0, 80.0 - (ratio / 0.25) * 15.0), 1)
    elif ratio < 0.50:
        stage_key = "DIAGNOSTICS"
        stage_idx = 2
        stage_name = "Automated Root-Cause Diagnostics"
        desc = "Auditing runtime state: scanning thread locks, inspecting memory heap leaks, resetting chaos buffers, and freeing resources."
        r_sub = (ratio - 0.25) / 0.25
        health_score = round(30.0 + r_sub * 25.0, 1)
        cpu = round(max(18.0, 65.0 - r_sub * 25.0), 1)
        mem = round(max(22.0, 65.0 - r_sub * 25.0), 1)
    elif ratio < 0.75:
        stage_key = "SERVICE_RESTART"
        stage_idx = 3
        stage_name = "Microservice Service Restart"
        desc = "Restarting application service workers, reloading database connections, re-binding HTTP listeners, and re-initializing internal cache."
        r_sub = (ratio - 0.50) / 0.25
        health_score = round(55.0 + r_sub * 25.0, 1)
        cpu = round(max(15.0, 40.0 - r_sub * 18.0), 1)
        mem = round(max(18.0, 40.0 - r_sub * 15.0), 1)
    else:
        stage_key = "HEALTH_VERIFICATION"
        stage_idx = 4
        stage_name = "Health Verification & Pre-Warmup"
        desc = "Running synthetic internal probes, verifying response latency SLAs, checking error budget, and preparing for traffic failback."
        r_sub = (ratio - 0.75) / 0.25
        health_score = round(80.0 + r_sub * 18.0, 1)
        cpu = round(max(10.0, 22.0 - r_sub * 8.0), 1)
        mem = round(max(15.0, 25.0 - r_sub * 8.0), 1)

    return {
        "stage": stage_key,
        "stage_index": stage_idx,
        "total_stages": 4,
        "stage_name": stage_name,
        "description": desc,
        "progress_pct": progress_pct,
        "remaining_sec": rem_sec,
        "health_score": health_score,
        "cpu": cpu,
        "memory": mem
    }

# Monotonic Request & Dynamic Simulation State Variables
simulation_state = {
    "cpu_active": False,
    "ram_allocated": [],
    "disk_allocated_mb": 0,
    "latency_seconds": 0.0,
    "error_rate": 0.0,
    "is_outage": False,
    "is_recovering": False,
    "recovery_start_time": 0.0,
    "recovery_duration_sec": DEFAULT_RECOVERY_SEC,
    "recovery_stage": None,
    "total_requests": 0,      # requests actually served (not blocked by outage)
    "raw_hits": 0,            # every incoming hit incl. blocked ones (for error_rate math)
    "active_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "error_count": 0,
    "start_time": time.time(),
    "last_request_time": time.time(),
    "total_response_time_ms": 0.0
}

# Prometheus Metrics
PROM_CPU = Gauge('server_cpu_usage_percent', 'CPU Usage Percentage', ['server_id'])
PROM_MEM = Gauge('server_memory_usage_percent', 'Memory Usage Percentage', ['server_id'])
PROM_DISK = Gauge('server_disk_usage_percent', 'Disk Usage Percentage', ['server_id'])
PROM_LATENCY = Gauge('server_response_latency_seconds', 'Response Latency in Seconds', ['server_id'])
PROM_ERROR_RATE = Gauge('server_error_rate_ratio', 'Error Rate Ratio', ['server_id'])
PROM_HEALTH = Gauge('server_health_status', 'Server Health Status 1=Healthy 0=Outage', ['server_id'])
PROM_REQUESTS = Counter('server_total_requests_count', 'Total HTTP Requests Served', ['server_id'])

# CPU Stress Worker Thread
def cpu_stress_worker():
    while simulation_state["cpu_active"]:
        _ = math.factorial(25000)
        time.sleep(0.001)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

# Initialize psutil CPU tracker
_last_cpu_time = 0.0
_last_cpu_val = 0.0

def get_node_telemetry_metrics():
    global _last_cpu_time, _last_cpu_val
    now = time.time()
    if now - _last_cpu_time >= 0.8:
        try:
            _last_cpu_val = psutil.cpu_percent(interval=0.08)
        except Exception:
            _last_cpu_val = psutil.cpu_percent(interval=None)
        _last_cpu_time = now

    sys_cpu = _last_cpu_val
    sys_mem = psutil.virtual_memory().percent
    sys_disk = psutil.disk_usage('/').percent

    if simulation_state["cpu_active"]:
        cpu = max(sys_cpu, 88.5)
    else:
        cpu = sys_cpu

    ram_chunks = len(simulation_state["ram_allocated"])
    if ram_chunks > 0:
        mem = max(sys_mem, min(99.0, sys_mem + (ram_chunks * 10.0)))
    else:
        mem = sys_mem

    disk = sys_disk
    lat_ms = simulation_state["latency_seconds"] * 1000.0
    # Use raw_hits as denominator so error_rate stays accurate during outage
    err_rate = (simulation_state["error_count"] / max(1, simulation_state["raw_hits"])) if simulation_state["raw_hits"] > 0 else 0.0
    if simulation_state["error_rate"] > 0:
        err_rate = max(err_rate, simulation_state["error_rate"])

    return round(cpu, 2), round(mem, 2), round(disk, 2), round(lat_ms, 2), round(err_rate, 4)

def calculate_dynamic_health_score(cpu, mem, disk, latency_ms, error_rate):
    if simulation_state["is_outage"]:
        return 0.0
        
    lat_penalty = min(100.0, (latency_ms / 2000.0) * 100.0)
    err_penalty = min(100.0, error_rate * 100.0)
    
    penalty = (0.30 * cpu) + (0.30 * mem) + (0.10 * disk) + (0.15 * lat_penalty) + (0.15 * err_penalty)
    score = max(0.0, min(100.0, 100.0 - (penalty * 0.6)))
    return round(score, 1)

def is_management_path(path):
    return (
        path in ["/health", "/api/metrics", "/metrics", "/status", "/favicon.ico"]
        or path.startswith("/simulate/")
        or path.startswith("/stress/")
    )

@app.before_request
def handle_simulated_delays_and_errors():
    request.start_time_ms = time.time() * 1000.0

    # Internal telemetry & management routes (/health, /api/metrics, /status, /simulate/...)
    # are monitoring probes. They MUST NOT be counted as served user requests,
    # nor delayed by simulated concurrency or artificial latency.
    if is_management_path(request.path):
        return None

    # Track actual user / client application traffic
    simulation_state["raw_hits"] += 1
    simulation_state["active_requests"] += 1
    simulation_state["last_request_time"] = time.time()

    # Dynamic Request Concurrency Load Scaling:
    if simulation_state["active_requests"] > 8:
        concurrency_delay = min(5.5, (simulation_state["active_requests"] - 8) * 0.12)
        time.sleep(concurrency_delay)
        _ = math.factorial(15000)

    # Latency injection
    if simulation_state["latency_seconds"] > 0:
        time.sleep(simulation_state["latency_seconds"])

    # Outage check: if node is in outage or recovering, user request is rejected with HTTP 503
    if simulation_state["is_outage"] or simulation_state["is_recovering"]:
        simulation_state["failed_requests"] += 1
        simulation_state["error_count"] += 1
        simulation_state["active_requests"] = max(0, simulation_state["active_requests"] - 1)
        err_msg = "Simulated Outage Active" if simulation_state["is_outage"] else "Server Undergoing Automated Self-Healing Recovery"
        return jsonify({
            "error": err_msg,
            "server_id": SERVER_ID,
            "status": "RECOVERING" if simulation_state["is_recovering"] else "OUTAGE"
        }), 503

    # Error injection
    if simulation_state["error_rate"] > 0:
        import random
        if random.random() < simulation_state["error_rate"]:
            simulation_state["failed_requests"] += 1
            simulation_state["error_count"] += 1
            simulation_state["active_requests"] = max(0, simulation_state["active_requests"] - 1)
            return jsonify({"error": "Simulated Fault Injection", "server_id": SERVER_ID}), 500

    # User request passed all gates and is actively served
    simulation_state["total_requests"] += 1

@app.after_request
def apply_headers_and_cleanup(response):
    if not is_management_path(request.path):
        simulation_state["active_requests"] = max(0, simulation_state["active_requests"] - 1)
        if response.status_code < 400:
            simulation_state["successful_requests"] += 1
            
        duration = (time.time() * 1000.0) - getattr(request, 'start_time_ms', time.time() * 1000.0)
        simulation_state["total_response_time_ms"] += duration
    
    # CRITICAL SECTION 16.1 REQUIREMENT: Proof Headers
    response.headers["X-Served-By"] = SERVER_ID
    response.headers["X-Server-Port"] = str(SERVER_PORT)
    response.headers["X-Request-Number"] = str(simulation_state["total_requests"])
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "X-Served-By, X-Server-Port, X-Request-Number"
    return response

@app.route("/health", methods=["GET"])
def health_check():
    now = time.time()
    if simulation_state.get("is_recovering", False):
        elapsed = now - simulation_state.get("recovery_start_time", 0.0)
        dur = simulation_state.get("recovery_duration_sec", DEFAULT_RECOVERY_SEC)
        if elapsed < dur:
            stg = get_recovery_stage_details(elapsed, dur)
            PROM_HEALTH.labels(server_id=SERVER_ID).set(0)
            return jsonify({
                "status": "RECOVERING",
                "recovery_stage": stg["stage"],
                "recovery_stage_index": stg["stage_index"],
                "total_stages": stg["total_stages"],
                "recovery_stage_name": stg["stage_name"],
                "description": stg["description"],
                "message": f"[{stg['stage_index']}/4] {stg['stage_name']} ({stg['remaining_sec']}s remaining)",
                "recovery_progress_pct": stg["progress_pct"],
                "recovery_remaining_sec": stg["remaining_sec"],
                "health_score": stg["health_score"],
                "server_name": SERVER_ID,
                "server_id": SERVER_ID,
                "role": SERVER_ROLE,
                "port": SERVER_PORT,
                "is_primary": IS_PRIMARY,
                "total_requests": simulation_state["total_requests"],
                "active_requests": simulation_state["active_requests"],
                "successful_requests": simulation_state["successful_requests"],
                "failed_requests": simulation_state["failed_requests"],
                "uptime": int(now - simulation_state["start_time"]),
                "last_request_time": simulation_state["last_request_time"],
                "cpu": stg["cpu"],
                "memory": stg["memory"],
                "disk": 1.6,
                "latency": 0.0,
                "error_rate": 0.0
            }), 503  # HTTP 503 ensures HAProxy / load balancer keeps Server A in DOWN state during recovery
        else:
            simulation_state["is_recovering"] = False
            simulation_state["is_outage"] = False
            simulation_state["recovery_stage"] = None

    cpu, mem, disk, lat_ms, err_rate = get_node_telemetry_metrics()
    health_score = calculate_dynamic_health_score(cpu, mem, disk, lat_ms, err_rate)
    
    is_unhealthy = (
        simulation_state["is_outage"] or 
        cpu >= 98.0 or 
        lat_ms >= 5000.0 or 
        err_rate >= 0.35 or 
        health_score < 25.0
    )
    is_healthy = not is_unhealthy
    
    status_str = "HEALTHY" if is_healthy else "UNHEALTHY"
    status_code = 200 if is_healthy else 503
    
    PROM_HEALTH.labels(server_id=SERVER_ID).set(1 if is_healthy else 0)
    return jsonify({
        "status": status_str,
        "health_score": health_score,
        "server_name": SERVER_ID,
        "server_id": SERVER_ID,
        "role": SERVER_ROLE,
        "port": SERVER_PORT,
        "is_primary": IS_PRIMARY,
        "total_requests": simulation_state["total_requests"],
        "active_requests": simulation_state["active_requests"],
        "successful_requests": simulation_state["successful_requests"],
        "failed_requests": simulation_state["failed_requests"],
        "uptime": int(now - simulation_state["start_time"]),
        "last_request_time": simulation_state["last_request_time"],
        "cpu": cpu,
        "memory": mem,
        "disk": disk,
        "latency": lat_ms,
        "error_rate": err_rate
    }), status_code

@app.route("/api/metrics", methods=["GET"])
@app.route("/status", methods=["GET"])
def get_metrics():
    now = time.time()
    if simulation_state.get("is_recovering", False):
        elapsed = now - simulation_state.get("recovery_start_time", 0.0)
        dur = simulation_state.get("recovery_duration_sec", DEFAULT_RECOVERY_SEC)
        if elapsed < dur:
            stg = get_recovery_stage_details(elapsed, dur)
            net = psutil.net_io_counters()
            metrics_data = {
                "server_name": SERVER_ID,
                "server_id": SERVER_ID,
                "role": SERVER_ROLE,
                "server_port": SERVER_PORT,
                "port": SERVER_PORT,
                "is_primary": IS_PRIMARY,
                "status": "RECOVERING",
                "recovery_stage": stg["stage"],
                "recovery_stage_index": stg["stage_index"],
                "total_stages": stg["total_stages"],
                "recovery_stage_name": stg["stage_name"],
                "description": stg["description"],
                "message": f"[{stg['stage_index']}/4] {stg['stage_name']} ({stg['remaining_sec']}s remaining)",
                "recovery_progress_pct": stg["progress_pct"],
                "recovery_remaining_sec": stg["remaining_sec"],
                "health_score": stg["health_score"],
                "cpu_percent": stg["cpu"],
                "cpu": stg["cpu"],
                "memory_percent": stg["memory"],
                "memory": stg["memory"],
                "disk_percent": 1.6,
                "disk": 1.6,
                "network_sent_mb": round(net.bytes_sent / (1024 * 1024), 2),
                "network_recv_mb": round(net.bytes_recv / (1024 * 1024), 2),
                "latency_ms": 0.0,
                "latency": 0.0,
                "response_time_ms": 12.0,
                "error_rate": 0.0,
                "total_requests": simulation_state["total_requests"],
                "active_requests": simulation_state["active_requests"],
                "successful_requests": simulation_state["successful_requests"],
                "failed_requests": simulation_state["failed_requests"],
                "uptime": int(now - simulation_state["start_time"]),
                "active_simulations": {
                    "cpu_stress": False,
                    "ram_allocated_mb": 0,
                    "disk_allocated_mb": 0,
                    "latency_injected_sec": 0.0,
                    "error_rate_injected": 0.0,
                    "is_outage": False,
                    "is_recovering": True,
                    "recovery_stage": stg["stage"],
                    "recovery_stage_name": stg["stage_name"],
                    "recovery_stage_index": stg["stage_index"],
                    "recovery_progress_pct": stg["progress_pct"],
                    "recovery_remaining_sec": stg["remaining_sec"]
                }
            }
            return jsonify(metrics_data)
        else:
            simulation_state["is_recovering"] = False
            simulation_state["is_outage"] = False
            simulation_state["recovery_stage"] = None

    cpu, mem, disk, lat_ms, err_rate = get_node_telemetry_metrics()
    net = psutil.net_io_counters()
    
    uptime_sec = int(time.time() - simulation_state["start_time"])
    health_score = calculate_dynamic_health_score(cpu, mem, disk, lat_ms, err_rate)
    
    is_unhealthy = (
        simulation_state["is_outage"] or 
        cpu >= 98.0 or 
        lat_ms >= 5000.0 or 
        err_rate >= 0.35 or 
        health_score < 25.0
    )
    
    if is_unhealthy:
        status_label = "UNHEALTHY"
    elif health_score < 65.0 or cpu > 85.0 or lat_ms >= 1500.0 or err_rate >= 0.10:
        status_label = "WARNING"
    else:
        status_label = "HEALTHY"

    avg_resp = (simulation_state["total_response_time_ms"] / max(1, simulation_state["total_requests"])) if simulation_state["total_requests"] > 0 else lat_ms + 12.0

    metrics_data = {
        "server_name": SERVER_ID,
        "server_id": SERVER_ID,
        "role": SERVER_ROLE,
        "server_port": SERVER_PORT,
        "port": SERVER_PORT,
        "is_primary": IS_PRIMARY,
        "status": status_label,
        "health_score": health_score,
        "cpu_percent": round(cpu, 2),
        "cpu": round(cpu, 2),
        "memory_percent": round(mem, 2),
        "memory": round(mem, 2),
        "disk_percent": round(disk, 2),
        "disk": round(disk, 2),
        "network_sent_mb": round(net.bytes_sent / (1024 * 1024), 2),
        "network_recv_mb": round(net.bytes_recv / (1024 * 1024), 2),
        "latency_ms": lat_ms,
        "latency": lat_ms,
        "response_time_ms": round(avg_resp, 2),
        "response_time": round(avg_resp, 2),
        "average_response_time": round(avg_resp, 2),
        "error_rate": err_rate,
        "total_requests": simulation_state["total_requests"],
        "request_count": simulation_state["total_requests"],
        "active_requests": simulation_state["active_requests"],
        "successful_requests": simulation_state["successful_requests"],
        "failed_requests": simulation_state["failed_requests"],
        "error_count": simulation_state["error_count"],
        "uptime": uptime_sec,
        "uptime_seconds": uptime_sec,
        "last_request_time": simulation_state["last_request_time"],
        "active_simulations": {
            "cpu_stress": simulation_state["cpu_active"],
            "ram_allocated_mb": len(simulation_state["ram_allocated"]) * 50,
            "disk_allocated_mb": simulation_state["disk_allocated_mb"],
            "latency_injected_sec": simulation_state["latency_seconds"],
            "error_rate_injected": simulation_state["error_rate"],
            "is_outage": simulation_state["is_outage"]
        }
    }
    
    PROM_CPU.labels(server_id=SERVER_ID).set(metrics_data["cpu_percent"])
    PROM_MEM.labels(server_id=SERVER_ID).set(metrics_data["memory_percent"])
    PROM_DISK.labels(server_id=SERVER_ID).set(metrics_data["disk_percent"])
    PROM_LATENCY.labels(server_id=SERVER_ID).set(simulation_state["latency_seconds"])
    PROM_ERROR_RATE.labels(server_id=SERVER_ID).set(metrics_data["error_rate"])
    PROM_HEALTH.labels(server_id=SERVER_ID).set(0 if is_unhealthy else 1)
    
    return jsonify(metrics_data)

HTML_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{server_id} — Target Node Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Outfit', sans-serif;
            background: #0f172a;
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            width: 100%;
            max-width: 900px;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 28px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid #334155;
            margin-bottom: 24px;
        }}
        .server-title {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .server-name {{
            font-size: 1.8rem;
            font-weight: 800;
            color: #38bdf8;
        }}
        .badge-role {{
            background: #1e1b4b;
            color: #a78bfa;
            border: 1px solid #6366f1;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 700;
        }}
        .status-pill {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: #064e3b;
            color: #34d399;
            border: 1px solid #10b981;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.9rem;
        }}
        .status-dot {{
            width: 10px;
            height: 10px;
            background: #34d399;
            border-radius: 50%;
            box-shadow: 0 0 10px #34d399;
            animation: pulse 1.5s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(0.95); opacity: 0.8; }}
            50% {{ transform: scale(1.15); opacity: 1; }}
            100% {{ transform: scale(0.95); opacity: 0.8; }}
        }}
        .proof-box {{
            background: #0f172a;
            border: 1px dashed #6366f1;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.88rem;
        }}
        .proof-title {{
            color: #818cf8;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        .proof-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }}
        .proof-item span {{
            color: #94a3b8;
        }}
        .proof-item strong {{
            color: #38bdf8;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .card {{
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
        }}
        .card-label {{
            color: #94a3b8;
            font-size: 0.85rem;
            margin-bottom: 6px;
        }}
        .card-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #f8fafc;
        }}
        .bar-bg {{
            background: #334155;
            height: 6px;
            border-radius: 3px;
            margin-top: 8px;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            width: 0%;
            transition: width 0.3s ease;
        }}
        .actions {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}
        .btn {{
            background: #334155;
            color: #f8fafc;
            border: 1px solid #475569;
            padding: 10px 16px;
            border-radius: 8px;
            font-family: inherit;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn:hover {{
            background: #475569;
            border-color: #38bdf8;
        }}
        .btn-danger {{
            background: #7f1d1d;
            border-color: #ef4444;
            color: #fca5a5;
        }}
        .btn-danger:hover {{
            background: #991b1b;
        }}
        .btn-success {{
            background: #064e3b;
            border-color: #10b981;
            color: #6ee7b7;
        }}
        .btn-success:hover {{
            background: #047857;
        }}
        .raw-json {{
            display: none;
            background: #090d16;
            border: 1px solid #334155;
            padding: 16px;
            border-radius: 10px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #34d399;
            white-space: pre-wrap;
            margin-top: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="server-title">
                <div class="server-name">{server_id}</div>
                <div class="badge-role">{role}</div>
            </div>
            <div class="status-pill" id="statusPill">
                <div class="status-dot" id="statusDot"></div>
                <span id="statusText">HEALTHY</span>
            </div>
        </div>

        <div class="proof-box">
            <div class="proof-title">🔒 Evaluator Independent Proof Headers (X-Headers)</div>
            <div class="proof-grid">
                <div class="proof-item"><span>X-Served-By:</span> <strong id="hdrServedBy">{server_id}</strong></div>
                <div class="proof-item"><span>X-Server-Port:</span> <strong id="hdrPort">{server_port}</strong></div>
                <div class="proof-item"><span>X-Request-Number:</span> <strong id="hdrReqNum">{total_requests}</strong></div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-label">Total Requests Served</div>
                <div class="card-value" id="valTotalReq">{total_requests}</div>
            </div>
            <div class="card">
                <div class="card-label">CPU Usage</div>
                <div class="card-value" id="valCpu">{cpu}%</div>
                <div class="bar-bg"><div class="bar-fill" id="barCpu" style="width: {cpu}%;"></div></div>
            </div>
            <div class="card">
                <div class="card-label">Memory Usage</div>
                <div class="card-value" id="valMem">{memory}%</div>
                <div class="bar-bg"><div class="bar-fill" id="barMem" style="width: {memory}%;"></div></div>
            </div>
            <div class="card">
                <div class="card-label">Network Latency</div>
                <div class="card-value" id="valLat">{latency} ms</div>
            </div>
        </div>

        <div class="actions">
            <button class="btn" onclick="triggerStress('cpu')">⚡ Inject CPU Stress</button>
            <button class="btn" onclick="triggerStress('latency')">🐢 Inject 5.5s Latency</button>
            <button class="btn btn-danger" onclick="triggerOutage()">💥 Simulate Outage</button>
            <button class="btn btn-success" onclick="triggerRecover()">💚 Recover Node</button>
            <button class="btn" onclick="toggleJson()">📜 Toggle Raw JSON View</button>
        </div>

        <pre class="raw-json" id="jsonBox">{raw_json}</pre>
    </div>

    <script>
        async function updateMetrics() {{
            try {{
                const res = await fetch('/api/metrics');
                const d = await res.json();
                document.getElementById('valTotalReq').innerText = d.total_requests;
                document.getElementById('valCpu').innerText = d.cpu + '%';
                document.getElementById('barCpu').style.width = Math.min(100, d.cpu) + '%';
                document.getElementById('valMem').innerText = d.memory + '%';
                document.getElementById('barMem').style.width = Math.min(100, d.memory) + '%';
                document.getElementById('valLat').innerText = d.latency + ' ms';
                document.getElementById('hdrReqNum').innerText = d.total_requests;
                document.getElementById('jsonBox').innerText = JSON.stringify(d, null, 2);
                
                const pill = document.getElementById('statusPill');
                const txt = document.getElementById('statusText');
                if (d.status === 'HEALTHY') {{
                    pill.style.background = '#064e3b';
                    pill.style.borderColor = '#10b981';
                    pill.style.color = '#34d399';
                    txt.innerText = 'HEALTHY';
                }} else {{
                    pill.style.background = '#7f1d1d';
                    pill.style.borderColor = '#ef4444';
                    pill.style.color = '#f87171';
                    txt.innerText = d.status;
                }}
            }} catch(e) {{}}
        }}

        async function triggerStress(type) {{
            if (type === 'cpu') fetch('/stress/cpu', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify({{enable:true}})}});
            if (type === 'latency') fetch('/stress/latency', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify({{seconds:5.5}})}});
            setTimeout(updateMetrics, 500);
        }}
        async function triggerOutage() {{
            fetch('/simulate/outage', {{method:'POST'}});
            setTimeout(updateMetrics, 500);
        }}
        async function triggerRecover() {{
            fetch('/simulate/recover', {{method:'POST'}});
            setTimeout(updateMetrics, 500);
        }}
        function toggleJson() {{
            const box = document.getElementById('jsonBox');
            box.style.display = box.style.display === 'block' ? 'none' : 'block';
        }}

        setInterval(updateMetrics, 1500);
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    local_ip = get_local_ip()
    print(f"[TRAFFIC INGRESS] {SERVER_ID} (Port {SERVER_PORT}) served Request #{simulation_state['total_requests']} at {time.strftime('%H:%M:%S')}")

    json_payload = {
        "message": f"Cloud Outage Prediction Target Node - {SERVER_ID}",
        "server_name": SERVER_ID,
        "server_id": SERVER_ID,
        "role": SERVER_ROLE,
        "is_primary": IS_PRIMARY,
        "server_port": SERVER_PORT,
        "port": SERVER_PORT,
        "local_ip": local_ip,
        "total_requests": simulation_state["total_requests"],
        "requests_served": simulation_state["total_requests"],
        "active_requests": simulation_state["active_requests"],
        "timestamp": time.time()
    }

    # If client specifically asks for JSON (e.g. curl / API request)
    accept_hdr = request.headers.get("Accept", "")
    if "application/json" in accept_hdr or request.args.get("format") == "json":
        return jsonify(json_payload)

    # Otherwise render HTML Dashboard UI for browser requests
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    lat_ms = round(simulation_state["latency_seconds"] * 1000.0, 1)

    html_content = HTML_INDEX_TEMPLATE.format(
        server_id=SERVER_ID,
        role=SERVER_ROLE,
        server_port=SERVER_PORT,
        total_requests=simulation_state["total_requests"],
        cpu=round(cpu, 1),
        memory=round(mem, 1),
        latency=lat_ms,
        raw_json=json.dumps(json_payload, indent=2)
    )
    return Response(html_content, mimetype="text/html")

# --- REALISTIC DEMO BUSINESS API ENDPOINTS ---

@app.route("/api/products", methods=["GET"])
def get_products():
    products = [
        {"id": "PROD-101", "name": "Compute Engine c2-standard-4", "category": "Virtual Machines", "price_per_hr": "$0.208", "stock": 42},
        {"id": "PROD-102", "name": "Cloud SQL PostgreSQL High-Avail", "category": "Databases", "price_per_hr": "$0.412", "stock": 18},
        {"id": "PROD-103", "name": "Cloud Storage Multi-Region Bucket", "category": "Object Storage", "price_per_gb": "$0.026", "stock": 999},
        {"id": "PROD-104", "name": "Kubernetes Managed Cluster (GKE)", "category": "Containers", "price_per_hr": "$0.100", "stock": 25},
        {"id": "PROD-105", "name": "Cloud Armor DDoS & WAF Protection", "category": "Networking", "price_per_mo": "$5.000", "stock": 100}
    ]
    return jsonify({
        "status": "SUCCESS",
        "action": "LOAD_PRODUCTS",
        "server_id": SERVER_ID,
        "server_port": SERVER_PORT,
        "role": SERVER_ROLE,
        "item_count": len(products),
        "products": products,
        "timestamp": time.time()
    })

@app.route("/api/dashboard-data", methods=["GET"])
def get_dashboard_data():
    cpu, mem, disk, lat_ms, err_rate = get_node_telemetry_metrics()
    return jsonify({
        "status": "SUCCESS",
        "action": "FETCH_DASHBOARD_DATA",
        "server_id": SERVER_ID,
        "server_port": SERVER_PORT,
        "role": SERVER_ROLE,
        "metrics": {
            "node_cpu_percent": cpu,
            "node_memory_percent": mem,
            "node_disk_percent": disk,
            "node_latency_ms": lat_ms,
            "node_error_rate": err_rate,
            "active_client_connections": simulation_state["active_requests"],
            "total_requests_served": simulation_state["total_requests"],
            "successful_transactions": simulation_state["successful_requests"]
        },
        "system_load": {
            "throughput_qps": round(simulation_state["total_requests"] / max(1.0, (time.time() - simulation_state["start_time"])), 2),
            "cache_hit_ratio": "96.4%",
            "active_workers": 4
        },
        "timestamp": time.time()
    })

@app.route("/api/orders", methods=["POST", "GET"])
def place_order():
    data = request.get_json(silent=True) or {}
    order_id = f"ORD-{int(time.time() * 1000) % 1000000}"
    item = data.get("item", "c2-standard-4 High-Memory Cloud Instance")
    quantity = int(data.get("quantity", 1))
    
    return jsonify({
        "status": "SUCCESS",
        "action": "PLACE_TEST_ORDER",
        "order_id": order_id,
        "server_id": SERVER_ID,
        "server_port": SERVER_PORT,
        "role": SERVER_ROLE,
        "order_details": {
            "item": item,
            "quantity": quantity,
            "allocated_cluster_node": SERVER_ID,
            "fulfillment_status": "PROVISIONED",
            "execution_ms": round((time.time() * 1000.0) - getattr(request, 'start_time_ms', time.time() * 1000.0), 2)
        },
        "timestamp": time.time()
    })

@app.route("/metrics", methods=["GET"])
def prometheus_metrics():
    get_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# --- CHAOS SIMULATION CONTROL ENDPOINTS ---

@app.route("/stress/cpu", methods=["POST"])
def stress_cpu():
    data = request.get_json(silent=True) or {}
    enable = data.get("enable", not simulation_state["cpu_active"])
    simulation_state["cpu_active"] = enable
    
    if enable:
        for _ in range(4):
            t = threading.Thread(target=cpu_stress_worker, daemon=True)
            t.start()
            
    return jsonify({"status": "OK", "cpu_stress_active": simulation_state["cpu_active"], "server_id": SERVER_ID})

@app.route("/stress/ram", methods=["POST"])
def stress_ram():
    data = request.get_json(silent=True) or {}
    mb = data.get("mb", 200)
    
    if mb > 0:
        chunk = bytearray(50 * 1024 * 1024)
        for _ in range(max(1, mb // 50)):
            simulation_state["ram_allocated"].append(chunk)
    else:
        simulation_state["ram_allocated"].clear()
        
    return jsonify({
        "status": "OK",
        "ram_allocated_mb": len(simulation_state["ram_allocated"]) * 50,
        "server_id": SERVER_ID
    })

@app.route("/stress/disk", methods=["POST"])
def stress_disk():
    data = request.get_json(silent=True) or {}
    mb = data.get("mb", 100)
    
    if mb > 0:
        temp_dir = tempfile.gettempdir()
        dummy_file = os.path.join(temp_dir, f"outage_stress_{SERVER_ID}_{SERVER_PORT}.tmp")
        with open(dummy_file, "wb") as f:
            f.write(b"0" * (mb * 1024 * 1024))
        simulation_state["disk_allocated_mb"] = mb
    else:
        temp_dir = tempfile.gettempdir()
        dummy_file = os.path.join(temp_dir, f"outage_stress_{SERVER_ID}_{SERVER_PORT}.tmp")
        if os.path.exists(dummy_file):
            try:
                os.remove(dummy_file)
            except Exception:
                pass
        simulation_state["disk_allocated_mb"] = 0
        
    return jsonify({"status": "OK", "disk_allocated_mb": simulation_state["disk_allocated_mb"], "server_id": SERVER_ID})

@app.route("/stress/latency", methods=["POST"])
def stress_latency():
    data = request.get_json(silent=True) or {}
    seconds = float(data.get("seconds", 5.5))
    simulation_state["latency_seconds"] = max(0.0, seconds)
    return jsonify({"status": "OK", "latency_seconds": simulation_state["latency_seconds"], "server_id": SERVER_ID})

@app.route("/stress/error", methods=["POST"])
def stress_error():
    data = request.get_json(silent=True) or {}
    rate = float(data.get("rate", 0.35))
    simulation_state["error_rate"] = max(0.0, min(1.0, rate))
    return jsonify({"status": "OK", "error_rate": simulation_state["error_rate"], "server_id": SERVER_ID})

def _execute_node_recovery(dur=None):
    if dur is None:
        dur = 20.0 if SERVER_ID == "SERVER_A" else (30.0 if SERVER_ID == "SERVER_B" else 20.0)
    
    simulation_state["cpu_active"] = False
    simulation_state["ram_allocated"].clear()
    simulation_state["disk_allocated_mb"] = 0
    simulation_state["latency_seconds"] = 0.0
    simulation_state["error_rate"] = 0.0
    simulation_state["error_count"] = 0
    simulation_state["failed_requests"] = 0
    simulation_state["raw_hits"] = simulation_state["total_requests"]
    simulation_state["is_outage"] = False
    
    # Enable node-specific recovery transition phase
    simulation_state["is_recovering"] = True
    simulation_state["recovery_start_time"] = time.time()
    simulation_state["recovery_duration_sec"] = dur
    
    def finish_recovery():
        time.sleep(dur)
        simulation_state["is_recovering"] = False
        simulation_state["is_outage"] = False
        simulation_state["recovery_stage"] = None
        simulation_state["error_count"] = 0
        simulation_state["failed_requests"] = 0
        simulation_state["raw_hits"] = simulation_state["total_requests"]
        print(f"[RECOVERY COMPLETE] {SERVER_ID} (Port {SERVER_PORT}) fully recovered to HEALTHY state after {dur}s.")
        
    t = threading.Thread(target=finish_recovery, daemon=True)
    t.start()
    
    temp_dir = tempfile.gettempdir()
    dummy_file = os.path.join(temp_dir, f"outage_stress_{SERVER_ID}_{SERVER_PORT}.tmp")
    if os.path.exists(dummy_file):
        try:
            os.remove(dummy_file)
        except Exception:
            pass

@app.route("/simulate/outage", methods=["POST"])
def simulate_outage():
    data = request.get_json(silent=True) or {}
    auto_recover = data.get("auto_recover", True)
    delay_sec = float(data.get("delay", 2.0))
    dur = float(data.get("duration", 20.0 if SERVER_ID == "SERVER_A" else 30.0))
    
    simulation_state["is_outage"] = True
    simulation_state["is_recovering"] = False
    
    if auto_recover:
        def start_delayed():
            time.sleep(delay_sec)
            # Only start if still in outage and not manually recovered
            if simulation_state["is_outage"] and not simulation_state["is_recovering"]:
                print(f"[AUTO-RECOVERY] Outage confirmed on {SERVER_ID}. Beginning staged automatic recovery ({dur}s)...")
                _execute_node_recovery(dur)
        t = threading.Thread(target=start_delayed, daemon=True)
        t.start()
        
    return jsonify({
        "status": "OUTAGE_TRIGGERED",
        "server_id": SERVER_ID,
        "port": SERVER_PORT,
        "auto_recover": auto_recover,
        "auto_recovery_starts_in_sec": delay_sec if auto_recover else 0,
        "recovery_duration_sec": dur
    })

@app.route("/simulate/recover", methods=["POST"])
def simulate_recover():
    data = request.get_json(silent=True) or {}
    dur = float(data.get("duration", 20.0 if SERVER_ID == "SERVER_A" else 30.0))
    _execute_node_recovery(dur)
    stg = get_recovery_stage_details(0.0, dur)
    return jsonify({
        "status": "RECOVERING",
        "stage": stg["stage"],
        "stage_name": stg["stage_name"],
        "description": stg["description"],
        "message": f"Staged recovery active for {SERVER_ID} ({int(dur)}s remaining)",
        "recovery_duration_sec": dur,
        "server_id": SERVER_ID,
        "port": SERVER_PORT
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVER_PORT, debug=False)
