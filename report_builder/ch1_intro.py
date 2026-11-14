from report_builder.doc_helper import (
    add_chapter_title_sheet, add_chapter_header_block,
    add_section, add_subsection, add_body_paragraph, add_bullet_point
)

def build_chapter_1(doc):
    # Separate Chapter Title Sheet
    add_chapter_title_sheet(doc, "Chapter 1", "INTRODUCTION")

    # Chapter Header Block on First Page
    add_chapter_header_block(doc, "Chapter 1", "INTRODUCTION")

    # ----------------------------------------------------
    # 1.1 Overview
    # ----------------------------------------------------
    add_section(doc, "1.1 Overview")
    
    add_body_paragraph(
        doc,
        "Over the past two decades, cloud computing has transitioned from an innovative operational model into the "
        "foundational backbone of the modern global digital economy. Enterprise organizations, financial institutions, "
        "healthcare systems, telecommunication networks, and mission-critical government infrastructures rely almost "
        "exclusively on distributed cloud environments to deliver continuous, high-concurrency digital services. In this "
        "hyper-connected ecosystem, system availability is governed by rigorous Service Level Agreements (SLAs) that "
        "customarily demand 'five nines' (99.999%) availability—a stringent threshold permitting no more than 5.26 minutes "
        "of cumulative unplanned downtime per calendar year. Despite monumental advances in virtualization, container "
        "orchestration (e.g., Kubernetes), microservice decomposition, and elastic auto-scaling, sudden and catastrophic "
        "cloud outages remain an existential hazard. Unanticipated server failures cost enterprises upwards of $300,000 "
        "per hour in direct financial penalties, customer attrition, regulatory sanctions, and irreversible reputational harm."
    )

    add_body_paragraph(
        doc,
        "An in-depth analysis of major cloud outages in industrial data centers reveals that infrastructure crashes "
        "are seldom unheralded binary events. Instead, the overwhelming majority of outages stem from progressive, "
        "compounding resource degradation phenomena. These include memory leaks caused by uncollected heap allocations, "
        "computational CPU saturation induced by anomalous traffic surges, thread-pool starvation, input/output (I/O) "
        "bottlenecks, network packet drops, and cascading microservice dependency timeouts. Under conventional cloud "
        "architectures, load balancers such as HAProxy, NGINX, and AWS Application Load Balancers operate on a strictly "
        "reactive paradigm. These reverse proxies employ periodic layer-4 or layer-7 health checks—such as dispatching an "
        "HTTP GET /health request every 2 to 5 seconds. A node is marked as degraded only after failing a predefined "
        "consecutive threshold (known as the 'fall' count). Consequently, during the critical 5 to 30 second window "
        "while health checks are failing, hundreds or thousands of client HTTP requests continue to be forwarded to the "
        "failing server. These in-flight requests inevitably experience severe latency surges, connection timeouts, or "
        "HTTP 500/503 errors, leading to severe data loss and transactional inconsistency."
    )

    add_body_paragraph(
        doc,
        "To fundamentally eliminate this vulnerability, this major project proposes and implements the Intelligent "
        "Cloud Outage Detection and Prediction System using a Multi-Region Dual-Twin Server Architecture. Rather than "
        "waiting for hardware collapse or service unreachability, the proposed system introduces a proactive, machine "
        "learning-driven intelligence layer that continuously senses multi-dimensional system telemetry (CPU usage, "
        "memory allocation, disk utilization, response latency, and client error rates) at 1.2-second polling intervals. "
        "A Deep Long Short-Term Memory (LSTM) recurrent neural network evaluates sliding temporal sequence windows to "
        "detect subtle, non-linear degradation trajectories, forecasting impending failure up to 30 seconds before "
        "service interruption occurs. Concurrently, a synchronized Digital Twin server mirrors runtime state, and an "
        "Automated Failover Controller dynamically reroutes ingress traffic seamlessly through HAProxy with zero dropped "
        "requests. Root causes are mathematically deciphered using SHapley Additive exPlanations (SHAP), providing cloud "
        "Site Reliability Engineers (SREs) with actionable, interpretable transparency."
    )

    # ----------------------------------------------------
    # 1.2 Objectives
    # ----------------------------------------------------
    add_section(doc, "1.2 Objectives")

    add_body_paragraph(
        doc,
        "The overarching aim of this project is to architect, develop, and empirically validate an autonomous, "
        "proactive cloud resilience framework that transcends the latency and packet-loss drawbacks of reactive "
        "infrastructure management. The specific, quantifiable technical objectives are defined as follows:"
    )

    add_bullet_point(
        doc,
        "1. Architectural Multi-Tier Server Design",
        "Design and implement a robust 3-tier microservice compute cluster comprising a Primary Server A (port 5001), "
        "a Digital Twin Backup Server B (port 5002), and an Emergency Quarantine Server C (port 5003), managed under an L7 "
        "HAProxy reverse proxy gateway on port 80."
    )

    add_bullet_point(
        doc,
        "2. Real-Time Telemetry Pipeline",
        "Construct a lightweight, non-intrusive asynchronous telemetry harvesting worker that samples operating system "
        "and application vitals (psutil CPU percentage, virtual memory, disk storage, request latency, and HTTP error rates) "
        "without adding computational overhead to active client request execution."
    )

    add_bullet_point(
        doc,
        "3. Time-Series LSTM Outage Forecasting",
        "Engineer, train, and deploy a Deep Long Short-Term Memory (LSTM) sequence neural network capable of processing "
        "10-step rolling temporal matrices to forecast outage risk probability (0.0 to 1.0) with an empirical test accuracy "
        "exceeding 95% and an F1-score surpassing 98%."
    )

    add_bullet_point(
        doc,
        "4. Mathematical Digital Twin Divergence Modeling",
        "Formulate a real-time mathematical divergence scoring algorithm that continuously quantifies state alignment "
        "and metric deltas between the primary operational server and its virtual digital twin standby counterpart."
    )

    add_bullet_point(
        doc,
        "5. Explainable AI Root-Cause Attribution",
        "Incorporate SHapley Additive exPlanations (SHAP) to interpret ML model inferences in real-time, attributing failure "
        "probabilities to exact physical features (e.g., 68% CPU saturation, 22% memory leak) for auditability."
    )

    add_bullet_point(
        doc,
        "6. Zero-Downtime Predictive Failover & Self-Healing",
        "Integrate automated orchestration logic that executes predictive traffic redirection before service crash, "
        "freezing completed request counters on Server A while seamlessly migrating incoming traffic to Server B, "
        "coupled with an autonomous background self-healing remediation workflow."
    )

    # ----------------------------------------------------
    # 1.3 Purpose, Scope, and Applicability
    # ----------------------------------------------------
    add_section(doc, "1.3 Purpose, Scope, and Applicability")

    add_subsection(doc, "1.3.1 Purpose")
    add_body_paragraph(
        doc,
        "The primary purpose of this project is to eliminate the costly blind spot inherent in reactive cloud load "
        "balancers. In enterprise distributed systems, the delay between the physical onset of server degradation and the "
        "subsequent trigger of a reactive failover threshold represents a 'danger zone' where transactions fail silently, "
        "TCP connections terminate abruptly, and database writes corrupt. By shifting cloud fault tolerance from reactive "
        "remediation to proactive anticipation, this project creates an intelligent infrastructure buffer. It ensures that "
        "unhealthy server instances are quarantined, workloads are reallocated, and autonomous remediation routines "
        "(such as garbage collection, cache purging, or container restarts) are executed without human intervention or "
        "service disruption."
    )

    add_subsection(doc, "1.3.2 Scope")
    add_body_paragraph(
        doc,
        "The functional scope of this Major Project Phase II encompasses the end-to-end realization of a distributed "
        "cloud resiliency harness within a containerized Docker and microservices ecosystem. The scope covers: "
        "(a) Containerization of multi-node Python Flask application services; (b) Layer-7 HAProxy ingress load balancing "
        "with active-passive and dynamic backup routing rules; (c) Synthetic and empirical chaos fault injection modules "
        "simulating 10 distinct cloud failure modes (CPU saturation, RAM leaks, latency surges, HTTP 500 error cascades, "
        "disk pressure, and abrupt crashes); (d) Machine learning pipeline engineering including MinMax feature scaling, "
        "Keras LSTM model training, and Random Forest baseline comparative validation; (e) Real-time Site Reliability "
        "Engineering (SRE) metric tracking incorporating Error Budgets, Service Level Objectives (SLO), and Service Level "
        "Indicators (SLI); and (f) An interactive Streamlit visual command center alongside a dedicated live traffic "
        "demonstration harness operating on Indian Standard Time (IST)."
    )
    add_body_paragraph(
        doc,
        "Scope Boundaries: The system is designed to evaluate server-level computational, memory, latency, and microservice "
        "application degradation. Physical hardware power supply failures, data center physical fiber severance, and "
        "hypervisor kernel panics outside the host container network boundary fall outside the immediate scope of this software implementation."
    )

    add_subsection(doc, "1.3.3 Applicability")
    add_body_paragraph(
        doc,
        "The algorithms, architectural designs, and software frameworks developed in this project possess direct "
        "applicability across diverse enterprise domains, including:"
    )
    add_bullet_point(
        doc,
        "Financial Technology & Core Banking",
        "High-frequency algorithmic trading platforms, payment processing gateways (UPI, Visa/Mastercard processing), "
        "and banking transaction ledgers where a dropped HTTP session represents immediate monetary loss."
    )
    add_bullet_point(
        doc,
        "Large-Scale E-Commerce",
        "Online retail portals undergoing intense flash-sale traffic spikes where unexpected server slowdowns result in "
        "abandoned shopping carts and degraded customer satisfaction."
    )
    add_bullet_point(
        doc,
        "Healthcare & Telemedicine Systems",
        "Patient monitoring telemetry ingestion, electronic health record (EHR) databases, and emergency dispatch systems "
        "demanding absolute zero-packet-loss reliability."
    )
    add_bullet_point(
        doc,
        "Public Cloud Service Providers & Edge Computing",
        "Infrastructure-as-a-Service (IaaS) and Platform-as-a-Service (PaaS) hyperscalers seeking to augment native Kubernetes "
        "horizontal pod autoscaling (HPA) and ingress controllers with predictive AI-driven health intelligence."
    )

    # ----------------------------------------------------
    # 1.4 Organization of the Report
    # ----------------------------------------------------
    add_section(doc, "1.4 Organization of the Report")
    add_body_paragraph(
        doc,
        "This project report is systematically organized into nine comprehensive chapters, strictly structured in "
        "accordance with the Visvesvaraya Technological University (VTU) and Bangalore Institute of Technology (BIT) "
        "Major Project Phase II guidelines:"
    )

    add_bullet_point(
        doc,
        "Chapter 1: Introduction",
        "Presents the project background, motivation, formal technical objectives, purpose, scope, industrial applicability, "
        "and architectural roadmap."
    )
    add_bullet_point(
        doc,
        "Chapter 2: Literature Survey",
        "Reviews ten peer-reviewed research papers (2021–2025) in ascending chronological order, analyzing existing AIOps, "
        "anomaly detection, and digital twin techniques while identifying critical research gaps."
    )
    add_bullet_point(
        doc,
        "Chapter 3: Requirement Engineering",
        "Details hardware and software specifications, conceptual UML analysis models (Use Case, Sequence, Activity, "
        "State Chart, Class diagrams), and formal functional and non-functional requirements."
    )
    add_bullet_point(
        doc,
        "Chapter 4: Project Planning",
        "Outlines the Work Breakdown Structure (WBS), milestone scheduling, Agile sprint cycles, Gantt project timelines, "
        "and risk mitigation frameworks."
    )
    add_bullet_point(
        doc,
        "Chapter 5: System Design",
        "Elaborates the multi-tier system architecture, component decomposition, REST API interface contracts, sliding-window "
        "data structures, and mathematical algorithms."
    )
    add_bullet_point(
        doc,
        "Chapter 6: Implementation",
        "Provides an exhaustive exposition of the actual codebase, microservice endpoints, Prometheus scrapers, Keras LSTM "
        "models, SHAP explainer, Digital Twin engine, and failover controller."
    )
    add_bullet_point(
        doc,
        "Chapter 7: Testing",
        "Presents rigorous Unit, Integration, and System testing methodologies, detailing comprehensive test tables, inputs, "
        "expected outputs, actual results, and verification statuses."
    )
    add_bullet_point(
        doc,
        "Chapter 8: Results and Performance Analysis",
        "Documents empirical experimental results, model confusion matrices, ROC-AUC curves, dashboard screenshots, and a "
        "quantitative 3-way comparative benchmark."
    )
    add_bullet_point(
        doc,
        "Chapter 9: Applications and Conclusion",
        "Synthesizes project accomplishments, industrial deployments, limitations, and future research trajectories "
        "(Kubernetes operators, eBPF telemetry, multi-region mesh)."
    )
    add_bullet_point(
        doc,
        "References & Annexures",
        "Provides IEEE-formatted citations alongside Annexure A (Glossary), Annexure B (Paper Publication Draft), and "
        "Annexure C (Competition Certificates)."
    )
