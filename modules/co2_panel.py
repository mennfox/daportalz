# co2_panel.py
import time
from rich.panel import Panel
from rich.text import Text

import board
import busio
import adafruit_scd4x

# Initialize sensor
i2c = busio.I2C(board.SCL, board.SDA)
scd4x = adafruit_scd4x.SCD4X(i2c)

# Start sensor
try:
    scd4x.start_periodic_measurement()
except Exception:
    pass

# Warm-up delay
time.sleep(30)

# Panel builder — CO₂ only
def get_co2_panel():
    try:
        if scd4x.data_ready:
            co2 = scd4x.CO2
            return Panel(Text(f"{co2:.0f} ppm", style="bold magenta"), title="CO₂", border_style="grey37")
        else:
            return Panel("Sensor not ready", title="CO₂", border_style="grey37")
    except Exception as e:
        return Panel(f"Sensor error: {e}", title="CO₂", border_style="red")
