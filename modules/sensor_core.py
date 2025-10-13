# modules/sensor_core.py

from collections import deque
from adafruit_htu21d import HTU21D
import board, busio

i2c = busio.I2C(board.SCL, board.SDA)
hts = HTU21D(i2c)

ZONES_TEMP = [(18, "blue"), (25, "green"), (28.5, "yellow"), (32, "red")]
ZONES_HUM = [(30, "sky_blue1"), (50, "cyan"), (70, "deep_sky_blue1"), (85, "steel_blue")]

temp_all_history = deque([0.0]*60, maxlen=60)
temp_spike_history = deque([0.0]*60, maxlen=60)
hum_history = deque([0.0]*60, maxlen=60)

max_values = {
    "HTU21d": {"Temp": float('-inf'), "Hum": float('-inf')}
}

