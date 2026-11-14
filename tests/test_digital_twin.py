import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from digital_twin.twin_engine import DigitalTwinEngine

class TestDigitalTwin(unittest.TestCase):
    def test_twin_divergence(self):
        engine = DigitalTwinEngine(divergence_threshold=15.0)
        m_a = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0, 'latency_ms': 50.0, 'error_rate': 0.01, 'status': 'HEALTHY'}
        m_b = {'cpu_percent': 32.0, 'memory_percent': 41.0, 'disk_percent': 50.0, 'latency_ms': 55.0, 'error_rate': 0.01, 'status': 'HEALTHY'}
        
        div = engine.calculate_divergence(m_a, m_b)
        self.assertEqual(div['sync_status'], 'SYNCHRONIZED')
        self.assertLess(div['divergence_score'], 15.0)

        m_b_degraded = {'cpu_percent': 90.0, 'memory_percent': 95.0, 'disk_percent': 50.0, 'latency_ms': 2500.0, 'error_rate': 0.20, 'status': 'UNHEALTHY'}
        div_bad = engine.calculate_divergence(m_a, m_b_degraded)
        self.assertEqual(div_bad['sync_status'], 'DIVERGING')
        self.assertGreaterEqual(div_bad['divergence_score'], 15.0)

    def test_twin_trend_forecasting(self):
        engine = DigitalTwinEngine()
        history = [
            {'cpu_percent': 30.0, 'memory_percent': 40.0},
            {'cpu_percent': 40.0, 'memory_percent': 50.0},
            {'cpu_percent': 50.0, 'memory_percent': 60.0},
            {'cpu_percent': 60.0, 'memory_percent': 70.0},
            {'cpu_percent': 70.0, 'memory_percent': 80.0}
        ]
        trends = engine.project_future_trends(history, horizons_sec=[10, 20, 30])
        self.assertIn(30, trends['projected_memory'])
        self.assertIn(trends['predicted_risk_in_30s'], ['HIGH', 'CRITICAL'])

    def test_twin_what_if_simulator(self):
        engine = DigitalTwinEngine()
        base = {'cpu_percent': 20.0, 'memory_percent': 30.0, 'disk_percent': 40.0, 'latency_ms': 50.0, 'error_rate': 0.0}
        sim = engine.simulate_what_if(base, cpu_delta=40.0, memory_delta=45.0, latency_delta=1000.0, error_delta=0.10)
        self.assertEqual(sim['simulated_metrics']['cpu_percent'], 60.0)
        self.assertGreater(sim['simulated_outage_probability_pct'], 10.0)

if __name__ == '__main__':
    unittest.main()
