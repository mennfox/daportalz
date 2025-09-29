# modules/system_panel.py

from rich.panel import Panel
from rich.table import Table
import os
import time
import psutil
from datetime import datetime
import socket

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
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

