# modules/moisture_chart.py

import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from rich.text import Text
from rich.panel import Panel

# Initialize I2C and ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c, address=0x49)

channels = [
    AnalogIn(ads, ADS.P0),
    AnalogIn(ads, ADS.P1),
    AnalogIn(ads, ADS.P2),
    AnalogIn(ads, ADS.P3)
]

def get_moisture_values():
    return [chan.voltage for chan in channels]

def build_moisture_panel():
    values = get_moisture_values()
    max_val = max(values) or 1.0
    height = 8  # Number of vertical levels
    blocks = " ▁▂▃▄▅▆▇█"

    lines = []
    for level in reversed(range(1, height + 1)):
        line = ""
        for val in values:
            idx = int((val / max_val) * height)
            line += " " + (blocks[level] if idx >= level else " ") + " "
        lines.append(Text(line, style="cyan"))

    labels = Text("  A   B   C   D", style="bold white")
    lines.append(labels)

    return Panel(Text("\n").join(lines), title="🌱 Moisture Chart", border_style="green")

