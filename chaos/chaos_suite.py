import os
import time
import requests

class ChaosEngineeringSuite:
    """
    Chaos Engineering Experiment Execution Engine.
    Provides controlled fault injection routines operating strictly inside the project environment:
    CPU Stress, RAM Leak, Latency Surge, Error Cascade, Disk Pressure, Traffic Spike, Service Crash, Dependency Slowdown.
    """
    def __init__(self, endpoint_a="http://localhost:5001"):
        self.endpoint_a = endpoint_a
        self.experiment_history = []

    def trigger_chaos_experiment(self, experiment_type, server_url=None, params=None):
        """
        Executes a controlled chaos experiment against the target server container.
        """
        target_url = server_url or self.endpoint_a
        params = params or {}
        exp_id = f"EXP-{int(time.time())}"
        start_time = time.time()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        success = False
        message = ""

        try:
            if experiment_type == "CPU_STRESS":
                r = requests.post(f"{target_url}/stress/cpu", json={"enable": True}, timeout=2.0)
                success = (r.status_code == 200)
                message = "Injected CPU compute stress via multi-threaded factorial computation."

            elif experiment_type == "RAM_LEAK":
                mb = params.get("mb", 300)
                r = requests.post(f"{target_url}/stress/ram", json={"mb": mb}, timeout=2.0)
                success = (r.status_code == 200)
                message = f"Allocated {mb} MB heap memory chunk to simulate memory leak."

            elif experiment_type == "LATENCY_INJECTION":
                sec = params.get("seconds", 5.5)
                r = requests.post(f"{target_url}/stress/latency", json={"seconds": sec}, timeout=2.0)
                success = (r.status_code == 200)
                message = f"Injected {sec} seconds response delay per HTTP request."

            elif experiment_type == "ERROR_CASCADE":
                rate = params.get("rate", 0.40)
                r = requests.post(f"{target_url}/stress/error", json={"rate": rate}, timeout=2.0)
                success = (r.status_code == 200)
                message = f"Injected {int(rate*100)}% HTTP 500 fault injection rate."

            elif experiment_type == "DISK_PRESSURE":
                mb = params.get("mb", 150)
                r = requests.post(f"{target_url}/stress/disk", json={"mb": mb}, timeout=2.0)
                success = (r.status_code == 200)
                message = f"Generated {mb} MB temporary file pressure."

            elif experiment_type == "SERVICE_CRASH":
                r = requests.post(f"{target_url}/simulate/outage", timeout=2.0)
                success = (r.status_code == 200)
                message = "Triggered simulated node service crash (HTTP 503)."

            elif experiment_type == "RECOVER_ALL":
                r = requests.post(f"{target_url}/simulate/recover", timeout=2.0)
                success = (r.status_code == 200)
                message = "Cleared all active fault injections and recovered node."

        except Exception as e:
            success = False
            message = f"Chaos injection error: {e}"

        record = {
            "experiment_id": exp_id,
            "timestamp": timestamp,
            "experiment_type": experiment_type,
            "target_url": target_url,
            "success": success,
            "details": message,
            "execution_duration_sec": round(time.time() - start_time, 3)
        }

        self.experiment_history.insert(0, record)
        return record

    def get_experiment_history(self):
        return self.experiment_history
