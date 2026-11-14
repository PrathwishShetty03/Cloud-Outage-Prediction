import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from remediation.remediation_engine import SelfHealingRemediationEngine
from monitoring.slo_tracker import SLOTracker
from failover.failover_controller import AutomatedFailoverController

class TestAuditRemediationSLO(unittest.TestCase):
    def test_remediation_engine(self):
        engine = SelfHealingRemediationEngine()
        history = engine.get_remediation_history()
        self.assertIsInstance(history, list)

    def test_slo_tracker(self):
        tracker = SLOTracker(availability_target=99.9, latency_target_ms=300.0)
        slo = tracker.calculate_slo(total_requests=1000, successful_requests=999, failed_requests=1, current_latency_ms=120.0)
        self.assertEqual(slo["availability_pct"], 99.9)
        self.assertEqual(slo["slo_status"], "PASSING")
        self.assertGreaterEqual(slo["error_budget_remaining_pct"], 0.0)

    def test_suitability_scores(self):
        controller = AutomatedFailoverController()
        snapshot = {
            "server_a": {"server_id": "SERVER_A", "health_score": 40.0, "cpu_percent": 85.0, "memory_percent": 90.0, "latency_ms": 2500.0, "status": "UNHEALTHY", "is_reachable": True},
            "server_b": {"server_id": "SERVER_B", "health_score": 95.0, "cpu_percent": 25.0, "memory_percent": 30.0, "latency_ms": 45.0, "status": "HEALTHY", "is_reachable": True},
            "server_c": {"server_id": "SERVER_C", "health_score": 88.0, "cpu_percent": 30.0, "memory_percent": 35.0, "latency_ms": 60.0, "status": "HEALTHY", "is_reachable": True}
        }
        prediction = {"outage_probability": 0.85}
        twin_res = {"divergence_score": 5.0}

        scores = controller.calculate_suitability_scores(snapshot, prediction, twin_res)
        self.assertGreater(scores["SERVER_B"]["suitability_score"], scores["SERVER_A"]["suitability_score"])
        self.assertGreaterEqual(scores["SERVER_B"]["suitability_score"], scores["SERVER_C"]["suitability_score"])

if __name__ == '__main__':
    unittest.main()
