import subprocess
import time
import os
import requests
from client import TranslationStatusClient
import signal

def test_integration():
    # Start the server in a subprocess
    # We'll set a lower PENDING_DURATION for quick testing
    env = os.environ.copy()
    env["PENDING_DURATION"] = "5"  # 5 seconds of pending before completion/error
    env["ERROR_PROBABILITY"] = "0.2"  # 20% chance of error

    server_process = subprocess.Popen(
        ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    # Give the server a moment to start
    time.sleep(2)

    # Check server health quickly
    try:
        r = requests.get("http://localhost:8000/status")
        r.raise_for_status()
        print("Server health check passed.")
    except Exception as e:
        print("Server did not start properly:", e)
        server_process.terminate()
        server_process.wait()
        return

    # Create a client and wait for the status to become completed or error
    client = TranslationStatusClient(server_url="http://localhost:8000/status")
    final_status = client.wait_for_status_completed(max_wait=30, initial_interval=1, backoff_factor=1.5)
    print(f"Final status from server: {final_status}")

    # Cleanup server process
    server_process.send_signal(signal.SIGINT)
    server_process.wait()

if __name__ == "__main__":
    test_integration()