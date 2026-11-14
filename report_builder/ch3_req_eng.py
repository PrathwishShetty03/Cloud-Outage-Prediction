import os
from report_builder.doc_helper import (
    add_chapter_title_sheet, add_chapter_header_block,
    add_section, add_subsection, add_body_paragraph, add_bullet_point,
    add_table_title, create_styled_table, add_image_figure
)

def build_chapter_3(doc, assets_dir):
    # Separate Chapter Title Sheet
    add_chapter_title_sheet(doc, "Chapter 3", "REQUIREMENT ENGINEERING")

    # Chapter Header Block on First Page
    add_chapter_header_block(doc, "Chapter 3", "REQUIREMENT ENGINEERING")

    # ----------------------------------------------------
    # 3.1 Software and Hardware Tools Used
    # ----------------------------------------------------
    add_section(doc, "3.1 Software and Hardware Tools Used")
    add_body_paragraph(
        doc,
        "The development, containerization, machine learning training, and empirical benchmarking of the Intelligent "
        "Cloud Outage Detection and Prediction System required a modern, high-performance computational hardware environment "
        "and an enterprise-grade software stack. The specifications and tooling infrastructure are detailed below:"
    )

    add_table_title(doc, "Table 3.1: Development Hardware Specifications and Host Operating Environment")
    headers_hw = ["Hardware Component", "Minimum Specification", "Actual Development Environment", "Operational Role"]
    data_hw = [
        ["Processor (CPU)", "Intel Core i5 (Quad-Core)", "Intel Core i7-12700H (14 Cores, 20 Threads)", "Host virtualization, multi-threaded stress generation"],
        ["System Memory (RAM)", "8 GB DDR4", "16 GB DDR5 @ 4800 MHz", "Container memory allocation, in-memory LSTM training"],
        ["Storage (Disk)", "256 GB SSD", "512 GB NVMe M.2 Solid State Drive", "Fast telemetry I/O, container image layers, logs"],
        ["Network Interface", "100 Mbps NIC", "Intel Wi-Fi 6 AX201 & 1 Gbps Gigabit Ethernet", "Microservice loopback & container bridge networking"],
        ["Host Operating System", "Windows 10 / Ubuntu 20.04", "Microsoft Windows 11 Pro (64-bit)", "Development host, Docker Desktop Hyper-V virtualization"]
    ]
    create_styled_table(doc, headers_hw, data_hw, [1.4, 1.4, 1.8, 1.4])

    add_table_title(doc, "Table 3.2: Software Technologies, Frameworks, and Container Infrastructure")
    headers_sw = ["Software Layer", "Technology / Framework", "Version", "Specific Project Utilization"]
    data_sw = [
        ["Programming Language", "Python", "3.10 / 3.13", "Core implementation of microservices, ML models, controller"],
        ["Ingress Load Balancer", "HAProxy", "2.8+ / Alpine Docker", "Layer-7 reverse proxy, health checks (inter 1000ms), failover"],
        ["Web Microservices", "Flask", "3.0+", "REST API targets: Server A (5001), B (5002), C (5003), Demo (5050)"],
        ["Deep Learning Engine", "TensorFlow / Keras", "2.16+", "Sequential LSTM neural network construction, training, prediction"],
        ["Machine Learning Baseline", "Scikit-Learn", "1.4+", "MinMaxScaler feature scaling, Random Forest comparative baseline"],
        ["Explainable AI (XAI)", "SHAP", "0.45+", "TreeExplainer & KernelSHAP feature attribution calculations"],
        ["Observability & Metrics", "Prometheus Client / psutil", "0.20+ / 5.9+", "Real-time CPU, RAM, disk, latency telemetry collection"],
        ["Visualization Dashboard", "Streamlit & Plotly", "1.32+ / 5.20+", "Interactive command center, KPI gauges, real-time IST charts"],
        ["Container Runtime", "Docker & Docker Compose", "26.0+ / 2.27+", "Multi-container orchestration, virtual network bridges"]
    ]
    create_styled_table(doc, headers_sw, data_sw, [1.3, 1.4, 1.0, 2.3])

    # ----------------------------------------------------
    # 3.2 Conceptual/Analysis Modeling
    # ----------------------------------------------------
    add_section(doc, "3.2 Conceptual/Analysis Modeling")
    add_body_paragraph(
        doc,
        "Conceptual analysis modeling provides a rigorous visual abstraction of the system's operational boundaries, "
        "actor interactions, temporal execution sequences, internal state transitions, and component relationships. "
        "In accordance with the Unified Modeling Language (UML) standard, five foundational diagrams are analyzed below:"
    )

    # 3.2.1 Use Case Diagram
    add_subsection(doc, "3.2.1 Use Case Diagram")
    add_body_paragraph(
        doc,
        "The Use Case Diagram defines the behavioral interactions between human actors (Cloud Site Reliability Engineers, "
        "System Administrators), external software actors (End-User Web Traffic, HAProxy Load Balancer), and the internal "
        "services of the resilience platform. Primary use cases include monitoring telemetry, executing controlled chaos "
        "experiments, calculating digital twin divergence, performing LSTM outage forecasting, and triggering automated "
        "failover and self-healing recovery."
    )
    fig_use_case = os.path.join(assets_dir, "fig_3_1_use_case_diagram.png")
    add_image_figure(doc, fig_use_case, "Figure 3.1: Use Case Diagram for Intelligent Cloud Outage Prediction System")

    # 3.2.2 Sequence Diagram
    add_subsection(doc, "3.2.2 Sequence Diagram")
    add_body_paragraph(
        doc,
        "The Sequence Diagram captures the chronologically ordered message exchanges across system boundaries during "
        "a proactive failover lifecycle. Initially, client requests flow through HAProxy on Port 80 to Primary Server A, "
        "which returns HTTP 200 with 'X-Served-By: SERVER_A'. Simultaneously, the background worker polls /api/metrics "
        "every 1.2 seconds. When chaos stress elevates CPU to 92% and latency to 5.5s, the LSTM predicts an outage probability "
        "of 0.88 (88%). The Automated Failover Controller instantly instructs HAProxy to reroute traffic to Digital Twin "
        "Server B, and subsequent client requests succeed seamlessly with 'X-Served-By: SERVER_B' before Server A collapses."
    )
    fig_seq = os.path.join(assets_dir, "fig_3_2_sequence_diagram.png")
    add_image_figure(doc, fig_seq, "Figure 3.2: Sequence Diagram of Predictive Telemetry, ML Inference, and Failover")

    # 3.2.3 Activity Diagram
    add_subsection(doc, "3.2.3 Activity Diagram")
    add_body_paragraph(
        doc,
        "The Activity Diagram delineates the procedural control flow and decision logic governing health evaluation. "
        "At each 1.2-second polling cycle, raw operating system metrics are scaled via MinMaxScaler into a 10x5 sequence "
        "matrix. If the LSTM model computes an outage risk >= 80% while Server A is still operational, the system branches "
        "into Predictive Failover. If Server A crashes abruptly (HTTP 503), it branches into Reactive Emergency Failover. "
        "Otherwise, normal active routing continues."
    )
    fig_act = os.path.join(assets_dir, "fig_3_3_activity_diagram.png")
    add_image_figure(doc, fig_act, "Figure 3.3: Activity Diagram of Proactive Outage Detection and Failover Logic")

    # 3.2.4 State Chart Diagram
    add_subsection(doc, "3.2.4 State Chart Diagram")
    add_body_paragraph(
        doc,
        "The State Chart Diagram models the dynamic operational states of Server A throughout stress escalation, "
        "failure anticipation, failover migration, and self-healing recovery. States transition from HEALTHY (baseline) "
        "to DEGRADED (stress injection), AT_RISK (LSTM risk >= 80%), FAILOVER_ACTIVE (traffic diverted to Server B), "
        "and RECOVERING (autonomous cooldown phase), before returning safely to HEALTHY standby."
    )
    fig_state = os.path.join(assets_dir, "fig_3_4_state_chart_diagram.png")
    add_image_figure(doc, fig_state, "Figure 3.4: State Chart Diagram for Server Life-Cycle and Failover States")

    # 3.2.5 Class Diagram
    add_subsection(doc, "3.2.5 Class Diagram")
    add_body_paragraph(
        doc,
        "The UML Class Diagram depicts the object-oriented structure, class attributes, public methods, and inter-module "
        "dependencies comprising the system architecture. Core classes include AutomatedFailoverController (central orchestrator), "
        "OutagePredictorML (inference and SHAP explainer), DigitalTwinEngine (divergence computation), SelfHealingRemediation "
        "(autonomous recovery), ChaosEngineeringSuite (fault injection), and SLOTracker (error budget monitoring)."
    )
    fig_class = os.path.join(assets_dir, "fig_3_5_class_diagram.png")
    add_image_figure(doc, fig_class, "Figure 3.5: UML Class Diagram of Primary Modules and Core Methods")

    # ----------------------------------------------------
    # 3.3 Software Requirements Specification (SRS)
    # ----------------------------------------------------
    add_section(doc, "3.3 Software Requirements Specification")

    add_subsection(doc, "3.3.1 User Requirements")
    add_body_paragraph(
        doc,
        "User requirements define the operational expectations and interactive capabilities provided to Site Reliability "
        "Engineers, system administrators, and evaluation evaluators:"
    )
    add_bullet_point(
        doc,
        "UR1: Real-Time Observability",
        "The user must be able to view real-time CPU, RAM, disk, latency, and error-rate vitals across Server A, Server B, "
        "and Server C with timestamped synchronization in Indian Standard Time (IST)."
    )
    add_bullet_point(
        doc,
        "UR2: Controlled Chaos Injection",
        "The user must be able to trigger targeted, non-destructive fault injection experiments (CPU stress, RAM leaks, "
        "latency surges, HTTP 500 error cascades, and node outages) directly from the visual dashboard."
    )
    add_bullet_point(
        doc,
        "UR3: Transparent AI Explanation",
        "The user must be provided with instant SHAP attribution breakdowns indicating the relative percentage impact of "
        "each telemetry metric on the computed outage probability."
    )
    add_bullet_point(
        doc,
        "UR4: Verifiable Traffic Audit Trail",
        "The user must be able to verify physical traffic routing via independent response headers ('X-Served-By', "
        "'X-Server-Port', 'X-Request-Number') and downloadable CSV audit proof logs."
    )

    add_subsection(doc, "3.3.2 System Requirements")
    add_body_paragraph(
        doc,
        "System requirements delineate the foundational constraints and platform preconditions necessary for correct execution:"
    )
    add_bullet_point(
        doc,
        "SR1: Containerized Execution",
        "All microservice target nodes and the HAProxy reverse proxy must execute within isolated Docker containers or "
        "dedicated host loopback processes communicating over standard TCP/IP network sockets."
    )
    add_bullet_point(
        doc,
        "SR2: Continuous Asynchronous Polling",
        "The telemetry harvesting engine must execute within an independent daemon thread, continuously sampling node metrics "
        "at 1.2-second intervals without blocking HTTP request serving threads."
    )
    add_bullet_point(
        doc,
        "SR3: Model Serialization & Persistence",
        "Trained Keras LSTM neural network weights (lstm_model.keras), MinMaxScaler parameters (scaler.pkl), and evaluation "
        "benchmarks (metrics.json) must be persisted on disk for instant runtime inference."
    )

    add_subsection(doc, "3.3.3 Functional Requirements")
    add_body_paragraph(
        doc,
        "Functional requirements formally specify the exact inputs, computational behaviors, and outputs mandated by the system:"
    )
    add_bullet_point(
        doc,
        "FR1: Layer-7 Ingress Load Balancing",
        "The system shall route incoming client HTTP requests on Port 80 to Server A under normal operations using HAProxy L7 routing."
    )
    add_bullet_point(
        doc,
        "FR2: Monotonic Request Accounting",
        "Each server instance shall maintain an atomic, monotonic counter of successfully served user requests, isolated from "
        "internal management and health inspection probes."
    )
    add_bullet_point(
        doc,
        "FR3: Cryptographic Proof Header Injection",
        "Every HTTP response served to clients shall include 'X-Served-By', 'X-Server-Port', and 'X-Request-Number' response headers."
    )
    add_bullet_point(
        doc,
        "FR4: Multi-Variate Telemetry Ingestion",
        "The system shall poll /api/metrics on each node every 1.2s, extracting CPU%, Memory%, Disk%, Latency (ms), and Error Rate."
    )
    add_bullet_point(
        doc,
        "FR5: Sliding-Window Feature Matrix Formatting",
        "The system shall maintain a sliding FIFO history queue of 30 snapshots, extracting the most recent 10-step sequence "
        "for ML neural inference."
    )
    add_bullet_point(
        doc,
        "FR6: Time-Series LSTM Outage Inference",
        "The system shall transform the 10x5 telemetry matrix via MinMaxScaler and execute Keras LSTM inference, generating an "
        "outage risk score between 0.0 and 1.0."
    )
    add_bullet_point(
        doc,
        "FR7: Dual-Model Comparison",
        "The system shall simultaneously evaluate a 100-tree Random Forest baseline model alongside the LSTM, providing comparative "
        "accuracy and probability validation."
    )
    add_bullet_point(
        doc,
        "FR8: Mathematical Digital Twin Divergence",
        "The system shall calculate a weighted divergence metric delta D = 0.35ΔCPU + 0.30ΔMem + 0.15ΔLat + 0.20ΔErr between Server A and Server B."
    )
    add_bullet_point(
        doc,
        "FR9: Predictive Failover Execution",
        "When computed risk >= 0.80 and Server A is still operational, the system shall execute predictive failover, migrating active traffic to Server B."
    )
    add_bullet_point(
        doc,
        "FR10: Reactive Emergency Failover",
        "If Server A returns HTTP 503 or suffers connection refusal, HAProxy health checks (fall 2) shall trigger emergency failover to Server B."
    )
    add_bullet_point(
        doc,
        "FR11: Autonomous Self-Healing Remediation",
        "Following predictive failover, the system shall asynchronously dispatch an autonomous recovery signal to Server A, resetting simulated stress."
    )
    add_bullet_point(
        doc,
        "FR12: Automatic Safe Failback",
        "When Server A recovers to 100% HEALTHY state and completes its stabilization cooldown, traffic shall be safely restored to Server A."
    )

    add_subsection(doc, "3.3.4 Non-Functional Requirements")
    add_body_paragraph(
        doc,
        "Non-functional requirements specify the performance benchmarks, reliability standards, security controls, and "
        "maintainability metrics governing the solution:"
    )
    add_bullet_point(
        doc,
        "NFR1: Failover Lead Time",
        "The LSTM prediction engine shall forecast impending failure at least 15 to 30 seconds prior to service collapse."
    )
    add_bullet_point(
        doc,
        "NFR2: Sub-Second Failover Latency",
        "The Automated Failover Controller shall execute traffic migration in under 1.5 seconds from risk threshold breach."
    )
    add_bullet_point(
        doc,
        "NFR3: Zero In-Flight Request Loss",
        "During proactive predictive failover, exactly 0.0% of client requests shall fail with HTTP 500, 502, or 503 errors."
    )
    add_bullet_point(
        doc,
        "NFR4: Inference Processing Overhead",
        "The LSTM forward pass (model.predict) and feature scaling shall consume less than 35 milliseconds per evaluation cycle."
    )
    add_bullet_point(
        doc,
        "NFR5: High Availability SLA Target",
        "The architecture shall preserve a 99.99% availability objective (SLO) under continuous high-concurrency client load."
    )
    add_bullet_point(
        doc,
        "NFR6: System Portability",
        "All components shall execute identically across native Linux container hosts and Windows development workstations."
    )
    add_bullet_point(
        doc,
        "NFR7: Auditability & Tamper-Proof Logging",
        "Every failover event, chaos trigger, and remediation step shall be logged with millisecond-precision IST timestamps."
    )
    add_bullet_point(
        doc,
        "NFR8: Fault Tolerance & Degraded Fallback",
        "If TensorFlow or Keras libraries encounter GPU/runtime exceptions, the system shall automatically fall back to Random Forest."
    )
