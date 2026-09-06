"""
Root launcher script.
Run the FastAPI backend from the project root using:
    python main.py
    OR
    uvicorn backend.app.main:app --reload
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), "backend"))
    subprocess.run(
        [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
        ],
        check=True,
    )