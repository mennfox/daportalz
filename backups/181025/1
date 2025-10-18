from rich.console import Console
from rich.panel import Panel
from rich.console import Group
from rich.table import Table
from rich.live import Live
import time
import board
import busio
from adafruit_as7341 import AS7341

# 🧩 Your custom modules only
from modules.as7341_sensor import init_as7341, create_as7341_cache, start_as7341_loop
from modules.as7341_panel import build_as7341_panel

# Initialize sensor and cache
as7341 = init_as7341()
as7341_cache = create_as7341_cache()
start_as7341_loop(as7341, as7341_cache)
from modules.watering import get_last_watered_text
from modules.dashboard_health import build_dashboard_health_panel
from modules.height import height_bar
from modules.moisture_chart import build_moisture_panel
from modules.system_panel import get_system_panel
from modules.i2c_panel import build_i2c_panel, scan_i2c_loop
from modules.performance_panels import (
    get_cpu_panel, get_memory_panel, get_disk_panel, get_network_panel
)
from modules.sensor_panels import build_sensor_cluster_panel

console = Console()
REFRESH_INTERVAL = 1.0

def build_dashboard():
    layout = Table.grid(padding=(1, 2))

    # 🧠 System + Performance Panels
    layout.add_row(
        get_cpu_panel(),
        get_memory_panel(),
        get_disk_panel(),
        get_network_panel(),
        get_system_panel()
    )

    # 🌱 Grow Tracker Panel
    grow_panel = Panel(
        Group(
            height_bar(42.0, 38.5),  # Example height values
            get_last_watered_text()
        ),
        title="🌱 Grow Tracker",
        border_style="green"
    )

    # 🌿 Moisture + I2C Panels
    layout.add_row(
        build_moisture_panel(),
        build_i2c_panel(),
        build_dashboard_health_panel(console),
        build_as7341_panel(as7341_cache),
        grow_panel
    )

    layout.add_row(build_sensor_cluster_panel())

    return layout

def run_dashboard():
    # Optional: start I2C scan loop
    import threading
    threading.Thread(target=scan_i2c_loop, name="i2c_scan_loop", daemon=True).start()

    with Live(console=console, refresh_per_second=10, screen=True) as live:
        while True:
            live.update(build_dashboard())
            time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    run_dashboard()

