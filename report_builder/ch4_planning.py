import os
from report_builder.doc_helper import (
    add_chapter_title_sheet, add_chapter_header_block,
    add_section, add_body_paragraph, add_bullet_point,
    add_table_title, create_styled_table, add_image_figure
)

def build_chapter_4(doc, assets_dir):
    # Separate Chapter Title Sheet
    add_chapter_title_sheet(doc, "Chapter 4", "PROJECT PLANNING")

    # Chapter Header Block on First Page
    add_chapter_header_block(doc, "Chapter 4", "PROJECT PLANNING")

    # ----------------------------------------------------
    # 4.1 Project Planning and Scheduling
    # ----------------------------------------------------
    add_section(doc, "4.1 Project Planning and Scheduling")
    add_body_paragraph(
        doc,
        "Systematic project planning, risk management, milestone definition, and developmental task scheduling "
        "form the cornerstone of successful software engineering endeavors. The Intelligent Cloud Outage Detection and "
        "Prediction System was executed across two cohesive academic cycles—Major Project Phase I (Problem Formulation, "
        "Literature Review, Architectural Modeling, and Containerized Baseline Setup) and Major Project Phase II (Dataset "
        "Engineering, Deep LSTM Training, Digital Twin Divergence Modeling, Automated Failover Controller Integration, "
        "Live Traffic Demo Harness Construction, and Empirical SRE Benchmarking). The planning adopted an Agile Scrum "
        "methodology structured around bi-weekly sprints, continuous integration, and mentor milestone reviews."
    )

    add_body_paragraph(
        doc,
        "The project lifecycle was decomposed into ten discrete developmental work packages. Table 4.1 details the "
        "Work Breakdown Structure (WBS), developmental deliverables, planned versus actual durations, and milestone validation criteria:"
    )

    add_table_title(doc, "Table 4.1: Major Project Work Breakdown Structure and Milestones Matrix")
    headers_plan = ["Work Package ID", "Development Phase & Module", "Duration", "Key Deliverable / Artifact", "Verification Milestone"]
    data_plan = [
        ["WP-01", "Domain Study & Literature Survey", "Weeks 1–4", "Comprehensive survey of 10 AIOps papers", "Approved problem statement & research gap"],
        ["WP-02", "SRS & UML Architectural Modeling", "Weeks 5–8", "UML Use Case, Sequence, Class models", "Signed Phase I SRS design specification"],
        ["WP-03", "Microservice Baseline & HAProxy Gateway", "Weeks 9–12", "Flask nodes on ports 5001-5003 + HAProxy", "Working HTTP ingress load balancing"],
        ["WP-04", "Phase I Interim Submission & Review", "Weeks 13–14", "Phase I Report & Initial viva presentation", "Internal Assessment approval"],
        ["WP-05", "Multi-Scenario Telemetry Generation", "Weeks 15–18", "1,500 synthetic sequences (10 scenarios)", "Balanced 70/15/15 scaled dataset"],
        ["WP-06", "LSTM Model Training & Optimization", "Weeks 19–22", "lstm_model.keras + scaler.pkl", "Achieved 99.11% accuracy on test split"],
        ["WP-07", "Digital Twin & Divergence Engine", "Weeks 23–26", "twin_engine.py divergence algorithm", "Real-time state synchronization verification"],
        ["WP-08", "Failover Controller & Remediation", "Weeks 27–30", "failover_controller.py + remediation", "Sub-1.2s zero-downtime traffic failover"],
        ["WP-09", "Streamlit Dashboard & Traffic Demo", "Weeks 31–34", "dashboard/ (8501) + traffic-demo/ (5050)", "Real-time IST UI with proof audit logs"],
        ["WP-10", "Phase II Final Report & Viva Defense", "Weeks 35–38", "Major_Project_Phase_II_Final_Report.docx", "Project Guide & Department final approval"]
    ]
    create_styled_table(doc, headers_plan, data_plan, [1.0, 1.8, 0.9, 1.8, 1.5])

    add_body_paragraph(
        doc,
        "Figure 4.1 illustrates the comprehensive Gantt chart representing the developmental trajectory, timeline "
        "interdependencies, and critical milestones across the entire 38-week academic project span:"
    )

    fig_gantt = os.path.join(assets_dir, "fig_4_1_gantt_chart.png")
    add_image_figure(doc, fig_gantt, "Figure 4.1: Gantt Chart for Major Project Phase I and Phase II Development Schedule")

    add_body_paragraph(
        doc,
        "Risk Management & Contingency Planning: Throughout project execution, three primary technical risks were proactively identified and managed:"
    )
    add_bullet_point(
        doc,
        "Risk 1: TensorFlow Runtime Instability on Windows Native Hosts",
        "Mitigation: The ML prediction engine was architected with an automatic fallback mechanism (OutagePredictor.load_models). "
        "If TensorFlow/Keras encounters platform or GPU library incompatibilities, the system automatically transitions "
        "inference to the Scikit-Learn Random Forest model without interrupting the 1.2-second telemetry cycle."
    )
    add_bullet_point(
        doc,
        "Risk 2: Monitoring Probe Request Contamination",
        "Mitigation: High-frequency telemetry polling (/api/metrics) and HAProxy health checking (/health) risked inflating "
        "the monotonic request counter on standby nodes. The server microservice code was refactored with an explicit "
        "is_management_path() gate, ensuring that only genuine client transactions are counted as served user traffic."
    )
    add_bullet_point(
        doc,
        "Risk 3: Failover Oscillation & Flapping",
        "Mitigation: Rapid failover switching back and forth between nodes (flapping) was prevented by introducing a mandatory "
        "stabilization cooldown window (DEFAULT_RECOVERY_SEC = 20.0s for Server A) and a sustained outage timer before autonomous "
        "failback is permitted."
    )
