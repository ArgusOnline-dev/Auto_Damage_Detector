"""Start both backend and frontend servers."""
import subprocess
import sys
import os
import time
import threading

def start_backend():
    """Start the FastAPI backend server."""
    print("Starting FastAPI backend server...")
    print("Backend will be available at: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "run.py"], check=True)
    except KeyboardInterrupt:
        print("\nBackend server stopped.")

def start_frontend():
    """Start the Vite frontend server."""
    # Wait a bit for backend to start
    time.sleep(2)
    
    web_dir = os.path.join("apps", "web")
    os.chdir(web_dir)
    
    print("\nStarting frontend development server...")
    print("Frontend will be available at: http://localhost:8080")
    print("=" * 60)
    
    try:
        subprocess.run(["npm", "run", "dev"], check=True)
    except KeyboardInterrupt:
        print("\nFrontend server stopped.")

def main():
    """Start both servers."""
    print("=" * 60)
    print("Starting Auto Damage Detector - Full Stack")
    print("=" * 60)
    print()
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in main thread
    start_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
        sys.exit(0)

