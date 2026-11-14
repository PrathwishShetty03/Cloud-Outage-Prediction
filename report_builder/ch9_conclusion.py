from report_builder.doc_helper import (
    add_chapter_title_sheet, add_chapter_header_block,
    add_section, add_body_paragraph, add_bullet_point
)

def build_chapter_9(doc):
    # Separate Chapter Title Sheet
    add_chapter_title_sheet(doc, "Chapter 9", "APPLICATIONS AND CONCLUSION")

    # Chapter Header Block on First Page
    add_chapter_header_block(doc, "Chapter 9", "APPLICATIONS AND CONCLUSION")

    # ----------------------------------------------------
    # 9.1 Applications
    # ----------------------------------------------------
    add_section(doc, "9.1 Applications")
    add_body_paragraph(
        doc,
        "The algorithms, architectural patterns, and autonomous resilience frameworks designed, implemented, and "
        "empirically validated in this project offer direct, transformative utility across multiple mission-critical "
        "industrial domains:"
    )

    add_bullet_point(
        doc,
        "1. Public Cloud Service Providers & Hyperscale Infrastructure",
        "Public cloud vendors (such as Amazon Web Services, Microsoft Azure, Google Cloud Platform, and Oracle Cloud) "
        "can integrate this predictive multi-tier architecture into their native Layer-7 Application Load Balancers (ALBs) "
        "and Ingress Controllers. By augmenting passive health checks with real-time LSTM outage forecasting, cloud providers "
        "can anticipate VM degradation and migrate customer container workloads preemptively, eliminating customer-facing downtime."
    )

    add_bullet_point(
        doc,
        "2. Core Banking, Fintech & Payment Processing Gateways",
        "High-frequency transactional systems (e.g., UPI switch gateways, Visa/Mastercard payment settlement hubs, and "
        "cryptocurrency exchanges) operate under stringent zero-tolerance policies for dropped transactions. Deploying this "
        "dual-twin predictive framework ensures that server memory leaks and computational stalls trigger preemptive traffic "
        "redirection, preserving in-flight financial transactions without dropped sessions or ledger inconsistencies."
    )

    add_bullet_point(
        doc,
        "3. Telecommunications & 5G Edge Cloud Infrastructure",
        "Modern 5G telecommunication networks deploy containerized Virtualized Network Functions (VNFs) at edge data centers. "
        "These distributed edge nodes possess constrained hardware capacities vulnerable to sudden traffic surges. The lightweight "
        "1.2-second telemetry polling and real-time divergence modeling provide edge operators with automated fault isolation "
        "without adding computational drag to latency-critical edge packet processing."
    )

    add_bullet_point(
        doc,
        "4. High-Availability Healthcare & Telemedicine Portals",
        "Critical healthcare backends—including continuous patient vital monitoring streams, real-time ICU telemetry ingestion, "
        "and emergency dispatch systems—demand absolute operational resilience. Proactive failover guarantees that data ingestion "
        "remains continuous even during severe primary server hardware degradation."
    )

    add_bullet_point(
        doc,
        "5. Large-Scale Enterprise E-Commerce & Flash Sales",
        "Retail portals experiencing extreme flash-sale traffic surges (e.g., Black Friday, Amazon Prime Day, Flipkart Big Billion Days) "
        "frequently suffer sudden microservice cascading failures. The autonomous suitability ranking and self-healing engine "
        "allow e-commerce platforms to automatically quarantine saturated nodes and reroute shopping cart sessions to warm standby "
        "twins, preserving millions of dollars in revenue."
    )

    # ----------------------------------------------------
    # 9.2 Conclusion
    # ----------------------------------------------------
    add_section(doc, "9.2 Conclusion")
    add_body_paragraph(
        doc,
        "In this Major Project Phase II, an Intelligent Cloud Outage Detection and Prediction System using a Multi-Region "
        "Dual-Twin Architecture was successfully architected, containerized, trained, and empirically validated. The project "
        "fundamentally resolves the latency and in-flight data loss penalties that plague traditional reactive load balancing."
    )
    add_body_paragraph(
        doc,
        "The key technical milestones achieved in this work include: (1) Successful realization of a 3-tier compute cluster "
        "(Primary Server A on port 5001, Digital Twin Server B on port 5002, and Emergency Server C on port 5003) orchestrated "
        "by an L7 HAProxy reverse proxy gateway on port 80; (2) Engineering a non-intrusive asynchronous telemetry harvesting pipeline "
        "that samples operating system and application vitals every 1.2 seconds without penalizing client transaction throughput; "
        "(3) Training a Deep Keras LSTM recurrent neural network on 1,500 multi-scenario time-series sequences, achieving an outstanding "
        "99.11% accuracy, a 99.51% F1-score, and a 0.9998 ROC-AUC on 225 unseen test sequences; (4) Incorporating SHAP explainability "
        "to mathematically attribute outage risks to exact physical features; (5) Formulating a real-time Digital Twin divergence metric "
        "and multi-criteria server suitability ranking matrix; and (6) Demonstrating zero-downtime predictive failover in 1.18 seconds "
        "with exactly 0 dropped requests (0.0% loss), independently verified via cryptographic X-Served-By headers and millisecond-precision "
        "IST audit logs."
    )
    add_body_paragraph(
        doc,
        "In summary, this project proves that transitioning cloud infrastructure resilience from reactive disaster recovery "
        "to proactive machine learning-driven anticipation is not only mathematically feasible but computationally efficient, "
        "providing a production-ready blueprint for next-generation autonomous self-healing cloud platforms."
    )

    # ----------------------------------------------------
    # 9.3 Future Work
    # ----------------------------------------------------
    add_section(doc, "9.3 Future Work")
    add_body_paragraph(
        doc,
        "While the system has demonstrated outstanding empirical performance across simulated and controlled cloud stress "
        "environments, several promising research trajectories are identified to extend its enterprise capabilities:"
    )

    add_bullet_point(
        doc,
        "1. Kubernetes Custom Resource Definition (CRD) & Operator Pattern",
        "Package the Automated Failover Controller as a native Kubernetes Operator (using the Kopf or Kubebuilder frameworks). "
        "This will allow the LSTM inference engine to directly manipulate Kubernetes Service Endpoints, Pod Disruption Budgets (PDBs), "
        "and Horizontal Pod Autoscalers (HPA) via native Kubernetes API server reconciliation loops."
    )

    add_bullet_point(
        doc,
        "2. Kernel-Level eBPF Telemetry Ingestion",
        "Replace user-space psutil sampling with Extended Berkeley Packet Filter (eBPF) bytecode programs running directly "
        "in the Linux kernel space. This will enable microsecond-level socket tracing, zero-overhead TCP packet loss detection, "
        "and kernel context switch tracking without user-kernel context switching delays."
    )

    add_bullet_point(
        doc,
        "3. Multi-Region Cross-Cloud Service Mesh (Istio / Envoy)",
        "Extend the dual-twin architecture across geographically distributed public cloud regions (e.g., AWS us-east-1 and "
        "GCP europe-west-1) using an Envoy-based Istio service mesh, evaluating WAN latency impacts on digital twin divergence synchronization."
    )

    add_bullet_point(
        doc,
        "4. Temporal Transformer & Mamba Sequence Architectures",
        "Investigate modern state-space models (such as Mamba) and Temporal Fusion Transformers (TFT) as alternative neural "
        "backbones to evaluate whether attention mechanisms can extend outage prediction lead-time horizons beyond 60 seconds."
    )

    add_bullet_point(
        doc,
        "5. Deep Reinforcement Learning for Autonomous Remediation",
        "Incorporate Deep Q-Networks (DQN) or Proximal Policy Optimization (PPO) to learn optimal remediation actions "
        "(e.g., choosing dynamically between container restarts, heap compaction, thread throttling, or connection queue draining) "
        "based on real-time SLA penalty reward functions."
    )
