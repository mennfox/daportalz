from rich.panel import Panel
from rich.text import Text
from datetime import datetime

# You’ll need to pass in the cache from dpz.py
def build_as7341_panel(as7341_cache):
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

