"""Start Living Ledger - Handles port conflicts automatically"""
import os
import sys
import subprocess
import platform

def kill_port_8000():
    """Kill any process using port 8000"""
    print("Checking for processes on port 8000...")
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # Find process using port 8000
            result = subprocess.run(
                ['netstat', '-ano'], 
                capture_output=True, 
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    pid = parts[-1]
                    print(f"  Found process {pid} using port 8000")
                    subprocess.run(['taskkill', '/F', '/PID', pid], 
                                 capture_output=True)
                    print(f"  Killed process {pid}")
        else:
            # Linux/Mac
            result = subprocess.run(
                ['lsof', '-ti:8000'], 
                capture_output=True, 
                text=True
            )
            if result.stdout:
                pid = result.stdout.strip()
                print(f"  Found process {pid} using port 8000")
                subprocess.run(['kill', '-9', pid])
                print(f"  Killed process {pid}")
    except Exception as e:
        print(f"  Note: {e}")
    
    print("  Port 8000 is now free!")

def main():
    print("=" * 60)
    print("LIVING LEDGER - STARTUP")
    print("=" * 60)
    print()
    
    # Kill existing processes
    kill_port_8000()
    print()
    
    # Start server
    print("Starting server...")
    print("=" * 60)
    print()
    
    try:
        import uvicorn
        from api import app
        
        print("Server will start on: http://localhost:8000")
        print()
        print("Available pages:")
        print("  - Simple:   http://localhost:8000/simple")
        print("  - Test:     http://localhost:8000/static/test.html")
        print("  - Full App: http://localhost:8000")
        print()
        print("=" * 60)
        print()
        
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTrying alternative port 8001...")
        uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main()
