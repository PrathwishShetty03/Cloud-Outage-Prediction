import time
import numpy as np

class SLOTracker:
    """
    SRE Service Level Objective (SLO), SLA & Error Budget Tracker.
    Calculates real Availability %, p95 Latency, Error Rate, and Error Budget consumption.
    """
    def __init__(self, availability_target=99.9, latency_target_ms=300.0, error_rate_target=0.01):
        self.availability_target = float(availability_target)
        self.latency_target_ms = float(latency_target_ms)
        self.error_rate_target = float(error_rate_target)
        self.latency_samples = []

    def calculate_slo(self, total_requests, successful_requests, failed_requests, current_latency_ms):
        """
        Calculates exact SRE metrics from empirical request counts and latency samples.
        """
        if current_latency_ms > 0:
            self.latency_samples.append(current_latency_ms)
            if len(self.latency_samples) > 200:
                self.latency_samples.pop(0)

        tot = max(1, int(total_requests))
        succ = int(successful_requests)
        fail = int(failed_requests)

        # Real Availability %
        availability_pct = round((succ / tot) * 100.0, 3)

        # Real Error Rate %
        error_rate = round((fail / tot), 4)
        error_rate_pct = round(error_rate * 100.0, 2)

        # Calculate p95 Latency from samples
        if self.latency_samples:
            p95_latency = round(float(np.percentile(self.latency_samples, 95)), 1)
            p50_latency = round(float(np.percentile(self.latency_samples, 50)), 1)
        else:
            p95_latency = round(current_latency_ms, 1)
            p50_latency = round(current_latency_ms, 1)

        # Error Budget Math (Allowed downtime / errors = 100% - target)
        allowed_error_ratio = (100.0 - self.availability_target) / 100.0  # e.g., 0.001 for 99.9%
        actual_error_ratio = (1.0 - (availability_pct / 100.0))

        if allowed_error_ratio > 0:
            budget_consumed_pct = round(min(100.0, (actual_error_ratio / allowed_error_ratio) * 100.0), 1)
        else:
            budget_consumed_pct = 0.0

        budget_remaining_pct = round(max(0.0, 100.0 - budget_consumed_pct), 1)

        is_slo_met = (
            availability_pct >= self.availability_target and
            p95_latency <= self.latency_target_ms and
            error_rate <= self.error_rate_target
        )

        return {
            "availability_pct": availability_pct,
            "availability_target": self.availability_target,
            "p95_latency_ms": p95_latency,
            "p50_latency_ms": p50_latency,
            "latency_target_ms": self.latency_target_ms,
            "error_rate": error_rate,
            "error_rate_pct": error_rate_pct,
            "error_rate_target": self.error_rate_target,
            "error_budget_consumed_pct": budget_consumed_pct,
            "error_budget_remaining_pct": budget_remaining_pct,
            "slo_status": "PASSING" if is_slo_met else "BREACHED"
        }
