import argparse
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def send_single_request(url):
    try:
        r = requests.get(url, timeout=3.0)
        served_by = r.headers.get("X-Served-By", "UNKNOWN")
        port = r.headers.get("X-Server-Port", "UNKNOWN")
        req_num = r.headers.get("X-Request-Number", "N/A")
        return {"status_code": r.status_code, "served_by": served_by, "port": port, "req_num": req_num, "error": None}
    except Exception as e:
        return {"status_code": 500, "served_by": "ERROR", "port": "N/A", "req_num": "N/A", "error": str(e)}

def send_traffic(url, count=500, threads=1, delay=0.005):
    print(f"[LOAD GENERATOR] Sending {count} HTTP requests to {url} across {threads} thread(s)...")
    success = 0
    errors = 0
    server_counts = {}

    if threads <= 1:
        for i in range(1, count + 1):
            res = send_single_request(url)
            if res["error"] is None and res["status_code"] < 400:
                success += 1
                srv = res["served_by"]
                server_counts[srv] = server_counts.get(srv, 0) + 1
            else:
                errors += 1

            if i % 50 == 0 or i == count or i <= 10:
                print(f"Request #{i:03d} -> HTTP {res['status_code']} | X-Served-By: {res['served_by']} (Port {res['port']}) | Server Request #{res['req_num']}")

            if delay > 0:
                time.sleep(delay)
    else:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(send_single_request, url) for _ in range(count)]
            for i, future in enumerate(as_completed(futures), 1):
                res = future.result()
                if res["error"] is None and res["status_code"] < 400:
                    success += 1
                    srv = res["served_by"]
                    server_counts[srv] = server_counts.get(srv, 0) + 1
                else:
                    errors += 1

                if i % 50 == 0 or i == count or i <= 10:
                    print(f"Request #{i:03d} -> HTTP {res['status_code']} | X-Served-By: {res['served_by']} (Port {res['port']}) | Server Request #{res['req_num']}")

    print("\n--- TRAFFIC GENERATION SUMMARY ---")
    print(f"Total Sent: {count} | Successful: {success} | Failed: {errors}")
    print("Breakdown by X-Served-By header:")
    for srv, cnt in server_counts.items():
        print(f"  - {srv}: {cnt} requests")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send HTTP requests through HAProxy")
    parser.add_argument("--url", default="http://localhost:80/", help="Target HAProxy URL")
    parser.add_argument("--count", type=int, default=500, help="Number of requests")
    parser.add_argument("--threads", type=int, default=1, help="Number of concurrent worker threads")
    parser.add_argument("--delay", type=float, default=0.005, help="Delay between requests in seconds")
    args = parser.parse_args()

    send_traffic(args.url, args.count, args.threads, args.delay)
