from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from datetime import datetime

def build_as7341_panel(as7341_cache):
    try:
        channels = as7341_cache.get("channels", {})
        timestamp = as7341_cache.get("timestamp", "Never")

        if "Error" in channels:
            return Panel(f"[red]Sensor Error: {channels['Error']}[/red]", title="🌈 AS7341 Spectral Sensor", border_style="grey37")

        lines = []

        # Normalize values
        values = list(channels.values())
        max_val = max(values) if values else 1
        norm_values = [v / max_val for v in values]

        # Build SPD curve using Unicode blocks
        curve = Text("SPD Curve: ", style="bold")
        for norm in norm_values:
            height = int(norm * 8)  # 8 levels of block height
            block = "▁▂▃▄▅▆▇█"[height - 1] if height > 0 else " "
            curve.append(block, style="dim")

        lines.append(curve)
        lines.append(Text(""))  # Spacer

        # Add channel bars
        for name, value in channels.items():
            norm = value / max_val
            bar_len = int(norm * 90)
            bar = "█" * bar_len
            color = name.lower()

            line = Text(f"{name:<7} [{value:5d}] ", style=color)
            line.append(bar, style=color)
            lines.append(line)

        lines.append(Text(f"Last updated: {timestamp}", style="dim"))
        return Panel(Text("\n").join(lines), title="🌈 AS7341 Spectral Power Distribution", border_style="grey37")

    except Exception as e:
        return Panel(f"[red]Panel Error: {e}[/red]", title="🌈 AS7341 Spectral Sensor", border_style="grey37")
