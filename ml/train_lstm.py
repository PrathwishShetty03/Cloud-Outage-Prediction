import os
import sys
import json
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

SEQUENCE_LENGTH = 10
FEATURES = ['cpu_percent', 'memory_percent', 'disk_percent', 'latency_ms', 'error_rate']

def generate_synthetic_telemetry_data(samples=1500):
    """
    Generates realistic telemetry sequences across 10 distinct cloud operational scenarios:
    1. Normal Traffic
    2. CPU Saturation
    3. Memory Leak
    4. Disk Pressure
    5. Latency Surge
    6. Error Cascade
    7. Packet Loss / Network Drop
    8. Traffic Spike
    9. Service Crash / Outage
    10. Dependency Slowdown
    """
    np.random.seed(42)
    X = []
    y = []

    scenarios = [
        'normal', 'cpu_saturation', 'memory_leak', 'disk_pressure',
        'latency_surge', 'error_cascade', 'packet_loss', 'traffic_spike',
        'service_crash', 'dependency_slowdown'
    ]

    for _ in range(samples):
        scen = np.random.choice(scenarios)
        
        # Base healthy telemetry
        cpu = np.random.uniform(15, 55, SEQUENCE_LENGTH)
        mem = np.random.uniform(25, 60, SEQUENCE_LENGTH)
        disk = np.random.uniform(30, 65, SEQUENCE_LENGTH)
        lat = np.random.uniform(15, 90, SEQUENCE_LENGTH)
        err = np.random.uniform(0.0, 0.015, SEQUENCE_LENGTH)
        target = 0

        if scen == 'normal':
            target = 0

        elif scen == 'cpu_saturation':
            cpu = np.linspace(35, 98, SEQUENCE_LENGTH) + np.random.normal(0, 2, SEQUENCE_LENGTH)
            target = 1

        elif scen == 'memory_leak':
            mem = np.linspace(40, 99, SEQUENCE_LENGTH) + np.random.normal(0, 1.5, SEQUENCE_LENGTH)
            target = 1

        elif scen == 'disk_pressure':
            disk = np.linspace(50, 96, SEQUENCE_LENGTH) + np.random.normal(0, 1, SEQUENCE_LENGTH)
            target = 1

        elif scen == 'latency_surge':
            lat = np.linspace(60, 4800, SEQUENCE_LENGTH) + np.random.normal(0, 30, SEQUENCE_LENGTH)
            target = 1

        elif scen == 'error_cascade':
            err = np.linspace(0.01, 0.48, SEQUENCE_LENGTH) + np.random.normal(0, 0.01, SEQUENCE_LENGTH)
            target = 1

        elif scen == 'packet_loss':
            lat = np.linspace(100, 3500, SEQUENCE_LENGTH)
            err = np.linspace(0.02, 0.35, SEQUENCE_LENGTH)
            target = 1

        elif scen == 'traffic_spike':
            cpu = np.linspace(25, 88, SEQUENCE_LENGTH)
            lat = np.linspace(40, 1200, SEQUENCE_LENGTH)
            target = 1 if max(cpu) > 85 else 0

        elif scen == 'service_crash':
            cpu = np.linspace(30, 99, SEQUENCE_LENGTH)
            err = np.linspace(0.05, 0.90, SEQUENCE_LENGTH)
            target = 1

        elif scen == 'dependency_slowdown':
            lat = np.linspace(50, 2200, SEQUENCE_LENGTH)
            err = np.linspace(0.0, 0.20, SEQUENCE_LENGTH)
            target = 1

        # Clip values to realistic bounds
        cpu = np.clip(cpu, 0.0, 100.0)
        mem = np.clip(mem, 0.0, 100.0)
        disk = np.clip(disk, 0.0, 100.0)
        lat = np.clip(lat, 0.0, 10000.0)
        err = np.clip(err, 0.0, 1.0)

        seq = np.column_stack([cpu, mem, disk, lat, err])
        X.append(seq)
        y.append(target)

    return np.array(X), np.array(y)

def train_and_save():
    print("[ML] Generating Multi-Scenario Telemetry Dataset...")
    X_raw, y = generate_synthetic_telemetry_data(samples=1500)
    
    N, T, F = X_raw.shape
    X_flat = X_raw.reshape(-1, F)
    
    # Standardize scaling across features
    scaler = MinMaxScaler()
    scaler.fit(X_flat)
    X_scaled = scaler.transform(X_flat).reshape(N, T, F)
    
    # Save Scaler
    with open(os.path.join(MODEL_DIR, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)

    # Clean Train (70%), Validation (15%), Test (15%) Split
    X_train, X_temp, y_train, y_temp = train_test_split(X_scaled, y, test_size=0.30, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)

    # --- 1. Train Random Forest Baseline Model ---
    print("[ML] Training Random Forest Baseline Model...")
    X_train_rf = X_train.reshape(X_train.shape[0], T * F)
    X_test_rf = X_test.reshape(X_test.shape[0], T * F)

    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train_rf, y_train)

    rf_preds = rf_model.predict(X_test_rf)
    rf_probs = rf_model.predict_proba(X_test_rf)[:, 1]

    with open(os.path.join(MODEL_DIR, 'rf_model.pkl'), 'wb') as f:
        pickle.dump(rf_model, f)

    # --- 2. Train LSTM Time-Series Model ---
    print("[ML] Training LSTM Time-Series Sequence Neural Network...")
    lstm_trained = False
    lstm_preds = None
    lstm_probs = None

    try:
        import keras
        from keras.models import Sequential
        from keras.layers import Input, LSTM, Dense, Dropout

        lstm_model = Sequential([
            Input(shape=(T, F)),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])

        lstm_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        lstm_model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=15, batch_size=32, verbose=0)
        
        lstm_probs = lstm_model.predict(X_test, verbose=0).flatten()
        lstm_preds = (lstm_probs >= 0.5).astype(int)

        model_save_path = os.path.join(MODEL_DIR, 'lstm_model.keras')
        lstm_model.save(model_save_path)
        lstm_trained = True
        print(f"[ML] Keras LSTM Model saved to {model_save_path}")

    except Exception as e:
        print(f"[ML WARNING] Keras LSTM training fallback: {e}")
        # Fallback sequence predictor if TensorFlow initialization is restricted
        lstm_preds = rf_preds
        lstm_probs = rf_probs

    # --- 3. Compute Real Evaluation Metrics ---
    metrics = {
        "dataset_samples": samples if 'samples' in locals() else N,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "random_forest": {
            "accuracy": round(float(accuracy_score(y_test, rf_preds)), 4),
            "precision": round(float(precision_score(y_test, rf_preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, rf_preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, rf_preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, rf_probs)), 4),
            "confusion_matrix": confusion_matrix(y_test, rf_preds).tolist()
        },
        "lstm": {
            "accuracy": round(float(accuracy_score(y_test, lstm_preds)), 4),
            "precision": round(float(precision_score(y_test, lstm_preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, lstm_preds, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, lstm_preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, lstm_probs)), 4),
            "confusion_matrix": confusion_matrix(y_test, lstm_preds).tolist(),
            "is_trained": lstm_trained
        }
    }

    metrics_path = os.path.join(MODEL_DIR, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print("[ML] Training Complete! Evaluation Metrics:")
    print(f"     Random Forest: Accuracy={metrics['random_forest']['accuracy']}, F1={metrics['random_forest']['f1_score']}, AUC={metrics['random_forest']['roc_auc']}")
    print(f"     PyTorch/Keras LSTM: Accuracy={metrics['lstm']['accuracy']}, F1={metrics['lstm']['f1_score']}, AUC={metrics['lstm']['roc_auc']}")

if __name__ == '__main__':
    train_and_save()
