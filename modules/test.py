# scd4x_panel.py
import time
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

import board
import busio
import adafruit_scd4x

console = Console()

# Initialize sensor
i2c = busio.I2C(board.SCL, board.SDA)
scd4x = adafruit_scd4x.SCD4X(i2c)

# Timestamp glyph
def glyph_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")

# Sensor startup
try:
    serial = scd4x.serial_number
    console.log(f"[blue]{glyph_timestamp()} | SCD4X Serial: {[hex(i) for i in serial]}[/blue]")
    scd4x.start_periodic_measurement()
    console.log(f"[green]{glyph_timestamp()} | Measurement started[/green]")
except Exception as e:
    console.log(f"[red]{glyph_timestamp()} | Sensor init error: {e}[/red]")

# Warm-up delay
time.sleep(30)

# Panel builder — reads live from sensor
def get_scd4x_panel():
    try:
        if scd4x.data_ready:
            co2 = scd4x.CO2
            temp = scd4x.temperature
            hum = scd4x.relative_humidity
            lines = [
                Text(f"CO₂: {co2:.0f} ppm", style="bold magenta"),
                Text(f"Temp: {temp:.1f} °C", style="green"),
                Text(f"Humidity: {hum:.1f} %", style="cyan"),
                Text(f"⏱ {glyph_timestamp()}", style="dim")
            ]
            return Panel(Text("\n").join(lines), title="🫁 SCD4X Sensor", border_style="grey37")
        else:
            return Panel(f"[yellow]Sensor not ready[/yellow]\n⏱ {glyph_timestamp()}", title="🫁 SCD4X Sensor", border_style="grey37")
    except Exception as e:
        return Panel(f"[red]Sensor Error: {e}[/red]\n⏱ {glyph_timestamp()}", title="🫁 SCD4X Sensor", border_style="grey37")
