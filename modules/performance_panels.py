# modules/performance_panels.py

import os, time, psutil, socket, subprocess
from collections import deque
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
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
core_colors = ["cyan", "magenta", "yellow", "green"]
network_cache = { "latency": "—", "last_ping": 0.0 }

# Helper functions
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

# Panel functions
def get_cpu_panel():
    cpu_percents = psutil.cpu_percent(percpu=True)
    freqs = psutil.cpu_freq(percpu=True)
    load1, load5, load15 = os.getloadavg()
    temps = psutil.sensors_temperatures().get("coretemp", [])
    temp_map = {i: t.current for i, t in enumerate(temps)} if temps else {}

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

    table.add_row("—", "—", "—", "—", Text(f"Load Avg: {load1:.2f}, {load5:.2f}, {load15:.2f}", style="dim"))
    table.add_row("—", "—", "—", "—", pressure_bar)

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

    table.add_row(f"{mem.used // (1024**2)} MB", f"{mem.total // (1024**2)} MB", colorize(mem.percent), graph)
    table.add_row(f"{swap.used // (1024**2)} MB", f"{swap.total // (1024**2)} MB", colorize(swap.percent), Text("Swap", style="dim"))
    table.add_row("—", "—", f"[bold magenta]{max_mem:.1f}%[/bold magenta]", Text("Peak", style="dim"))

    return Panel(table, border_style="grey37")

def get_disk_panel():
    usage = psutil.disk_usage("/")
    swap = psutil.swap_memory()
    if not hasattr(console, "prev_disk_io"):
        console.prev_disk_io = psutil.disk_io_counters()
    curr_io = psutil.disk_io_counters()
    read_rate = (curr_io.read_bytes - console.prev_disk_io.read_bytes) / 1024
    write_rate = (curr_io.write_bytes - console.prev_disk_io.write_bytes) / 1024
    console.prev_disk_io = curr_io

    bar = dual_bar_visual(usage.used, usage.total, width=30, used_color="blue", free_color="yellow")

    table = Table(title="[bold yellow]Disk & Swap[/bold yellow]", expand=True)
    table.add_column("Used")
    table.add_column("Total")
    table.add_column("Usage")
    table.add_column("Graph")

    table.add_row(f"{usage.used // (1024**3)} GB", f"{usage.total // (1024**3)} GB", colorize(usage.percent), bar)
    table.add_row(f"{swap.used // (1024**2)} MB", f"{swap.total // (1024**2)} MB", colorize(swap.percent), Text("Swap", style="dim"))
    table.add_row(f"{read_rate:.1f} KB/s", f"{write_rate:.1f} KB/s", "—", Text("I/O Rate", style="dim"))

    return Panel(table, border_style="grey37")

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
    table
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

