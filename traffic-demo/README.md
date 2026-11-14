# Live Traffic & High Availability Failover Demo Application

A dedicated, standalone web application built to visually and interactively demonstrate real-time HTTP traffic routing, autonomous HAProxy failover from **Server A** to **Server B**, and controlled recovery for project vivas and jury presentations.

---

## 1. Quick Start Guide

### Prerequisites
Make sure your existing Docker cluster is running:
```powershell
docker compose ps
```
*(If containers are stopped, start them with `docker compose up -d`)*

### Launching the Traffic Demo Application
Run the launcher from the project root:
```powershell
python run_traffic_demo.py
```
*Or run directly:*
```powershell
python traffic-demo/app.py --port 5050
```

Open your browser and navigate to:
👉 **`http://localhost:5050`**

---

## 2. Cluster Architecture & Port Mapping

```
                                  [ User Demo Browser / Client ]
                                                │
                                    (HTTP Real User Traffic)
                                                ▼
                                    ┌───────────────────────┐
                                    │    HAProxy Ingress    │
                                    │       Port :80        │
                                    └───────────┬───────────┘
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       │                                                 │
          (Active Ingress Route)                                (Standby Backup)
                       │                                                 │
                       ▼                                                 ▼
             ┌───────────────────┐                             ┌───────────────────┐
             │     Server A      │                             │     Server B      │
             │     Port :5001    │                             │     Port :5002    │
             │   Cluster Primary │                             │   Cluster Backup  │
             └───────────────────┘                             └───────────────────┘
```

| Service | Host Port | Role in Architecture |
| :--- | :--- | :--- |
| **Traffic Demo App** | `:5050` | Dedicated Interactive UI & Live Request Auditor |
| **HAProxy Ingress** | `:80` | High-Availability Load Balancer & Health Gate |
| **HAProxy Stats** | `:8404` | HAProxy Native Statistics Socket & Report |
| **Server A** | `:5001` | Primary Ingress Node (`SERVER_A`) |
| **Server B** | `:5002` | Hot Standby / Digital Twin Node (`SERVER_B`) |
| **Server C** | `:5003` | Disaster Emergency Standby (`SERVER_C`) |
| **Main Dashboard** | `:8501` | Original Streamlit ML Telemetry Command Center |

---

## 3. Step-by-Step Viva Demonstration Walkthrough

Follow these exact steps in front of the evaluator/examiner:

### Step 1: Demonstrate Normal Active Operation
1. Open **`http://localhost:5050`**.
2. Notice the **Topology Flowchart** at the top:
   - **Server A** is marked **`● HEALTHY`** and **`ACTIVE INGRESS`**.
   - **Server B** is marked **`● HEALTHY`** and **`STANDBY`**.
3. Click the interactive action buttons:
   - **Load Products** (`GET /api/products`)
   - **Fetch Dashboard Data** (`GET /api/dashboard-data`)
   - **Place Test Order** (`POST /api/orders`)
   - **Refresh Server Status** (`GET /`)
4. Point out the **Live Request Log Table**:
   - Responding Server shows **`Server A`** (Port `:5001`).
   - Status code is **`200 OK`**.
   - Verification badge displays **`X-Served-By: SERVER_A ✓`**.
   - Timestamp is accurately formatted in **Indian Standard Time (IST)**.
   - Click **"View Payload"** to inspect the real JSON returned by Server A.

### Step 2: Trigger Controlled Server A Outage
1. Click the red **"💥 Simulate Server A Outage"** button.
2. Server A immediately enters an outage (HTTP 503).
3. Observe the UI:
   - Server A changes to **`● DOWN / OUTAGE`** (red pulse).
   - Server A's request counter **freezes**.
   - HAProxy marks Server A DOWN after 2 consecutive failed health checks.

### Step 3: Demonstrate Seamless Autonomous Failover
1. Click any action button: **Load Products**, **Place Test Order**, or **Send 5 Requests in Burst**.
2. Observe what happens:
   - A prominent **`⚡ HIGH AVAILABILITY FAILOVER ACTIVE`** alert banner appears with the exact IST timestamp.
   - Server B automatically switches to **`ACTIVE SERVING TRAFFIC`** (green glow).
   - In the Live Request Log Table:
     - All new requests are now handled by **`Server B`** (Port `:5002`).
     - HTTP Status Code is **`200 OK`** (zero downtime for users!).
     - Verification badge confirms **`X-Served-By: SERVER_B ✓`**.
   - Server B's request counter increments with each click, while Server A stays frozen.

### Step 4: Demonstrate Safe Recovery & Failback
1. Click the green **"🟢 Restore Server A"** button.
2. Server A enters the controlled recovery transition phase:
   - Badge shows **`● RECOVERING (Xs)`**.
   - HAProxy keeps routing traffic to Server B while Server A is remediating.
3. Once recovery finishes, Server A returns to **`● HEALTHY`**.
4. Send another request (e.g. **Place Test Order**):
   - Traffic seamlessly returns to **`Server A`** (Port `:5001`).
   - A **`FAILBACK_RESTORED`** event is logged in the audit trail.

---

## 4. Technical Summary of Changes Made

1. **New Separate Application (`traffic-demo/`)**:
   - `traffic-demo/app.py`: Flask server on port `:5050` with proxy routes, IST timestamps, real latency measurements, and failover event tracking.
   - `traffic-demo/templates/index.html`: Responsive glassmorphism dashboard with topology diagram, interactive control deck, live request logs, and payload inspection modal.
   - `run_traffic_demo.py`: Root-level launcher.
2. **Backend Business Endpoints Added to `server_app/server_app.py`**:
   - `GET /api/products`: Returns real product catalog.
   - `GET /api/dashboard-data`: Returns live node compute and IOPS telemetry.
   - `POST /api/orders`: Executes order provisioning transactions.
   - Added `X-Served-By`, `X-Server-Port`, and `X-Request-Number` proof headers to all responses.
3. **Internal Probes Isolated from Request Counters**:
   - Telemetry scraping (`/api/metrics`) and health checks (`/health`) no longer inflate the served request count.
