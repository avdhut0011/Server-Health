"""
PyInstaller Script to package the Windows Agent as a standalone executable.
Output: dist/ServerMonitorAgent.exe
"""

import subprocess
import sys
import os

def build_exe():
    print("Building Windows Server Monitor Agent Executable...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name=ServerMonitorAgent",
        "--clean",
        os.path.join(os.path.dirname(__file__), "agent.py")
    ]
    try:
        subprocess.run(cmd, check=True)
        print("Build Complete! Binary output located in dist/ServerMonitorAgent.exe")
    except Exception as e:
        print(f"To build executable, ensure PyInstaller is installed: pip install pyinstaller\nError: {e}")

if __name__ == "__main__":
    build_exe()
