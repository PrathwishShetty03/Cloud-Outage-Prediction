import os
import shutil
import subprocess


def _docker_bin():
    return shutil.which("docker")


def current_replica_count(service_name, project_dir=None):
    """
    Count running Compose replicas via `docker compose ps`.
    Returns None when the Docker CLI is unavailable.
    """
    docker = _docker_bin()
    if not docker:
        return None
    cwd = project_dir or os.getcwd()
    try:
        proc = subprocess.run(
            [docker, "compose", "ps", "-q", "--status", "running", service_name],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if proc.returncode != 0:
            return None
        ids = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        return len(ids)
    except (OSError, subprocess.TimeoutExpired):
        return None


def apply_replica_count(service_name, replicas, project_dir=None, compose_file="docker-compose.yml"):
    """
    Manual-compatible Compose scale: docker compose up -d --scale SERVICE=N --no-deps SERVICE
    """
    docker = _docker_bin()
    if not docker:
        return {"applied": False, "error": "docker CLI not found"}
    cwd = project_dir or os.getcwd()
    replicas = max(0, int(replicas))
    cmd = [
        docker, "compose",
        "-f", compose_file,
        "up", "-d",
        "--scale", f"{service_name}={replicas}",
        "--no-deps",
        service_name,
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        return {
            "applied": proc.returncode == 0,
            "replicas": replicas,
            "command": " ".join(cmd),
            "stdout": (proc.stdout or "")[-2000:],
            "stderr": (proc.stderr or "")[-2000:],
            "returncode": proc.returncode,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"applied": False, "error": str(exc), "replicas": replicas}
