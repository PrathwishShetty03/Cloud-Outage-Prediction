import os
import sys
import time
import json
import threading
from flask import Flask, jsonify, request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from autoscaling.config import AutoscalerConfig
from autoscaling.autoscaler import RuleBasedAutoscaler, InstanceSnapshot
from autoscaling.discovery import discover_instance_urls, fetch_instance_metrics
from autoscaling.docker_scaler import current_replica_count, apply_replica_count

LOGS_DIR = os.path.abspath(os.path.join(ROOT, "logs"))
os.makedirs(LOGS_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(LOGS_DIR, "autoscaler_history.json")
STATE_FILE = os.path.join(LOGS_DIR, "autoscaler_state.json")

app = Flask(__name__)

STATE_LOCK = threading.Lock()
autoscaler_state = {
    "status": "STARTING",
    "service_name": "app",
    "current_instances": 0,
    "desired_instances": 0,
    "healthy_instances": 0,
    "in_cooldown": False,
    "last_action": "hold",
    "last_reason": "INITIALIZING",
    "signals": {},
    "discovered_urls": [],
    "discovered_instances": [],
    "config": {},
    "last_scale_timestamp": 0.0,
    "total_scale_up_events": 0,
    "total_scale_down_events": 0,
    "total_evaluations": 0,
    "last_eval_timestamp": 0.0,
    "history": []
}


def load_persisted_autoscaler_data():
    """Hydrates autoscaler state and decision history from disk if present."""
    global autoscaler_state
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                saved_state = json.load(f)
                with STATE_LOCK:
                    for k, v in saved_state.items():
                        if k in autoscaler_state:
                            autoscaler_state[k] = v
        except Exception as e:
            print(f"[PERSISTENCE WARNING] Could not load {STATE_FILE}: {e}", flush=True)

    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                saved_history = json.load(f)
                if isinstance(saved_history, list):
                    with STATE_LOCK:
                        autoscaler_state["history"] = saved_history[:100]
        except Exception as e:
            print(f"[PERSISTENCE WARNING] Could not load {HISTORY_FILE}: {e}", flush=True)


def save_persisted_autoscaler_data():
    """Atomically persists autoscaler state and history to disk."""
    with STATE_LOCK:
        state_copy = {
            "status": autoscaler_state.get("status", "RUNNING"),
            "service_name": autoscaler_state.get("service_name", "app"),
            "current_instances": autoscaler_state.get("current_instances", 0),
            "desired_instances": autoscaler_state.get("desired_instances", 0),
            "healthy_instances": autoscaler_state.get("healthy_instances", 0),
            "in_cooldown": autoscaler_state.get("in_cooldown", False),
            "last_action": autoscaler_state.get("last_action", "hold"),
            "last_reason": autoscaler_state.get("last_reason", ""),
            "last_scale_timestamp": autoscaler_state.get("last_scale_timestamp", 0.0),
            "total_scale_up_events": autoscaler_state.get("total_scale_up_events", 0),
            "total_scale_down_events": autoscaler_state.get("total_scale_down_events", 0),
            "total_evaluations": autoscaler_state.get("total_evaluations", 0),
            "last_eval_timestamp": autoscaler_state.get("last_eval_timestamp", time.time())
        }
        history_copy = list(autoscaler_state.get("history", []))[:100]

    try:
        tmp_state = f"{STATE_FILE}.tmp"
        with open(tmp_state, "w", encoding="utf-8") as f:
            json.dump(state_copy, f, indent=2)
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        os.rename(tmp_state, STATE_FILE)
    except Exception as e:
        print(f"[PERSISTENCE ERROR] Failed to save {STATE_FILE}: {e}", flush=True)

    try:
        tmp_hist = f"{HISTORY_FILE}.tmp"
        with open(tmp_hist, "w", encoding="utf-8") as f:
            json.dump(history_copy, f, indent=2)
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        os.rename(tmp_hist, HISTORY_FILE)
    except Exception as e:
        print(f"[PERSISTENCE ERROR] Failed to save {HISTORY_FILE}: {e}", flush=True)


def _snapshots_from_urls(urls):
    snaps = []
    for url in urls:
        m = fetch_instance_metrics(url)
        snaps.append(InstanceSnapshot(
            instance_id=m["instance_id"],
            cpu_percent=m["cpu_percent"],
            memory_percent=m["memory_percent"],
            latency_ms=m["latency_ms"],
            request_rate=m["request_rate"],
            total_requests=m["total_requests"],
            healthy=m["healthy"],
        ))
    return snaps


def run_loop(cfg=None):
    cfg = cfg or AutoscalerConfig()
    load_persisted_autoscaler_data()
    scaler = RuleBasedAutoscaler(cfg)
    # Restore last scale timestamp to protect cooldown across restarts
    if autoscaler_state.get("last_scale_timestamp", 0.0) > 0:
        scaler._last_scale_ts = float(autoscaler_state["last_scale_timestamp"])

    print(
        f"[AUTOSCALE] min={cfg.min_instances} max={cfg.max_instances} "
        f"cooldown={cfg.cooldown_seconds}s hysteresis={cfg.hysteresis} "
        f"apply={cfg.apply_enabled} service={cfg.service_name} status_port={cfg.status_port} "
        f"persisted_history_count={len(autoscaler_state.get('history', []))}"
    )
    while True:
        try:
            urls = discover_instance_urls(cfg.app_dns_name, cfg.app_port, cfg.instance_urls)
            snaps = _snapshots_from_urls(urls)
            scaler.compute_request_rates(snaps)
            docker_count = current_replica_count(cfg.service_name, cfg.compose_project_dir)
            replica_count = docker_count if docker_count is not None else len(snaps)
            decision = scaler.evaluate(snaps, replica_count=replica_count)
            now_ts = time.time()
            payload = {
                "timestamp": now_ts,
                "action": decision.action,
                "current": decision.current_instances,
                "desired": decision.desired_instances,
                "healthy": decision.healthy_instances,
                "in_cooldown": decision.in_cooldown,
                "reason": decision.reason,
                "signals": decision.signals,
                "discovered_urls": urls,
            }
            apply_result = None
            if cfg.apply_enabled and decision.action in ("scale_up", "scale_down") and decision.desired_instances != decision.current_instances:
                apply_result = apply_replica_count(
                    cfg.service_name,
                    decision.desired_instances,
                    project_dir=cfg.compose_project_dir,
                    compose_file=cfg.compose_file,
                )
                payload["apply"] = apply_result

            with STATE_LOCK:
                autoscaler_state["status"] = "RUNNING"
                autoscaler_state["service_name"] = cfg.service_name
                autoscaler_state["current_instances"] = decision.current_instances
                autoscaler_state["desired_instances"] = decision.desired_instances
                autoscaler_state["healthy_instances"] = decision.healthy_instances
                autoscaler_state["in_cooldown"] = decision.in_cooldown
                autoscaler_state["last_action"] = decision.action
                autoscaler_state["last_reason"] = decision.reason
                autoscaler_state["signals"] = decision.signals
                autoscaler_state["discovered_urls"] = urls
                autoscaler_state["total_evaluations"] = autoscaler_state.get("total_evaluations", 0) + 1
                if decision.action == "scale_up" and decision.desired_instances != decision.current_instances:
                    autoscaler_state["total_scale_up_events"] = autoscaler_state.get("total_scale_up_events", 0) + 1
                    autoscaler_state["last_scale_timestamp"] = now_ts
                elif decision.action == "scale_down" and decision.desired_instances != decision.current_instances:
                    autoscaler_state["total_scale_down_events"] = autoscaler_state.get("total_scale_down_events", 0) + 1
                    autoscaler_state["last_scale_timestamp"] = now_ts

                autoscaler_state["discovered_instances"] = [
                    {
                        "instance_id": s.instance_id,
                        "cpu_percent": s.cpu_percent,
                        "memory_percent": s.memory_percent,
                        "latency_ms": s.latency_ms,
                        "request_rate": s.request_rate,
                        "total_requests": s.total_requests,
                        "healthy": s.healthy,
                    }
                    for s in snaps
                ]
                autoscaler_state["config"] = {
                    "min_instances": cfg.min_instances,
                    "max_instances": cfg.max_instances,
                    "cooldown_seconds": cfg.cooldown_seconds,
                    "hysteresis": cfg.hysteresis,
                    "apply_enabled": cfg.apply_enabled,
                    "service_name": cfg.service_name,
                    "watermarks": {
                        "cpu_high": cfg.cpu_high,
                        "cpu_low": cfg.cpu_low,
                        "memory_high": cfg.memory_high,
                        "memory_low": cfg.memory_low,
                        "latency_high_ms": cfg.latency_high_ms,
                        "latency_low_ms": cfg.latency_low_ms,
                        "request_rate_high": cfg.request_rate_high,
                        "request_rate_low": cfg.request_rate_low,
                    },
                }
                autoscaler_state["last_eval_timestamp"] = now_ts
                autoscaler_state["history"].insert(0, payload)
                if len(autoscaler_state["history"]) > 100:
                    autoscaler_state["history"].pop()

            save_persisted_autoscaler_data()
            print(json.dumps(payload), flush=True)
        except Exception as e:
            print(f"[AUTOSCALE ERROR] {e}", flush=True)
        time.sleep(max(2.0, cfg.eval_interval_seconds))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "HEALTHY", "service": "autoscaler", "timestamp": time.time()})


@app.route("/status", methods=["GET"])
@app.route("/api/status", methods=["GET"])
def status():
    with STATE_LOCK:
        return jsonify(autoscaler_state)


@app.route("/history", methods=["GET"])
def history():
    with STATE_LOCK:
        return jsonify(autoscaler_state.get("history", []))


@app.route("/metrics", methods=["GET"])
def prometheus_metrics():
    with STATE_LOCK:
        s_name = autoscaler_state.get("service_name", "app")
        cur_inst = autoscaler_state.get("current_instances", 0)
        des_inst = autoscaler_state.get("desired_instances", 0)
        hlth_inst = autoscaler_state.get("healthy_instances", 0)
        in_cool = 1 if autoscaler_state.get("in_cooldown") else 0
        status_num = 1 if autoscaler_state.get("status") == "RUNNING" else 0
        tot_up = autoscaler_state.get("total_scale_up_events", 0)
        tot_down = autoscaler_state.get("total_scale_down_events", 0)
        tot_eval = autoscaler_state.get("total_evaluations", 0)
        
        cfg = autoscaler_state.get("config", {})
        min_i = cfg.get("min_instances", 1)
        max_i = cfg.get("max_instances", 5)
        
        wm = cfg.get("watermarks", {})
        cpu_h = wm.get("cpu_high", 75.0)
        cpu_l = wm.get("cpu_low", 52.5)
        mem_h = wm.get("memory_high", 75.0)
        mem_l = wm.get("memory_low", 52.5)
        lat_h = wm.get("latency_high_ms", 800.0)
        lat_l = wm.get("latency_low_ms", 560.0)
        rps_h = wm.get("request_rate_high", 25.0)
        rps_l = wm.get("request_rate_low", 17.5)

        sig = autoscaler_state.get("signals", {})
        avg_cpu = sig.get("avg_cpu", 0.0)
        avg_mem = sig.get("avg_memory", 0.0)
        avg_lat = sig.get("avg_latency_ms", 0.0)
        avg_rps = sig.get("request_rate_per_instance", 0.0)

    lines = [
        "# HELP autoscaler_current_instances Current number of running worker replicas",
        "# TYPE autoscaler_current_instances gauge",
        f'autoscaler_current_instances{{service="{s_name}"}} {cur_inst}',
        "# HELP autoscaler_desired_instances Desired number of worker replicas",
        "# TYPE autoscaler_desired_instances gauge",
        f'autoscaler_desired_instances{{service="{s_name}"}} {des_inst}',
        "# HELP autoscaler_healthy_instances Number of healthy worker replicas",
        "# TYPE autoscaler_healthy_instances gauge",
        f'autoscaler_healthy_instances{{service="{s_name}"}} {hlth_inst}',
        "# HELP autoscaler_min_instances Configured minimum replica limit",
        "# TYPE autoscaler_min_instances gauge",
        f'autoscaler_min_instances{{service="{s_name}"}} {min_i}',
        "# HELP autoscaler_max_instances Configured maximum replica limit",
        "# TYPE autoscaler_max_instances gauge",
        f'autoscaler_max_instances{{service="{s_name}"}} {max_i}',
        "# HELP autoscaler_in_cooldown Is the scaler currently in scaling cooldown",
        "# TYPE autoscaler_in_cooldown gauge",
        f'autoscaler_in_cooldown{{service="{s_name}"}} {in_cool}',
        "# HELP autoscaler_daemon_status Status of the autoscaler daemon (1=RUNNING, 0=OFFLINE)",
        "# TYPE autoscaler_daemon_status gauge",
        f'autoscaler_daemon_status{{service="{s_name}"}} {status_num}',
        "# HELP autoscaler_scale_up_events_total Cumulative count of scale-up operations",
        "# TYPE autoscaler_scale_up_events_total counter",
        f'autoscaler_scale_up_events_total{{service="{s_name}"}} {tot_up}',
        "# HELP autoscaler_scale_down_events_total Cumulative count of scale-down operations",
        "# TYPE autoscaler_scale_down_events_total counter",
        f'autoscaler_scale_down_events_total{{service="{s_name}"}} {tot_down}',
        "# HELP autoscaler_evaluations_total Total number of evaluation cycles executed",
        "# TYPE autoscaler_evaluations_total counter",
        f'autoscaler_evaluations_total{{service="{s_name}"}} {tot_eval}',
        "# HELP autoscaler_signal_avg_cpu Average observed CPU utilization percent",
        "# TYPE autoscaler_signal_avg_cpu gauge",
        f'autoscaler_signal_avg_cpu{{service="{s_name}"}} {avg_cpu}',
        "# HELP autoscaler_signal_avg_memory Average observed memory utilization percent",
        "# TYPE autoscaler_signal_avg_memory gauge",
        f'autoscaler_signal_avg_memory{{service="{s_name}"}} {avg_mem}',
        "# HELP autoscaler_signal_avg_latency_ms Average observed response latency in milliseconds",
        "# TYPE autoscaler_signal_avg_latency_ms gauge",
        f'autoscaler_signal_avg_latency_ms{{service="{s_name}"}} {avg_lat}',
        "# HELP autoscaler_signal_avg_rps Average observed request rate per instance",
        "# TYPE autoscaler_signal_avg_rps gauge",
        f'autoscaler_signal_avg_rps{{service="{s_name}"}} {avg_rps}',
        "# HELP autoscaler_watermark_cpu_high High CPU watermark threshold",
        "# TYPE autoscaler_watermark_cpu_high gauge",
        f'autoscaler_watermark_cpu_high{{service="{s_name}"}} {cpu_h}',
        "# HELP autoscaler_watermark_cpu_low Low CPU watermark threshold",
        "# TYPE autoscaler_watermark_cpu_low gauge",
        f'autoscaler_watermark_cpu_low{{service="{s_name}"}} {cpu_l}',
        "# HELP autoscaler_watermark_memory_high High Memory watermark threshold",
        "# TYPE autoscaler_watermark_memory_high gauge",
        f'autoscaler_watermark_memory_high{{service="{s_name}"}} {mem_h}',
        "# HELP autoscaler_watermark_latency_high_ms High Latency watermark threshold",
        "# TYPE autoscaler_watermark_latency_high_ms gauge",
        f'autoscaler_watermark_latency_high_ms{{service="{s_name}"}} {lat_h}',
        "",
    ]
    return Response("\n".join(lines), mimetype="text/plain; version=0.0.4; charset=utf-8")


if __name__ == "__main__":
    cfg = AutoscalerConfig()
    loop_thread = threading.Thread(target=run_loop, args=(cfg,), daemon=True)
    loop_thread.start()
    app.run(host="0.0.0.0", port=cfg.status_port, debug=False)

