# dpz Dashboard
from collections import deque

co2_history = deque([0.0]*60, maxlen=60)
lux_history = deque([0.0]*60, maxlen=60)
temp_all_history = deque([0.0]*60, maxlen=60)
hum_history = deque([0.0]*60, maxlen=60)
pressure_history = deque([0.0]*60, maxlen=60)  # Optional
temp_spike_history = deque([0.0]*60, maxlen=60)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.layout import Layout
import psutil
import os
import time
import threading
from datetime import datetime
from collections import deque

import board
import busio
import adafruit_hts221
import adafruit_scd4x
import adafruit_bh1750
from adafruit_as7341 import AS7341
import adafruit_sht31d
import adafruit_mcp9808
import adafruit_adt7410

import smbus2
import bme280

# Initialize I2C and sensors
i2c = busio.I2C(board.SCL, board.SDA)
hts = adafruit_hts221.HTS221(i2c)
scd4x = adafruit_scd4x.SCD4X(i2c)
scd4x.start_periodic_measurement()
bh1750 = adafruit_bh1750.BH1750(i2c)
as7341 = AS7341(i2c)
sht31 = adafruit_sht31d.SHT31D(i2c, address=0x44)
mcp9808 = adafruit_mcp9808.MCP9808(i2c)
adt7410 = adafruit_adt7410.ADT7410(i2c)

bme_bus = smbus2.SMBus(1)
bme_address = 0x76
bme_calibration = bme280.load_calibration_params(bme_bus, bme_address)

# Historical max trackers for sensors
max_values = {
    "Environment": {"CO₂": float('-inf'), "Pressure": float('-inf')},
    "BH1750": {"Lux": float('-inf')},
    "HTS221": {"Temp": float('-inf'), "Hum": float('-inf')},
    "SCD4X": {"Temp": float('-inf'), "Hum": float('-inf')},
    "BME280": {"Temp": float('-inf'), "Hum": float('-inf')},
    "Room": {"Temp": float('-inf'), "Hum": float('-inf')},
    "Tent": {
        "MCP9808": float('-inf'),
        "ADT7410": float('-inf'),
        "BME280": float('-inf')
    }
}
console = Console()
REFRESH_INTERVAL = 1.0
SCD4X_REFRESH = 10.0

scd4x_data = {"Temperature": "Waiting...", "Humidity": "Waiting..."}
environment_data = {"CO₂": "Waiting...", "Pressure": "Waiting..."}
HISTORY_LEN = 30
cpu_histories = [deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN) for _ in range(psutil.cpu_count())]
mem_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
disk_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
net_sent_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
net_recv_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
prev_net = psutil.net_io_counters()

core_colors = ["cyan", "magenta", "yellow", "green"]

def sparkline(data, max_value=100, color="white"):
    blocks = "▁▂▃▄▅▆▇█"
    scaled = [min(int((val / max_value) * (len(blocks) - 1)), len(blocks) - 1) for val in data]
    return Text("".join(blocks[i] for i in scaled), style=color)

def colorize(value, thresholds=(50, 75)):
    if value < thresholds[0]:
        return f"[green]{value:.1f}%[/green]"
    elif value < thresholds[1]:
        return f"[yellow]{value:.1f}%[/yellow]"
    else:
        return f"[red]{value:.1f}%[/red]"

def bar_visual(value, max_value=100, width=20, color="white"):
    if max_value == 0:
        return Text(" " * width, style="dim")  # Prevent crash
    filled_len = min(int((value / max_value) * width), width)
    bar = "█" * filled_len + " " * (width - filled_len)
    return Text(bar, style=color)

def zone_color(value, zones):
    for threshold, color in zones:
        if value <= threshold:
            return color
    return zones[-1][1]

def format_zone_bar(value, zones, label="", unit="", width=20):
    color = zone_color(value, zones)
    bar = bar_visual(value, max_value=zones[-1][0], width=width, color=color)
    return Text(f"{label:<10} {value:.1f}{unit:<3} ", style=color) + bar

def get_cpu_panel():
    cpu_percents = psutil.cpu_percent(percpu=True)
    table = Table(title="[bold cyan]CPU Usage[/bold cyan]", expand=True)
    table.add_column("Core", style="bold")
    table.add_column("Usage", style="bold")
    table.add_column("Graph")
    for i, percent in enumerate(cpu_percents):
        cpu_histories[i].append(percent)
        color = core_colors[i] if i < len(core_colors) else "white"
        graph = sparkline(cpu_histories[i], color=color)
        table.add_row(f"Core {i}", colorize(percent), graph)
    return Panel(table, border_style="grey37")

def get_memory_panel():
    mem = psutil.virtual_memory()
    mem_history.append(mem.percent)
    graph = sparkline(mem_history, color="magenta")
    table = Table(title="[bold magenta]Memory[/bold magenta]", expand=True)
    table.add_column("Used")
    table.add_column("Total")
    table.add_column("Usage")
    table.add_column("Graph")
    table.add_row(
        f"{mem.used // (1024**2)} MB",
        f"{mem.total // (1024**2)} MB",
        colorize(mem.percent),
        graph
    )
    return Panel(table, border_style="grey37")

def get_disk_panel():
    usage = psutil.disk_usage("/")
    disk_history.append(usage.percent)
    graph = sparkline(disk_history, color="yellow")
    table = Table(title="[bold yellow]Disk Usage[/bold yellow]", expand=True)
    table.add_column("Used")
    table.add_column("Total")
    table.add_column("Usage")
    table.add_column("Graph")
    table.add_row(
        f"{usage.used // (1024**3)} GB",
        f"{usage.total // (1024**3)} GB",
        colorize(usage.percent),
        graph
    )
    return Panel(table, border_style="grey37")

def get_network_panel():
    global prev_net
    net_io = psutil.net_io_counters()
    sent = (net_io.bytes_sent - prev_net.bytes_sent) / 1024
    recv = (net_io.bytes_recv - prev_net.bytes_recv) / 1024
    prev_net = net_io
    net_sent_history.append(sent)
    net_recv_history.append(recv)
    graph_sent = sparkline(net_sent_history, max_value=1000, color="cyan")
    graph_recv = sparkline(net_recv_history, max_value=1000, color="magenta")
    table = Table(title="[bold green]Network I/O[/bold green]", expand=True)
    table.add_column("Metric", style="bold")
    table.add_column("KB/s")
    table.add_column("Graph")
    table.add_row("Sent", f"[cyan]{sent:.1f}[/cyan]", graph_sent)
    table.add_row("Recv", f"[magenta]{recv:.1f}[/magenta]", graph_recv)
    return Panel(table, border_style="grey37")

def get_system_panel():
    load1, load5, load15 = os.getloadavg()
    uptime_sec = time.time() - psutil.boot_time()
    hours = int(uptime_sec // 3600)
    minutes = int((uptime_sec % 3600) // 60)
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    table = Table(title="[bold blue]System Info[/bold blue]", expand=True)
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Load Avg", f"[white]{load1:.2f}, {load5:.2f}, {load15:.2f}[/white]")
    table.add_row("Uptime", f"[white]{hours}h {minutes}m[/white]")
    table.add_row("Time", f"[white]{now}[/white]")
    return Panel(table, border_style="grey37")

def update_scd4x_loop():
    while True:
        time.sleep(SCD4X_REFRESH)
        if scd4x.data_ready:
            co2_value = scd4x.CO2
            environment_data["CO₂"] = f"{co2_value} ppm"
            co2_history.append(co2_value)
            environment_data["CO₂"] = f"{scd4x.CO2} ppm"
            scd4x_data["Temperature"] = scd4x.temperature
            scd4x_data["Humidity"] = scd4x.relative_humidity
        else:
            environment_data["CO₂"] = "Not ready"
            scd4x_data["Temperature"] = "-"
            scd4x_data["Humidity"] = "-"

def auto_scale_zones(history, base_colors):
    valid = [v for v in history if v > 0]
    if not valid:
        return [(1, c) for c in base_colors]  # Safe fallback
    min_val, max_val = min(valid), max(valid)
    step = (max_val - min_val) / len(base_colors) or 1
    return [(min_val + step * (i + 1), base_colors[i]) for i in range(len(base_colors))]

def build_i2c_panel():
    lines = []

    # busio.I2C(board.SCL, board.SDA)
    lines.append(Text("🔌 busio.I2C(board.SCL, board.SDA)", style="bold cyan"))
    lines.append(Text("  ├─ HTS221 @ 0x5F"))
    lines.append(Text("  ├─ SCD4X @ 0x62"))
    lines.append(Text("  ├─ BH1750 @ 0x23"))
    lines.append(Text("  ├─ AS7341 @ 0x39"))
    lines.append(Text("  ├─ SHT31D @ 0x44"))
    lines.append(Text("  ├─ MCP9808 @ 0x18"))
    lines.append(Text("  └─ ADT7410 @ 0x48"))

    lines.append(Text(""))  # Spacer

    # smbus2.SMBus(1)
    lines.append(Text("🔌 smbus2.SMBus(1)", style="bold magenta"))
    lines.append(Text("  └─ BME280 @ 0x76"))

    body = Text("\n").join(lines)
    return Panel(body, title="🧭 I²C Port Map", border_style="grey37")

def get_autoscaled_max(history, base_colors):
    zones = auto_scale_zones(history, base_colors)
    return zones[-1][0] if zones else 100  # Fallback

def get_hts221_stats():
    try:
        temp = hts.temperature
        humidity = hts.relative_humidity
        temp_all_history.append(temp)
        for i, val in enumerate(temp_all_history):
            temp_spike_history[i] = max(temp_spike_history[i], val)
        hum_history.append(humidity)
        return {"Temperature": temp, "Humidity": humidity}
    except Exception as e:
        return {"Sensor Error": str(e)}

def get_bme280_stats():
    try:
        data = bme280.sample(bme_bus, bme_address, bme_calibration)
        pressure = data.pressure
        pressure_history.append(pressure)
        environment_data["Pressure"] = f"{data.pressure:.2f} hPa"
        return {"Temperature": data.temperature, "Humidity": data.humidity}
    except Exception as e:
        return {"Sensor Error": str(e)}

def get_bh1750_stats():
    try:
        lux = bh1750.lux
        lux_history.append(lux)
        max_values["BH1750"]["Lux"] = max(max_values["BH1750"]["Lux"], lux)
        return {
            "Light Level": f"{lux:.2f} Lux",
            "Max Lux": f"{max_values['BH1750']['Lux']:.2f} Lux"
        }
    except Exception as e:
        return {"Sensor Error": str(e)}

def get_as7341_panel():
    try:
        channels = {
            "Violet": (as7341.channel_415nm, "bright_magenta"),
            "Indigo": (as7341.channel_445nm, "blue"),
            "Blue":   (as7341.channel_480nm, "bright_blue"),
            "Cyan":   (as7341.channel_515nm, "cyan"),
            "Green":  (as7341.channel_555nm, "green"),
            "Yellow": (as7341.channel_590nm, "yellow"),
            "Orange": (as7341.channel_630nm, "orange3"),
            "Red":    (as7341.channel_680nm, "red")
        }

        lines = []
        for name, (value, color) in channels.items():
            bar_len = min(int(value / 1000), 40)
            bar = "█" * bar_len
            line = Text(f"{name:<7} [{value:5d}] ", style=color)
            line.append(bar, style=color)
            lines.append(line)

        return Panel(Text("\n").join(lines), title="🌈 AS7341 Spectral Sensor", border_style="grey37")

    except Exception as e:
        return Panel(f"[red]Sensor Error: {e}", title="🌈 AS7341 Spectral Sensor", border_style="grey37")

def build_timestamp_panel():
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return Panel(f"[bold green]Last Refresh:[/bold green] {now}", border_style="grey37")

def build_hts221_panel():
    data = get_hts221_stats()
    if "Sensor Error" in data:
        body = f"[red]{data['Sensor Error']}[/red]"
    else:
        temp = data["Temperature"]
        hum = data["Humidity"]
        temp_all_history.append(temp)
        for i, val in enumerate(temp_all_history):
            temp_spike_history[i] = max(temp_spike_history[i], val)
        max_values["HTS221"]["Temp"] = max(max_values["HTS221"]["Temp"], temp)
        max_values["HTS221"]["Hum"] = max(max_values["HTS221"]["Hum"], hum)

        zones_temp = auto_scale_zones(temp_all_history, ["blue", "green", "yellow", "red"])
        zones_hum = auto_scale_zones(hum_history, ["sky_blue1", "cyan", "deep_sky_blue1", "steel_blue"])

        lines = [
            format_zone_bar(temp, zones_temp, label="Temp", unit="°C"),
            Text(f"Max Temp: {max_values['HTS221']['Temp']:.1f}°C", style="bold green"),
            format_zone_bar(hum, zones_hum, label="Humidity", unit="%"),
            Text(f"Max Hum: {max_values['HTS221']['Hum']:.1f}%", style="bold cyan")
        ]
        body = Text("\n").join(lines)
    return Panel(body, title="💧 HTS221 Sensor", border_style="grey37")

def build_scd4x_panel():
    if isinstance(scd4x_data["Temperature"], float):
        temp = scd4x_data["Temperature"]
        hum = scd4x_data["Humidity"]
        temp_all_history.append(temp)
        for i, val in enumerate(temp_all_history):
            temp_spike_history[i] = max(temp_spike_history[i], val)
        max_values["SCD4X"]["Temp"] = max(max_values["SCD4X"]["Temp"], temp)
        max_values["SCD4X"]["Hum"] = max(max_values["SCD4X"]["Hum"], hum)

        zones_temp = auto_scale_zones(temp_all_history, ["blue", "green", "yellow", "red"])
        zones_hum = auto_scale_zones(hum_history, ["sky_blue1", "cyan", "deep_sky_blue1", "steel_blue"])

        lines = [
            format_zone_bar(temp, zones_temp, label="Temp", unit="°C"),
            Text(f"Max Temp: {max_values['SCD4X']['Temp']:.1f}°C", style="bold green"),
            format_zone_bar(hum, zones_hum, label="Humidity", unit="%"),
            Text(f"Max Hum: {max_values['SCD4X']['Hum']:.1f}%", style="bold cyan")
        ]
        body = Text("\n").join(lines)
    else:
        body = f"[red]Sensor not ready[/red]"
    return Panel(body, title="🫁 SCD4x Sensor", border_style="grey37")

def build_bme280_panel():
    data = get_bme280_stats()
    if "Sensor Error" in data:
        body = f"[red]{data['Sensor Error']}[/red]"
    else:
        temp = data["Temperature"]
        hum = data["Humidity"]
        temp_all_history.append(temp)
        for i, val in enumerate(temp_all_history):
            temp_spike_history[i] = max(temp_spike_history[i], val)
        max_values["BME280"]["Temp"] = max(max_values["BME280"]["Temp"], temp)
        max_values["BME280"]["Hum"] = max(max_values["BME280"]["Hum"], hum)

        zones_temp = auto_scale_zones(temp_all_history, ["blue", "green", "yellow", "red"])
        zones_hum = auto_scale_zones(hum_history, ["sky_blue1", "cyan", "deep_sky_blue1", "steel_blue"])

        lines = [
            format_zone_bar(temp, zones_temp, label="Temp", unit="°C"),
            Text(f"Max Temp: {max_values['BME280']['Temp']:.1f}°C", style="bold green"),
            format_zone_bar(hum, zones_hum, label="Humidity", unit="%"),
            Text(f"Max Hum: {max_values['BME280']['Hum']:.1f}%", style="bold cyan")
        ]
        body = Text("\n").join(lines)
    return Panel(body, title="🌤 BME280 Sensor", border_style="grey37")

def build_bh1750_panel():
    data = get_bh1750_stats()
    if "Sensor Error" in data:
        body = f"[red]{data['Sensor Error']}[/red]"
    else:
        lux_value = float(data['Light Level'].split()[0])
        max_values["BH1750"]["Lux"] = max(max_values["BH1750"]["Lux"], lux_value)
        zones_lux = auto_scale_zones(lux_history, ["blue", "green", "yellow", "red"])
        lines = [
            format_zone_bar(lux_value, zones_lux, label="Lux", unit="Lux"),
            Text(f"Max Lux: {max_values['BH1750']['Lux']:.2f} Lux", style="bold green")
        ]
        body = Text("\n").join(lines)
    return Panel(body, title="🔆 BH1750 Sensor", border_style="grey37")

def build_environment_panel():
    try:
        co2_str = environment_data["CO₂"]
        pressure_str = environment_data["Pressure"]

        co2_value = float(co2_str.split()[0]) if "ppm" in co2_str else 0.0
        pressure_value = float(pressure_str.split()[0]) if "hPa" in pressure_str else 0.0

        # Update max values
        max_values["Environment"]["CO₂"] = max(max_values["Environment"]["CO₂"], co2_value)
        max_values["Environment"]["Pressure"] = max(max_values["Environment"]["Pressure"], pressure_value)

        # Define zones
        zones_co2 = auto_scale_zones(co2_history, ["blue", "green", "yellow", "red"])
        zones_pressure = auto_scale_zones(pressure_history, ["blue", "green", "yellow", "red"])
    
        # Build visual lines
        lines = [
            format_zone_bar(co2_value, zones_co2, label="CO₂", unit="ppm"),
            Text(f"Max CO₂: {max_values['Environment']['CO₂']:.1f} ppm", style="bold green"),
            format_zone_bar(pressure_value, zones_pressure, label="Pressure", unit="hPa"),
            Text(f"Max Pressure: {max_values['Environment']['Pressure']:.2f} hPa", style="bold cyan")
        ]
        body = Text("\n").join(lines)
    except Exception as e:
        body = f"[red]Sensor Error: {e}[/red]"

    return Panel(body, title="🌍 Environment", border_style="grey37")

def build_room_panel():
    try:
        temp = sht31.temperature
        humidity = sht31.relative_humidity
        temp_all_history.append(temp)
        for i, val in enumerate(temp_all_history):
            temp_spike_history[i] = max(temp_spike_history[i], val)
        max_values["Room"]["Temp"] = max(max_values["Room"]["Temp"], temp)
        max_values["Room"]["Hum"] = max(max_values["Room"]["Hum"], humidity)

        zones_temp = auto_scale_zones(temp_all_history, ["blue", "green", "yellow", "red"])
        zones_hum = auto_scale_zones(hum_history, ["sky_blue1", "cyan", "deep_sky_blue1", "steel_blue"])
        lines = [
            format_zone_bar(temp, zones_temp, label="Room Temp", unit="°C"),
            Text(f"Max Temp: {max_values['Room']['Temp']:.1f}°C", style="bold green"),
            format_zone_bar(humidity, zones_hum, label="Room Hum", unit="%"),
            Text(f"Max Hum: {max_values['Room']['Hum']:.1f}%", style="bold cyan")
        ]
        body = Text("\n").join(lines)
    except Exception as e:
        body = f"[red]Sensor Error: {e}[/red]"
    return Panel(body, title="🏠 Room Stats (SHT31)", border_style="grey37")

def build_tent_panel():
    try:
        temp_mcp = mcp9808.temperature
        temp_adt = adt7410.temperature
        data_bme = get_bme280_stats()
        temp_bme = data_bme["Temperature"] if "Sensor Error" not in data_bme else None
        max_values["Tent"]["MCP9808"] = max(max_values["Tent"]["MCP9808"], temp_mcp)
        max_values["Tent"]["ADT7410"] = max(max_values["Tent"]["ADT7410"], temp_adt)
        if temp_bme is not None:
            max_values["Tent"]["BME280"] = max(max_values["Tent"]["BME280"], temp_bme)

        zones_temp = auto_scale_zones(temp_all_history, ["blue", "green", "yellow", "red"])

        lines = [
            format_zone_bar(temp_mcp, zones_temp, label="MCP9808", unit="°C"),
            Text(f"Max MCP: {max_values['Tent']['MCP9808']:.1f}°C", style="bold green"),
            format_zone_bar(temp_adt, zones_temp, label="ADT7410", unit="°C"),
            Text(f"Max ADT: {max_values['Tent']['ADT7410']:.1f}°C", style="bold green")
        ]
        if temp_bme is not None:
            lines.extend([
                format_zone_bar(temp_bme, zones_temp, label="BME280", unit="°C"),
                Text(f"Max BME: {max_values['Tent']['BME280']:.1f}°C", style="bold green")
            ])

        body = Text("\n").join(lines)
    except Exception as e:
        body = f"[red]Sensor Error: {e}[/red]"
    return Panel(body, title="🌡 Tent Heatmap", border_style="grey37")

def render_high_graph(data, threshold, max_value, width=60):
    blocks = "▁▂▃▄▅▆▇█"
    graph = []
    for val in list(data)[-width:]:
        try:
            val = float(val)
        except:
            val = 0.0
        if val >= threshold:
            idx = min(int((val / max_value) * (len(blocks) - 1)), len(blocks) - 1)
            graph.append(blocks[idx])
        else:
            graph.append(" ")
    return Text("".join(graph), style="bold green")


def max_overlay_graph(current, spikes, threshold, max_value, width=60):
    blocks = "▁▂▃▄▅▆▇█"
    graph = []

    for i in range(width):
        val = float(current[i]) if i < len(current) else 0.0
        spike = float(spikes[i]) if i < len(spikes) else 0.0
        show_val = max(val, spike)

        if show_val >= threshold:
            idx = min(int((show_val / max_value) * (len(blocks) - 1)), len(blocks) - 1)
            block = blocks[idx]
            style = "bold red" if spike > val else "bold yellow"
            graph.append((block, style))
        else:
            graph.append((" ", "dim"))

    return Text.assemble(*[Text(char, style=style) for char, style in graph])

def build_sensor_graph_panel():
    try:
        graphs = []

        graphs.append(Text("CO₂ ──┬───────────────────────────────────────────────"))
        graphs.append(Text(f" │ {render_high_graph(co2_history, 1500, get_autoscaled_max(co2_history, ['blue','green','yellow','red'])).plain}"))

        graphs.append(Text("Lux ──┬───────────────────────────────────────────────"))
        graphs.append(Text(f" │ {render_high_graph(lux_history, 9000, get_autoscaled_max(lux_history, ['blue','green','yellow','red'])).plain}"))

        graphs.append(Text("°C Max ─┬───────────────────────────────────────────────"))
        graphs.append(Text(f" │ {max_overlay_graph(temp_all_history, temp_spike_history, 28.5, get_autoscaled_max(temp_all_history, ['blue','green','yellow','red'])).plain}"))

        graphs.append(Text("Rh ──┬───────────────────────────────────────────────"))
        graphs.append(Text(f" │ {render_high_graph(hum_history, 70, get_autoscaled_max(hum_history, ['sky_blue1','cyan','deep_sky_blue1','steel_blue'])).plain}"))

        graphs.append(Text("hPa ─┬────────────────────────────────────────────"))
        graphs.append(Text(f" │ {render_high_graph(pressure_history, 1020, get_autoscaled_max(pressure_history, ['blue','green','yellow','red'])).plain}"))

        graphs.append(Text("Time → [Last 24h]"))

        body = Text("\n").join(graphs)
    except Exception as e:
        body = Text(f"[red]Sensor Graph Error: {e}[/red]")

    return Panel(body, title="📊 High Sensor Readings", border_style="grey37")

def build_dashboard():
    layout = Table.grid(padding=(1, 2))
    layout.add_row(
        get_cpu_panel(),
        get_memory_panel(),
        get_disk_panel(),
        get_network_panel(),
        get_system_panel()
    )
    layout.add_row(
        get_as7341_panel(),
        build_environment_panel(),
        build_hts221_panel(),
        build_scd4x_panel(),
        build_bme280_panel(),
    )
    layout.add_row(
        build_room_panel(),
        build_tent_panel(),
        build_bh1750_panel(),
        build_timestamp_panel(),
        build_sensor_graph_panel(),
        layout.add_row(build_i2c_panel()) 
    )
    return layout

def run_dashboard():
    threading.Thread(target=update_scd4x_loop, daemon=True).start()
    with Live(console=console, refresh_per_second=10, screen=True) as live:
        while True:
            live.update(build_dashboard())
            time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    run_dashboard()

