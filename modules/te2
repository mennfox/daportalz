from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
import adafruit_mcp9808
import adafruit_adt7410
import adafruit_bh1750
import board
import busio
import time
from modules.scd4x_module import SCD4xGlyph
from modules.bme280_module import get_bme280_stats

# ─── Initialize I2C and Sensors ─────────────────────────────────────
i2c = busio.I2C(board.SCL, board.SDA)
mcp9808 = adafruit_mcp9808.MCP9808(i2c)
adt7410 = adafruit_adt7410.ADT7410(i2c)
bh1750 = adafruit_bh1750.BH1750(i2c)
scd4x = SCD4xGlyph(warmup_seconds=20, max_retries=6, retry_interval=0.5)
# ─── Threshold Zones ────────────────────────────────────────────────
ZONES_TEMP = [(18, "blue"), (25, "green"), (28.5, "yellow"), (32, "red")]
ZONES_CO2 = [(600, "blue"), (1000, "green"), (1500, "yellow"), (2000, "red")]
ZONES_PRESSURE = [(980, "blue"), (1013, "green"), (1100, "yellow"), (1200, "red")]

ZONES_LUX = [(50, "blue"), (500, "green"), (1500, "yellow"), (3000, "red")]

# ─── Global Values ──────────────────────────────────────────────────
co2_value = 0.0
last_co2_update = 0
last_pressure_update = 0
last_lux_update = 0

# ─── Heatmap Bar Renderer ───────────────────────────────────────────
def render_heat_bar(temp, label, zones, width=30):
    blocks = "░▒▓█"
    max_temp = zones[-1][0]
    index = min(int((temp / max_temp) * (len(blocks) - 1)), len(blocks) - 1)
    block = blocks[index]
    color = next((c for t, c in reversed(zones) if temp >= t), "white")
    bar = block * width
    return Text(f"{label:<18} {temp:>5.1f}°C ", style="bold") + Text(bar, style=color)

# ─── Dial Gauge Renderer ────────────────────────────────────────────
def render_dial_lines(value, label, max_value=100):
    pointer_pos = int((value / max_value) * 12)
    arc_top = "╭───────────────╮"
    arc_mid = "│               │"
    arc_bot = "|||||||||||||||||"
    pointer = " " * pointer_pos + "▲"
    if value < max_value * 0.33:
        color = "green"
    elif value < max_value * 0.66:
        color = "yellow"
    else:
        color = "red"
    return [
        f"[bold {color}]{label:^16}[/bold {color}]",
        f"[cyan]{arc_top}[/cyan]",
        f"[cyan]{arc_mid}[/cyan]",
        f"[cyan]{arc_bot}[/cyan]",
        f"[{color}]{pointer} {value:>5.1f}[/{color}]"
    ]

def _refresh_co2_if_due(now: float, interval: float = 20.0):
    global co2_value, last_co2_update
    if now - last_co2_update >= interval:
        reading = scd4x.update()
        numeric = scd4x.get_latest_numeric()
        if numeric["co2"] > 0.0 or "ppm" in reading.get("co2", ""):
            co2_value = numeric["co2"]
        last_co2_update = now

# ─── Panel Builder ──────────────────────────────────────────────────
def build_tent_environment_panel():
    global co2_value, last_co2_update, last_pressure_update, last_lux_update

    bme = get_bme280_stats()
    temp_mcp = mcp9808.temperature
    temp_adt = adt7410.temperature
    temp_bme = bme["Temperature"]
    pressure = bme["Pressure"]
    lux = bh1750.lux

    last_pressure_update = time.time()
    last_lux_update = time.time()

    lines = []
    # Heatmap bars
    lines.append(render_heat_bar(temp_mcp, "MCP9808 - UPPER", ZONES_TEMP))
    lines.append(render_heat_bar(temp_adt, "ADT7410 - MID", ZONES_TEMP))
    lines.append(render_heat_bar(temp_bme, "BME280 - LOWER", ZONES_TEMP))
    lines.append(Text("\n"))

    # Horizontal dial layout with rightward centering
    co2_lines = render_dial_lines(co2_value, "Co₂", max_value=2000)
    hpa_lines = render_dial_lines(pressure, "hPa", max_value=1200)
    lux_lines = render_dial_lines(lux, "Lux", max_value=3000)

    pad = " " * 10  # adjust padding to center the row visually
    for i in range(len(co2_lines)):
        line = pad + f"{co2_lines[i]:<25} {hpa_lines[i]:<25} {lux_lines[i]}"
        lines.append(Text.from_markup(line))

    # Timestamp row
    ts_pad = " " * 10
    ts_line = (
        ts_pad +
        f"[dim]Last Co₂: {time.strftime('%H:%M:%S', time.localtime(last_co2_update))}[/dim]".ljust(25) +
        f"[dim]Last hPa: {time.strftime('%H:%M:%S', time.localtime(last_pressure_update))}[/dim]".ljust(25) +
        f"[dim]Last Lux: {time.strftime('%H:%M:%S', time.localtime(last_lux_update))}[/dim]"
    )
    lines.append(Text.from_markup("\n" + ts_line))

    return Panel(Text("\n").join(lines), title="🌍 Tent + Environment", border_style="grey37")

# ─── Live Runner ────────────────────────────────────────────────────
def run_live_panel():
    global co2_value, last_co2_update
    console = Console()

    with Live(console=console, refresh_per_second=1, screen=True) as live:
        while True:
            now = time.time()
            # Only ping SCD4x every 20 seconds
            if now - last_co2_update >= 20:
                scd4x.update()
                scd = scd4x.get_latest()
                co2_value = float(scd["co2"].split()[0]) if "ppm" in scd["co2"] else 0.0
                last_co2_update = now

            panel = build_tent_environment_panel()
            live.update(panel)
            time.sleep(10)

if __name__ == "__main__":
    run_live_panel()

