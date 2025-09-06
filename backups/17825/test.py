from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
import time
import random  # Replace with actual sensor reads

console = Console()

# Constants
PANEL_WIDTH = 30
REFRESH_INTERVAL = 1.0  # seconds

# Simulated live data (replace with actual sensor reads)
def get_system_stats():
    return {
        "CPU": f"{round(random.uniform(4.0, 6.0), 1)}%",
        "RAM": f"{round(random.uniform(2.5, 3.5), 1)}%",
        "Disk": f"{round(random.uniform(15.0, 17.0), 1)}%",
        "Swap": "0.0%",
        "Swap Used": "0.0MB / 209.7MB",
        "Net Up": f"{round(random.uniform(11.0, 13.0), 1)}MB",
        "Net Down": f"{round(random.uniform(1.5, 2.5), 1)}MB"
    }

def get_sht31_data():
    return {
        "Temp": f"{round(random.uniform(27.5, 28.5), 2)}°C",
        "Humidity": f"{round(random.uniform(51.0, 53.0), 2)}%"
    }

def get_hts221_data():
    return {
        "Temp": f"{round(random.uniform(29.0, 30.0), 2)}°C",
        "Humidity": f"{round(random.uniform(76.0, 78.0), 2)}%"
    }

def get_scd4x_data():
    return {
        "CO₂": f"{round(random.uniform(500, 520), 2)} ppm",
        "Temp": f"{round(random.uniform(30.5, 31.5), 2)}°C",
        "Humidity": f"{round(random.uniform(51.0, 53.0), 2)}%"
    }

# Panel builders
def build_system_panel():
    stats = get_system_stats()
    body = "\n".join([f"[bold cyan]{k}:[/bold cyan] {v}" for k, v in stats.items()])
    return Panel(body, title="🖥 System Stats", border_style="cyan", width=PANEL_WIDTH)

def build_sensor_panel(title, data, color):
    body = "\n".join([f"[bold]{k}:[/bold] {v}" for k, v in data.items()])
    return Panel(body, title=title, border_style=color, width=PANEL_WIDTH)

# Main dashboard layout
def build_dashboard():
    table = Table.grid(padding=(0, 2))
    table.add_row(
        build_sensor_panel("🌿 SHT31-D", get_sht31_data(), "green"),
        build_sensor_panel("💧 HTS221", get_hts221_data(), "blue"),
        build_sensor_panel("🫁 SCD4x", get_scd4x_data(), "magenta")
    )
    layout = Table.grid()
    layout.add_row(build_system_panel())
    layout.add_row(table)
    return layout

# Live dashboard loop
def run_dashboard():
    with Live(console=console, refresh_per_second=10, screen=True) as live:
        while True:
            live.update(build_dashboard())
            time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    run_dashboard()
