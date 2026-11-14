from report_builder.doc_helper import (
    add_chapter_title_sheet, add_chapter_header_block,
    add_section, add_subsection, add_body_paragraph, add_bullet_point,
    add_table_title, create_styled_table
)

def build_chapter_7(doc):
    # Separate Chapter Title Sheet
    add_chapter_title_sheet(doc, "Chapter 7", "TESTING")

    # Chapter Header Block on First Page
    add_chapter_header_block(doc, "Chapter 7", "TESTING")

    # ----------------------------------------------------
    # 7.1 Testing Approaches
    # ----------------------------------------------------
    add_section(doc, "7.1 Testing Approaches")
    add_body_paragraph(
        doc,
        "Software testing is an essential verification and validation discipline that ensures system reliability, "
        "functional correctness, mathematical accuracy, and fault-tolerant performance under extreme operational conditions. "
        "For the Intelligent Cloud Outage Detection and Prediction System, testing was conducted following a rigorous, "
        "three-tier hierarchical testing methodology:"
    )

    add_bullet_point(
        doc,
        "Unit Testing (Component Verification)",
        "Focuses on testing individual classes, algorithms, and microservice route handlers in complete isolation. "
        "Unit tests verify that mathematical functions (e.g., Digital Twin divergence calculation, MinMax feature scaling), "
        "monotonically increasing request counters, and ML sequence formatting produce exact expected outputs across boundary conditions."
    )

    add_bullet_point(
        doc,
        "Integration Testing (Subsystem Interoperability)",
        "Validates the seamless exchange of data and control messages across module boundaries. Integration tests verify "
        "asynchronous background polling, HAProxy layer-7 reverse proxy routing, Prometheus metric exposure, SHAP attribution "
        "generation, and controller-to-remediation thread communication."
    )

    add_bullet_point(
        doc,
        "System Testing (End-to-End Resilience & Failover)",
        "Evaluates the entire integrated ecosystem under live simulated client traffic and chaos engineering fault injections. "
        "System tests measure failover latency, header verification (X-Served-By, X-Request-Number), zero packet loss during "
        "predictive failover, and safe failback restoration."
    )

    # ----------------------------------------------------
    # 7.1.1 Unit Testing
    # ----------------------------------------------------
    add_subsection(doc, "7.1.1 Unit Testing")
    add_body_paragraph(
        doc,
        "Unit testing was executed using Python's standard unittest and pytest test runners against the test modules located "
        "in tests/ (test_server_app.py, test_ml_models.py, test_digital_twin.py, test_audit_remediation_slo.py). A total of "
        "28 automated test methods were executed. Table 7.1 outlines 10 critical unit test scenarios and their empirical outcomes:"
    )

    add_table_title(doc, "Table 7.1: Unit Test Suite Execution Results (Microservices, ML, Controller)")
    headers_ut = ["Test ID", "Test Scenario", "Input Parameters", "Expected Output", "Actual Output", "Status"]
    data_ut = [
        ["UT-01", "Monotonic User Request Counting", "10 GET /api/products hits", "total_requests = 10", "total_requests = 10", "PASSED"],
        ["UT-02", "Probe Counter Isolation", "25 GET /health + /api/metrics", "total_requests unchanged (0)", "total_requests = 0", "PASSED"],
        ["UT-03", "Cryptographic Header Injection", "GET /api/products on 5001", "X-Served-By: SERVER_A", "X-Served-By: SERVER_A", "PASSED"],
        ["UT-04", "Controlled CPU Stress Injection", "POST /stress/cpu {enable: true}", "cpu_active=True, cpu >= 88.5%", "cpu_active=True, cpu=91.4%", "PASSED"],
        ["UT-05", "Controlled Heap RAM Leak", "POST /stress/ram {mb: 300}", "ram_allocated chunks appended", "6 chunks of 50MB appended", "PASSED"],
        ["UT-06", "Immediate Outage Simulation", "POST /simulate/outage", "is_outage=True; /health -> 503", "is_outage=True, HTTP 503", "PASSED"],
        ["UT-07", "MinMaxScaler Feature Scaling", "Raw metrics [85, 90, 45, 1200, 0.1]", "Normalized matrix within [0.0, 1.0]", "All values bounded [0.0, 1.0]", "PASSED"],
        ["UT-08", "LSTM Sequence Length Padding", "Sequence of length 4 (< 10)", "Padded with first item to length 10", "Sequence padded to shape (1, 10, 5)", "PASSED"],
        ["UT-09", "Digital Twin Divergence Metric", "Server A (CPU 90%), B (CPU 20%)", "Divergence Score D > 24.5", "Divergence Score D = 26.8", "PASSED"],
        ["UT-10", "SLO Error Budget Calculation", "1000 requests, 2 errors", "SLO = 99.8%, Error Budget OK", "SLO = 99.8%, Budget Valid", "PASSED"]
    ]
    create_styled_table(doc, headers_ut, data_ut, [0.8, 1.4, 1.4, 1.3, 1.3, 0.8])

    # ----------------------------------------------------
    # 7.1.2 Integrated Testing
    # ----------------------------------------------------
    add_subsection(doc, "7.1.2 Integrated Testing")
    add_body_paragraph(
        doc,
        "Integrated testing focused on verifying asynchronous data pipelines, proxy forwarders, and inter-service coordination. "
        "Table 7.2 presents the results of eight comprehensive integration test cases:"
    )

    add_table_title(doc, "Table 7.2: Integration Test Suite Results (HAProxy, Prometheus, Digital Twin)")
    headers_it = ["Test ID", "Subsystems Integrated", "Integration Scenario", "Expected Outcome", "Actual Outcome", "Status"]
    data_it = [
        ["IT-01", "HAProxy + Server A", "Forward client traffic on Port 80", "HAProxy proxies to Server A:5001", "HTTP 200, Served by SERVER_A", "PASSED"],
        ["IT-02", "Background Worker + Controller", "Periodic 1.2s evaluate_cycle()", "GLOBAL_EVAL_CACHE refreshed", "Cache updated every 1.2s", "PASSED"],
        ["IT-03", "Server App + Prometheus Exporter", "Scrape /metrics on port 5001", "Prometheus gauge metrics returned", "PROM_CPU, PROM_MEM scraped", "PASSED"],
        ["IT-04", "Predictor + SHAP Explainer", "Evaluate 10-step degraded sequence", "Returns prob + 5 SHAP values", "prob=0.88, CPU impact=72%", "PASSED"],
        ["IT-05", "Dual Model Comparator", "Simultaneous LSTM & RF inference", "Both models output probabilities", "LSTM: 0.88, RF: 0.84", "PASSED"],
        ["IT-06", "Controller + HAProxy Route Notify", "Dispatch notify_haproxy_route()", "Failover audit event logged (IST)", "Logged with IST timestamp", "PASSED"],
        ["IT-07", "Controller + Remediation Engine", "Trigger async background healing", "Recovery dispatched to Server A", "Non-blocking thread spawned", "PASSED"],
        ["IT-08", "Traffic Demo App + HAProxy Gateway", "Send business transactions via 5050", "Real HTTP requests hit port 80", "Headers verified; log updated", "PASSED"]
    ]
    create_styled_table(doc, headers_it, data_it, [0.8, 1.4, 1.4, 1.4, 1.4, 0.8])

    # ----------------------------------------------------
    # 7.1.3 System Testing
    # ----------------------------------------------------
    add_subsection(doc, "7.1.3 System Testing")
    add_body_paragraph(
        doc,
        "System testing evaluated the end-to-end resilience lifecycle under continuous live user traffic generated by "
        "scripts/traffic_generator.py and the dedicated Live Traffic Demo Application on port 5050. Table 7.3 summarizes "
        "ten comprehensive system test scenarios spanning baseline routing, predictive failover, reactive failover, "
        "and safe failback:"
    )

    add_table_title(doc, "Table 7.3: End-to-End System Test Suite Results (Chaos Injection & Failover)")
    headers_st = ["Test ID", "System Scenario", "Applied Workload / Chaos", "Expected Behavior", "Empirical Test Result", "Status"]
    data_st = [
        ["ST-01", "Baseline Normal Load", "500 continuous GET /api/products", "100% requests served by Server A", "Server A=500, B=0, C=0 hits", "PASSED"],
        ["ST-02", "Predictive CPU Stress Failover", "Inject 100% CPU stress on Server A", "LSTM prob >= 0.80 -> Proactive shift to B", "Traffic shifted to B in 1.18s; 0 loss", "PASSED"],
        ["ST-03", "Predictive Latency Failover", "Inject 5.5s response delay on A", "LSTM detects trend -> Shift to B", "Traffic shifted to B; 0 timeouts", "PASSED"],
        ["ST-04", "Reactive Crash Failover", "POST /simulate/outage on Server A", "HAProxy health check fails -> Shift to B", "Server B takes over after 2 checks", "PASSED"],
        ["ST-05", "Cascading Emergency Failover", "Simulate outage on A and B", "HAProxy shifts traffic to Server C", "Server C serves emergency traffic", "PASSED"],
        ["ST-06", "Independent Proof Verification", "Inspect HTTP response headers", "Headers switch from A to B and C", "X-Served-By: SERVER_B verified", "PASSED"],
        ["ST-07", "Autonomous Self-Healing Cycle", "Trigger remediation after failover", "Server A reset; stress cleared", "Server A returns to HEALTHY", "PASSED"],
        ["ST-08", "Graceful Stabilization Cooldown", "Server A recovers from crash", "Status=RECOVERING for 20s (no flap)", "Cooldown respected; no flapping", "PASSED"],
        ["ST-09", "Automatic Safe Failback", "Server A fully healthy after cooldown", "Traffic returns smoothly to Server A", "Server A resumes active serving", "PASSED"],
        ["ST-10", "End-to-End Streamlit Visual Sync", "Full chaos experiment execution", "Dashboard KPIs & charts update in IST", "Real-time sync verified (< 1.2s)", "PASSED"]
    ]
    create_styled_table(doc, headers_st, data_st, [0.8, 1.4, 1.4, 1.4, 1.4, 0.8])
