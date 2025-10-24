from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table

from collections import deque
from statistics import mean, median, mode, StatisticsError
temp_history = deque(maxlen=60)
hum_history = deque(maxlen=60)

import board, busio, smbus2, time, threading
from datetime import datetime
from adafruit_htu21d import HTU21D
import adafruit_sht31d
import adafruit_ahtx0
import bme280

console = Console()
REFRESH_INTERVAL = 1.0

# Initialize sensors
i2c = busio.I2C(board.SCL, board.SDA)
htu = HTU21D(i2c)
sht31 = adafruit_sht31d.SHT31D(i2c)
ahtx0 = adafruit_ahtx0.AHTx0(i2c)
bme_bus = smbus2.SMBus(1)
bme_address = 0x76
bme_cal = bme280.load_calibration_params(bme_bus, bme_address)

# Shared data
max_values = {
    "HTU21D": {"Temp": float("-inf"), "Hum": float("-inf")},
    "BME280": {"Temp": float("-inf"), "Hum": float("-inf")},
    "Room": {"Temp": float("-inf"), "Hum": float("-inf")},
    "AHTx0": {"Temp": float("-inf"), "Hum": float("-inf")},
    "Pressure": float("-inf")
}

# Zones
ZONES_TEMP = [(18, "blue"), (25, "green"), (28.5, "yellow"), (32, "red")]
ZONES_TEMP_ROOM = [(18, "blue"), (25, "green"), (30, "yellow"), (40, "red")]
ZONES_HUM = [(30, "sky_blue1"), (50, "cyan"), (70, "deep_sky_blue1"), (85, "steel_blue")]
ZONES_PRESSURE = [(980, "blue"), (1013, "green"), (1030, "yellow"), (1050, "red")]
def zone_color(value, zones):
    for threshold, color in zones:
        if value <= threshold:
            return color
    return zones[-1][1]

def format_zone_bar(value, zones, label="", unit="", width=20, max_value=None):
    color = zone_color(value, zones)
    scale = max_value if max_value else zones[-1][0]
    filled_len = min(int((value / scale) * width), width)
    bar = "█" * filled_len + " " * (width - filled_len)
    return Text(f"{label:<10} {value:.1f}{unit:<3} ", style=color) + Text(bar, style=color)

def sensor_zone_lines(value, zones, label, unit, max_val):
    return [
        format_zone_bar(value, zones, label=label, unit=unit),
        Text(f"Max {label}: {max_val:.2f} {unit}", style="bold green")
    ]


def get_htu21d_panel():
    try:
        temp = htu.temperature
        hum = htu.relative_humidity
        max_values["HTU21D"]["Temp"] = max(max_values["HTU21D"]["Temp"], temp)
        max_values["HTU21D"]["Hum"] = max(max_values["HTU21D"]["Hum"], hum)
        lines = sensor_zone_lines(temp, ZONES_TEMP, "Temp", "°C", max_values["HTU21D"]["Temp"])
        lines += sensor_zone_lines(hum, ZONES_HUM, "Humidity", "%", max_values["HTU21D"]["Hum"])
        return Panel(Text("\n").join(lines), title="💧 HTU21D Sensor", border_style="grey37")
    except Exception as e:
        return Panel(f"[red]Sensor Error: {e}[/red]", title="💧 HTU21D Sensor", border_style="grey37")

def get_bme280_panel():
    try:
        data = bme280.sample(bme_bus, bme_address, bme_cal)
        temp = data.temperature
        hum = data.humidity
        temp_history.append(temp)
        hum_history.append(hum)
        pressure = data.pressure
        max_values["BME280"]["Temp"] = max(max_values["BME280"]["Temp"], temp)
        max_values["BME280"]["Hum"] = max(max_values["BME280"]["Hum"], hum)
        max_values["Pressure"] = max(max_values["Pressure"], pressure)
        lines = sensor_zone_lines(temp, ZONES_TEMP, "Temp", "°C", max_values["BME280"]["Temp"])
        lines += sensor_zone_lines(hum, ZONES_HUM, "Humidity", "%", max_values["BME280"]["Hum"])
        lines += sensor_zone_lines(pressure, ZONES_PRESSURE, "Pressure", "hPa", max_values["Pressure"])
        return Panel(Text("\n").join(lines), title="🌤 BME280 Sensor", border_style="grey37")
    except Exception as e:
        return Panel(f"[red]Sensor Error: {e}[/red]", title="🌤 BME280 Sensor", border_style="grey37")

def get_ahtx0_panel():
    try:
        temp = ahtx0.temperature
        hum = ahtx0.relative_humidity
        temp_history.append(temp)
        hum_history.append(hum)
        max_values["AHTx0"]["Temp"] = max(max_values["AHTx0"]["Temp"], temp)
        max_values["AHTx0"]["Hum"] = max(max_values["AHTx0"]["Hum"], hum)
        lines = sensor_zone_lines(temp, ZONES_TEMP, "Duct Temp", "°C", max_values["AHTx0"]["Temp"])
        lines += sensor_zone_lines(hum, ZONES_HUM, "Duct RH", "%", max_values["AHTx0"]["Hum"])
        return Panel(Text("\n").join(lines), title="🌀 Duct Sensor (AHTx0)", border_style="grey37")
    except Exception as e:
        return Panel(f"[red]Sensor Error: {e}[/red]", title="🌀 Duct Sensor (AHTx0)", border_style="grey37")

def get_room_panel():
    try:
        temp = sht31.temperature
        hum = sht31.relative_humidity
        temp_history.append(temp)
        hum_history.append(hum)
        max_values["Room"]["Temp"] = max(max_values["Room"]["Temp"], temp)
        max_values["Room"]["Hum"] = max(max_values["Room"]["Hum"], hum)
        lines = sensor_zone_lines(temp, ZONES_TEMP_ROOM, "Room Temp", "°C", max_values["Room"]["Temp"])
        lines += sensor_zone_lines(hum, ZONES_HUM, "Room Hum", "%", max_values["Room"]["Hum"])
        return Panel(Text("\n").join(lines), title="🏠 Room Stats (SHT31)", border_style="grey37")
    except Exception as e:
        return Panel(f"[red]Sensor Error: {e}[/red]", title="🏠 Room Stats (SHT31)", border_style="grey37")


def build_averages_panel():
    try:
        temps = list(temp_history)
        hums = list(hum_history)

        temp_mean = mean(temps)
        temp_median = median(temps)
        try:
            temp_mode = mode(temps)
        except StatisticsError:
            temp_mode = "No mode"

        hum_mean = mean(hums)
        hum_median = median(hums)
        try:
            hum_mode = mode(hums)
        except StatisticsError:
            hum_mode = "No mode"

        lines = [
            Text("🌡 Temperature Stats", style="bold underline"),
            Text(f"Mean: {temp_mean:.2f} °C", style="green"),
            Text(f"Median: {temp_median:.2f} °C", style="yellow"),
            Text(f"Mode: {temp_mode} °C", style="blue"),
            Text("💧 Humidity Stats", style="bold underline"),
            Text(f"Mean: {hum_mean:.2f} %", style="green"),
            Text(f"Median: {hum_median:.2f} %", style="yellow"),
            Text(f"Mode: {hum_mode} %", style="blue"),
        ]
        return Panel(Text("\n").join(lines), title="📈 Sensor Averages", border_style="grey37")
    except Exception as e:
        return Panel(f"[red]Error calculating averages: {e}[/red]", title="📈 Sensor Averages", border_style="red")

def build_sensor_cluster_panel():
    grid = Table.grid(padding=(1, 2))
    grid.add_row(get_htu21d_panel(), get_ahtx0_panel()) 
    grid.add_row(get_room_panel(), build_averages_panel())
#    grid.add_row(build_sensor_cluster_panel())  # 👈 Final row
    return Panel(grid, title="🌡 Sensor Cluster", border_style="cyan", expand=True)

def build_dashboard():
    layout = Table.grid(padding=(1, 2))
#    layout.add_row(build_sensor_cluster_panel())
    return layout

def run_dashboard():
    threading.Thread(target=update_scd4x_loop, name="update_scd4x_loop", daemon=True).start()
    with Live(console=console, refresh_per_second=10, screen=True) as live:
        while True:
            live.update(build_dashboard())
            time.sleep(REFRESH_INTERVAL)
