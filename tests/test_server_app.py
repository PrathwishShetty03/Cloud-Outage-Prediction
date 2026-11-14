import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server_app.server_app import app

class TestServerApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'HEALTHY')
        self.assertIn('health_score', data)
        self.assertIn('cpu', data)
        self.assertIn('memory', data)
        self.assertIn('X-Served-By', response.headers)

    def test_api_metrics_endpoint(self):
        response = self.client.get('/api/metrics')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('cpu_percent', data)
        self.assertIn('memory_percent', data)
        self.assertIn('latency_ms', data)
        self.assertIn('error_rate', data)

    def test_stress_and_recover(self):
        r1 = self.client.post('/stress/latency', json={'seconds': 1.0})
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.get_json()['latency_seconds'], 1.0)

        r2 = self.client.post('/simulate/recover')
        self.assertEqual(r2.status_code, 200)
        self.assertIn(r2.get_json()['status'], ['RECOVERING', 'RECOVERED_HEALTHY'])

if __name__ == '__main__':
    unittest.main()
