from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group
import psutil, os, time, subprocess, socket
from datetime import datetime
from collections import deque

# Import shared functions if needed
from test import sparkline, colorize, format_zone_bar, dual_bar_visual, zone_color

# Histories (can be passed in or redefined here)
HISTORY_LEN = 30
cpu_histories = [deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN) for _ in range(psutil.cpu_count())]
mem_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
disk_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
net_sent_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
net_recv_history = deque([0]*HISTORY_LEN, maxlen=HISTORY_LEN)
network_cache = {"latency": "—", "last_ping": 0.0}
prev_net = psutil.net_io_counters()
core_colors = ["cyan", "magenta", "yellow", "green"]

def get_system_panels():
    return [
        get_cpu_panel(),
        get_memory_panel(),
        get_disk_panel(),
        get_network_panel(),
        get_system_panel()
    ]

