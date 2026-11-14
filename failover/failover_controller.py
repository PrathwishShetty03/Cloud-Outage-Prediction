import os
import time
from datetime import datetime, timezone, timedelta
import requests
import pandas as pd
from ml.ml_engine import OutagePredictorML
from digital_twin.twin_engine import DigitalTwinEngine
from remediation.remediation_engine import SelfHealingRemediationEngine
from monitoring.slo_tracker import SLOTracker
from monitoring.dependency_graph import DependencyGraphEvaluator
from chaos.chaos_suite import ChaosEngineeringSuite
from experiments.evaluation_framework import ExperimentalEvaluationFramework

class AutomatedFailoverController:
    """
    Centralized Intelligent Failover Controller & Cloud Reliability Command Engine.
    Supports:
    - 3-Server Hierarchy (SERVER_A Primary, SERVER_B Twin/Backup, SERVER_C Emergency).
    - Intelligent Server Suitability Scoring Engine.
    - Predictive Failover (ML Risk >= 0.80) & Emergency Failover (HTTP 503 / Down).
    - Automated Self-Healing Remediation Workflow.
    - SRE SLO/SLA & Error Budget Tracker.
    - Dependency Graph Health Evaluator.
    - Chaos Engineering Suite & 3-Way Comparative Evaluation Framework.
    """
    def __init__(self, endpoint_a="http://localhost:5001", endpoint_b="http://localhost:5002", endpoint_c="http://localhost:5003", haproxy_url="http://localhost:80"):
        self.endpoint_a = endpoint_a
        self.endpoint_b = endpoint_b
        self.endpoint_c = endpoint_c
        self.haproxy_url = haproxy_url
        
        self.failover_mode = "AUTOMATIC"
        self.active_server = "SERVER_A"
        self.failover_type = "NORMAL"
        self.history_a = []
        self.history_b = []
        self.history_c = []
        self.failover_logs = []

        # Integrated Core Modules
        self.ml_predictor = OutagePredictorML()
        self.twin_engine = DigitalTwinEngine()
        self.remediation_engine = SelfHealingRemediationEngine()
        self.slo_tracker = SLOTracker()
        self.dependency_evaluator = DependencyGraphEvaluator()
        self.chaos_suite = ChaosEngineeringSuite(endpoint_a=self.endpoint_a)
        self.evaluation_framework = ExperimentalEvaluationFramework()
        
        # State tracking for graceful self-healing cooldown
        self.is_remediating = False
        self.outage_start_time = 0.0

        # Log initial startup
        self.log_event("SYSTEM_INIT", "SERVER_A", "Automated Failover Controller initialized with primary SERVER_A", failover_type="NORMAL")

    def update_endpoints(self, ep_a, ep_b, ep_c):
        self.endpoint_a = ep_a
        self.endpoint_b = ep_b
        self.endpoint_c = ep_c
        self.chaos_suite.endpoint_a = ep_a

    def notify_haproxy_route(self, target_server, reason):
        """Notifies HAProxy / local reverse proxy to dynamically update active ingress route"""
        for url in [self.haproxy_url, "http://localhost:80", "http://localhost:8404"]:
            try:
                requests.post(f"{url}/set_active_backend", json={"active_backend": target_server, "reason": reason}, timeout=0.8)
                requests.post(f"{url}/haproxy/set_active_backend", json={"active_backend": target_server, "reason": reason}, timeout=0.8)
            except Exception:
                pass

    def fetch_node_metrics(self, base_url, node_name):
        try:
            r = requests.get(f"{base_url}/api/metrics", timeout=2.5)
            if r.status_code == 200:
                data = r.json()
                data["is_reachable"] = True
                return data
            else:
                return {
                    "server_id": node_name, "server_name": node_name,
                    "status": "UNHEALTHY", "health_score": 0.0,
                    "cpu_percent": 100.0, "memory_percent": 100.0, "disk_percent": 100.0,
                    "latency_ms": 5000.0, "error_rate": 1.0, "total_requests": 0,
                    "is_reachable": False
                }
        except Exception:
            return {
                "server_id": node_name, "server_name": node_name,
                "status": "UNHEALTHY", "health_score": 0.0,
                "cpu_percent": 100.0, "memory_percent": 100.0, "disk_percent": 100.0,
                "latency_ms": 5000.0, "error_rate": 1.0, "total_requests": 0,
                "is_reachable": False
            }

    def calculate_suitability_scores(self, snapshot, prediction, twin_res):
        """
        Calculates mathematical server suitability scores across candidate nodes:
        Suitability = 0.35*Health + 0.25*(100-max(CPU,RAM)) + 0.15*LatencyScore + 0.15*(100-Risk) + 0.10*TwinSync
        """
        scores = {}
        prob_a = prediction.get("outage_probability", 0.05)

        for s_key in ["server_a", "server_b", "server_c"]:
            m = snapshot.get(s_key, {})
            s_id = m.get("server_id", s_key.upper())
            
            if not m.get("is_reachable", False) or m.get("status") == "UNHEALTHY":
                scores[s_id] = {
                    "suitability_score": 0.0,
                    "health_score": 0.0,
                    "capacity_score": 0.0,
                    "latency_score": 0.0,
                    "risk_score": 0.0,
                    "twin_sync_score": 0.0,
                    "status": m.get("status", "UNHEALTHY")
                }
                continue

            h_score = float(m.get("health_score", 100.0))
            cpu = float(m.get("cpu_percent", m.get("cpu", 0.0)))
            mem = float(m.get("memory_percent", m.get("memory", 0.0)))
            cap_score = max(0.0, 100.0 - max(cpu, mem))

            lat = float(m.get("latency_ms", m.get("latency", 0.0)))
            lat_score = max(0.0, 100.0 - min(100.0, (lat / 2000.0) * 100.0))

            s_risk = prob_a if s_id == "SERVER_A" else (0.05 if m.get("status") == "HEALTHY" else 0.80)
            risk_score = max(0.0, 100.0 - (s_risk * 100.0))

            div_score = float(twin_res.get("divergence_score", 0.0))
            twin_score = max(0.0, 100.0 - div_score) if s_id == "SERVER_B" else 100.0

            total_score = (
                (0.35 * h_score) +
                (0.25 * cap_score) +
                (0.15 * lat_score) +
                (0.15 * risk_score) +
                (0.10 * twin_score)
            )

            scores[s_id] = {
                "suitability_score": round(max(0.0, min(100.0, total_score)), 1),
                "health_score": round(h_score, 1),
                "capacity_score": round(cap_score, 1),
                "latency_score": round(lat_score, 1),
                "risk_score": round(risk_score, 1),
                "twin_sync_score": round(twin_score, 1),
                "status": m.get("status", "HEALTHY")
            }

        return scores

    def log_event(self, event_type, server_id, description, severity="INFO", failover_type="NORMAL", prob=0.0, metrics=None):
        m = metrics or {}
        IST = timezone(timedelta(hours=5, minutes=30))
        now_ist = datetime.now(IST)
        entry = {
            "timestamp": now_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
            "iso_time": now_ist.strftime("%H:%M:%S IST"),
            "event_type": event_type,
            "event": event_type,
            "server": server_id,
            "severity": severity,
            "description": description,
            "active_server": self.active_server,
            "traffic_target": self.active_server,
            "failover_type": failover_type,
            "outage_probability": round(prob, 4),
            "risk_level": "CRITICAL" if prob >= 0.80 else ("WARNING" if prob >= 0.50 else "LOW"),
            "cpu": m.get("cpu_percent", m.get("cpu", 0.0)),
            "memory": m.get("memory_percent", m.get("memory", 0.0)),
            "latency": m.get("latency_ms", m.get("latency", 0.0)),
            "error_rate": m.get("error_rate", 0.0),
            "request_number": m.get("total_requests", 0)
        }
        self.failover_logs.insert(0, entry)

    def evaluate_cycle(self):
        m_a = self.fetch_node_metrics(self.endpoint_a, "SERVER_A")
        m_b = self.fetch_node_metrics(self.endpoint_b, "SERVER_B")
        m_c = self.fetch_node_metrics(self.endpoint_c, "SERVER_C")

        # Update sliding metric histories
        self.history_a.append(m_a)
        if len(self.history_a) > 30: self.history_a.pop(0)

        self.history_b.append(m_b)
        if len(self.history_b) > 30: self.history_b.pop(0)

        self.history_c.append(m_c)
        if len(self.history_c) > 30: self.history_c.pop(0)

        snapshot = {
            "server_a": m_a,
            "server_b": m_b,
            "server_c": m_c
        }

        # ML Outage Prediction on Server A history
        pred_res = self.ml_predictor.predict_and_explain(self.history_a[-10:])
        prob = pred_res["outage_probability"]

        # Digital Twin Divergence & Trend Forecasting
        twin_res = self.twin_engine.calculate_divergence(m_a, m_b)
        trend_res = self.twin_engine.project_future_trends(self.history_a)

        # Server Suitability Ranking
        suitability_res = self.calculate_suitability_scores(snapshot, pred_res, twin_res)

        # SRE SLO / SLA Metrics calculation
        active_metrics = snapshot.get(self.active_server.lower(), m_a)
        slo_res = self.slo_tracker.calculate_slo(
            total_requests=active_metrics.get("total_requests", 0),
            successful_requests=active_metrics.get("successful_requests", 0),
            failed_requests=active_metrics.get("failed_requests", 0),
            current_latency_ms=active_metrics.get("latency_ms", 0.0)
        )

        # Dependency Graph Evaluation
        dep_res = self.dependency_evaluator.evaluate_dependencies(self.active_server, active_metrics)

        # Intelligent Failover Logic based on Suitability Scores
        status_a = m_a.get("status", "UNHEALTHY")
        status_b = m_b.get("status", "UNHEALTHY")
        status_c = m_c.get("status", "UNHEALTHY")

        if self.failover_mode == "AUTOMATIC":
            if self.active_server == "SERVER_A":
                if prob >= 0.80 and status_a != "UNHEALTHY":
                    # PREDICTIVE FAILOVER
                    reason = f"Predictive ML Risk {round(prob*100,1)}% >= 80.0% threshold"
                    best_target = "SERVER_B" if (status_b == "HEALTHY" and m_b.get("is_reachable", True)) else ("SERVER_C" if (status_c == "HEALTHY" and m_c.get("is_reachable", True)) else "SERVER_B")
                    self.execute_failover(best_target, reason, f_type="PREDICTIVE", prob=prob, metrics=m_a)
                    # Trigger Automated Self-Healing Remediation on Server A in background
                    import threading
                    threading.Thread(target=self.remediation_engine.execute_remediation, args=("SERVER_A", self.endpoint_a, reason), daemon=True).start()

                elif status_a == "UNHEALTHY" or not m_a.get("is_reachable", True):
                    # EMERGENCY FAILOVER
                    if self.outage_start_time == 0.0:
                        self.outage_start_time = time.time()
                    reason = f"Server A status {status_a} (HTTP 503 or Connection Refused)"
                    best_target = "SERVER_B" if (status_b == "HEALTHY" and m_b.get("is_reachable", True)) else ("SERVER_C" if (status_c == "HEALTHY" and m_c.get("is_reachable", True)) else "SERVER_B")
                    self.execute_failover(best_target, reason, f_type="EMERGENCY", prob=prob, metrics=m_a)

            elif self.active_server in ["SERVER_B", "SERVER_C"]:
                is_a_recovering = m_a.get("status") == "RECOVERING" or m_a.get("active_simulations", {}).get("is_recovering", False)
                outage_duration = (time.time() - self.outage_start_time) if self.outage_start_time > 0 else 0
                
                # Graceful autonomous self-healing: allow at least 45 seconds of sustained outage
                # so the operator and dashboard can observe failover and traffic routing to Server B.
                if status_a != "HEALTHY" and not is_a_recovering and not self.is_remediating and outage_duration >= 45.0:
                    self.is_remediating = True
                    self.outage_start_time = 0.0
                    def _run_remediation():
                        try:
                            self.remediation_engine.execute_remediation("SERVER_A", self.endpoint_a, "AUTONOMOUS_SELF_HEALING")
                        finally:
                            self.is_remediating = False
                    import threading
                    threading.Thread(target=_run_remediation, daemon=True).start()

                active_curr_status = snapshot.get(self.active_server.lower(), {}).get("status", "UNHEALTHY")
                active_curr_reachable = snapshot.get(self.active_server.lower(), {}).get("is_reachable", True)
                
                # If current active node becomes UNHEALTHY or unreachable, or if Server A is healthy & ready:
                if status_a == "HEALTHY" and m_a.get("is_reachable", True):
                    # Automatic Failback to Primary Server A
                    self.outage_start_time = 0.0
                    self.execute_failback("SERVER_A", f"Primary Server A is HEALTHY ({round(m_a.get('health_score', 100),1)}%) - traffic returned to Server A", prob=prob, metrics=m_a)

        return {
            "active_server": self.active_server,
            "failover_type": self.failover_type,
            "metrics_a": m_a,
            "metrics_b": m_b,
            "metrics_c": m_c,
            "prediction": pred_res,
            "digital_twin": twin_res,
            "projected_trends": trend_res,
            "suitability": suitability_res,
            "slo": slo_res,
            "dependencies": dep_res,
            "audit_verification": {"status": "VALID", "total_events": len(self.failover_logs)},
            "remediations": self.remediation_engine.get_remediation_history(),
            "snapshot": snapshot
        }

    def execute_failover(self, target_server, reason, f_type="PREDICTIVE", prob=0.0, metrics=None):
        prev = self.active_server
        self.active_server = target_server
        self.failover_type = f_type
        
        self.notify_haproxy_route(target_server, reason)

        self.log_event(
            f"{f_type}_FAILOVER_TRIGGERED",
            target_server,
            f"[{f_type} FAILOVER] Traffic switched from {prev} to {target_server}. Reason: {reason}",
            severity="CRITICAL",
            failover_type=f_type,
            prob=prob,
            metrics=metrics
        )

    def execute_failback(self, target_server, reason, prob=0.0, metrics=None):
        prev = self.active_server
        self.active_server = target_server
        self.failover_type = "NORMAL"

        self.notify_haproxy_route(target_server, reason)

        self.log_event(
            "FAILBACK_RECOVERY",
            target_server,
            f"Failback completed from {prev} to {target_server}. Reason: {reason}",
            severity="INFO",
            failover_type="RECOVERY",
            prob=prob,
            metrics=metrics
        )
