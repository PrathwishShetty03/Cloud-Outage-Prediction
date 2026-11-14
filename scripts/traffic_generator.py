"""
Continuous Traffic Generator
==============================
Sends real HTTP user traffic through HAProxy (port 80) indefinitely.
HAProxy routes each request to the active backend (SERVER_A / B / C).
X-Served-By response header proves which server actually handled it.

Usage (outside Docker - from host machine):
    python scripts/traffic_generator.py

Usage (inside Docker network):
    python scripts/traffic_generator.py --url http://haproxy:80/ --rps 5

Press Ctrl+C to stop.
"""

import time
import argparse
import threading
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict

IST = timezone(timedelta(hours=5, minutes=30))

def ist_now():
    return datetime.now(IST).strftime("%H:%M:%S IST")

def send_one(url, session, counters, lock):
    try:
        r = session.get(url, timeout=5.0, headers={"Accept": "application/json"})
        served_by = r.headers.get("X-Served-By", r.headers.get("X-Served-By".lower(), "UNKNOWN"))
        req_num   = r.headers.get("X-Request-Number", "?")
        port      = r.headers.get("X-Server-Port", "?")
        status    = r.status_code

        with lock:
            counters["total"] += 1
            if status < 400:
                counters["success"] += 1
                counters["by_server"][served_by] += 1
            else:
                counters["errors"] += 1
                counters["by_server"][f"{served_by}[{status}]"] += 1

        # Live log line
        tag = "✅" if status < 400 else "❌"
        print(f"[{ist_now()}] {tag} #{counters['total']:>5} → HTTP {status} | "
              f"Routed→ {served_by} :{port} | ServerReq#{req_num}")

    except Exception as e:
        with lock:
            counters["total"] += 1
            counters["errors"] += 1
        print(f"[{ist_now()}] ⚠️  #{counters['total']:>5} → CONNECTION ERROR: {e}")


def stats_printer(counters, lock, interval=10):
    """Prints a summary every `interval` seconds."""
    while True:
        time.sleep(interval)
        with lock:
            total   = counters["total"]
            success = counters["success"]
            errors  = counters["errors"]
            by_srv  = dict(counters["by_server"])
        print("\n" + "─" * 60)
        print(f"  📊 TRAFFIC SUMMARY  [{ist_now()}]")
        print(f"  Total: {total}  |  Success: {success}  |  Errors: {errors}")
        print("  Distribution by server (X-Served-By):")
        for srv, cnt in sorted(by_srv.items(), key=lambda x: -x[1]):
            pct = (cnt / max(1, total)) * 100
            bar = "█" * int(pct / 4)
            print(f"    {srv:<20} {cnt:>5} requests  ({pct:5.1f}%)  {bar}")
        print("─" * 60 + "\n")


def run(url, rps, threads):
    print("=" * 60)
    print(f"  🚀 Continuous Traffic Generator")
    print(f"  Target  : {url}")
    print(f"  Rate    : {rps} req/s  |  Workers: {threads}")
    print(f"  Started : {ist_now()}")
    print("  Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    counters = {
        "total": 0,
        "success": 0,
        "errors": 0,
        "by_server": defaultdict(int)
    }
    lock = threading.Lock()
    delay = 1.0 / rps  # inter-request delay per thread

    # Stats printer thread
    t_stats = threading.Thread(target=stats_printer, args=(counters, lock, 10), daemon=True)
    t_stats.start()

    sessions = [requests.Session() for _ in range(threads)]

    try:
        while True:
            thread_list = []
            for i in range(threads):
                t = threading.Thread(
                    target=send_one,
                    args=(url, sessions[i % len(sessions)], counters, lock),
                    daemon=True
                )
                t.start()
                thread_list.append(t)
            # Wait between bursts to maintain target RPS
            time.sleep(delay * threads)
    except KeyboardInterrupt:
        print(f"\n\n[{ist_now()}] 🛑 Traffic generator stopped by user.")
        with lock:
            total   = counters["total"]
            success = counters["success"]
            errors  = counters["errors"]
            by_srv  = dict(counters["by_server"])
        print("\n📋 FINAL SUMMARY:")
        print(f"  Total Sent : {total}")
        print(f"  Successful : {success}")
        print(f"  Errors     : {errors}")
        print("  By Server  :")
        for srv, cnt in sorted(by_srv.items(), key=lambda x: -x[1]):
            print(f"    {srv}: {cnt}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Continuous traffic generator through HAProxy")
    parser.add_argument("--url",     default="http://localhost:80/", help="HAProxy URL (default: http://localhost:80/)")
    parser.add_argument("--rps",     type=float, default=3.0,        help="Requests per second (default: 3)")
    parser.add_argument("--threads", type=int,   default=2,          help="Concurrent worker threads (default: 2)")
    args = parser.parse_args()
    run(args.url, args.rps, args.threads)
