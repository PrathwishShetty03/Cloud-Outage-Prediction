import os


def _env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return int(default)


def _env_float(name, default):
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return float(default)


def _env_bool(name, default=False):
    raw = os.environ.get(name)
    if raw is None:
        return bool(default)
    return raw.strip().lower() in ("1", "true", "yes", "on")


class AutoscalerConfig:
    """
    Configurable min/max replica limits, watermarks, cooldown, and hysteresis.
    High/low watermark pairs form a deadband so the scaler does not oscillate.
    """

    def __init__(
        self,
        min_instances=None,
        max_instances=None,
        cooldown_seconds=None,
        hysteresis=None,
        cpu_high=None,
        cpu_low=None,
        memory_high=None,
        memory_low=None,
        latency_high_ms=None,
        latency_low_ms=None,
        request_rate_high=None,
        request_rate_low=None,
        scale_up_step=None,
        scale_down_step=None,
        eval_interval_seconds=None,
        apply_enabled=None,
        service_name=None,
        compose_file=None,
        compose_project_dir=None,
        app_dns_name=None,
        app_port=None,
        instance_urls=None,
        status_port=None,
    ):
        hysteresis = float(hysteresis if hysteresis is not None else _env_float("AUTOSCALE_HYSTERESIS", 0.30))
        hysteresis = min(0.80, max(0.05, hysteresis))

        cpu_high = float(cpu_high if cpu_high is not None else _env_float("AUTOSCALE_CPU_HIGH", 75.0))
        memory_high = float(memory_high if memory_high is not None else _env_float("AUTOSCALE_MEMORY_HIGH", 75.0))
        latency_high_ms = float(latency_high_ms if latency_high_ms is not None else _env_float("AUTOSCALE_LATENCY_HIGH_MS", 800.0))
        request_rate_high = float(request_rate_high if request_rate_high is not None else _env_float("AUTOSCALE_RPS_HIGH", 25.0))

        self.min_instances = int(min_instances if min_instances is not None else _env_int("AUTOSCALE_MIN_INSTANCES", 1))
        self.max_instances = int(max_instances if max_instances is not None else _env_int("AUTOSCALE_MAX_INSTANCES", 10))
        if self.min_instances < 1:
            self.min_instances = 1
        if self.max_instances < self.min_instances:
            self.max_instances = self.min_instances

        self.cooldown_seconds = float(cooldown_seconds if cooldown_seconds is not None else _env_float("AUTOSCALE_COOLDOWN_SECONDS", 45.0))
        self.hysteresis = hysteresis

        self.cpu_high = cpu_high
        self.cpu_low = float(cpu_low if cpu_low is not None else _env_float("AUTOSCALE_CPU_LOW", cpu_high * (1.0 - hysteresis)))
        self.memory_high = memory_high
        self.memory_low = float(memory_low if memory_low is not None else _env_float("AUTOSCALE_MEMORY_LOW", memory_high * (1.0 - hysteresis)))
        self.latency_high_ms = latency_high_ms
        self.latency_low_ms = float(latency_low_ms if latency_low_ms is not None else _env_float("AUTOSCALE_LATENCY_LOW_MS", latency_high_ms * (1.0 - hysteresis)))
        self.request_rate_high = request_rate_high
        self.request_rate_low = float(request_rate_low if request_rate_low is not None else _env_float("AUTOSCALE_RPS_LOW", request_rate_high * (1.0 - hysteresis)))

        self.scale_up_step = int(scale_up_step if scale_up_step is not None else _env_int("AUTOSCALE_UP_STEP", 1))
        self.scale_down_step = int(scale_down_step if scale_down_step is not None else _env_int("AUTOSCALE_DOWN_STEP", 1))
        self.eval_interval_seconds = float(eval_interval_seconds if eval_interval_seconds is not None else _env_float("AUTOSCALE_EVAL_INTERVAL_SECONDS", 10.0))
        self.apply_enabled = bool(apply_enabled if apply_enabled is not None else _env_bool("AUTOSCALE_APPLY", False))

        self.service_name = service_name if service_name is not None else os.environ.get("AUTOSCALE_SERVICE_NAME", "app")
        self.compose_file = compose_file if compose_file is not None else os.environ.get("COMPOSE_FILE", "docker-compose.yml")
        self.compose_project_dir = compose_project_dir if compose_project_dir is not None else os.environ.get("COMPOSE_PROJECT_DIR", os.getcwd())
        self.app_dns_name = app_dns_name if app_dns_name is not None else os.environ.get("APP_SERVICE_DNS", "app")
        self.app_port = int(app_port if app_port is not None else _env_int("APP_SERVICE_PORT", 5001))
        self.status_port = int(status_port if status_port is not None else _env_int("AUTOSCALE_PORT", 9090))

        urls_raw = instance_urls if instance_urls is not None else os.environ.get("APP_INSTANCE_URLS", "")
        if isinstance(urls_raw, str):
            self.instance_urls = [u.strip() for u in urls_raw.split(",") if u.strip()]
        else:
            self.instance_urls = list(urls_raw or [])
