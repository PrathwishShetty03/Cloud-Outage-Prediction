import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autoscaling.config import AutoscalerConfig
from autoscaling.autoscaler import RuleBasedAutoscaler, InstanceSnapshot
from autoscaling.discovery import discover_instance_urls


def _inst(**kwargs):
    defaults = dict(
        instance_id="app-1",
        cpu_percent=20.0,
        memory_percent=25.0,
        latency_ms=40.0,
        request_rate=1.0,
        total_requests=10,
        healthy=True,
    )
    defaults.update(kwargs)
    return InstanceSnapshot(**defaults)


class TestRuleBasedAutoscaler(unittest.TestCase):
    def setUp(self):
        self.cfg = AutoscalerConfig(
            min_instances=1,
            max_instances=5,
            cooldown_seconds=30.0,
            hysteresis=0.30,
            cpu_high=75.0,
            cpu_low=40.0,
            memory_high=75.0,
            memory_low=40.0,
            latency_high_ms=800.0,
            latency_low_ms=200.0,
            request_rate_high=20.0,
            request_rate_low=5.0,
        )
        self.scaler = RuleBasedAutoscaler(self.cfg)

    def test_scale_up_on_high_cpu(self):
        inst = _inst(cpu_percent=90.0)
        decision = self.scaler.evaluate([inst], replica_count=1, now=1000.0)
        self.assertEqual(decision.action, "scale_up")
        self.assertEqual(decision.desired_instances, 2)
        self.assertIn("cpu", decision.reason.lower())

    def test_scale_up_on_high_memory(self):
        decision = self.scaler.evaluate([_inst(memory_percent=88.0)], replica_count=2, now=1000.0)
        self.assertEqual(decision.action, "scale_up")
        self.assertEqual(decision.desired_instances, 3)

    def test_scale_up_on_high_latency(self):
        decision = self.scaler.evaluate([_inst(latency_ms=1200.0)], replica_count=1, now=1000.0)
        self.assertEqual(decision.action, "scale_up")

    def test_scale_up_on_high_request_rate(self):
        decision = self.scaler.evaluate([_inst(request_rate=40.0)], replica_count=1, now=1000.0)
        self.assertEqual(decision.action, "scale_up")

    def test_scale_up_uses_active_instance_count(self):
        decision = self.scaler.evaluate(
            [_inst(cpu_percent=90.0), _inst(instance_id="app-2", cpu_percent=91.0)],
            replica_count=2,
            now=1000.0,
        )
        self.assertEqual(decision.current_instances, 2)
        self.assertEqual(decision.desired_instances, 3)

    def test_hysteresis_deadband_holds(self):
        inst = _inst(cpu_percent=55.0, memory_percent=50.0, latency_ms=300.0, request_rate=8.0)
        decision = self.scaler.evaluate([inst], replica_count=2, now=1000.0)
        self.assertEqual(decision.action, "hold")
        self.assertEqual(decision.desired_instances, 2)

    def test_scale_down_only_when_all_signals_low(self):
        low = _inst(cpu_percent=10.0, memory_percent=12.0, latency_ms=30.0, request_rate=0.5)
        decision = self.scaler.evaluate([low, _inst(instance_id="app-2", cpu_percent=11.0, memory_percent=10.0, latency_ms=20.0, request_rate=0.2)], replica_count=2, now=1000.0)
        self.assertEqual(decision.action, "scale_down")
        self.assertEqual(decision.desired_instances, 1)

    def test_cooldown_blocks_oscillation(self):
        high = _inst(cpu_percent=90.0)
        first = self.scaler.evaluate([high], replica_count=1, now=1000.0)
        self.assertEqual(first.action, "scale_up")
        second = self.scaler.evaluate([high], replica_count=1, now=1010.0)
        self.assertEqual(second.action, "hold")
        self.assertTrue(second.in_cooldown)
        third = self.scaler.evaluate([high], replica_count=1, now=1040.0)
        self.assertEqual(third.action, "scale_up")

    def test_respects_max_instances(self):
        decision = self.scaler.evaluate([_inst(cpu_percent=99.0)], replica_count=5, now=1000.0)
        self.assertEqual(decision.action, "hold")
        self.assertEqual(decision.desired_instances, 5)
        self.assertIn("max_instances", decision.reason)

    def test_respects_min_instances(self):
        low = _inst(cpu_percent=5.0, memory_percent=5.0, latency_ms=10.0, request_rate=0.1)
        decision = self.scaler.evaluate([low], replica_count=1, now=1000.0)
        self.assertEqual(decision.action, "hold")
        self.assertEqual(decision.desired_instances, 1)

    def test_scale_up_when_below_min(self):
        decision = self.scaler.evaluate([], replica_count=0, now=1000.0)
        self.assertEqual(decision.action, "scale_up")
        self.assertEqual(decision.desired_instances, 1)

    def test_unhealthy_instances_trigger_scale_up(self):
        bad = _inst(healthy=False, cpu_percent=20.0)
        decision = self.scaler.evaluate([bad], replica_count=1, now=1000.0)
        self.assertEqual(decision.action, "scale_up")

    def test_config_clamps_max_above_min(self):
        cfg = AutoscalerConfig(min_instances=3, max_instances=2)
        self.assertEqual(cfg.min_instances, 3)
        self.assertEqual(cfg.max_instances, 3)

    def test_request_rate_delta(self):
        a = _inst(instance_id="x", total_requests=100, request_rate=0.0)
        self.scaler.compute_request_rates([a], now=10.0)
        b = _inst(instance_id="x", total_requests=130, request_rate=0.0)
        self.scaler.compute_request_rates([b], now=20.0)
        self.assertEqual(b.request_rate, 3.0)

    def test_discover_instance_urls_dedupes_extras(self):
        urls = discover_instance_urls("", 5001, ["http://localhost:5010", "http://localhost:5010/"])
        self.assertEqual(urls, ["http://localhost:5010"])

    def test_cooldown_preserved_across_restart(self):
        # Simulates process restart where _last_scale_ts is restored from persisted state
        scaler_pre = RuleBasedAutoscaler(self.cfg)
        decision_1 = scaler_pre.evaluate([_inst(cpu_percent=90.0)], replica_count=1, now=1000.0)
        self.assertEqual(decision_1.action, "scale_up")
        saved_scale_ts = scaler_pre._last_scale_ts

        # Create fresh scaler instance (simulating restart) and restore persisted timestamp
        scaler_post = RuleBasedAutoscaler(self.cfg)
        scaler_post._last_scale_ts = saved_scale_ts

        # Check that cooldown is still active 10 seconds later (cooldown is 30s)
        decision_2 = scaler_post.evaluate([_inst(cpu_percent=90.0)], replica_count=2, now=1010.0)
        self.assertEqual(decision_2.action, "hold")
        self.assertTrue(decision_2.in_cooldown)

        # Check that scaling unlocks once cooldown period expires
        decision_3 = scaler_post.evaluate([_inst(cpu_percent=90.0)], replica_count=2, now=1040.0)
        self.assertEqual(decision_3.action, "scale_up")


if __name__ == "__main__":
    unittest.main()
