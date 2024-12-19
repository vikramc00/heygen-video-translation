# Project Name: Heygen Video Translation Status Client

## Overview:
This project simulates a video translation backend server and provides a Python client library to intelligently poll the server for the job status, minimizing unnecessary frequent calls while ensuring timely retrieval of completion status.

## How It Works:
•	The server (server/main.py) simulates a time-consuming video translation process. It returns "pending" until a configured duration has passed, then returns either "completed" or "error" with some probability.
•	The client library (client/client.py) provides:
	•	A get_status() method to fetch the current status.
	•	A wait_for_status_completed() method that uses adaptive backoff to poll the server, starting with a short interval and increasing wait times to reduce load.

## How to Run the Server:
```bash
cd server
uvicorn main:app --reload
```

The server will listen on http://localhost:8000/status.

You can configure the behavior with environment variables:
•	PENDING_DURATION: How long (in seconds) the server should return “pending”. Default: 10.
•	ERROR_PROBABILITY: Probability of returning “error” once the job is complete. Default: 0.1.

## How to Use the Client Library:
```python
from client.client import TranslationStatusClient

client = TranslationStatusClient("http://localhost:8000/status")
final_status = client.wait_for_status_completed(
    max_wait=60,
    initial_interval=2,
    backoff_factor=1.5
)
print("Job final status:", final_status)
```

## Integration Test:
•	The test script client/test_client.py starts a local server and uses the client library to poll for completion.
•	Run:
```bash
cd client
python3 test_client.py
```

You should see logs demonstrating the polling and eventually a final status.

## Demonstrated Features:
•	Adaptive polling with increasing delays.
•	Graceful handling of errors and timeouts.
•	Clear logging for transparency.
•	Straightforward usage for third-party integrators.
•	Integration test showing end-to-end usage.