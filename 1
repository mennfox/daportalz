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

import smbus2
import bme280

# Initialize I2C and sensors
i2c = busio.I2C(board.SCL, board.SDA)
hts = adafruit_hts221.HTS221(i2c)
scd4x = adafruit_scd4x.SCD4X(i2c)
scd4x.start_periodic_measurement()
bh1750 = adafruit_bh1750.BH1750(i2c)
as7341 = AS7341(i2c)

bme_bus = smbus2.SMBus(1)
bme_address = 0x76
bme_calibration = bme280.load_calibration_params(bme_bus, bme_address)

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
    return Panel(table, border_style="cyan")

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
    return Panel(table, border_style="magenta")

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
    return Panel(table, border_style="yellow")

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
    return Panel(table, border_style="green")

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
    return Panel(table, border_style="blue")
# SCD4x update loop
def update_scd4x_loop():
    while True:
        time.sleep(SCD4X_REFRESH)
        if scd4x.data_ready:
            environment_data["CO₂"] = f"{scd4x.CO2} ppm"
            scd4x_data["Temperature"] = f"{scd4x.temperature:.1f}°C"
            scd4x_data["Humidity"] = f"{scd4x.relative_humidity:.1f}%"
        else:
            environment_data["CO₂"] = "Not ready"
            scd4x_data["Temperature"] = "-"
            scd4x_data["Humidity"] = "-"

def get_hts221_stats():
    try:
        temp = hts.temperature
        humidity = hts.relative_humidity
        return {
            "Temperature": f"{temp:.2f}°C",
            "Humidity": f"{humidity:.2f}% rH"
        }
    except Exception as e:
        return {"Sensor Error": str(e)}

def get_bme280_stats():
    try:
        data = bme280.sample(bme_bus, bme_address, bme_calibration)
        environment_data["Pressure"] = f"{data.pressure:.2f} hPa"
        return {
            "Temperature": f"{data.temperature:.2f}°C",
            "Humidity": f"{data.humidity:.2f}%"
        }
    except Exception as e:
        return {"Sensor Error": str(e)}

def get_bh1750_stats():
    try:
        lux = bh1750.lux
        return {"Light Level": f"{lux:.2f} Lux"}
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

        return Panel(Text("\n").join(lines), title="🌈 AS7341 Spectral Sensor", border_style="bright_white")

    except Exception as e:
        return Panel(f"[red]Sensor Error: {e}", title="🌈 AS7341 Spectral Sensor", border_style="red")

def build_environment_panel():
    body = "\n".join([f"[bold white]{k}:[/bold white] {v}" for k, v in environment_data.items()])
    return Panel(body, title="🌍 Environment", border_style="white")

def build_hts221_panel():
    data = get_hts221_stats()
    body = "\n".join([f"[bold green]{k}:[/bold green] {v}" for k, v in data.items()])
    return Panel(body, title="💧 HTS221 Sensor", border_style="green")

def build_scd4x_panel():
    body = "\n".join([f"[bold magenta]{k}:[/bold magenta] {v}" for k, v in scd4x_data.items()])
    return Panel(body, title="🫁 SCD4x Sensor", border_style="magenta")

def build_bme280_panel():
    data = get_bme280_stats()
    body = "\n".join([f"[bold yellow]{k}:[/bold yellow] {v}" for k, v in data.items()])
    return Panel(body, title="🌤  BME280 Sensor", border_style="yellow")

def build_bh1750_panel():
    data = get_bh1750_stats()
    body = "\n".join([f"[bold blue]{k}:[/bold blue] {v}" for k, v in data.items()])
    return Panel(body, title="🔆 BH1750 Sensor", border_style="blue")
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
        build_hts221_panel(),
        build_scd4x_panel(),
        build_bme280_panel(),
        build_bh1750_panel(),
        get_as7341_panel(),
        build_environment_panel()
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


