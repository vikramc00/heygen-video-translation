import os
import time
import random
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Configuration
# The server will return "pending" until `PENDING_DURATION` seconds have passed since start.
# After that, it may return "completed" or "error".
PENDING_DURATION = float(os.environ.get("PENDING_DURATION", "10"))
ERROR_PROBABILITY = float(os.environ.get("ERROR_PROBABILITY", "0.1"))

start_time = time.time()

@app.get("/status")
def get_status():
    elapsed = time.time() - start_time
    if elapsed < PENDING_DURATION:
        return JSONResponse(content={"result": "pending"})
    else:
        # After the threshold, randomly decide "completed" or "error"
        if random.random() < ERROR_PROBABILITY:
            return JSONResponse(content={"result": "error"})
        else:
            return JSONResponse(content={"result": "completed"})

if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)