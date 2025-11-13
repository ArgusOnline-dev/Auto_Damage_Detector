#!/usr/bin/env python3
"""Frontend server reload script."""
import sys
import subprocess
import os
import signal
import time
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
WEB_DIR = ROOT_DIR / "apps" / "web"
PID_FILE = ROOT_DIR / ".frontend.pid"


def is_process_running(pid):
    """Check if a process with the given PID is running."""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                check=False
            )
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except (OSError, ProcessLookupError):
        return False


def stop_frontend():
    """Stop the frontend server if running."""
    if not PID_FILE.exists():
        return False
    
    try:
        pid = int(PID_FILE.read_text().strip())
        if is_process_running(pid):
            print(f"[STOP] Stopping frontend (PID: {pid})...")
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], 
                             capture_output=True, check=False)
            else:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                if is_process_running(pid):
                    os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
            PID_FILE.unlink()
            print("[OK] Frontend stopped")
            return True
    except Exception as e:
        print(f"[ERROR] Error stopping frontend: {e}")
        if PID_FILE.exists():
            PID_FILE.unlink()
    return False


def start_frontend():
    """Start the frontend server."""
    print("[START] Starting frontend development server...")
    print("   Frontend: http://localhost:8080")
    print("   Make sure backend is running on http://localhost:8000")
    print("=" * 60)
    
    npm_cmd = shutil.which("npm")
    if not npm_cmd:
        print("[ERROR] npm not found in PATH")
        print("   Please install Node.js and npm")
        print("   Download from: https://nodejs.org/")
        return False
    
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
    
    process = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(WEB_DIR),
        creationflags=creation_flags,
    )
    
    PID_FILE.write_text(str(process.pid))
    print(f"[OK] Frontend started (PID: {process.pid})")
    return True


def main():
    """Reload the frontend server."""
    stop_frontend()
    time.sleep(1)
    start_frontend()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[WARNING] Interrupted by user")
        sys.exit(0)

