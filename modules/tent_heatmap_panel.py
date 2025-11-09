from rich.panel import Panel
from rich.text import Text
from rich.console import Console

import adafruit_mcp9808
import adafruit_adt7410
import board
import busio

from modules.bme280_module import get_bme280_stats

# ─── Initialize I2C and Sensors ─────────────────────────────────────
i2c = busio.I2C(board.SCL, board.SDA)
mcp9808 = adafruit_mcp9808.MCP9808(i2c)
adt7410 = adafruit_adt7410.ADT7410(i2c)

# ─── Threshold Zones ────────────────────────────────────────────────
ZONES_TEMP = [(18, "blue"), (25, "green"), (28.5, "yellow"), (32, "red")]

# ─── Heat Bar Renderer ──────────────────────────────────────────────
def render_heat_bar(temp, label, zones, width=30):
    blocks = "░▒▓█"
    max_temp = zones[-1][0]
    index = min(int((temp / max_temp) * (len(blocks) - 1)), len(blocks) - 1)
    block = blocks[index]
    color = next((c for t, c in reversed(zones) if temp >= t), "white")
    bar = block * width
    return Text(f"{label:<18} {temp:>5.1f}°C  ", style="bold") + Text(bar, style=color)

# ─── Public Panel Function ──────────────────────────────────────────
def get_tent_heatmap_panel():
    try:
        temp_mcp = mcp9808.temperature
        temp_adt = adt7410.temperature
        temp_bme = get_bme280_stats()["Temperature"]

        lines = [
            render_heat_bar(temp_mcp, "MCP9808 - UPPER", ZONES_TEMP),
            render_heat_bar(temp_adt, "ADT7410 - MID", ZONES_TEMP),
            render_heat_bar(temp_bme, "BME280 - LOWER", ZONES_TEMP),
        ]

        return Panel(Text("\n").join(lines), title="🔥 Tent HeatMap", border_style="magenta")

    except Exception as e:
        return Panel(f"[red]Sensor Error: {e}[/red]", title="🔥 Tent HeatMap", border_style="red")

