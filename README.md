# Predictive Self-Healing Cloud Infrastructure Using Digital Twins and Explainable AI

Final-Year B.E. Computer Science & Engineering Major Capstone Project.

---

## 🌟 Architectural Pillars

```text
                 ┌─────────────┐
                 │   PREDICT   │  (PyTorch/Keras LSTM + Random Forest)
                 └──────┬──────┘
                        │
                 ┌──────▼──────┐
                 │   EXPLAIN   │  (SHAP Feature Importance & Root Cause Analysis)
                 └──────┬──────┘
                        │
                 ┌──────▼──────┐
                 │  SIMULATE   │  (Digital Twin Divergence, Trends & What-If Engine)
                 └──────┬──────┘
                        │
                 ┌──────▼──────┐
                 │ SELF-HEAL   │  (Suitability Failover + Automated Remediation)
                 └─────────────┘
```

---

## 🚀 Key Implemented Features

1. **3-Server Multi-Node Infrastructure**: Target Flask microservices on ports `5001` (Server A Primary), `5002` (Server B Digital Twin / Backup), and `5003` (Server C Emergency).
2. **HAProxy Load Balancer Ingress**: Ingress load balancer on port `80` with HTTP health checks (`/health`) and dynamic route switching API (`/set_active_backend`).
3. **Machine Learning Outage Engine**: Time-series LSTM neural network (`lstm_model.keras`) trained alongside Random Forest baseline classifier (`rf_model.pkl`) across 10 telemetry failure scenarios.
4. **Explainable AI (SHAP)**: Feature contribution breakdown across CPU, Memory, Disk, Latency, and Error Rate using `TreeExplainer`.
5. **Real-Time Digital Twin**: Multi-metric divergence score calculation, trend forecasting (+10s, +20s, +30s), and interactive What-If scenario simulation.
6. **Intelligent Server Suitability Ranking**:
   $$\text{Suitability}(S) = 0.35 \cdot \text{Health} + 0.25 \cdot (100 - \max(\text{CPU}, \text{RAM})) + 0.15 \cdot \text{LatencyScore} + 0.15 \cdot (100 - \text{Risk}) + 0.10 \cdot \text{TwinSync}$$
7. **Automated Self-Healing Remediation**: Drains degraded primary node, triggers process recovery (`/simulate/recover`), polls health verification, synchronizes Digital Twin, and restores node to standby mode.
8. **Tamper-Evident SHA-256 Audit Ledger**: Cryptographic hash chaining ($H_i = \text{SHA256}(H_{i-1} \parallel \text{data})$) with instant chain integrity verification (`Audit Integrity: VALID`).
9. **SRE Service Level Objectives (SLO/SLA)**: Availability % tracking (Target 99.9%), p95 Latency (<300ms), Error Rate (<1.0%), and Error Budget consumption monitoring.
10. **Chaos Engineering & 3-Way Comparative Evaluation**: Safe fault injection suite (CPU stress, RAM leak, latency surge, error cascade, disk pressure) + comparative evaluation benchmarks (Reactive vs Predictive vs Self-Healing).

---

## 💻 Tech Stack & Machine Requirements

- **Operating Environment**: Laptop / PC (8 GB RAM min, 4 CPU cores, CPU-only execution)
- **Programming Language**: Python 3.10+
- **Backend Framework**: Flask, Werkzeug, Requests
- **Machine Learning**: TensorFlow / Keras (LSTM), Scikit-Learn (Random Forest), NumPy, Pandas
- **Explainable AI**: SHAP (SHapley Additive exPlanations)
- **Container Infrastructure**: Docker, Docker Compose, HAProxy 2.8 Alpine
- **Observability**: Prometheus Client, Psutil
- **Frontend Dashboard**: Streamlit Cloud Reliability Command Center, Plotly

---

## ⚡ Quickstart Execution Guide

### Option 1: Local Python Execution

1. Install Dependencies:
   ```bash
   pip install -r server_app/requirements.txt
   pip install streamlit pandas numpy plotly scikit-learn shap requests psutil prometheus_client
   ```

2. Train Machine Learning Models:
   ```bash
   python ml/train_lstm.py
   ```

3. Launch 3 Target Server Microservices (Terminals 1–3):
   ```bash
   # Terminal 1: Primary Server A
   SERVER_ID=SERVER_A SERVER_PORT=5001 python server_app/server_app.py

   # Terminal 2: Backup/Twin Server B
   SERVER_ID=SERVER_B SERVER_PORT=5002 python server_app/server_app.py

   # Terminal 3: Emergency Server C
   SERVER_ID=SERVER_C SERVER_PORT=5003 python server_app/server_app.py
   ```

4. Launch Local HAProxy Reverse Proxy (Terminal 4):
   ```bash
   HAPROXY_PORT=80 python haproxy/local_haproxy_proxy.py
   ```

5. Launch Streamlit Command Center (Terminal 5):
   ```bash
   streamlit run dashboard/app.py
   ```

---

### Option 2: Docker Compose Launch

```bash
docker compose up --build -d
```

#### Access Points:
- **HAProxy Ingress Route**: `http://localhost:80/`
- **HAProxy Stats Dashboard**: `http://localhost:8404/stats`
- **Streamlit Command Center**: `http://localhost:8501/`

---

## 🧪 Testing & Verification

Run the automated test suite:
```bash
python -m unittest discover -s tests -v
```

---

## 📊 Major Project USP

This platform bridges predictive machine learning, digital twin simulation, and SRE self-healing into an integrated cloud reliability command center. Unlike traditional reactive monitoring tools that failover only after an HTTP 503 outage has occurred, this platform forecasts outage risks up to 20 seconds in advance, pinpoints root causes using SHAP explainability, selects the optimal target node via mathematical suitability scoring, and executes automated self-healing remediation while preserving cryptographic proof in a SHA-256 audit ledger.
