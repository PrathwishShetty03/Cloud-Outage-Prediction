import socket
import requests


def discover_instance_urls(dns_name, port, extra_urls=None):
    """
    Resolves Docker Compose DNS A-records for a scaled service plus any explicit URLs.
    """
    urls = []
    for raw in extra_urls or []:
        u = (raw or "").strip().rstrip("/")
        if u:
            urls.append(u)
    if dns_name:
        try:
            infos = socket.getaddrinfo(dns_name, int(port), socket.AF_INET, socket.SOCK_STREAM)
            ips = sorted({item[4][0] for item in infos})
            for ip in ips:
                urls.append(f"http://{ip}:{int(port)}")
        except (socket.gaierror, OSError, ValueError, TypeError):
            pass
    seen = set()
    deduped = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)
    return deduped


def fetch_instance_metrics(base_url, timeout=2.0):
    try:
        r = requests.get(f"{base_url.rstrip('/')}/api/metrics", timeout=timeout)
        if r.status_code != 200:
            return {
                "instance_id": base_url,
                "cpu_percent": 100.0,
                "memory_percent": 100.0,
                "latency_ms": 5000.0,
                "request_rate": 0.0,
                "total_requests": 0,
                "healthy": False,
                "url": base_url,
            }
        data = r.json()
        status = str(data.get("status", "HEALTHY")).upper()
        return {
            "instance_id": data.get("server_id", data.get("server_name", base_url)),
            "cpu_percent": float(data.get("cpu_percent", data.get("cpu", 0.0))),
            "memory_percent": float(data.get("memory_percent", data.get("memory", 0.0))),
            "latency_ms": float(data.get("latency_ms", data.get("latency", 0.0))),
            "request_rate": float(data.get("request_rate", 0.0)),
            "total_requests": int(data.get("total_requests", data.get("request_count", 0))),
            "healthy": status in ("HEALTHY", "WARNING") and data.get("is_reachable", True) is not False,
            "url": base_url,
            "raw": data,
        }
    except Exception:
        return {
            "instance_id": base_url,
            "cpu_percent": 100.0,
            "memory_percent": 100.0,
            "latency_ms": 5000.0,
            "request_rate": 0.0,
            "total_requests": 0,
            "healthy": False,
            "url": base_url,
        }
