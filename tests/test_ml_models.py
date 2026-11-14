import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml.predict import OutagePredictor
from ml.ml_engine import OutagePredictorML
from ml.shap_explain import SHAPExplainer

class TestMLModels(unittest.TestCase):
    def test_ml_prediction(self):
        predictor = OutagePredictor()
        seq_healthy = [{'cpu_percent': 20.0, 'memory_percent': 30.0, 'disk_percent': 40.0, 'latency_ms': 50.0, 'error_rate': 0.0}] * 10
        prob_healthy = predictor.predict_outage_probability(seq_healthy, model_type="LSTM")
        self.assertTrue(0.0 <= prob_healthy <= 0.50)

        seq_outage = [{'cpu_percent': 95.0, 'memory_percent': 98.0, 'disk_percent': 90.0, 'latency_ms': 4500.0, 'error_rate': 0.35}] * 10
        prob_outage = predictor.predict_outage_probability(seq_outage, model_type="LSTM")
        self.assertGreaterEqual(prob_outage, 0.80)

    def test_ml_engine_predict_and_explain(self):
        ml_engine = OutagePredictorML()
        seq = [{'cpu_percent': 85.0, 'memory_percent': 90.0, 'disk_percent': 50.0, 'latency_ms': 1200.0, 'error_rate': 0.15}] * 10
        res = ml_engine.predict_and_explain(seq)
        self.assertIn('outage_probability', res)
        self.assertIn('risk_level', res)
        self.assertIn('shap_contributions', res)
        self.assertIn('top_influential_feature', res)

    def test_shap_explainer(self):
        explainer = SHAPExplainer()
        seq = [{'cpu_percent': 50.0, 'memory_percent': 60.0, 'disk_percent': 40.0, 'latency_ms': 200.0, 'error_rate': 0.02}] * 10
        res = explainer.explain_prediction(seq)
        self.assertIn('contributions', res)
        self.assertIn('top_feature', res)
        self.assertEqual(len(res['contributions']), 5)

if __name__ == '__main__':
    unittest.main()
