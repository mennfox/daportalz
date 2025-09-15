# modules/moisture_chart.py

import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# Initialize I2C and ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c, address=0x49)
channels = [
    AnalogIn(ads, ADS.P0),
    AnalogIn(ads, ADS.P1),
    AnalogIn(ads, ADS.P2),
    AnalogIn(ads, ADS.P3)
]

# Moisture voltage thresholds
MIN_VOLTAGE = 1.5  # Fully wet
MAX_VOLTAGE = 3.3  # Fully dry

def moisture_percent(voltage):
    percent = 100 * (1 - (voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE))
    return max(0, min(100, round(percent)))

def moisture_color(percent):
    if percent > 80:
        return "bright_blue"
    elif percent > 60:
        return "green"
    elif percent > 40:
        return "yellow"
    else:
        return "red"

def moisture_status(percent):
    if percent > 80:
        return "Saturated"
    elif percent > 60:
        return "Moist"
    elif percent > 40:
        return "Drying"
    else:
        return "Dry"

def build_moisture_panel():
    table = Table(title="🌱 Moisture Chart", box=box.SQUARE, expand=True)
    table.add_column("Zone", justify="center", style="bold white")
    table.add_column("Moisture", justify="center")
    table.add_column("Status", justify="center")

    zones = ["A", "B", "C", "D"]
    for i, chan in enumerate(channels):
        voltage = chan.voltage
        percent = moisture_percent(voltage)
        color = moisture_color(percent)
        status = moisture_status(percent)

        # Build colored bar
        bar_blocks = "▁▂▃▄▅▆▇█"
        bar_level = int((percent / 100) * (len(bar_blocks) - 1))
        bar = Text(bar_blocks[bar_level] * 10, style=color)

        table.add_row(zones[i], f"{percent}% {bar}", status)

    # Legend
    legend = Text("\nLegend:\n", style="bold white")
    legend.append("Dry < 40%  ", style="red")
    legend.append("Drying 40–60%  ", style="yellow")
    legend.append("Moist 60–80%  ", style="green")
    legend.append("Saturated > 80%", style="bright_blue")

    return Panel.fit(table, subtitle=legend, border_style="grey50")

# Optional: run standalone for testing
if __name__ == "__main__":
    console = Console(color_system="truecolor")
    panel = build_moisture_panel()
    console.print(panel)

