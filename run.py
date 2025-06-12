#!/usr/bin/env python3
"""
Entry point for the Menu Maestro application.
This script sets up the Python path correctly to avoid import issues.
"""
import os
import sys
import subprocess

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # Run the Streamlit app directly using the streamlit CLI
    app_path = os.path.join(os.path.dirname(__file__), "app", "app.py")
    subprocess.run(["streamlit", "run", app_path])