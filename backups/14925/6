# dpz Dashboard

from collections import deque
ahtx0_temp_history = deque([0.0]*60, maxlen=60)
ahtx0_hum_history = deque([0.0]*60, maxlen=60)
co2_history = deque([0.0]*60, maxlen=60)
lux_history = deque([0.0]*60, maxlen=60)
htu21d_history = deque([0.0]*60, maxlen=60)
scd4x_history = deque([0.0]*60, maxlen=60)
sht31d_history = deque([0.0]*60, maxlen=60)
sht31d_spike_history = deque([0.0]*60, maxlen=60)
mcp9808_history = deque([0.0]*60, maxlen=60)
adt7410_history = deque([0.0]*60, maxlen=60)
hum_history = deque([0.0]*60, maxlen=60)
pressure_history = deque([0.0]*60, maxlen=60)  # Optional
temp_all_history = deque([0.0]*60, maxlen=60)
temp_spike_history = deque([0.0]*60, maxlen=60)

from statistics import mean, median, mode, StatisticsError
from rich.console import Console
from rich.panel import Panel
from rich.console import Group
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.layout import Layout
import psutil
import os
import time
import threading
from datetime import datetime
from pyfiglet import Figlet
import subprocess
import board
import busio
from adafruit_htu21d import HTU21D
import adafruit_scd4x
import adafruit_bh1750
from adafruit_as7341 import AS7341
import adafruit_sht31d
import adafruit_mcp9808
import adafruit_adt7410
import smbus2
import bme280
import adafruit_ahtx0
import json
from pathlib import Path
import re
import traceback
import socket
from modules.watering import get_last_watered_text
from rich.progress import BarColumn
from datetime import datetime, timedelta
from modules import height
from modules.height import height_bar

WATCHDOG_LOG_DIR = Path("logs")
WATCHDOG_LOG_DIR.mkdir(parents=True, exist_ok=True)
WATCHDOG_LOG_FILE = WATCHDOG_LOG_DIR / f"watchdog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

WATCHDOG_CHECK_INTERVAL = 10.0
WATCHDOG_STALL_THRESHOLD = 5.0
WATCHDOG_SCROLL_INDEX = 0
WATCHDOG_SCROLL_WINDOW = 14  # Number of lines to show
WATCHDOG_FILTER_MODE = False  # Toggle to show only warnings/errors

# Globals

LOG_SCROLL_WINDOW = 20
log_scroll_index = 0

SUMMARY_SCROLL_WINDOW = 10  # Match height of averages panel
summary_scroll_index = 0    # Scroll position tracker

network_cache = {
    "latency": "—",
    "last_ping": 0.0
}

as7341_cache = {
    "channels": {},
    "timestamp": "Never"
}

# Zone Constants
ZONES_LUX       = [(100, "blue"), (5500, "green"), (8500, "yellow"), (10000, "red")]
ZONES_TEMP      = [(18, "blue"), (25, "green"), (28.5, "yellow"), (32, "red")]
ZONES_TEMP_ROOM = [(18, "blue"), (25, "green"), (30, "yellow"), (40, "red")]
ZONES_HUM       = [(30, "sky_blue1"), (50, "cyan"), (70, "deep_sky_blue1"), (85, "steel_blue")]
ZONES_CO2       = [(600, "blue"), (1000, "green"), (1500, "yellow"), (2000, "red")]
ZONES_PRESSURE  = [(980, "blue"), (1013, "green"), (1030, "yellow"), (1050, "red")]

# Initialize I2C and sensors
i2c = busio.I2C(board.SCL, board.SDA)
hts = HTU21D(i2c)
scd4x = adafruit_scd4x.SCD4X(i2c)
scd4x.start_periodic_measurement()
bh1750 = adafruit_bh1750.BH1750(i2c)
as7341 = AS7341(i2c)
sht31 = adafruit_sht31d.SHT31D(i2c, address=0x44)
mcp9808 = adafruit_mcp9808.MCP9808(i2c)
adt7410 = adafruit_adt7410.ADT7410(i2c)
ahtx0 = adafruit_ahtx0.AHTx0(i2c)

bme_bus = smbus2.SMBus(1)
bme_address = 0x76
bme_calibration = bme280.load_calibration_params(bme_bus, bme_address)

# Historical max trackers for sensors
max_values = {
    "Environment": {"CO₂": float('-inf'), "Pressure": float('-inf')},
    "BH1750": {"Lux": float('-inf')},
    "HTU21d": {"Temp": float('-inf'), "Hum": float('-inf')},
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
    safe_max = max_value if max_value > 0 else 1.0
    scaled = [min(int((val / safe_max) * (len(blocks) - 1)), len(blocks) - 1) for val in data]
    return Text("".join(blocks[i] for i in scaled), style=color)

def colorize(value, thresholds=(50, 75)):
    if value < thresholds[0]:
        return f"[green]{value:.1f}%[/green]"
    elif value < thresholds[1]:
        return f"[yellow]{value:.1f}%[/yellow]"
    else:
        return f"[red]{value:.1f}%[/red]"

def bar_visual(value, max_value=100, width=20, color="white"):
    filled_len = min(int((value / max_value) * width), width)
    bar = "█" * filled_len + " " * (width - filled_len)
    return Text(bar, style=color)

def dual_bar_visual(used, total, width=20, used_color="blue", free_color="orange1"):
    used_len = min(int((used / total) * width), width)
    free_len = width - used_len
    used_bar = Text("█" * used_len, style=used_color)
    free_bar = Text("█" * free_len, style=free_color)
    return used_bar + free_bar

def zone_color(value, zones):
    for threshold, color in zones:
        if value <= threshold:
            return color
    return zones[-1][1]

def format_zone_bar(value, zones, label="", unit="", width=20, max_value=None):
    color = zone_color(value, zones)
    scale = max_value if max_value else zones[-1][0]
    bar = bar_visual(value, max_value=scale, width=width, color=color)
    return Text(f"{label:<10} {value:.1f}{unit:<3} ", style=color) + bar

def get_cpu_panel():
    cpu_percents = psutil.cpu_percent(percpu=True)
    freqs = psutil.cpu_freq(percpu=True)
    load1, load5, load15 = os.getloadavg()

    # Optional: Core temps
    temps = psutil.sensors_temperatures().get("coretemp", [])
    temp_map = {i: t.current for i, t in enumerate(temps)} if temps else {}

    # Zone bar for overall CPU pressure
    avg_usage = sum(cpu_percents) / len(cpu_percents)
    ZONES_CPU = [(30, "green"), (60, "yellow"), (90, "red")]
    pressure_bar = format_zone_bar(avg_usage, ZONES_CPU, label="CPU", unit="%", width=30)

    table = Table(title="[bold cyan]CPU Usage[/bold cyan]", expand=True)
    table.add_column("Core", style="bold")
    table.add_column("Usage")
    table.add_column("Freq")
    table.add_column("Temp")
    table.add_column("Graph")

    for i, percent in enumerate(cpu_percents):
        cpu_histories[i].append(percent)
        color = core_colors[i] if i < len(core_colors) else "white"
        graph = sparkline(cpu_histories[i], color=color)
        freq = f"{freqs[i].current:.0f} MHz" if i < len(freqs) else "—"
        temp = f"{temp_map.get(i, '—'):.1f}°C" if temp_map else "—"
        table.add_row(f"Core {i}", colorize(percent), freq, temp, graph)

    # Add system-wide metrics
    table.add_row("—", "—", "—", "—", Text(f"Load Avg: {load1:.2f}, {load5:.2f}, {load15:.2f}", style="dim"))
    table.add_row("—", "—", "—", "—", pressure_bar)

    # Top process snapshot
    try:
        top_proc = max(psutil.process_iter(['pid', 'name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'])
        proc_info = f"{top_proc.info['name']} ({top_proc.info['cpu_percent']:.1f}%)"
        table.add_row("—", "—", "—", "—", Text(f"Top Proc: {proc_info}", style="dim"))
    except Exception:
        table.add_row("—", "—", "—", "—", Text("Top Proc: —", style="dim"))

    return Panel(table, border_style="grey37")

def get_memory_panel():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    mem_history.append(mem.percent)
    max_mem = max(mem_history) or 1.0
    graph = sparkline(mem_history, max_value=max_mem, color="magenta")

    table = Table(title="[bold magenta]Memory[/bold magenta]", expand=True)
    table.add_column("Used")
    table.add_column("Total")
    table.add_column("Usage")
    table.add_column("Graph")

    # RAM row
    table.add_row(
        f"{mem.used // (1024**2)} MB",
        f"{mem.total // (1024**2)} MB",
        colorize(mem.percent),
        graph
    )

    # Swap row
    table.add_row(
        f"{swap.used // (1024**2)} MB",
        f"{swap.total // (1024**2)} MB",
        colorize(swap.percent),
        Text("Swap", style="dim")
    )

    # Peak usage row
    table.add_row(
        "—",
        "—",
        f"[bold magenta]{max_mem:.1f}%[/bold magenta]",
        Text("Peak", style="dim")
    )

    # Top processes section
    try:
        top_procs = sorted(
            psutil.process_iter(['name', 'memory_info']),
            key=lambda p: p.info['memory_info'].rss,
            reverse=True
        )[:3]

        for proc in top_procs:
            mem_mb = proc.info['memory_info'].rss // (1024**2)
            table.add_row(
                f"[cyan]{proc.info['name']}[/cyan]",
                f"{mem_mb} MB",
                "—",
                Text("Top Proc", style="dim")
            )
    except Exception as e:
        table.add_row("Error", "—", "—", Text(str(e), style="red"))

    return Panel(table, border_style="grey37")

def get_disk_panel():
    usage = psutil.disk_usage("/")
    swap = psutil.swap_memory()

    # I/O rate
    if not hasattr(console, "prev_disk_io"):
        console.prev_disk_io = psutil.disk_io_counters()
    curr_io = psutil.disk_io_counters()
    read_rate = (curr_io.read_bytes - console.prev_disk_io.read_bytes) / REFRESH_INTERVAL / 1024
    write_rate = (curr_io.write_bytes - console.prev_disk_io.write_bytes) / REFRESH_INTERVAL / 1024
    console.prev_disk_io = curr_io

    # Bar visual for disk usage
    bar = dual_bar_visual(
        usage.used,
        usage.total,
        width=30,
        used_color="blue",
        free_color="yellow"
    )

    # Build table
    table = Table(title="[bold yellow]Disk & Swap[/bold yellow]", expand=True)
    table.add_column("Used")
    table.add_column("Total")
    table.add_column("Usage")
    table.add_column("Graph")

    # Disk row with inline bar
    table.add_row(
        f"{usage.used // (1024**3)} GB",
        f"{usage.total // (1024**3)} GB",
        colorize(usage.percent),
        bar
    )

    # Swap row
    table.add_row(
        f"{swap.used // (1024**2)} MB",
        f"{swap.total // (1024**2)} MB",
        colorize(swap.percent),
        Text("Swap", style="dim")
    )

    # I/O rate row
    table.add_row(
        f"{read_rate:.1f} KB/s",
        f"{write_rate:.1f} KB/s",
        "—",
        Text("I/O Rate", style="dim")
    )

    return Panel(table, border_style="grey37")

def update_network_latency_loop():
    while True:
        try:
            result = subprocess.getoutput("ping -c 1 -W 1 192.168.1.1 | grep 'time='")
            latency_val = result.split("time=")[-1].split()[0]
            network_cache["latency"] = f"{latency_val} ms"
            network_cache["last_ping"] = time.time()
        except Exception:
            network_cache["latency"] = "—"
        time.sleep(30)  # Refresh every 30s

def get_network_panel():
    global prev_net
    net_io = psutil.net_io_counters()
    sent = (net_io.bytes_sent - prev_net.bytes_sent) / 1024
    recv = (net_io.bytes_recv - prev_net.bytes_recv) / 1024
    prev_net = net_io

    net_sent_history.append(sent)
    net_recv_history.append(recv)

    max_sent = max(net_sent_history) or 1.0
    max_recv = max(net_recv_history) or 1.0

    graph_sent = sparkline(net_sent_history, max_value=max_sent, color="cyan")
    graph_recv = sparkline(net_recv_history, max_value=max_recv, color="magenta")

    errors = net_io.errin + net_io.errout
    drops = net_io.dropin + net_io.dropout
    latency_text = network_cache.get("latency", "—")

    table = Table(title="[bold green]Network I/O[/bold green]", expand=True)
    table.add_column("Metric", style="bold")
    table.add_column("KB/s")
    table.add_column("Graph")

    table.add_row("Sent", f"[cyan]{sent:.1f}[/cyan]", graph_sent)
    table.add_row("Recv", f"[magenta]{recv:.1f}[/magenta]", graph_recv)
    table.add_row("Peak Sent", f"{max_sent:.1f}", Text("Peak", style="dim"))
    table.add_row("Peak Recv", f"{max_recv:.1f}", Text("Peak", style="dim"))
    table.add_row("Errors", f"{errors}", Text("Packets", style="red" if errors else "dim"))
    table.add_row("Drops", f"{drops}", Text("Packets", style="yellow" if drops else "dim"))
    table.add_row("Latency", latency_text, Text("Ping", style="dim"))

    return Panel(table, border_style="grey37")

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google's DNS
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unavailable"

def get_system_panel():
    load1, load5, load15 = os.getloadavg()
    uptime_sec = time.time() - psutil.boot_time()
    hours = int(uptime_sec // 3600)
    minutes = int((uptime_sec % 3600) // 60)
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ip_address = get_ip_address()

    # System metadata
    uname = os.uname()
    hostname = uname.nodename
    kernel = uname.release

    table = Table(title="[bold blue]System Info[/bold blue]", expand=True)
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    table.add_row("Load Avg", f"[white]{load1:.2f}, {load5:.2f}, {load15:.2f}[/white]")
    table.add_row("Uptime", f"[white]{hours}h {minutes}m[/white]")
    table.add_row("Time", f"[white]{now}[/white]")
    table.add_row("IP Address", f"[white]{ip_address}[/white]")
    table.add_row("Hostname", f"[white]{hostname}[/white]")
    table.add_row("Kernel", f"[white]{kernel}[/white]")

    return Panel(table, border_style="grey37")

def hydration_urgency_bar(days_ago, max_days=10, width=30):
    color = "green" if days_ago < 2 else "yellow" if days_ago < 5 else "red"
    filled = min(int((days_ago / max_days) * width), width)
    bar = "█" * filled + " " * (width - filled)
    return Text(f"{days_ago:.1f} days ago ", style=color) + Text(bar, style=color)

def sensor_zone_lines(value, zones, label, unit, max_val):
    return [
        format_zone_bar(value, zones, label=label, unit=unit),
        Text(f"Max {label}: {max_val:.2f} {unit}", style="bold green")
    ]

def fade_spike_history(history, decay=0.99, floor=28.5):
    for i in range(len(history)):
        if history[i] > floor:
            history[i] *= decay
        if history[i] < floor:
            history[i] = 0.0  # Optional: reset below threshold


def calculate_weeks(prop_date_str):
    try:
        prop_date = datetime.strptime(prop_date_str, "%d/%m/%y")
        today = datetime.today()
        delta = today - prop_date
        return max(delta.days // 7, 0)
    except Exception:
        return 0

def get_growth_stage():
    try:
        with open("plants.json", "r") as f:
            plants = json.load(f)
        if not plants:
            return "Unknown"
        prop_date = plants[0].get("propagation_date", "")
        weeks = calculate_weeks(prop_date)
        if weeks < 2:
            return "Seedling"
        elif weeks < 5:
            return "Veg"
        elif weeks < 8:
            return "Early Flower"
        elif weeks < 12:
            return "Mid Flower"
        elif weeks < 16:
            return "Late Flower"
        else:
            return "Finish"
    except:
        return "Unknown"

def update_scd4x_loop():
    while True:
        time.sleep(SCD4X_REFRESH)
        try:
            if scd4x.data_ready:
                co2_value = scd4x.CO2
                co2_history.append(co2_value)
                environment_data["CO₂"] = f"{co2_value} ppm"
                scd4x_data["Temperature"] = scd4x.temperature
                scd4x_data["Humidity"] = scd4x.relative_humidity
            else:
                environment_data["CO₂"] = "Not ready"
                scd4x_data["Temperature"] = "-"
                scd4x_data["Humidity"] = "-"
        except Exception as e:
            console.log(f"[red]SCD4X read error: {e}[/red]")
            environment_data["CO₂"] = "Error"
            scd4x_data["Temperature"] = "-"
            scd4x_data["Humidity"] = "-"
def update_bh1750_loop():
    while True:
        try:
            lux = bh1750.lux
            lux_history.append(lux)
            environment_data["Lux"] = f"{lux:.2f} Lux"
            max_values["Environment"]["Lux"] = max(
                max_values["Environment"].get("Lux", float('-inf')),
                lux
            )
        except Exception as e:
            environment_data["Lux"] = "Error"
        time.sleep(REFRESH_INTERVAL)

def get_last_watered_text():
    try:
        with open("watering_log.json", "r") as f:
            notes = json.load(f)
        if not notes:
            return Text("Last watered: [dim]No data[/dim]")
        last = max(notes, key=lambda n: n["timestamp"])
        date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(last["timestamp"]))
        method = last.get("method", "unknown")
        volume = last.get("volume_ml", "—")
        return Text(f"Last watered: {date_str} — {volume}ml via {method}", style="green")
    except Exception as e:
        return Text(f"[red]Error reading watering log: {e}[/red]")

def get_last_watering_info():
    try:
        with open("watering_log.json", "r") as f:
            notes = json.load(f)
        if not notes:
            return None
        last = max(notes, key=lambda n: n["timestamp"])
        days_ago = (time.time() - last["timestamp"]) / 86400
        date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(last["timestamp"]))
        return {
            "text": f"{last['volume_ml']}ml via {last['method']} — {last['uptake']} uptake — {last['pot_size_l']}L pot",
            "date": date_str,
            "days_ago": days_ago
        }
    except Exception as e:
        return {"error": str(e)}


def print_animated_banner(text="DaPortalZ", font="slant", delay=0.1):
    figlet = Figlet(font=font)
    banner_lines = figlet.renderText(text).splitlines()
    terminal_width = os.get_terminal_size().columns

    for line in banner_lines:
        padded_line = line.center(terminal_width)
        console.print(padded_line, style="bold cyan")
        time.sleep(delay)

def get_mood_lux_palette():
    from datetime import datetime
    hour = datetime.now().hour

    if hour < 6:
        return [(50, "grey23"), (1000, "dark_blue"), (5000, "purple"), (10000, "red"), (16000, "deep_pink1")]
    elif hour < 12:
        return [(50, "blue"), (1000, "green"), (5000, "yellow"), (10000, "orange1"), (16000, "red")]
    elif hour < 18:
        return [(50, "sky_blue1"), (1000, "bright_green"), (5000, "gold1"), (10000, "red"), (16000, "deep_pink1")]
    else:
        return [(50, "dark_orange"), (1000, "orange3"), (5000, "red"), (10000, "deep_pink1"), (16000, "magenta")]

def color_for_address(addr):
    val = int(addr, 16)
    if val < 0x20:
        return "grey50"
    elif val < 0x40:
        return "blue"
    elif val < 0x60:
        return "green"
    else:
        return "yellow"

i2c_scan_cache = {"addresses": [], "timestamp": "Never"}

def scan_i2c_loop(bus_id, interval):
    global i2c_scan_cache
    while True:
        bus = smbus2.SMBus(bus_id)
        found = []
        for address in range(0x03, 0x77):
            try:
                bus.write_quick(address)
                found.append(f"0x{address:02X}")
            except OSError:
                continue
        bus.close()
        i2c_scan_cache["addresses"] = found
        i2c_scan_cache["timestamp"] = datetime.now().strftime("%H:%M:%S")
        time.sleep(interval)

def log_watchdog(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(WATCHDOG_LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def read_watchdog_log_scrolled(lines=LOG_SCROLL_WINDOW):
    global log_scroll_index
    try:
        log_files = sorted(WATCHDOG_LOG_DIR.glob("watchdog_*.log"), reverse=True)
        if not log_files:
            return Text("No log files found.", style="dim")
        latest_log = log_files[0]
        with latest_log.open("r") as f:
            content = f.readlines()

        total_lines = len(content)
        if total_lines == 0:
            return Text("Log file is empty.", style="dim")

        # Scroll logic
        start = log_scroll_index % total_lines
        end = start + lines
        visible_lines = content[start:end]
        log_scroll_index += 1

        # Highlight errors and warnings
        styled_lines = []
        for line in visible_lines:
            if "❌" in line or "error" in line.lower():
                styled_lines.append(Text(line.strip(), style="bold red"))
            elif "⚠️" in line or "warning" in line.lower():
                styled_lines.append(Text(line.strip(), style="yellow"))
            elif "✓" in line or "healthy" in line.lower():
                styled_lines.append(Text(line.strip(), style="green"))
            else:
                styled_lines.append(Text(line.strip(), style="white"))

        return Text("\n").join(styled_lines)

    except Exception as e:
        return Text(f"[red]Log read error: {e}[/red]")

def update_as7341_loop(interval=3600):  # 3600 seconds = 1 hour
    global as7341_cache
    while True:
        try:
            channels = {
                "Violet": as7341.channel_415nm,
                "Indigo": as7341.channel_445nm,
                "Blue": as7341.channel_480nm,
                "Cyan": as7341.channel_515nm,
                "Green": as7341.channel_555nm,
                "Yellow": as7341.channel_590nm,
                "Orange": as7341.channel_630nm,
                "Red": as7341.channel_680nm
            }
            as7341_cache["channels"] = channels
            as7341_cache["timestamp"] = datetime.now().strftime("%H:%M:%S")
        except Exception as e:
            as7341_cache["channels"] = {"Error": str(e)}
        time.sleep(interval)

# def get

def get_ahtx0_stats():
    try:
        temp = ahtx0.temperature
        hum = ahtx0.relative_humidity
        ahtx0_temp_history.append(temp)
        ahtx0_hum_history.append(hum)

        max_values["AHTx0"] = {
            "Temp": max(max_values.get("AHTx0", {}).get("Temp", float('-inf')), temp),
            "Hum": max(max_values.get("AHTx0", {}).get("Hum", float('-inf')), hum)
        }

        return {"Temperature": temp, "Humidity": hum}
    except Exception as e:
        return {"Sensor Error": str(e)}

def get_htu21d_stats():
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

        # Update max tracker
        max_values["Environment"]["Lux"] = max(
            max_values["Environment"].get("Lux", float('-inf')),
            lux
        )

        # Populate shared environment dictionary
        environment_data["Lux"] = f"{lux:.2f} Lux"

        return {"Lux": lux}
    except Exception as e:
        environment_data["Lux"] = "Error"
        return {"Sensor Error": str(e)}

def get_as7341_panel():
    try:
        channels = as7341_cache.get("channels", {})
        timestamp = as7341_cache.get("timestamp", "Never")
        if "Error" in channels:
            return Panel(f"[red]Sensor Error: {channels['Error']}[/red]", title="🌈 AS7341 Spectral Sensor", border_style="grey37")

        lines = []
        for name, value in channels.items():
            bar_len = min(int(value / 1000), 40)
            bar = "█" * bar_len
            color = name.lower()
            line = Text(f"{name:<7} [{value:5d}] ", style=color)
            line.append(bar, style=color)
            lines.append(line)
        lines.append(Text(f"Last updated: {timestamp}", style="dim"))
        return Panel(Text("\n").join(lines), title="🌈 AS7341 Spectral Sensor", border_style="grey37")
    except Exception as e:
        return Panel(f"[red]Panel Error: {e}[/red]", title="🌈 AS7341 Spectral Sensor", border_style="grey37")

def watchdog_ping_loop():
    while True:
        time.sleep(WATCHDOG_CHECK_INTERVAL)
        now = time.time()
        if not hasattr(console, "last_loop_time"):
            console.last_loop_time = now
            continue
        drift = now - console.last_loop_time
        if drift > WATCHDOG_STALL_THRESHOLD:
            log_watchdog(f"⚠️ Dashboard stalled! Drift: {drift:.2f}s")
            log_watchdog("Active threads:")
            for t in threading.enumerate():
                log_watchdog(f" - {t.name}")
            if hasattr(console, "last_exception"):
                log_watchdog(f"❌ Last Exception: {console.last_exception}")
        else:
            log_watchdog(f"✅ Dashboard healthy. Drift: {drift:.2f}s")
# Builds

def build_watchdog_log_panel():
    global WATCHDOG_SCROLL_INDEX, WATCHDOG_FILTER_MODE
    try:
        with open(WATCHDOG_LOG_FILE, "r") as f:
            lines = [line.strip() for line in f.readlines()]

        # Optional filtering
        if WATCHDOG_FILTER_MODE:
            lines = [line for line in lines if "⚠️" in line or "❌" in line]

        total_lines = len(lines)
        if total_lines == 0:
            body = Text("No watchdog entries yet.", style="dim")
        else:
            # Scroll logic with reset
            start = WATCHDOG_SCROLL_INDEX
            end = start + WATCHDOG_SCROLL_WINDOW
            if end >= total_lines:
                WATCHDOG_SCROLL_INDEX = 0
                start = 0
                end = WATCHDOG_SCROLL_WINDOW
            visible = lines[start:end]
            WATCHDOG_SCROLL_INDEX += 1
            body = Text("\n".join(visible), style="white")

        title = "🧩 Watchdog Logs"
        if WATCHDOG_FILTER_MODE:
            title += " [Filtered]"

        return Panel(body, title=title, border_style="grey37")

    except Exception as e:
        return Panel(f"[red]Error reading watchdog log: {e}[/red]", title="🧩 Watchdog Logs", border_style="red")

def build_i2c_panel():
    addresses = i2c_scan_cache.get("addresses", [])
    timestamp = i2c_scan_cache.get("timestamp", "Never")
    lines = [Text("🔌 Detected I²C Addresses", style="bold cyan")]
    for addr in addresses:
        color = color_for_address(addr)
        lines.append(Text(f" ├─ {addr}", style=color))
    return Panel(Text("\n").join(lines), title="🧭 I²C Port Map", border_style="grey37")

def build_averages_panel():
    try:
        temps = list(temp_all_history)
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
            Text(f"Mean:    {temp_mean:.2f} °C", style="green"),
            Text(f"Median:  {temp_median:.2f} °C", style="yellow"),
            Text(f"Mode:    {temp_mode} °C", style="blue"),
            Text("💧 Humidity Stats", style="bold underline"),
            Text(f"Mean:    {hum_mean:.2f} %", style="green"),
            Text(f"Median:  {hum_median:.2f} %", style="yellow"),
            Text(f"Mode:    {hum_mode} %", style="blue"),
        ]

        return Panel(Text("\n").join(lines), title="📈 Sensor Averages", border_style="grey37")

    except Exception as e:
        return Panel(f"[red]Error calculating averages: {e}[/red]", title="📈 Sensor Averages", border_style="red")

def build_ahtx0_panel():
    data = get_ahtx0_stats()
    if "Sensor Error" in data:
        body = f"[red]{data['Sensor Error']}[/red]"
    else:
        temp = data["Temperature"]
        hum = data["Humidity"]
        lines = []
        lines += sensor_zone_lines(temp, ZONES_TEMP, "Duct Temp", "°C", max_values["AHTx0"]["Temp"])
        lines += sensor_zone_lines(hum, ZONES_HUM, "Duct RH", "%", max_values["AHTx0"]["Hum"])
        body = Text("\n").join(lines)
    return Panel(body, title="🌀 Duct Sensor (AHTx0)", border_style="grey37")

def build_watering_panel():
    recent_notes = [n for n in watering_notes if time.time() - n["timestamp"] < 7 * 86400]
    if not recent_notes:
        body = Text("No watering notes in the last 7 days.", style="dim")
    else:
        lines = [f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(n['timestamp']))} — {n['text']}" for n in recent_notes[-5:]]
        body = Text("\n".join(lines), style="green")
    return Panel(body, title="🪴 Watering Log", border_style="grey37")

def build_htu21d_panel():
    data = get_htu21d_stats()
    if "Sensor Error" in data:
        body = f"[red]{data['Sensor Error']}[/red]"
    else:
        temp = data["Temperature"]
        hum = data["Humidity"]
        htu21d_history.append(temp)
        for i, val in enumerate(temp_all_history):
            temp_spike_history[i] = max(temp_spike_history[i], val)
        max_values["HTU21d"]["Temp"] = max(max_values["HTU21d"]["Temp"], temp)
        max_values["HTU21d"]["Hum"] = max(max_values["HTU21d"]["Hum"], hum)
        lines = []
        lines += sensor_zone_lines(temp, ZONES_TEMP, "Temp", "°C", max_values["HTU21d"]["Temp"])
        lines += sensor_zone_lines(hum, ZONES_HUM, "Humidity", "%", max_values["HTU21d"]["Hum"])
        body = Text("\n").join(lines)
    return Panel(body, title="💧 HTU21d Sensor", border_style="grey37")

def build_scd4x_panel():
    if isinstance(scd4x_data["Temperature"], float):
        temp = scd4x_data["Temperature"]
        hum = scd4x_data["Humidity"]
        scd4x_history.append(temp)
        for i, val in enumerate(temp_all_history):
            temp_spike_history[i] = max(temp_spike_history[i], val)
        max_values["SCD4X"]["Temp"] = max(max_values["SCD4X"]["Temp"], temp)
        max_values["SCD4X"]["Hum"] = max(max_values["SCD4X"]["Hum"], hum)
        lines = []
        lines += sensor_zone_lines(temp, ZONES_TEMP, "Temp", "°C", max_values["SCD4X"]["Temp"])
        lines += sensor_zone_lines(hum, ZONES_HUM, "Humidity", "%", max_values["SCD4X"]["Hum"])

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
        lines = []
        lines += sensor_zone_lines(temp, ZONES_TEMP, "Temp", "°C", max_values["BME280"]["Temp"])
        lines += sensor_zone_lines(hum, ZONES_HUM, "Humidity", "%", max_values["BME280"]["Hum"])
        body = Text("\n").join(lines)
    return Panel(body, title="🌤 BME280 Sensor", border_style="grey37")

def build_bh1750_panel():
    data = get_bh1750_stats()
    if "Sensor Error" in data:
        body = f"[red]{data['Sensor Error']}[/red]"
    else:
        lux_value = float(data['Light Level'].split()[0])
        # max_values["BH1750"]["Lux"] = max(max_values["BH1750"]["Lux"], lux_value)
        lines = [
            format_zone_bar(lux_value, get_mood_lux_palette(), label="Lux", unit="Lux", max_value=max_values["BH1750"]["Lux"]), 
            Text(f"Max Lux: {max_values['BH1750']['Lux']:.2f} Lux", style="bold green")
]

        body = Text("\n").join(lines)
    return Panel(body, title="🔆 BH1750 Sensor", border_style="grey37")

def build_environment_panel():
    try:
        co2_str = environment_data["CO₂"]
        pressure_str = environment_data["Pressure"]
        lux_str = environment_data.get("Lux", "Waiting...")

        co2_value = float(co2_str.split()[0]) if "ppm" in co2_str else 0.0
        pressure_value = float(pressure_str.split()[0]) if "hPa" in pressure_str else 0.0
        lux_value = float(lux_str.split()[0]) if "Lux" in lux_str else 0.0

        # Update max values
        max_values["Environment"]["CO₂"] = max(max_values["Environment"].get("CO₂", float('-inf')), co2_value)
        max_values["Environment"]["Pressure"] = max(max_values["Environment"].get("Pressure", float('-inf')), pressure_value)
        max_values["Environment"]["Lux"] = max(max_values["Environment"].get("Lux", float('-inf')), lux_value)

        # Build panel lines
        lines = []
        lines += sensor_zone_lines(co2_value, ZONES_CO2, "CO₂", "ppm", max_values["Environment"]["CO₂"])
        lines += sensor_zone_lines(pressure_value, ZONES_PRESSURE, "Pressure", "hPa", max_values["Environment"]["Pressure"])
        lines += sensor_zone_lines(lux_value, get_mood_lux_palette(), "Lux", "Lux", max_values["Environment"]["Lux"])

        body = Text("\n").join(lines)
    except Exception as e:
        body = f"[red]Sensor Error: {e}[/red]"

    return Panel(body, title="🌍 Environment", border_style="grey37")

def build_room_panel():
    try:
        temp = sht31.temperature
        humidity = sht31.relative_humidity
        sht31d_history.append(temp)
        for i, val in enumerate(temp_all_history):
            temp_spike_history[i] = max(temp_spike_history[i], val)
        for i, val in enumerate(sht31d_history):
            sht31d_spike_history[i] = max(sht31d_spike_history[i], val)
        max_values["Room"]["Temp"] = max(max_values["Room"]["Temp"], temp)
        max_values["Room"]["Hum"] = max(max_values["Room"]["Hum"], humidity)
        lines = []
        lines += sensor_zone_lines(temp, ZONES_TEMP_ROOM, "Room Temp", "°C", max_values["Room"]["Temp"])
        lines += sensor_zone_lines(humidity, ZONES_HUM, "Room Hum", "%", max_values["Room"]["Hum"])
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

        lines = []
        lines += sensor_zone_lines(temp_mcp, ZONES_TEMP, "MCP9808", "°C", max_values["Tent"]["MCP9808"])
        lines += sensor_zone_lines(temp_adt, ZONES_TEMP, "ADT7410", "°C", max_values["Tent"]["ADT7410"])
        if temp_bme is not None:
            lines += sensor_zone_lines(temp_bme, ZONES_TEMP, "BME280", "°C", max_values["Tent"]["BME280"])
        body = Text("\n").join(lines)
    except Exception as e:
        body = f"[red]Sensor Error: {e}[/red]"
    return Panel(body, title="🌡 Tent Heatmap", border_style="grey37")

def watering_rhythm_sparkline():
    try:
        with open("watering_log.json", "r") as f:
            notes = sorted(json.load(f), key=lambda n: n["timestamp"])
        intervals = [
            (notes[i]["timestamp"] - notes[i - 1]["timestamp"]) / 86400
            for i in range(1, len(notes))
        ]
        return sparkline(intervals, max_value=10, color="cyan")
    except:
        return Text("No rhythm data", style="dim")

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
            style = "bold red"
        else:
            block = " "
            style = "dim"
        graph.append((block, style))
    return Text.assemble(*[Text(char, style=style) for char, style in graph])
GRAPH_WIDTH = 30  # Compact width for snazzier layout

def label_bar(label, width=GRAPH_WIDTH, style="bold cyan"):
    return Text(f"{label:<8} ─┬" + "─" * width, style=style)

GRAPH_WIDTH = 30  # Compact width

def label_graph(label, graph_text, style="bold cyan"):
    return Text(f"{label:<8} ─┬ ", style=style) + graph_text

def build_sensor_graph_panel():
    try:
        lines = []

        # Helper: Annotate sensor with 3-line format
        def sensor_block(history, spike_history, zones, label, unit, threshold):
            try:
                current = mean(list(history)[-1:]) if history else 0.0
                max_val = max(spike_history) if spike_history else current
                breach_hours = sum(1 for val in history if val > threshold) * (REFRESH_INTERVAL / 3600)

                block = [
                    label_graph(label, render_high_graph(history, threshold, zones[-1][0], width=GRAPH_WIDTH), style=f"bold {zone_color(current, zones)}"),
                    Text(f"Max {label}: {max_val:.2f} {unit}", style="bold green"),
                    Text(f"Breach: {breach_hours:.1f} hrs", style="yellow" if breach_hours > 0 else "dim")
                ]
                return block
            except Exception as e:
                console.log(f"[red]{label} block error: {e}[/red]")
                return [Text(f"[red]{label} block error: {e}[/red]")]

        # 🌡 Temp block — now using standard format
        lines += sensor_block(temp_all_history, temp_spike_history, ZONES_TEMP, "Temp", "°C", 28.5)

        # Other sensor blocks
        lines += sensor_block(co2_history, co2_history, ZONES_CO2, "CO₂", "ppm", 1500)
        lines += sensor_block(lux_history, lux_history, ZONES_LUX, "Lux", "Lux", 9000)
        lines += sensor_block(hum_history, hum_history, ZONES_HUM, "Rh", "%", 70)
        lines += sensor_block(pressure_history, pressure_history, ZONES_PRESSURE, "hPa", "hPa", 1020)

        # Footer
        lines.append(Text("Time → [Last 24h]", style="dim"))

        body = Text("\n").join(lines)
        return Panel(body, title="📊 High Sensor Readings", border_style="grey37")

    except Exception as e:
        console.log(f"[red]Sensor Graph Error: {e}[/red]")
        return Panel(Text(f"[red]Sensor Graph Error: {e}[/red]"), title="📊 High Sensor Readings", border_style="red")


# Initialize thread metadata store
if not hasattr(console, "thread_meta"):
    console.thread_meta = {}

def build_dashboard_health_panel():
    lines = []
    active_threads = threading.enumerate()
    now = time.time()

    expected_threads = [
        "update_scd4x_loop",
        "watchdog_ping_loop"
    ]

    def format_thread_info(name):
        # Find matching thread
        thread = next((t for t in active_threads if name in t.name), None)
        is_active = thread is not None
        symbol = "[green]✓[/green]" if is_active else "[red]✗[/red]"

        # Metadata tracking
        meta = console.thread_meta.get(name, {})
        if is_active:
            if "start_time" not in meta:
                meta["start_time"] = now
                meta["restarts"] = meta.get("restarts", 0) + 1
            uptime = timedelta(seconds=int(now - meta["start_time"]))
        else:
            uptime = "—"

        # Age bar
        age_secs = (now - meta.get("start_time", now)) if is_active else 0
        age_color = "green" if age_secs < 60 else "yellow" if age_secs < 300 else "red"
        age_bar = "█" * min(int(age_secs / 10), 20)
        age_bar = Text(age_bar.ljust(20), style=age_color)

        # CPU/mem overlay
        try:
            process = psutil.Process(os.getpid())
            cpu = process.cpu_percent(interval=None)
            mem_mb = process.memory_info().rss / (1024 ** 2)
            usage = f"CPU: {cpu:.1f}% | Mem: {mem_mb:.1f}MB"
        except Exception:
            usage = "Usage: [red]Error[/red]"

        # Store updated meta
        console.thread_meta[name] = meta

        return Group(
            Text.from_markup(f"[bold]{symbol} Thread: {name}[/bold]"),
            Text(f"Uptime: {uptime}", style="cyan"),
            Text(f"Restarts: {meta.get('restarts', 0)}", style="magenta"),
            Text("Age Bar: ") + age_bar,
            Text(usage, style="blue")
        )

    for name in expected_threads:
        lines.append(format_thread_info(name))

    # 🔁 Refresh Interval
    try:
        lines.append(Text(f"Refresh Interval: {REFRESH_INTERVAL:.2f}s", style="cyan"))
    except NameError:
        lines.append(Text("Refresh Interval: [red]Not Defined[/red]"))

    # 🎭 Banner Status
    banner_flag = getattr(console, "banner_rendered", True)
    banner_status = "[green]✓[/green]" if banner_flag else "[yellow]Pending[/yellow]"
    lines.append(Text.from_markup(f"Banner Animation: {banner_status}"))

    # 🧨 Last Exception
    if hasattr(console, "last_exception"):
        lines.append(Text(f"[red]Last Exception: {console.last_exception}[/red]"))

    # 🫀 Frame Render Timing
    try:
        if not hasattr(console, "last_frame_time"):
            console.last_frame_time = now
            frame_delta = 0.0
        else:
            frame_delta = now - console.last_frame_time
            console.last_frame_time = now
        lines.append(Text(f"Frame Render Δ: {frame_delta:.3f}s", style="blue"))
    except Exception as e:
        lines.append(Text(f"Frame Timing Error: {str(e)}", style="red"))

    # 🧭 Loop Drift Detection
    try:
        if not hasattr(console, "last_loop_time"):
            console.last_loop_time = now
            drift = 0.0
        else:
            drift = now - console.last_loop_time - REFRESH_INTERVAL
            console.last_loop_time = now
        drift_color = "green" if abs(drift) < 0.1 else "yellow" if abs(drift) < 0.5 else "red"
        lines.append(Text(f"Loop Drift: {drift:+.3f}s", style=drift_color))
    except Exception as e:
        lines.append(Text(f"Loop Drift Error: {str(e)}", style="red"))

    # 🧾 Panel Assembly
    body = Group(*lines)
    return Panel(body, title="📊 Dashboard Runtime Monitor", border_style="grey37")


def get_mood_color(temp_str):
    try:
        temp_val = int(temp_str.replace("+", "").replace("°C", "").replace("−", "-"))
        if temp_val < 10:
            return "blue"
        elif temp_val < 20:
            return "green"
        elif temp_val < 28:
            return "yellow"
        else:
            return "red"
    except:
        return "grey50"



BLOCKS = "▁▂▃▄▅▆▇█"
GROW_ZONES = [
    (2, "blue"),     # Seedling
    (5, "green"),    # Veg
    (8, "yellow"),   # Early Flower
    (12, "orange1"), # Mid Flower
    (16, "red"),     # Late Flower
    (25, "magenta")  # Ripening / Finish
]

def grow_zone_color(week):
    for threshold, color in GROW_ZONES:
        if week <= threshold:
            return color
    return GROW_ZONES[-1][1]

def calc_progress(prop_date, repot_date=None):
    try:
        fmt = "%d/%m/%y"
        start = datetime.strptime(prop_date, fmt)
        now = datetime.now()

        total_weeks = 25  # Max visual cycle
        elapsed_weeks = max(0, (now - start).days // 7)
        bar_len = min(elapsed_weeks, total_weeks)

        blocks = []
        for week in range(1, bar_len + 1):
            block_idx = min(int((week / total_weeks) * (len(BLOCKS) - 1)), len(BLOCKS) - 1)
            block = BLOCKS[block_idx]
            color = grow_zone_color(week)
            blocks.append(Text(block, style=color))

        bar = Text.assemble(*blocks)
        bar.append(f" {elapsed_weeks}w", style="bold white")
        return bar

    except Exception:
        return Text("[Invalid]", style="red")

def build_summary_panel():
    global summary_scroll_index
    amber = "bold orange1"
    lines = []

    def timestamped(label, value):
        now = datetime.now().strftime("%H:%M:%S")
        return Text(f"[{now}] {label}: {value}", style=amber)

    # System stats
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    load1, load5, load15 = os.getloadavg()
    uptime_sec = time.time() - psutil.boot_time()
    hours = int(uptime_sec // 3600)
    minutes = int((uptime_sec % 3600) // 60)

    # Sensor snapshots
    ahtx0_data = get_ahtx0_stats()
    htu21d_data = get_htu21d_stats()
    bme280_data = get_bme280_stats()
    bh1750_data = get_bh1750_stats()
    co2 = environment_data.get("CO₂", "--")
    pressure = environment_data.get("Pressure", "--")
    last_note = recent_notes[-1]["text"] if recent_notes else "None"

    # Build full summary lines
    lines += [
        timestamped("CPU Load Avg", f"{load1:.2f}, {load5:.2f}, {load15:.2f}"),
        timestamped("Uptime", f"{hours}h {minutes}m"),
        timestamped("Memory Usage", f"{mem.percent:.1f}%"),
        timestamped("Disk Usage", f"{disk.percent:.1f}%"),
        timestamped("Net Sent", f"{net.bytes_sent / 1024:.1f} KB"),
        timestamped("Net Recv", f"{net.bytes_recv / 1024:.1f} KB"),
        timestamped("AHTx0 Temp", f"{ahtx0_data.get('Temperature', '--'):.2f} °C"),
        timestamped("AHTx0 Hum", f"{ahtx0_data.get('Humidity', '--'):.2f} %"),
        timestamped("HTU21d Temp", f"{htu21d_data.get('Temperature', '--'):.2f} °C"),
        timestamped("HTU21d Hum", f"{htu21d_data.get('Humidity', '--'):.2f} %"),
        timestamped("BME280 Temp", f"{bme280_data.get('Temperature', '--'):.2f} °C"),
        timestamped("BME280 Hum", f"{bme280_data.get('Humidity', '--'):.2f} %"),
        timestamped("BH1750 Lux", bh1750_data.get("Light Level", "--")),
        timestamped("CO₂", co2),
        timestamped("Pressure", pressure),
        timestamped("Last Watering Note", last_note)
    ]

    # Scroll logic
    total_lines = len(lines)
    if total_lines > SUMMARY_SCROLL_WINDOW:
        start = summary_scroll_index % total_lines
        end = start + SUMMARY_SCROLL_WINDOW
        visible = lines[start:end]
        summary_scroll_index += 1
    else:
        visible = lines

    body = Text("\n").join(visible)
    return Panel(body, title="📋 Summary Panel", border_style="grey37")

def build_grow_panel():
    try:
        with open("plants.json", "r") as f:
            plants_data = json.load(f)
    except Exception as e:
        return Panel(f"[red]Error loading plants.json: {e}[/red]", title="🌱 Grow Tracker", border_style="red")

    # 🧱 Table with expand=True to stretch full width
    table = Table(title="[bold green]Grow Tracker[/bold green]", expand=True)
    table.add_column("Name", style="bold green", justify="left", no_wrap=True)
    table.add_column("Type", style="cyan", justify="center")
    table.add_column("Propergated", style="magenta", justify="center")
    table.add_column("Re-Potted", style="yellow", justify="center")
    table.add_column("Progress", style="white", justify="left")
    table.add_column("Watering Schedule", style="blue", justify="center")
    table.add_column("Height", style="green", justify="center")

    for entry in plants_data:
        name = f"[link=]{entry['name']}[/link]"
        type_ = entry.get("type", "Unknown")
        prop_date = entry.get("propagation_date", "N/A")
        repot_date = entry.get("repot_date", "")
        last_watered = get_last_watered_text()
        progress = calc_progress(prop_date, repot_date)
        repot = repot_date if repot_date else "[Pending]"
        height_val = entry.get("height", 0.0)
        height = height_bar(height_val)
        table.add_row(name, type_, prop_date, repot, progress, last_watered, height)

    return Panel(table, border_style="grey37")

def build_watering_panel(show_panel=True):
    if not show_panel:
        return Panel(Text("Watering panel hidden", style="dim"), title="🪴 Watering Panel", border_style="grey37")

    info = get_last_watering_info()
    if not info or "error" in info:
        return Panel(Text(f"Error: {info.get('error', 'No data')}", style="red"), title="🪴 Watering Panel")

    urgency = hydration_urgency_bar(info["days_ago"])
    growth_stage = get_growth_stage()
    rhythm_graph = watering_rhythm_sparkline()

    lines = [
        Text(f"Last watered: {info['date']} — {info['text']}", style="green"),
        Text(f"Growth stage: {growth_stage}", style="magenta"),
        Text("Hydration urgency:", style="bold"),
        urgency,
        Text("Watering rhythm:", style="bold"),
        rhythm_graph
    ]
    return Panel(Text("\n").join(lines), title="🪴 Watering Panel", border_style="grey37")

def build_dashboard():
    # Main layout for top panels
    layout = Table.grid(padding=(1, 2))

    first_row_panels = [
        get_cpu_panel(),
        get_memory_panel(),
        get_disk_panel(),
        get_network_panel(),
        get_system_panel()
    ]


    second_row_panels = [
        build_dashboard_health_panel(),
        build_watchdog_log_panel(),
        build_i2c_panel(),
        build_tent_panel(),
        build_environment_panel()
    ]

    third_row_panels = [
        build_htu21d_panel(),
        build_scd4x_panel(),
        build_bme280_panel(),
        build_ahtx0_panel(),
        build_room_panel()
    ]
    fourth_row_panels = [
        get_as7341_panel(),
        build_averages_panel(),
        build_sensor_graph_panel()
    ]


    # Add rows to main layout
    layout.add_row(*first_row_panels)
    layout.add_row(*second_row_panels)
    layout.add_row(*third_row_panels)
    layout.add_row(*fourth_row_panels)

# 🪴 Toggle for Watering Panel
    SHOW_WATERING_PANEL = True  # Flip to False to hide panel

# 🌱 Separate layout for Grow Panel to avoid column stretching
    grow_layout = Table.grid(padding=(1, 2))
    grow_layout.add_row(build_grow_panel())  # Full-width, isolated

# 🧩 Optional Watering Panel
    if SHOW_WATERING_PANEL:
        grow_layout.add_row(build_watering_panel(show_panel=True))

# 🧠 Combine both layouts
    return Group(layout, grow_layout)


def run_dashboard():
    threading.Thread(target=update_scd4x_loop, name="update_scd4x_loop", daemon=True).start()
    threading.Thread(target=watchdog_ping_loop, name="watchdog_ping_loop", daemon=True).start()
    threading.Thread(target=update_as7341_loop, name="as7341_loop", daemon=True).start()
    threading.Thread(target=update_bh1750_loop, name="update_bh1750_loop", daemon=True).start()
    threading.Thread(target=update_network_latency_loop, name="network_latency_loop", daemon=True).start()
    # 🧼 Clear screen before banner
    os.system("clear")  

    # 🎭 Animated banner intro
    print_animated_banner()
    time.sleep(2)  # Optional pause before dashboard kicks in
    threading.Thread(target=scan_i2c_loop, args=(1, 7200), name="i2c_scan_loop", daemon=True).start()

    with Live(console=console, refresh_per_second=10, screen=True) as live:
        while True:
            try:
                fade_spike_history(temp_spike_history)
                live.update(build_dashboard())
                console.last_loop_time = time.time()
                time.sleep(REFRESH_INTERVAL)
            except Exception as e:
                console.last_exception = traceback.format_exc()
                log_watchdog(f"❌ Exception caught in main loop:\n{console.last_exception}")


if __name__ == "__main__":
    run_dashboard()
