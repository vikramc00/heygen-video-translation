import time
import logging
import requests
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationStatusClient:
    """
    A client library to poll the Heygen video translation server.

    Features:
    - Simple HTTP get_status() call to the provided server endpoint.
    - A wait_for_status_completed() method that intelligently polls the server:
      * Uses adaptive backoff to minimize unnecessary calls.
      * Allows the caller to specify a maximum waiting time.
      * Stops if the status becomes 'completed' or 'error'.

    Usage:
    ```python
    from client import TranslationStatusClient

    client = TranslationStatusClient(server_url="http://localhost:8000/status")
    final_status = client.wait_for_status_completed(
        max_wait=60,
        initial_interval=1,
        backoff_factor=1.5
    )
    print("Final status:", final_status)
    ```
    """

    def __init__(self, server_url: str):
        self.server_url = server_url

    def get_status(self) -> str:
        """
        Makes a GET request to the server status endpoint and returns the status as a string.
        Possible return values: 'pending', 'completed', 'error'
        """
        try:
            response = requests.get(self.server_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("result", "error")
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Error fetching status: {e}")
            return "error"

    def wait_for_status_completed(
        self,
        max_wait: float = 60.0,
        initial_interval: float = 2.0,
        backoff_factor: float = 1.5
    ) -> Optional[str]:
        """
        Waits until the server reports status 'completed' or 'error', or until max_wait seconds have elapsed.
        
        Polls with an adaptive backoff delay to minimize load on the server.
        
        :param max_wait: Maximum time in seconds to wait.
        :param initial_interval: The initial polling interval in seconds.
        :param backoff_factor: The factor by which the interval is multiplied after each unsuccessful attempt.
        
        :return: The final status ('completed' or 'error'), or None if timed out.
        """
        start = time.time()
        interval = initial_interval

        while True:
            elapsed = time.time() - start
            if elapsed > max_wait:
                logger.error("Timed out waiting for a completed status.")
                return None

            status = self.get_status()
            logger.info(f"Polled server: status={status}")

            if status == "completed":
                return "completed"
            elif status == "error":
                return "error"

            # If still pending, wait and then retry with a longer interval next time.
            time.sleep(interval)
            interval *= backoff_factor