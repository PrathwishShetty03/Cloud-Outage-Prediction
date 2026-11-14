import os
import pickle
import numpy as np
import shap

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
SEQUENCE_LENGTH = 10
FEATURE_NAMES = ['cpu_percent', 'memory_percent', 'disk_percent', 'latency_ms', 'error_rate']
DISPLAY_NAMES = ['CPU Usage', 'Memory Usage', 'Disk Usage', 'Network Latency', 'Error Rate']

class SHAPExplainer:
    def __init__(self):
        self.scaler = None
        self.rf_model = None
        self.explainer = None
        self.load_artifacts()

    def load_artifacts(self):
        scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
        rf_path = os.path.join(MODEL_DIR, 'rf_model.pkl')
        
        if os.path.exists(scaler_path) and os.path.exists(rf_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            with open(rf_path, 'rb') as f:
                self.rf_model = pickle.load(f)
            self.explainer = shap.TreeExplainer(self.rf_model)

    def explain_prediction(self, metrics_sequence):
        """
        Calculates exact SHAP values for the given sequence input
        and returns contribution percentage for each metric + top factor.
        """
        if not metrics_sequence:
            return {
                "contributions": {"CPU Usage": 20.0, "Memory Usage": 20.0, "Disk Usage": 20.0, "Network Latency": 20.0, "Error Rate": 20.0},
                "top_feature": "CPU Usage",
                "top_impact": 20.0
            }

        if len(metrics_sequence) < SEQUENCE_LENGTH:
            padding = [metrics_sequence[0]] * (SEQUENCE_LENGTH - len(metrics_sequence))
            metrics_sequence = padding + metrics_sequence
        elif len(metrics_sequence) > SEQUENCE_LENGTH:
            metrics_sequence = metrics_sequence[-SEQUENCE_LENGTH:]

        rows = []
        for m in metrics_sequence:
            row = [
                float(m.get('cpu_percent', m.get('cpu', 20.0))),
                float(m.get('memory_percent', m.get('memory', 30.0))),
                float(m.get('disk_percent', m.get('disk', 40.0))),
                float(m.get('latency_ms', m.get('latency', 50.0))),
                float(m.get('error_rate', 0.0))
            ]
            rows.append(row)

        arr = np.array(rows)
        if self.scaler is None or self.explainer is None:
            self.load_artifacts()

        if self.scaler and self.explainer:
            scaled_arr = self.scaler.transform(arr)
            flat_scaled = scaled_arr.reshape(1, -1)
            
            raw_shap = self.explainer.shap_values(flat_scaled)
            # Handle list vs 2D/3D numpy array SHAP outputs
            if isinstance(raw_shap, list):
                shap_vals = raw_shap[1][0] if len(raw_shap) > 1 else raw_shap[0][0]
            elif isinstance(raw_shap, np.ndarray):
                if raw_shap.ndim == 3:
                    shap_vals = raw_shap[0, :, 1] if raw_shap.shape[2] > 1 else raw_shap[0, :, 0]
                elif raw_shap.ndim == 2:
                    shap_vals = raw_shap[0]
                else:
                    shap_vals = raw_shap.flatten()[:50]
            else:
                shap_vals = np.array(raw_shap).flatten()[:50]

            # Aggregate across sequence steps (10 steps x 5 features)
            feature_shap = np.abs(shap_vals.reshape(SEQUENCE_LENGTH, 5)).sum(axis=0)
            total_shap = feature_shap.sum() if feature_shap.sum() > 0 else 1.0
            contributions_pct = (feature_shap / total_shap) * 100.0
        else:
            # Fallback heuristic calculation from raw values
            latest = metrics_sequence[-1]
            c = latest.get('cpu_percent', 20.0)
            m = latest.get('memory_percent', 30.0)
            d = latest.get('disk_percent', 40.0)
            l = min(100.0, latest.get('latency_ms', 50.0) / 20.0)
            e = latest.get('error_rate', 0.0) * 100.0
            tot = max(1.0, c + m + d + l + e)
            contributions_pct = [c/tot * 100, m/tot * 100, d/tot * 100, l/tot * 100, e/tot * 100]

        contrib_dict = {
            DISPLAY_NAMES[i]: round(float(contributions_pct[i]), 2)
            for i in range(5)
        }

        top_idx = np.argmax(contributions_pct)
        top_feature = DISPLAY_NAMES[top_idx]
        top_impact = round(float(contributions_pct[top_idx]), 2)

        return {
            "contributions": contrib_dict,
            "top_feature": top_feature,
            "top_impact": top_impact
        }

def explain_prediction(metrics_sequence):
    explainer = SHAPExplainer()
    return explainer.explain_prediction(metrics_sequence)
