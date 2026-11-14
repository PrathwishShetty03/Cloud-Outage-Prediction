import time
import requests

class DependencyGraphEvaluator:
    """
    Lightweight Dependency Health Graph Evaluator.
    Distinguishes server infrastructure failures from downstream dependency degradations:
    Server A -> [Database, Redis Cache, External Payment API].
    """
    def __init__(self):
        self.dependencies = {
            "SERVER_A": [
                {"name": "PostgreSQL Database", "type": "DATABASE", "status": "HEALTHY", "latency_ms": 12.0},
                {"name": "Redis Cache", "type": "CACHE", "status": "HEALTHY", "latency_ms": 2.5},
                {"name": "External Payment Gateway API", "type": "EXTERNAL_API", "status": "HEALTHY", "latency_ms": 45.0}
            ],
            "SERVER_B": [
                {"name": "PostgreSQL Database (Replica)", "type": "DATABASE", "status": "HEALTHY", "latency_ms": 14.0},
                {"name": "Redis Cache (Standby)", "type": "CACHE", "status": "HEALTHY", "latency_ms": 3.0},
                {"name": "External Payment Gateway API", "type": "EXTERNAL_API", "status": "HEALTHY", "latency_ms": 46.0}
            ],
            "SERVER_C": [
                {"name": "PostgreSQL Database (Emergency)", "type": "DATABASE", "status": "HEALTHY", "latency_ms": 18.0},
                {"name": "Redis Cache (Emergency)", "type": "CACHE", "status": "HEALTHY", "latency_ms": 4.0},
                {"name": "External Payment Gateway API", "type": "EXTERNAL_API", "status": "HEALTHY", "latency_ms": 50.0}
            ]
        }

    def evaluate_dependencies(self, server_id, server_metrics):
        """
        Evaluates dependency health against server metrics.
        Returns dependency health summary and identified root cause.
        """
        deps = self.dependencies.get(server_id, [])
        lat = float(server_metrics.get("latency_ms", server_metrics.get("latency", 0.0)))
        err = float(server_metrics.get("error_rate", 0.0))
        cpu = float(server_metrics.get("cpu_percent", server_metrics.get("cpu", 0.0)))
        mem = float(server_metrics.get("memory_percent", server_metrics.get("memory", 0.0)))

        dep_status = "HEALTHY"
        primary_root_cause = "INFRASTRUCTURE_HEALTHY"

        if lat > 1500.0 and cpu < 70.0 and mem < 70.0:
            dep_status = "DEGRADED"
            primary_root_cause = "Database Query Latency Bottleneck"
            deps[0]["status"] = "DEGRADED"
            deps[0]["latency_ms"] = lat * 0.8
        elif err > 0.15 and cpu < 70.0:
            dep_status = "DEGRADED"
            primary_root_cause = "External API Gateway Timeout / Error Rate Surge"
            deps[2]["status"] = "DEGRADED"
            deps[2]["latency_ms"] = 850.0
        elif cpu >= 85.0:
            primary_root_cause = "Local CPU Saturation"
            dep_status = "HEALTHY"
        elif mem >= 85.0:
            primary_root_cause = "Local RAM Exhaustion"
            dep_status = "HEALTHY"

        return {
            "server_id": server_id,
            "dependency_status": dep_status,
            "suspected_root_cause": primary_root_cause,
            "dependencies": deps
        }
