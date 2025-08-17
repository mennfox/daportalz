import psutil
import os
import time
from datetime import datetime
from collections import deque
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

console = Console()

# History buffers
HISTORY_LEN = 30
cpu_histories = [deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN) for _ in range(psutil.cpu_count())]
mem_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
disk_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
net_sent_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
net_recv_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
prev_net = psutil.net_io_counters()

# Assign distinct colors to cores 0–3, fallback to white for others
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
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # UK format
    table = Table(title="[bold blue]System Info[/bold blue]", expand=True)
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Load Avg", f"[white]{load1:.2f}, {load5:.2f}, {load15:.2f}[/white]")
    table.add_row("Uptime", f"[white]{hours}h {minutes}m[/white]")
    table.add_row("Time", f"[white]{now}[/white]")
    return Panel(table, border_style="blue")

def build_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="top", ratio=2),
        Layout(name="bottom", ratio=1)
    )
    layout["top"].split_row(
        Layout(get_cpu_panel()),
        Layout(get_memory_panel()),
        Layout(get_disk_panel())
    )
    layout["bottom"].split_row(
        Layout(get_network_panel()),
        Layout(get_system_panel())
    )
    return layout

def main():
    with Live(build_layout(), refresh_per_second=1, screen=True) as live:
        while True:
            time.sleep(1)
            live.update(build_layout())

if __name__ == "__main__":
    main()
