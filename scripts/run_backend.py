#!/usr/bin/env python3
"""Backend server reload script."""
import sys
import subprocess
import os
import signal
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
PROJECT_VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
WORKSPACE_VENV_PYTHON = ROOT_DIR.parent / ".venv" / "Scripts" / "python.exe"
PID_FILE = ROOT_DIR / ".backend.pid"


def get_python_exe():
    """Get the Python executable to use."""
    candidates = [
        PROJECT_VENV_PYTHON,
        WORKSPACE_VENV_PYTHON,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    print(f"[WARN] Virtualenv python not found; using current interpreter: {sys.executable}")
    return sys.executable


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


def _find_additional_backend_pids():
    """Locate stray uvicorn processes for the backend (fallback)."""
    matches = []

    # Preferred: use psutil if available for this interpreter
    try:
        import psutil  # type: ignore

        for proc in psutil.process_iter(["pid", "cmdline"]):
            try:
                cmdline = proc.info.get("cmdline") or []
                if not cmdline:
                    continue
                cmd_str = " ".join(cmdline).lower()
                if "uvicorn" in cmd_str and "apps.api.main" in cmd_str:
                    matches.append(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        pass

    if sys.platform == "win32":
        # Fallback for Windows without psutil: use PowerShell to query processes
        try:
            ps_script = (
                "Get-CimInstance Win32_Process | "
                "Where-Object { $_.CommandLine -like '*uvicorn*apps.api.main*' } | "
                "Select-Object -ExpandProperty ProcessId"
            )
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    ps_script.replace("$_", "`$_"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.isdigit():
                    matches.append(int(line))
        except FileNotFoundError:
            pass

        # Also capture forked worker processes started via multiprocessing
        try:
            ps_script = (
                "Get-CimInstance Win32_Process | "
                "Where-Object { $_.CommandLine -like '*spawn_main(parent_pid=*' } | "
                "ForEach-Object { "
                "$pid=$_.ProcessId; "
                "$parent=''; "
                "if ($_.CommandLine -match 'parent_pid=(\\d+)') { $parent=$matches[1]; } "
                "Write-Output \"$pid,$parent\" }"
            )
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    ps_script.replace("$_", "`$_"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                pid_part, _, parent_part = line.partition(",")
                if pid_part.isdigit():
                    matches.append(int(pid_part))
                if parent_part.isdigit():
                    matches.append(int(parent_part))
        except FileNotFoundError:
            pass

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for pid in matches:
        if pid not in seen:
            seen.add(pid)
            unique.append(pid)
    return unique


def stop_backend():
    """Stop the backend server if running."""
    if not PID_FILE.exists():
        stopped = False
    else:
        stopped = False

        try:
            pid = int(PID_FILE.read_text().strip())
            if is_process_running(pid):
                print(f"[STOP] Stopping backend (PID: {pid})...")
                if sys.platform == "win32":
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(pid)],
                        capture_output=True,
                        check=False,
                    )
                else:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)
                    if is_process_running(pid):
                        os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
                stopped = True
            else:
                print(f"[WARN] Backend PID file stale (PID {pid} not running)")
        except Exception as e:
            print(f"[ERROR] Error stopping backend via PID file: {e}")
        finally:
            try:
                PID_FILE.unlink()
            except OSError:
                pass
    
    extra_pids = _find_additional_backend_pids()
    killed_any = False
    for extra_pid in extra_pids:
        try:
            if is_process_running(extra_pid):
                print(f"[STOP] Terminating backend worker (PID: {extra_pid})...")
                if sys.platform == "win32":
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(extra_pid)],
                        capture_output=True,
                        check=False,
                    )
                else:
                    os.kill(extra_pid, signal.SIGTERM)
                    time.sleep(1)
                    if is_process_running(extra_pid):
                        os.kill(extra_pid, signal.SIGKILL)
                killed_any = True
        except Exception as e:
            print(f"[ERROR] Failed to terminate worker PID {extra_pid}: {e}")

    if stopped or killed_any:
        print("[OK] Backend stopped")
        return True
    return False


def start_backend():
    """Start the backend server."""
    python_exe = get_python_exe()
    print("[START] Starting FastAPI backend server...")
    print(f"   Python: {python_exe}")
    print("   Backend: http://localhost:8000")
    print("   API docs: http://localhost:8000/docs")
    print("=" * 60)
    
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
    
    process = subprocess.Popen(
        [
            python_exe, "-m", "uvicorn",
            "apps.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ],
        cwd=str(ROOT_DIR),
        creationflags=creation_flags,
    )
    
    PID_FILE.write_text(str(process.pid))
    print(f"[OK] Backend started (PID: {process.pid})")
    return True


def main():
    """Reload the backend server."""
    stop_backend()
    time.sleep(1)
    start_backend()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[WARNING] Interrupted by user")
        sys.exit(0)

