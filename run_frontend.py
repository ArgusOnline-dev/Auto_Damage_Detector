"""Start script for frontend development server."""
import subprocess
import sys
import os

def main():
    """Start the Vite development server."""
    # Change to web directory
    web_dir = os.path.join(os.path.dirname(__file__), "apps", "web")
    os.chdir(web_dir)
    
    print("Starting frontend development server...")
    print("Frontend will be available at: http://localhost:8080")
    print("Make sure the backend is running on http://localhost:8000")
    print("=" * 60)
    
    # Run npm dev command
    try:
        subprocess.run([sys.executable, "-m", "npm", "run", "dev"], check=True)
    except subprocess.CalledProcessError:
        # Fallback to direct npm if python -m npm doesn't work
        subprocess.run(["npm", "run", "dev"], check=True)

if __name__ == "__main__":
    main()

