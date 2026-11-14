import math

class DigitalTwinEngine:
    """
    Real-time Digital Twin synchronization, divergence evaluation,
    trend forecasting, and What-If simulation engine between Primary Server A
    and Digital Twin Backup Server B.
    """
    def __init__(self, divergence_threshold=15.0):
        self.divergence_threshold = divergence_threshold

    def calculate_divergence(self, metrics_a, metrics_b):
        """
        Calculates exact metric divergence percentages and total divergence score.
        metrics_a and metrics_b are dictionaries returned from /api/metrics or /health.
        """
        if not metrics_a or not metrics_b:
            return {
                "divergence_score": 0.0,
                "sync_status": "UNKNOWN",
                "cpu_delta": 0.0,
                "memory_delta": 0.0,
                "disk_delta": 0.0,
                "latency_delta_ms": 0.0,
                "error_rate_delta": 0.0,
                "request_delta": 0,
                "state_match": True,
                "server_a_status": "UNKNOWN",
                "server_b_status": "UNKNOWN"
            }

        cpu_a = float(metrics_a.get("cpu_percent", metrics_a.get("cpu", 0.0)))
        cpu_b = float(metrics_b.get("cpu_percent", metrics_b.get("cpu", 0.0)))
        cpu_delta = abs(cpu_a - cpu_b)

        mem_a = float(metrics_a.get("memory_percent", metrics_a.get("memory", 0.0)))
        mem_b = float(metrics_b.get("memory_percent", metrics_b.get("memory", 0.0)))
        mem_delta = abs(mem_a - mem_b)

        disk_a = float(metrics_a.get("disk_percent", metrics_a.get("disk", 0.0)))
        disk_b = float(metrics_b.get("disk_percent", metrics_b.get("disk", 0.0)))
        disk_delta = abs(disk_a - disk_b)

        lat_a = float(metrics_a.get("latency_ms", metrics_a.get("latency", 0.0)))
        lat_b = float(metrics_b.get("latency_ms", metrics_b.get("latency", 0.0)))
        lat_delta_ms = abs(lat_a - lat_b)
        lat_delta_normalized = min(100.0, (lat_delta_ms / 2000.0) * 100.0)

        err_a = float(metrics_a.get("error_rate", 0.0))
        err_b = float(metrics_b.get("error_rate", 0.0))
        err_delta = abs(err_a - err_b) * 100.0

        status_a = metrics_a.get("status", "HEALTHY")
        status_b = metrics_b.get("status", "HEALTHY")
        state_match = (status_a == status_b)
        state_penalty = 0.0 if state_match else 35.0

        req_a = int(metrics_a.get("total_requests", 0))
        req_b = int(metrics_b.get("total_requests", 0))
        req_delta = abs(req_a - req_b)

        # Weighted Divergence Score Formula
        weighted_score = (
            (0.25 * cpu_delta) +
            (0.25 * mem_delta) +
            (0.10 * disk_delta) +
            (0.20 * lat_delta_normalized) +
            (0.20 * err_delta) +
            state_penalty
        )

        divergence_score = round(max(0.0, min(100.0, weighted_score)), 2)
        sync_status = "SYNCHRONIZED" if divergence_score < self.divergence_threshold else "DIVERGING"

        return {
            "divergence_score": divergence_score,
            "sync_status": sync_status,
            "cpu_delta": round(cpu_delta, 2),
            "memory_delta": round(mem_delta, 2),
            "disk_delta": round(disk_delta, 2),
            "latency_delta_ms": round(lat_delta_ms, 2),
            "error_rate_delta": round(err_delta, 4),
            "request_delta": req_delta,
            "state_match": state_match,
            "server_a_status": status_a,
            "server_b_status": status_b
        }

    def project_future_trends(self, history_a, horizons_sec=[10, 20, 30]):
        """
        Projects telemetry metric trends into future horizons (+10s, +20s, +30s)
        using metric slope calculation across recent sliding history.
        """
        if not history_a or len(history_a) < 2:
            current_mem = float(history_a[-1].get("memory_percent", 30.0)) if history_a else 30.0
            current_cpu = float(history_a[-1].get("cpu_percent", 20.0)) if history_a else 20.0
            return {
                "growth_rate_mem_per_sec": 0.0,
                "growth_rate_cpu_per_sec": 0.0,
                "projected_memory": {h: round(current_mem, 1) for h in horizons_sec},
                "projected_cpu": {h: round(current_cpu, 1) for h in horizons_sec},
                "predicted_risk_in_30s": "LOW"
            }

        n = len(history_a)
        m_start = history_a[0]
        m_end = history_a[-1]

        cpu_start = float(m_start.get("cpu_percent", m_start.get("cpu", 0.0)))
        cpu_end = float(m_end.get("cpu_percent", m_end.get("cpu", 0.0)))

        mem_start = float(m_start.get("memory_percent", m_start.get("memory", 0.0)))
        mem_end = float(m_end.get("memory_percent", m_end.get("memory", 0.0)))

        # Simple linear rate per step / approx second
        cpu_rate = (cpu_end - cpu_start) / max(1, n - 1)
        mem_rate = (mem_end - mem_start) / max(1, n - 1)

        projected_cpu = {}
        projected_mem = {}

        for h in horizons_sec:
            projected_cpu[h] = round(max(0.0, min(100.0, cpu_end + (cpu_rate * (h / 2.0)))), 1)
            projected_mem[h] = round(max(0.0, min(100.0, mem_end + (mem_rate * (h / 2.0)))), 1)

        max_projected_mem = projected_mem[horizons_sec[-1]]
        max_projected_cpu = projected_cpu[horizons_sec[-1]]

        if max_projected_mem >= 90.0 or max_projected_cpu >= 90.0:
            risk_30s = "CRITICAL"
        elif max_projected_mem >= 75.0 or max_projected_cpu >= 75.0:
            risk_30s = "HIGH"
        elif max_projected_mem >= 60.0 or max_projected_cpu >= 60.0:
            risk_30s = "MEDIUM"
        else:
            risk_30s = "LOW"

        return {
            "growth_rate_mem_per_sec": round(mem_rate, 2),
            "growth_rate_cpu_per_sec": round(cpu_rate, 2),
            "projected_memory": projected_mem,
            "projected_cpu": projected_cpu,
            "predicted_risk_in_30s": risk_30s
        }

    def simulate_what_if(self, base_metrics, cpu_delta=0.0, memory_delta=0.0, latency_delta=0.0, error_delta=0.0, predictor=None):
        """
        Executes a transparent What-If simulation given metric offsets.
        Calculates simulated metrics, simulated outage probability, and twin divergence.
        """
        if not base_metrics:
            base_metrics = {"cpu_percent": 20.0, "memory_percent": 30.0, "disk_percent": 40.0, "latency_ms": 50.0, "error_rate": 0.0}

        sim_cpu = max(0.0, min(100.0, float(base_metrics.get("cpu_percent", base_metrics.get("cpu", 20.0))) + cpu_delta))
        sim_mem = max(0.0, min(100.0, float(base_metrics.get("memory_percent", base_metrics.get("memory", 30.0))) + memory_delta))
        sim_disk = float(base_metrics.get("disk_percent", base_metrics.get("disk", 40.0)))
        sim_lat = max(0.0, float(base_metrics.get("latency_ms", base_metrics.get("latency", 50.0))) + latency_delta)
        sim_err = max(0.0, min(1.0, float(base_metrics.get("error_rate", 0.0)) + error_delta))

        sim_metrics = {
            "cpu_percent": sim_cpu,
            "memory_percent": sim_mem,
            "disk_percent": sim_disk,
            "latency_ms": sim_lat,
            "error_rate": sim_err,
            "status": "UNHEALTHY" if (sim_cpu > 92 or sim_mem > 92 or sim_lat > 4000 or sim_err > 0.25) else "HEALTHY"
        }

        sim_seq = [sim_metrics] * 10
        if predictor:
            sim_prob = predictor.predict_outage_probability(sim_seq)
        else:
            # Model-based transparent calculation fallback
            c_norm = sim_cpu / 100.0
            m_norm = sim_mem / 100.0
            l_norm = min(1.0, sim_lat / 3000.0)
            e_norm = min(1.0, sim_err / 0.30)
            sim_prob = round(min(0.99, max(0.05, (0.3 * c_norm) + (0.3 * m_norm) + (0.2 * l_norm) + (0.2 * e_norm))), 4)

        sim_risk = "CRITICAL" if sim_prob >= 0.80 else ("HIGH" if sim_prob >= 0.70 else ("MEDIUM" if sim_prob >= 0.50 else "LOW"))

        div_res = self.calculate_divergence(sim_metrics, base_metrics)

        return {
            "simulated_metrics": sim_metrics,
            "simulated_outage_probability": sim_prob,
            "simulated_outage_probability_pct": round(sim_prob * 100.0, 1),
            "simulated_risk_level": sim_risk,
            "simulated_divergence_score": div_res["divergence_score"],
            "simulated_sync_status": div_res["sync_status"]
        }
