#!/usr/bin/env python3
"""
E-Book Maker Launcher
Choose between Flask (traditional web server) or Streamlit (modern UI)
"""

import subprocess
import sys
from pathlib import Path

def launch_flask():
    """Launch Flask web server"""
    print("🚀 Launching Flask web server...")
    print("   Access at: http://127.0.0.1:5000")
    print("   Press Ctrl+C to stop\n")
    subprocess.run([sys.executable, "server.py"])

def launch_streamlit():
    """Launch Streamlit app"""
    print("🚀 Launching Streamlit interface...")
    print("   Press Ctrl+C to stop\n")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app_streamlit.py"])

def main():
    print("=" * 60)
    print("📚 E-Book Maker - Interface Launcher")
    print("=" * 60)
    print()
    print("Choose your interface:")
    print()
    print("1. Flask (Traditional Web Server)")
    print("   - Classic web interface")
    print("   - Runs on http://127.0.0.1:5000")
    print("   - Best for: Familiar web UI, multiple tabs")
    print()
    print("2. Streamlit (Modern Data App)")
    print("   - Modern, reactive interface")
    print("   - Auto-refreshing UI")
    print("   - Best for: Quick tasks, streamlined workflow")
    print()
    print("3. Exit")
    print()

    while True:
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            launch_flask()
            break
        elif choice == "2":
            launch_streamlit()
            break
        elif choice == "3":
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
            print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)
