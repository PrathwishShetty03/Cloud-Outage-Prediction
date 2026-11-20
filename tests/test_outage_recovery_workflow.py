"""
Test Suite: Outage Simulation, Staged Autonomous Recovery, and Dynamic Failover Workflow
========================================================================================
Validates:
1. Normal Operation (Server A Healthy, HTTP 200)
2. Outage Simulation (Server A Down, HTTP 503)
3. Autonomous Staged Recovery:
   - Stage 1: Outage Detection & Isolation
   - Stage 2: Automated Root-Cause Diagnostics
   - Stage 3: Microservice Service Restart
   - Stage 4: Self-Healing Health Verification
4. Server A health check genuinely returns 503 during all recovery stages to enforce failover
5. Server A fully recovers (elapsed >= duration), returning to HEALTHY with HTTP 200 OK
"""

import unittest
import time
from server_app.server_app import app, simulation_state, _execute_node_recovery, get_recovery_stage_details

class TestOutageRecoveryWorkflow(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        simulation_state["is_outage"] = False
        simulation_state["is_recovering"] = False
        simulation_state["recovery_start_time"] = 0.0
        simulation_state["cpu_active"] = False
        simulation_state["ram_allocated"].clear()
        simulation_state["latency_seconds"] = 0.0
        simulation_state["error_rate"] = 0.0
        time.sleep(0.1)

    def test_normal_operation(self):
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get("status"), "HEALTHY")

    def test_outage_trigger_returns_503(self):
        res_outage = self.client.post('/simulate/outage', json={"auto_recover": False})
        self.assertEqual(res_outage.status_code, 200)
        self.assertTrue(simulation_state["is_outage"])

        res_h = self.client.get('/health')
        self.assertEqual(res_h.status_code, 503)
        self.assertEqual(res_h.json.get("status"), "UNHEALTHY")

    def test_staged_recovery_details(self):
        dur = 20.0
        # Stage 1: 0% to 25% (2.0s)
        stg1 = get_recovery_stage_details(2.0, dur)
        self.assertEqual(stg1["stage"], "OUTAGE_DETECTION")
        self.assertEqual(stg1["stage_index"], 1)

        # Stage 2: 25% to 50% (7.0s)
        stg2 = get_recovery_stage_details(7.0, dur)
        self.assertEqual(stg2["stage"], "DIAGNOSTICS")
        self.assertEqual(stg2["stage_index"], 2)

        # Stage 3: 50% to 75% (12.0s)
        stg3 = get_recovery_stage_details(12.0, dur)
        self.assertEqual(stg3["stage"], "SERVICE_RESTART")
        self.assertEqual(stg3["stage_index"], 3)

        # Stage 4: 75% to 100% (17.0s)
        stg4 = get_recovery_stage_details(17.0, dur)
        self.assertEqual(stg4["stage"], "HEALTH_VERIFICATION")
        self.assertEqual(stg4["stage_index"], 4)

    def test_health_check_returns_503_during_recovery(self):
        # Trigger fast recovery for testing (duration = 0.4s)
        _execute_node_recovery(dur=0.4)
        self.assertTrue(simulation_state["is_recovering"])

        res_h = self.client.get('/health')
        self.assertEqual(res_h.status_code, 503)
        self.assertEqual(res_h.json.get("status"), "RECOVERING")
        self.assertIn("recovery_stage", res_h.json)

        # User requests during recovery must also be safely blocked with 503
        res_prod = self.client.get('/api/products')
        self.assertEqual(res_prod.status_code, 503)

        # Wait for recovery background thread to complete
        for _ in range(30):
            if not simulation_state["is_recovering"]:
                break
            time.sleep(0.05)
        self.assertFalse(simulation_state["is_recovering"])
        self.assertFalse(simulation_state["is_outage"])

        # After recovery finishes, health check must return HTTP 200 OK
        res_after = self.client.get('/health')
        self.assertEqual(res_after.status_code, 200)
        self.assertEqual(res_after.json.get("status"), "HEALTHY")

if __name__ == "__main__":
    unittest.main()
