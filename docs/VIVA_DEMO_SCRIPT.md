# 🛡️ VIVA DEMO SCRIPT & EVALUATOR PROOF CHECKLIST

**Project Title**: Predictive Cloud Outage Prevention & Dual Twin Failover Architecture  
**Department**: Computer Science & Engineering  

---

## 📋 PRE-DEMO ENVIRONMENT SETUP CHECKLIST

- [ ] **Step 1**: Start Primary Server A (port 5001), Server B (port 5002 / LAN IP:5001), and Emergency Server C (port 5003).
  ```bash
  python server_app/server_app.py --id SERVER_A --port 5001 --role PRIMARY
  python server_app/server_app.py --id SERVER_B --port 5002 --role BACKUP
  python server_app/server_app.py --id SERVER_C --port 5003 --role EMERGENCY
  ```
- [ ] **Step 2**: Start HAProxy reverse proxy load balancer on port 80 & stats on port 8404:
  ```bash
  python haproxy/local_haproxy_proxy.py
  ```
- [ ] **Step 3**: Launch Streamlit Command Center dashboard:
  ```bash
  streamlit run dashboard/app.py
  ```
- [ ] **Step 4**: Prepare terminal split-screen:
  - **Left Window**: Live terminal watching headers:
    ```bash
    watch -n 1 "curl -i -s http://localhost:80/ | grep -E 'HTTP/|X-Served-By|X-Server-Port|X-Request-Number'"
    ```
  - **Right Window**: Browser showing Streamlit Command Center at `http://localhost:8501`.

---

## 🎬 STEP-BY-STEP LIVE VIVA DEMONSTRATION SCRIPT (OUTAGE PREVENTION BEFORE FAILURE)

### Step 1: Establish Normal Operations (Primary Server A Active)
**🗣️ What to say to evaluators:**
> *"Currently, Server A is our primary server handling all application traffic. Server B is standing by as our Digital Twin backup."*
1. Point evaluators to the left terminal running `curl -i http://localhost:80/`.
2. Highlight response headers: `X-Served-By: SERVER_A` and `X-Server-Port: 5001`.
3. Run baseline traffic generator:
   ```bash
   python scripts/send_requests.py --count 100
   ```
4. Point evaluators to the Streamlit Dashboard (`http://localhost:8501`) showing Server A counter climbing to 100 requests.

---

### Step 2: Digital Twin Standby Verification
**🗣️ What to say to evaluators:**
> *"Server B is continuously monitored on its own hardware metrics and is currently in STANDBY mode, receiving zero client traffic while maintaining digital twin metric synchronization."*
1. Point to **Digital Twin Divergence Page (`/digital-twin`)**:
   - Show divergence score < 15.0% (`SYNCHRONIZED`).

---

### Step 3: Workload Escalation on Server A
**🗣️ What to say to evaluators:**
> *"I will now increase the workload on Server A. Notice how CPU, Memory, and Latency increase naturally from the actual request load."*
1. Click **"🚀 Run Predictive Demo"** in Streamlit or run terminal load generator:
   ```bash
   python scripts/run_predictive_demo.py
   ```
2. Point evaluators to the real-time resource charts:
   - CPU rises: `35% → 55% → 72% → 85% → 92%`
   - Latency rises: `15ms → 300ms → 1500ms → 3400ms`

---

### Step 4: ML Outage Prediction Calculation
**🗣️ What to say to evaluators:**
> *"Our LSTM machine learning model is observing these deteriorating telemetry signals over a 10-step sliding window and calculating the probability of an outage."*
1. Point evaluators to **ML Outage Prediction Section (`/prediction`)**:
   - Outage Probability climbs past **0.80 (80.0%)** (e.g. `Outage Risk: 87.5%`).
   - SHAP Waterfall chart highlights **Network Latency & CPU Usage** as top risk drivers.

---

### Step 5: Predictive Risk Threshold Crossed
**🗣️ What to say to evaluators:**
> *"The predicted outage probability has crossed our critical 0.80 threshold. Notice that Server A is technically STILL reachable and returning HTTP 200 responses."*

---

### Step 6: Proactive Traffic Redirection (PREDICTION BEFORE FAILURE)
**🗣️ What to say to evaluators:**
> *"Instead of waiting for Server A to completely fail or crash, our system proactively moves all NEW application traffic to Server B before any outage occurs."*
1. Point evaluators to the **PREDICTIVE FAILOVER STATUS** card:
   - `Active Server`: `SERVER_B`
   - `Primary Status`: `AT RISK (Probability: 87.5%)`
   - `Failover Mode`: `PREDICTIVE`

---

### Step 7: Independent Request Header Proof
**🗣️ What to say to evaluators:**
> *"Let's send a new request through HAProxy on Port 80 to verify traffic redirection."*
1. Execute single request in terminal:
   ```bash
   curl -i http://localhost:80/
   ```
2. Point evaluators to the response header:
   - `X-Served-By: SERVER_B`
   - `X-Server-Port: 5002` (or LAN port)
   - `X-Request-Number: 1`

---

### Step 8: Outage Prevention Verification
**🗣️ What to say to evaluators:**
> *"Server A has NOT crashed yet, but we have already protected the application from the predicted outage. Completed requests on Server A remain frozen at 100, while new requests are served by Server B."*

---

### Step 9: Optional Server A Shutdown & Handover of Proof Artifacts
**🗣️ What to say to evaluators:**
> *"Now if we simulate a complete failure on Server A, Server B continues serving traffic seamlessly."*
1. Stop Server A (`curl -X POST http://localhost:5001/simulate/outage`).
2. Show that `http://localhost:80/` continues returning HTTP 200 with `X-Served-By: SERVER_B`.
3. Open **`/logs` Page** and click **"Download Proof Log (PDF)"** / **"Download Proof Log (CSV)"**.
4. Hand over the generated PDF report ([`latest_failover_proof.pdf`](file:///C:/Users/prath/.gemini/antigravity/scratch/cloud-outage-prediction/logs/proof_logs/latest_failover_proof.pdf)) to the evaluation committee!
