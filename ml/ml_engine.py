import os
from ml.predict import OutagePredictor
from ml.shap_explain import SHAPExplainer

class OutagePredictorML:
    """
    Unified ML Outage Prediction and SHAP Explainability Engine.
    Exposes dual model predictions (LSTM vs Random Forest), SHAP contributions, and evaluation metrics.
    """
    def __init__(self):
        self.predictor = OutagePredictor()
        self.explainer = SHAPExplainer()

    def predict_and_explain(self, metrics_sequence, model_type="LSTM"):
        prob = self.predictor.predict_outage_probability(metrics_sequence, model_type=model_type)
        dual_res = self.predictor.get_dual_prediction(metrics_sequence)
        shap_res = self.explainer.explain_prediction(metrics_sequence)

        # Estimate Time-to-Failure (TTF) based on trend slope and probability
        ttf_seconds = None
        if prob >= 0.50 and metrics_sequence and len(metrics_sequence) >= 2:
            m_first = metrics_sequence[0]
            m_last = metrics_sequence[-1]
            cpu_slope = float(m_last.get("cpu_percent", m_last.get("cpu", 0))) - float(m_first.get("cpu_percent", m_first.get("cpu", 0)))
            mem_slope = float(m_last.get("memory_percent", m_last.get("memory", 0))) - float(m_first.get("memory_percent", m_first.get("memory", 0)))
            err_slope = float(m_last.get("error_rate", 0)) - float(m_first.get("error_rate", 0))
            
            max_slope = max(cpu_slope, mem_slope, err_slope * 100.0)
            if max_slope > 0.5:
                margin = (1.0 - prob) * 100.0
                ttf_seconds = round(max(3.0, min(120.0, margin / (max_slope / len(metrics_sequence)))), 1)
            else:
                ttf_seconds = round(max(5.0, (1.0 - prob) * 60.0), 1)

        risk_level = "CRITICAL" if prob >= 0.80 else ("HIGH" if prob >= 0.70 else ("MEDIUM" if prob >= 0.50 else "LOW"))

        return {
            "outage_probability": prob,
            "outage_probability_pct": round(prob * 100.0, 1),
            "risk_level": risk_level,
            "estimated_ttf_seconds": ttf_seconds,
            "model_used": dual_res["selected_model"] if model_type == "LSTM" else "RANDOM_FOREST",
            "dual_predictions": dual_res,
            "shap_contributions": shap_res["contributions"],
            "top_influential_feature": shap_res["top_feature"],
            "top_impact_percent": shap_res["top_impact"]
        }

    def get_evaluation_metrics(self):
        return self.predictor.get_evaluation_metrics()
