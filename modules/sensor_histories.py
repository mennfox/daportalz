from collections import deque

# History buffers (adjust maxlen as needed)
temp_all_history = deque(maxlen=86400)       # 24h at 1s intervals
temp_spike_history = deque(maxlen=86400)
co2_history = deque(maxlen=86400)
hum_history = deque(maxlen=86400)
lux_history = deque(maxlen=86400)
pressure_history = deque(maxlen=86400)

