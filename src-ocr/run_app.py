"""
Run Streamlit from the currently active Python interpreter or from the project's virtual environment.
"""

import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_FILE = os.path.join(SCRIPT_DIR, "app.py")

if not os.path.exists(APP_FILE):
    raise FileNotFoundError(f"Could not find app.py in {SCRIPT_DIR}")

print("Starting Streamlit application...")
print(f"Using Python interpreter: {sys.executable}")

try:
    subprocess.run([sys.executable, "-m", "streamlit", "run", APP_FILE], check=True)
except subprocess.CalledProcessError as err:
    print("Failed to launch Streamlit.")
    print(err)
    sys.exit(err.returncode)
