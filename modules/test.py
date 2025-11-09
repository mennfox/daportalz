from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from time import sleep
from modules.scd4x_module import SCD4xGlyph

# ─── Setup ─────────────────────────────────────────────────────────
console = Console()
scd4x = SCD4xGlyph()
max_points = 30
temp_data = []
hum_data = []

def get_readings():
    scd4x.update()
    data = scd4x.get_latest()
    temp = float(data["temperature"].split()[0]) if "°C" in data["temperature"] else 0.0
    hum = float(data["humidity"].split()[0]) if "%" in data["humidity"] else 0.0
    return temp, hum

def render_line(data, label, color, height=10):
    if not data:
        return Text(f"{label}: no data", style="dim")

    max_val = max(data)
    min_val = min(data)
    span = max_val - min_val or 1
    scaled = [int((val - min_val) / span * (height - 1)) for val in data]

    lines = [f"{label:<6}"] + [""] * height
    for i in range(len(data)):
        for row in range(height):
            if height - row - 1 == scaled[i]:
                lines[row + 1] += "•"
            else:
                lines[row + 1] += " "

    return Text("\n".join(lines), style=color)

def run_live_graph():
    with Live(console=console, refresh_per_second=1) as live:
        while True:
            temp, hum = get_readings()
            temp_data.append(temp)
            hum_data.append(hum)
            if len(temp_data) > max_points:
                temp_data.pop(0)
                hum_data.pop(0)

            temp_graph = render_line(temp_data, "Temp", "red")
            hum_graph = render_line(hum_data, "Hum", "cyan")
            panel = Panel(Text.assemble(temp_graph, "\n\n", hum_graph), title="🌡️ Live Temp & Hum", border_style="grey37")
            live.update(panel)
            sleep(10)

if __name__ == "__main__":
    run_live_graph()

