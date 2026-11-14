import os
from report_builder.doc_helper import (
    add_chapter_title_sheet, add_chapter_header_block,
    add_section, add_subsection, add_body_paragraph, add_bullet_point,
    add_table_title, create_styled_table, add_image_figure,
    add_formula_callout, add_code_snippet
)

def build_chapter_5(doc, assets_dir):
    # Separate Chapter Title Sheet
    add_chapter_title_sheet(doc, "Chapter 5", "SYSTEM DESIGN")

    # Chapter Header Block on First Page
    add_chapter_header_block(doc, "Chapter 5", "SYSTEM DESIGN")

    # ----------------------------------------------------
    # 5.1 System Architecture
    # ----------------------------------------------------
    add_section(doc, "5.1 System Architecture")
    add_body_paragraph(
        doc,
        "The overall system architecture of the Intelligent Cloud Outage Detection and Prediction System is engineered "
        "as a decoupled, multi-tier resilience harness. The architecture bridges the gap between Layer-7 ingress network "
        "routing, distributed microservice compute nodes, deep learning time-series inference, and autonomous self-healing "
        "orchestration. As depicted in Figure 5.1, the platform is partitioned into three foundational operational layers:"
    )

    add_bullet_point(
        doc,
        "Layer 1: Ingress Load Balancing & Traffic Routing Layer",
        "Managed by an enterprise-grade HAProxy Layer-7 reverse proxy gateway binding on Port 80 (public HTTP entrypoint) "
        "and Port 8404 (live statistics dashboard). HAProxy acts as the single point of contact for external client traffic, "
        "distributing requests dynamically to the active backend node while continuously executing non-blocking health checks "
        "at 1,000ms intervals."
    )

    add_bullet_point(
        doc,
        "Layer 2: Multi-Tier Microservice Compute Cluster",
        "Composed of three heterogeneous Flask target nodes executing in isolated network namespaces: Primary Server A (port 5001), "
        "Digital Twin Backup Server B (port 5002), and Emergency Quarantine Server C (port 5003). Each microservice instance "
        "exposes business transaction endpoints alongside dedicated /health and /api/metrics telemetry endpoints."
    )

    add_bullet_point(
        doc,
        "Layer 3: Resilience Intelligence & Orchestration Layer",
        "Housing the Deep LSTM Outage Prediction Engine, the SHAP Explainability Engine, the Mathematical Digital Twin Divergence "
        "Engine, the Site Reliability Engineering (SRE) SLO Tracker, the Autonomous Remediation Engine, and the Automated "
        "Failover Controller. This intelligence stack continuously inspects telemetry without adding latency to client request threads."
    )

    fig_arch = os.path.join(assets_dir, "fig_5_1_system_architecture.png")
    add_image_figure(doc, fig_arch, "Figure 5.1: Overall System Architecture of Intelligent Cloud Outage Prediction System")

    # ----------------------------------------------------
    # 5.2 Component Design / Module Decomposition
    # ----------------------------------------------------
    add_section(doc, "5.2 Component Design / Module Decomposition")
    add_body_paragraph(
        doc,
        "The system decomposes functionally into six high-cohesion, loosely-coupled software modules interacting via "
        "standardized RESTful API contracts and shared memory queues. Figure 5.2 illustrates the detailed component hierarchy:"
    )

    fig_comp = os.path.join(assets_dir, "fig_5_2_component_architecture.png")
    add_image_figure(doc, fig_comp, "Figure 5.2: Detailed Component Architecture of Intelligent Cloud Resilience Stack")

    add_subsection(doc, "5.2.1 Target Node Microservices (server_app.py)")
    add_body_paragraph(
        doc,
        "Each server instance encapsulates a lightweight, high-throughput microservice responsible for: (a) Serving realistic "
        "business transactions (/api/products, /api/dashboard-data, /api/orders); (b) Tracking atomic monotonic counters of "
        "successfully served user requests (simulation_state['total_requests']); (c) Injecting cryptographic verification "
        "headers (X-Served-By, X-Server-Port, X-Request-Number); and (d) Sponsoring controlled chaos stress hooks."
    )

    add_subsection(doc, "5.2.2 Asynchronous Telemetry Harvester (state.py)")
    add_body_paragraph(
        doc,
        "A persistent background worker (bg_telemetry_worker) spawned in a dedicated daemon thread. It invokes the controller's "
        "evaluate_cycle() routine every 1.2 seconds, sampling CPU, memory, disk, response latency, and error rates across all "
        "three servers. Metric snapshots are appended to sliding FIFO queues and cached under thread-safe locks (GLOBAL_CACHE_LOCK)."
    )

    add_subsection(doc, "5.2.3 Deep LSTM Outage Prediction Engine (predict.py & train_lstm.py)")
    add_body_paragraph(
        doc,
        "The predictive core of the system. It ingests 10-step rolling sequences of 5 telemetry features, applies MinMax normalization, "
        "and executes forward-pass inference through a compiled Keras sequential LSTM neural network to yield an outage risk probability."
    )

    add_subsection(doc, "5.2.4 SHAP Explainability Engine (shap_explain.py)")
    add_body_paragraph(
        doc,
        "A game-theoretic attribution module employing Shapley Additive exPlanations. It computes the marginal contribution of each "
        "telemetry parameter to the current outage risk, attributing the dominant failure vector (e.g., CPU vs Memory) for SRE auditability."
    )

    add_subsection(doc, "5.2.5 Digital Twin & Divergence Engine (twin_engine.py)")
    add_body_paragraph(
        doc,
        "Maintains a mathematical shadow model of Primary Server A against Digital Twin Server B. It computes real-time metric divergence "
        "and projects multi-step future linear resource trends to detect state decoupling."
    )

    add_subsection(doc, "5.2.6 Automated Failover Controller (failover_controller.py)")
    add_body_paragraph(
        doc,
        "The master operational orchestrator. It evaluates dual-path failover logic (Predictive vs. Emergency), calculates multi-criteria "
        "server suitability ranking scores, controls HAProxy routing notification hooks, logs timestamped audit events in IST, "
        "and coordinates autonomous self-healing remediation."
    )

    # ----------------------------------------------------
    # 5.3 Interface Design
    # ----------------------------------------------------
    add_section(doc, "5.3 Interface Design")
    add_body_paragraph(
        doc,
        "Inter-module communication is established strictly over standardized TCP/IP network interfaces using RESTful HTTP/JSON "
        "payloads and Layer-7 reverse proxy rules. Figure 5.6 details the port allocation and network topology:"
    )

    fig_comm = os.path.join(assets_dir, "fig_5_6_server_communication.png")
    add_image_figure(doc, fig_comm, "Figure 5.6: TCP/IP Port Allocation and Multi-Node Network Topology")

    add_table_title(doc, "Table 5.1: Microservice REST API Endpoint Specification and Payload Contracts")
    headers_api = ["Method & Path", "Target Server", "Payload / Parameters", "HTTP Status", "Functional Description"]
    data_api = [
        ["GET /health", "Ports 5001-5003", "None", "200 OK / 503 Outage", "L7 Health check for HAProxy (inter 1000ms fall 2)"],
        ["GET /api/metrics", "Ports 5001-5003", "None", "200 OK (JSON)", "Telemetry vitals (CPU, RAM, Latency, Error Rate)"],
        ["GET /api/products", "Ports 5001-5003", "Optional query params", "200 OK (Catalog JSON)", "Business API serving realistic e-commerce products"],
        ["POST /api/orders", "Ports 5001-5003", "JSON: {item_id, qty}", "201 Created", "Business API processing simulated user purchase orders"],
        ["POST /stress/cpu", "Server A (5001)", "JSON: {enable: true}", "200 OK", "Spawns 4 CPU threads executing math.factorial(25000)"],
        ["POST /stress/ram", "Server A (5001)", "JSON: {mb: 300}", "200 OK", "Allocates 50MB bytearrays on Python heap to leak RAM"],
        ["POST /stress/latency", "Server A (5001)", "JSON: {seconds: 5.5}", "200 OK", "Injects artificial 5.5s sleep delay on request handling"],
        ["POST /simulate/outage", "Server A (5001)", "None", "200 OK", "Sets is_outage=True; immediately returns HTTP 503"],
        ["POST /simulate/recover", "Server A (5001)", "None", "200 OK", "Clears active fault hooks; enters 20s recovery phase"],
        ["GET /stats", "HAProxy (8404)", "Basic HTTP Auth", "200 OK (HTML/CSV)", "Real-time HAProxy node session stats & byte metrics"]
    ]
    create_styled_table(doc, headers_api, data_api, [1.4, 1.1, 1.3, 1.0, 1.8])

    # ----------------------------------------------------
    # 5.4 Data Structures Used
    # ----------------------------------------------------
    add_section(doc, "5.4 Data Structures Used")
    add_body_paragraph(
        doc,
        "To achieve sub-millisecond data transformation and non-blocking streaming ingestion, the system incorporates "
        "several optimized in-memory data structures:"
    )

    add_bullet_point(
        doc,
        "1. Sliding Telemetry Queue (self.history_a)",
        "A bounded First-In-First-Out (FIFO) queue of maximum length 30, implemented using Python lists with atomic append "
        "and pop(0) operations. Each element represents an immutable dictionary containing timestamped telemetry vitals."
    )

    add_bullet_point(
        doc,
        "2. MinMax Feature Vector (10 × 5 Matrix)",
        "A two-dimensional NumPy array of shape (10, 5) representing 10 consecutive temporal timesteps across 5 normalized features: "
        "[cpu_percent, memory_percent, disk_percent, latency_ms, error_rate]. Transformed into a 3D tensor of shape (1, 10, 5) "
        "for Keras LSTM batch inference."
    )

    add_bullet_point(
        doc,
        "3. Real-Time IST Audit Log Queue (self.failover_logs)",
        "A reverse-chronological list holding structured dictionary records of every system event, failover trigger, and "
        "remediation dispatch with millisecond-precision Indian Standard Time (IST) timestamps."
    )

    add_bullet_point(
        doc,
        "4. Server Suitability Vector",
        "A multi-dimensional scoring dictionary computed per node, storing normalized scalar metrics for Health, Available Capacity, "
        "Latency Performance, ML Risk Buffer, and Digital Twin State Synchronization."
    )

    # ----------------------------------------------------
    # 5.5 Algorithms
    # ----------------------------------------------------
    add_section(doc, "5.5 Algorithms")
    add_body_paragraph(
        doc,
        "The core intelligence and decision-making logic of the system are governed by three mathematical algorithms, "
        "formally detailed below:"
    )

    # Algorithm 1: Divergence
    add_subsection(doc, "5.5.1 Algorithm 1: Digital Twin Divergence Computation")
    add_formula_callout(
        doc,
        "Formula 5.1: Weighted Digital Twin Divergence Score (D)",
        "D = 0.35 · |ΔCPU| + 0.30 · |ΔMemory| + 0.15 · min(100, (ΔLatency / 2000) · 100) + 0.20 · (ΔErrorRate · 100)",
        [
            ("ΔCPU", "Absolute percentage delta in CPU utilization between Primary Server A and Twin Server B"),
            ("ΔMemory", "Absolute percentage delta in virtual memory consumption between Primary and Twin"),
            ("ΔLatency", "Response latency delta normalized to a 2,000ms scaling boundary"),
            ("ΔErrorRate", "HTTP 5xx error rate difference scaled to a 100-point percentage scale"),
            ("Divergence Threshold", "D >= 40.0 triggers a State Desynchronization Warning")
        ]
    )

    # Algorithm 2: LSTM Inference
    add_subsection(doc, "5.5.2 Algorithm 2: Deep LSTM Sequence Inference & Outage Risk Estimation")
    add_body_paragraph(
        doc,
        "The LSTM model processes sequential input vectors through a recurrent network to capture progressive degradation trajectories. "
        "The forward inference algorithm is formalized below:"
    )
    add_code_snippet(
        doc,
        "Algorithm 2: Real-Time LSTM Outage Probability Inference\n"
        "Input: Sliding telemetry history sequence H_A = [m_{t-9}, m_{t-8}, ..., m_t]\n"
        "Output: Outage Risk Probability P_out in range [0.0, 1.0], Risk Level R\n\n"
        "1:  If length(H_A) < 10 then\n"
        "2:      Pad sequence with earliest available metric snapshot\n"
        "3:  Extract feature matrix X of shape (10, 5):\n"
        "        X = [[cpu_i, mem_i, disk_i, lat_i, err_i] for i in H_A]\n"
        "4:  Transform X using pre-fitted MinMaxScaler: X_scaled = Scaler.transform(X)\n"
        "5:  Reshape tensor to 3D input: X_tensor = reshape(X_scaled, (1, 10, 5))\n"
        "6:  Compute neural forward pass: raw_p = LSTM_Model.predict(X_tensor, verbose=0)[0][0]\n"
        "7:  // Safety rule-based guardrail for extreme sudden stress:\n"
        "8:  latest = H_A[-1]\n"
        "9:  If latest.is_outage == True or latest.cpu >= 90% or latest.lat >= 4000ms then\n"
        "10:     P_out = max(raw_p, 0.95)\n"
        "11: Else if latest.cpu >= 75% or latest.lat >= 1500ms then\n"
        "12:     P_out = max(raw_p, 0.82)\n"
        "13: Else:\n"
        "14:     P_out = raw_p\n"
        "15: Determine Risk Level: R = 'CRITICAL' if P_out >= 0.80 else ('HIGH' if P_out >= 0.70 else 'LOW')\n"
        "16: Return P_out, R",
        "Algorithm 5.1: Real-Time LSTM Sequence Inference Pipeline"
    )

    # Algorithm 3: Failover Decision Matrix
    add_subsection(doc, "5.5.3 Algorithm 3: Multi-Criteria Server Suitability Ranking & Failover")
    add_formula_callout(
        doc,
        "Formula 5.2: Server Suitability Ranking Score (S_i)",
        "S_i = 0.35 · Health_i + 0.25 · (100 - max(CPU_i, Mem_i)) + 0.15 · LatScore_i + 0.15 · (100 - Risk_i) + 0.10 · TwinSync_i",
        [
            ("Health_i", "Dynamic composite health score of candidate server i (0.0 to 100.0)"),
            ("max(CPU, Mem)", "Peak hardware saturation penalty; evaluates available headroom capacity"),
            ("LatScore_i", "Latency score: max(0, 100 - (Latency_ms / 2000) * 100)"),
            ("Risk_i", "Machine learning outage risk probability expressed as a percentage"),
            ("TwinSync_i", "Digital twin state alignment score (100 - Divergence Score)")
        ]
    )

    add_body_paragraph(
        doc,
        "Figure 5.5 visualizes the dual-path decision tree distinguishing proactive predictive failover from reactive emergency failover:"
    )
    fig_failover = os.path.join(assets_dir, "fig_5_5_failover_workflow.png")
    add_image_figure(doc, fig_failover, "Figure 5.5: Decision Logic Flow for Predictive vs. Reactive Failover")
