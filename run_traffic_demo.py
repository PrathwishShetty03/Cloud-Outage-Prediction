"""
Convenience launcher for Live Traffic & Failover Demo Application
==================================================================
Runs the demo server on http://localhost:5050
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    app_dir = os.path.join(os.path.dirname(__file__), "traffic-demo")
    app_path = os.path.join(app_dir, "app.py")
    
    print(f"\n=======================================================")
    print(f"  LAUNCHING LIVE TRAFFIC DEMO WEB APPLICATION")
    print(f"=======================================================")
    print(f"  Location: {app_path}")
    print(f"  URL:      http://localhost:5050")
    print(f"=======================================================\n")
    
    cmd = [sys.executable, app_path] + sys.argv[1:]
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nDemo application stopped cleanly.")
