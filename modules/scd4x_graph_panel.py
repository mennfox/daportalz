from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from modules.scd4x_module import SCD4xGlyph

import time

MAX_POINTS = 60
REFRESH_INTERVAL = 10  # seconds

# Data buffers
temp_data = []
humid_data = []

def build_scd4x_graph_panel():
    scd4x = SCD4xGlyph()
    scd4x.update()
    scd = scd4x.get_latest()

    temp = float(scd["temperature"])
    humid = float(scd["humidity"])

    temp_data.append(temp)
    humid_data.append(humid)

    if len(temp_data) > MAX_POINTS:
        temp_data.pop(0)
        humid_data.pop(0)

    graph = Table.grid(padding=(0, 1))
    graph.add_column(justify="left")
    graph.add_row(Text("🌡️ SCD4x Temp & Humidity Tracker", style="bold magenta"))

    # Graph lines
    for i in range(len(temp_data)):
        t = temp_data[i]
        h = humid_data[i]
        t_bar = "█" * int((t / 40) * 30)
        h_bar = "█" * int((h / 100) * 30)
        graph.add_row(
            Text(f"{t:>5.1f}°C ", style="red") + Text(t_bar, style="red"),
            Text(f"{h:>5.1f}%  ", style="cyan") + Text(h_bar, style="cyan")
        )

    return Panel(graph, title="📈 SCD4x Graph", border_style="grey37")

