import os
import time
import threading
import requests
from flask import Flask, request, Response, jsonify

# Parse .env if available
for env_path in [
    os.path.join(os.path.dirname(__file__), "..", ".env"),
    os.path.join(os.path.dirname(__file__), "..", "config", ".env")
]:
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k.strip()] = v.strip()

app = Flask(__name__)
stats_app = Flask(__name__ + "_stats")

SERVER_A_URL = os.environ.get("SERVER_A_URL", "http://127.0.0.1:5001")
SERVER_B_URL = os.environ.get("SERVER_B_URL", "http://127.0.0.1:5002")
SERVER_C_URL = os.environ.get("SERVER_C_URL", "http://127.0.0.1:5003")

server_status = {
    "server_a": {"url": SERVER_A_URL, "status": "UP", "health_code": 200, "consecutive_fails": 0},
    "server_b": {"url": SERVER_B_URL, "status": "UP", "health_code": 200, "consecutive_fails": 0},
    "server_c": {"url": SERVER_C_URL, "status": "UP", "health_code": 200, "consecutive_fails": 0}
}

active_backend = "SERVER_A"
override_backend = None

def health_checker():
    global active_backend, override_backend
    while True:
        for srv_key, target in [("server_a", SERVER_A_URL), ("server_b", SERVER_B_URL), ("server_c", SERVER_C_URL)]:
            try:
                r = requests.get(f"{target}/health", timeout=3.0)
                if r.status_code == 200:
                    server_status[srv_key]["status"] = "UP"
                    server_status[srv_key]["health_code"] = 200
                    server_status[srv_key]["consecutive_fails"] = 0
                else:
                    server_status[srv_key]["consecutive_fails"] += 1
                    if server_status[srv_key]["consecutive_fails"] >= 2:
                        server_status[srv_key]["status"] = "DOWN"
                        server_status[srv_key]["health_code"] = r.status_code
            except Exception:
                server_status[srv_key]["consecutive_fails"] += 1
                if server_status[srv_key]["consecutive_fails"] >= 2:
                    server_status[srv_key]["status"] = "DOWN"
                    server_status[srv_key]["health_code"] = 503

        # Route evaluation logic with Predictive Failover override support
        if override_backend:
            # If Server A has completed full recovery to UP, clear override to allow automatic failback
            if override_backend == "SERVER_B" and server_status["server_a"]["status"] == "UP" and server_status["server_a"]["health_code"] == 200:
                print("[HAPROXY FAILBACK] Server A health check passed (HTTP 200). Resetting override to restore Primary Server A.")
                override_backend = None
                active_backend = "SERVER_A"
            elif override_backend == "SERVER_B" and server_status["server_b"]["status"] != "DOWN":
                active_backend = "SERVER_B"
            elif override_backend == "SERVER_C" and server_status["server_c"]["status"] != "DOWN":
                active_backend = "SERVER_C"
            elif override_backend == "SERVER_A" and server_status["server_a"]["status"] != "DOWN":
                active_backend = "SERVER_A"
            else:
                if server_status["server_b"]["status"] != "DOWN":
                    active_backend = "SERVER_B"
                elif server_status["server_c"]["status"] != "DOWN":
                    active_backend = "SERVER_C"
                else:
                    active_backend = "SERVER_A"
        else:
            if server_status["server_a"]["status"] == "UP":
                active_backend = "SERVER_A"
            elif server_status["server_b"]["status"] != "DOWN":
                active_backend = "SERVER_B"
            else:
                active_backend = "SERVER_C"

        time.sleep(1.0)

@app.route('/set_active_backend', methods=['POST'])
@app.route('/haproxy/set_active_backend', methods=['POST'])
def set_active_backend_route():
    global override_backend, active_backend
    data = request.get_json(silent=True) or {}
    target = data.get("active_backend", "SERVER_B").upper()
    reason = data.get("reason", "PREDICTIVE_FAILOVER")
    override_backend = target
    active_backend = target
    print(f"[HAPROXY PREDICTIVE ROUTE] Active backend switched to {target}. Reason: {reason}")
    return jsonify({"status": "OK", "active_backend": active_backend, "override_active": True, "reason": reason})

@app.route('/reset_backend', methods=['POST'])
@app.route('/haproxy/reset_backend', methods=['POST'])
def reset_backend_route():
    global override_backend
    override_backend = None
    print("[HAPROXY ROUTE RESET] Returned to automatic health-check routing.")
    return jsonify({"status": "OK", "active_backend": active_backend, "override_active": False})

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy_handler(path):
    if path in ['set_active_backend', 'haproxy/set_active_backend', 'reset_backend', 'haproxy/reset_backend']:
        if path.endswith('reset_backend'):
            return reset_backend_route()
        return set_active_backend_route()

    if active_backend == "SERVER_A":
        target_base = SERVER_A_URL
        port_num = 5001
    elif active_backend == "SERVER_B":
        target_base = SERVER_B_URL
        port_num = 5002
    else:
        target_base = SERVER_C_URL
        port_num = 5003

    url = f"{target_base}/{path}" if path else f"{target_base}/"
    try:
        req_headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'content-length']}
        resp = requests.request(
            method=request.method,
            url=url,
            headers=req_headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=5.0
        )
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded_headers]
        
        # Inject explicit HAProxy tracking headers indicating which server handled the HTTP request
        headers.append(("X-Served-By", active_backend))
        headers.append(("X-Served-By-Port", str(port_num)))
        headers.append(("X-HAProxy-Ingress", "Port 80"))

        print(f"[HAPROXY INGRESS PORT 80] {request.method} /{path} --> FORWARDED TO: {active_backend} (Port {port_num}) | HTTP {resp.status_code}")

        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        print(f"[HAPROXY ERROR] Failed forwarding request to {active_backend} ({target_base}): {e}")
        err_headers = [
            ("X-Served-By", active_backend),
            ("X-Served-By-Port", str(port_num)),
            ("X-HAProxy-Ingress", "Port 80")
        ]
        return Response(f"HAProxy Proxy Error: {e}", status=502, headers=err_headers)

@stats_app.route('/stats', methods=['GET'])
@stats_app.route('/stats;csv', methods=['GET'])
def haproxy_stats():
    csv_header = "# pxname,svname,status,check_status,check_code,active\n"
    rows = [
        f"app_servers,server_a,{server_status['server_a']['status']},L7OK,{server_status['server_a']['health_code']},1\n",
        f"app_servers,server_b,{server_status['server_b']['status']},L7OK,{server_status['server_b']['health_code']},1\n",
        f"app_servers,server_c,{server_status['server_c']['status']},L7OK,{server_status['server_c']['health_code']},1\n"
    ]
    if request.path.endswith(';csv') or 'csv' in request.args:
        return Response(csv_header + "".join(rows), mimetype='text/csv')
    
    html = f"""
    <html>
    <head><title>HAProxy Load Balancer Stats</title>
    <style>body {{ font-family: sans-serif; background: #0f172a; color: #fff; padding: 20px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #334155; padding: 10px; text-align: left; }}
    th {{ background: #1e293b; }}
    .UP {{ color: #34d399; font-weight: bold; }}
    .DOWN {{ color: #f87171; font-weight: bold; }}
    </style></head>
    <body>
    <h2>HAProxy Load Balancer Telemetry & Status</h2>
    <p>Active Backend Route: <b>{active_backend}</b> {'(PREDICTIVE OVERRIDE ACTIVE)' if override_backend else ''}</p>
    <table>
        <tr><th>Backend</th><th>Server</th><th>Status</th><th>Health Check</th><th>HTTP Code</th></tr>
        <tr><td>app_servers</td><td>server_a (PRIMARY)</td><td class="{server_status['server_a']['status']}">{server_status['server_a']['status']}</td><td>GET /health</td><td>{server_status['server_a']['health_code']}</td></tr>
        <tr><td>app_servers</td><td>server_b (BACKUP)</td><td class="{server_status['server_b']['status']}">{server_status['server_b']['status']}</td><td>GET /health</td><td>{server_status['server_b']['health_code']}</td></tr>
        <tr><td>app_servers</td><td>server_c (EMERGENCY)</td><td class="{server_status['server_c']['status']}">{server_status['server_c']['status']}</td><td>GET /health</td><td>{server_status['server_c']['health_code']}</td></tr>
    </table>
    </body>
    </html>
    """
    return Response(html, mimetype='text/html')

def run_stats_server():
    stats_app.run(host="0.0.0.0", port=8404, debug=False)

if __name__ == "__main__":
    t_health = threading.Thread(target=health_checker, daemon=True)
    t_health.start()

    t_stats = threading.Thread(target=run_stats_server, daemon=True)
    t_stats.start()

    port_to_bind = int(os.environ.get("HAPROXY_PORT", 80))
    print(f"[HAPROXY] Starting Local HAProxy Reverse Proxy on port {port_to_bind}...")
    try:
        app.run(host="0.0.0.0", port=port_to_bind, debug=False)
    except PermissionError:
        print(f"[HAPROXY WARNING] Port {port_to_bind} requires admin rights. Binding to port 8080 instead...")
        app.run(host="0.0.0.0", port=8080, debug=False)
