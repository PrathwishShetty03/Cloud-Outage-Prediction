import time
from dataclasses import dataclass, field


@dataclass
class InstanceSnapshot:
    instance_id: str
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    latency_ms: float = 0.0
    request_rate: float = 0.0
    total_requests: int = 0
    healthy: bool = True


@dataclass
class ScaleDecision:
    action: str
    current_instances: int
    desired_instances: int
    healthy_instances: int
    reason: str
    in_cooldown: bool
    signals: dict = field(default_factory=dict)


class RuleBasedAutoscaler:
    """
    Rule-based horizontal autoscaler (no ML capacity model).

    Scale-up if any high watermark is exceeded (CPU, memory, per-instance
    request rate, or latency), or if healthy instance count is below min.

    Scale-down only when every signal is below its low watermark (hysteresis
    deadband) and replica count is above min.

    Cooldown blocks another scale action until cooldown_seconds have elapsed.
    """

    def __init__(self, config):
        self.config = config
        self._last_scale_ts = 0.0
        self._prev_totals = {}
        self._prev_ts = None

    def compute_request_rates(self, instances, now=None):
        """Fills request_rate from total_requests deltas when callers omit RPS."""
        now = time.time() if now is None else now
        dt = (now - self._prev_ts) if self._prev_ts else 0.0
        for inst in instances:
            prev = self._prev_totals.get(inst.instance_id)
            if dt > 0 and prev is not None:
                inst.request_rate = max(0.0, (inst.total_requests - prev) / dt)
            elif inst.request_rate:
                pass
            else:
                inst.request_rate = 0.0
            self._prev_totals[inst.instance_id] = inst.total_requests
        self._prev_ts = now
        return instances

    def _aggregate(self, instances):
        n = max(1, len(instances))
        healthy = [i for i in instances if i.healthy]
        cpu = sum(i.cpu_percent for i in instances) / n
        mem = sum(i.memory_percent for i in instances) / n
        lat = sum(i.latency_ms for i in instances) / n
        rps_total = sum(i.request_rate for i in instances)
        rps_per_instance = rps_total / n
        return {
            "avg_cpu": round(cpu, 2),
            "avg_memory": round(mem, 2),
            "avg_latency_ms": round(lat, 2),
            "request_rate_total": round(rps_total, 3),
            "request_rate_per_instance": round(rps_per_instance, 3),
            "healthy_instances": len(healthy),
            "observed_instances": len(instances),
        }

    def evaluate(self, instances, replica_count=None, now=None):
        now = time.time() if now is None else now
        instances = list(instances or [])
        cfg = self.config
        current = replica_count if replica_count is not None else len(instances)
        current = max(0, int(current))

        signals = self._aggregate(instances) if instances else {
            "avg_cpu": 0.0,
            "avg_memory": 0.0,
            "avg_latency_ms": 0.0,
            "request_rate_total": 0.0,
            "request_rate_per_instance": 0.0,
            "healthy_instances": 0,
            "observed_instances": 0,
        }
        signals["active_instance_count"] = current
        healthy = signals["healthy_instances"]

        desired = current
        reason = "HOLD: metrics inside hysteresis deadband"
        action = "hold"

        scale_up_needed = False
        scale_up_reasons = []
        if current < cfg.min_instances:
            scale_up_needed = True
            scale_up_reasons.append(f"replicas {current} < min {cfg.min_instances}")
        if instances and healthy < cfg.min_instances:
            scale_up_needed = True
            scale_up_reasons.append(f"healthy {healthy} < min {cfg.min_instances}")
        if signals["avg_cpu"] >= cfg.cpu_high:
            scale_up_needed = True
            scale_up_reasons.append(f"cpu {signals['avg_cpu']}>= {cfg.cpu_high}")
        if signals["avg_memory"] >= cfg.memory_high:
            scale_up_needed = True
            scale_up_reasons.append(f"memory {signals['avg_memory']}>= {cfg.memory_high}")
        if signals["avg_latency_ms"] >= cfg.latency_high_ms:
            scale_up_needed = True
            scale_up_reasons.append(f"latency {signals['avg_latency_ms']}ms>= {cfg.latency_high_ms}")
        if signals["request_rate_per_instance"] >= cfg.request_rate_high:
            scale_up_needed = True
            scale_up_reasons.append(
                f"rps/instance {signals['request_rate_per_instance']}>= {cfg.request_rate_high}"
            )

        scale_down_ok = (
            current > cfg.min_instances
            and signals["avg_cpu"] <= cfg.cpu_low
            and signals["avg_memory"] <= cfg.memory_low
            and signals["avg_latency_ms"] <= cfg.latency_low_ms
            and signals["request_rate_per_instance"] <= cfg.request_rate_low
            and (not instances or healthy >= max(1, current - cfg.scale_down_step))
        )

        if scale_up_needed and current < cfg.max_instances:
            desired = min(cfg.max_instances, current + cfg.scale_up_step)
            if current < cfg.min_instances:
                desired = min(cfg.max_instances, max(desired, cfg.min_instances))
            action = "scale_up"
            reason = "SCALE_UP: " + "; ".join(scale_up_reasons)
        elif scale_up_needed and current >= cfg.max_instances:
            action = "hold"
            reason = f"HOLD: at max_instances={cfg.max_instances} ({'; '.join(scale_up_reasons)})"
            desired = cfg.max_instances
        elif scale_down_ok:
            desired = max(cfg.min_instances, current - cfg.scale_down_step)
            action = "scale_down"
            reason = (
                f"SCALE_DOWN: cpu={signals['avg_cpu']} mem={signals['avg_memory']} "
                f"lat={signals['avg_latency_ms']} rps/inst={signals['request_rate_per_instance']} "
                f"all below low watermarks"
            )
        elif current > cfg.max_instances:
            desired = cfg.max_instances
            action = "scale_down"
            reason = f"SCALE_DOWN: replicas {current} > max {cfg.max_instances}"

        in_cooldown = False
        if action in ("scale_up", "scale_down") and desired != current:
            elapsed = now - self._last_scale_ts
            if self._last_scale_ts > 0 and elapsed < cfg.cooldown_seconds:
                in_cooldown = True
                reason = (
                    f"COOLDOWN: {round(cfg.cooldown_seconds - elapsed, 1)}s remaining "
                    f"(blocked {action} {current}->{desired})"
                )
                action = "hold"
                desired = current
            else:
                self._last_scale_ts = now
        else:
            action = "hold"
            desired = current
            if reason.startswith("SCALE_"):
                reason = "HOLD: no replica change required"

        return ScaleDecision(
            action=action,
            current_instances=current,
            desired_instances=int(desired),
            healthy_instances=healthy,
            reason=reason,
            in_cooldown=in_cooldown,
            signals=signals,
        )
