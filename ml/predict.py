import os
import json
import pickle
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
SEQUENCE_LENGTH = 10
FEATURE_NAMES = ['cpu_percent', 'memory_percent', 'disk_percent', 'latency_ms', 'error_rate']

class OutagePredictor:
    """
    Unified Inference Engine for Outage Risk Prediction.
    Supports dual model evaluation: PyTorch/Keras LSTM Time-Series Model and Random Forest Baseline.
    """
    def __init__(self):
        self.scaler = None
        self.rf_model = None
        self.lstm_model = None
        self.metrics_data = {}
        self.load_models()

    def load_models(self):
        scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
        rf_path = os.path.join(MODEL_DIR, 'rf_model.pkl')
        lstm_path = os.path.join(MODEL_DIR, 'lstm_model.keras')
        metrics_path = os.path.join(MODEL_DIR, 'metrics.json')

        if not (os.path.exists(scaler_path) and os.path.exists(rf_path)):
            from ml.train_lstm import train_and_save
            train_and_save()

        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

        if os.path.exists(rf_path):
            with open(rf_path, 'rb') as f:
                self.rf_model = pickle.load(f)

        if os.path.exists(lstm_path):
            try:
                import keras
                self.lstm_model = keras.models.load_model(lstm_path)
            except Exception as e:
                print(f"[ML WARNING] Could not load LSTM model: {e}")
                self.lstm_model = None

        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r') as f:
                    self.metrics_data = json.load(f)
            except Exception:
                self.metrics_data = {}

    def predict_outage_probability(self, metrics_sequence, model_type="LSTM"):
        """
        Calculates outage probability (0.0 to 1.0) given recent metrics sequence.
        model_type can be 'LSTM' or 'RANDOM_FOREST'.
        """
        if not metrics_sequence:
            return 0.05

        # Format to sequence of length 10
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
        if self.scaler is None:
            self.load_models()

        scaled_arr = self.scaler.transform(arr)

        prob = 0.05
        use_rf = (model_type.upper() == "RANDOM_FOREST" or self.lstm_model is None)

        if not use_rf and self.lstm_model is not None:
            try:
                seq_input = scaled_arr.reshape(1, SEQUENCE_LENGTH, len(FEATURE_NAMES))
                raw_p = float(self.lstm_model.predict(seq_input, verbose=0)[0][0])
                prob = raw_p
            except Exception as e:
                use_rf = True

        if use_rf and self.rf_model:
            flat_scaled = scaled_arr.reshape(1, -1)
            prob = float(self.rf_model.predict_proba(flat_scaled)[0][1])

        # Edge-case safety checks for extreme stress testing
        latest = metrics_sequence[-1]
        cpu = latest.get('cpu_percent', latest.get('cpu', 0.0))
        mem = latest.get('memory_percent', latest.get('memory', 0.0))
        lat = latest.get('latency_ms', latest.get('latency', 0.0))
        err = latest.get('error_rate', 0.0)

        if latest.get('is_outage', False) or cpu >= 90.0 or mem >= 90.0 or lat >= 4000.0 or err >= 0.25:
            prob = max(prob, 0.95)
        elif cpu >= 75.0 or mem >= 75.0 or lat >= 1500.0 or err >= 0.10:
            prob = max(prob, 0.82)

        return round(float(prob), 4)

    def get_dual_prediction(self, metrics_sequence):
        """
        Returns predictions from both LSTM and Random Forest models for comparative analysis.
        """
        p_lstm = self.predict_outage_probability(metrics_sequence, model_type="LSTM")
        p_rf = self.predict_outage_probability(metrics_sequence, model_type="RANDOM_FOREST")
        return {
            "lstm_probability": p_lstm,
            "rf_probability": p_rf,
            "selected_model": "LSTM" if self.lstm_model else "RANDOM_FOREST"
        }

    def get_evaluation_metrics(self):
        return self.metrics_data

def predict_from_sequence(sequence):
    predictor = OutagePredictor()
    return predictor.predict_outage_probability(sequence)
