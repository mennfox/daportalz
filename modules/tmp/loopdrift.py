import time
from collections import deque

REFRESH_INTERVAL = 1.0  # You can override this from outside if needed
drift_history = deque([0.0]*60, maxlen=60)

def calculate_drift(console, refresh_interval=REFRESH_INTERVAL):
    if not hasattr(console, "last_loop_time"):
        console.last_loop_time = time.time()
        drift = 0.0
    else:
        current = time.time()
        drift = current - console.last_loop_time - refresh_interval
        console.last_loop_time = current

    drift_history.append(drift)
    return drift

