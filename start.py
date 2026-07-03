#!/usr/bin/env python3
"""
Simple startup script for ATM FSM demo.
Starts both Flask backend and HTTP static server.
"""
import subprocess
import sys
import time
import os

def main():
    print("\n" + "="*50)
    print("ATM FSM - Interactive Demo")
    print("="*50 + "\n")
    
    # Install deps
    print("[1/3] Installing dependencies...")
    os.system("pip install -q flask flask-cors 2>/dev/null")
    print("✓ Dependencies ready\n")
    
    # Start backend
    print("[2/3] Starting backend on http://127.0.0.1:5000...")
    backend = subprocess.Popen([sys.executable, "app.py"], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
    time.sleep(2)
    print("✓ Backend running\n")
    
    # Start frontend
    print("[3/3] Starting frontend on http://127.0.0.1:8000...")
    frontend = subprocess.Popen([sys.executable, "-m", "http.server", "8000"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    time.sleep(1)
    print("✓ Frontend running\n")
    
    print("="*50)
    print("✅ READY!")
    print("="*50)
    print("\n📱 Open in browser: http://127.0.0.1:8000")
    print("\n🔐 Demo Credentials:")
    print("   Account: 1234")
    print("   PIN:     9")
    print("\n📊 Backend API: http://127.0.0.1:5000")
    print("\nPress Ctrl+C to stop.\n")
    
    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        backend.terminate()
        frontend.terminate()
        backend.wait(timeout=2)
        frontend.wait(timeout=2)
        print("✓ All servers stopped.\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
