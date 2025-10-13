# modules/utils.py

from rich.text import Text

def zone_color(value, zones):
    for threshold, color in zones:
        if value <= threshold:
            return color
    return zones[-1][1]

def bar_visual(value, max_value=100, width=20, color="white"):
    filled_len = min(int((value / max_value) * width), width)
    bar = "█" * filled_len + " " * (width - filled_len)
    return Text(bar, style=color)

def format_zone_bar(value, zones, label="", unit="", width=20, max_value=None):
    color = zone_color(value, zones)
    scale = max_value if max_value else zones[-1][0]
    bar = bar_visual(value, max_value=scale, width=width, color=color)
    return Text(f"{label:<10} {value:.1f}{unit:<3} ", style=color) + bar

def sensor_zone_lines(value, zones, label, unit, max_val):
    return [
        format_zone_bar(value, zones, label=label, unit=unit),
        Text(f"Max {label}: {max_val:.2f} {unit}", style="bold green")
    ]

def get_mood_lux_palette():
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 6:
        return [(50, "grey23"), (1000, "dark_blue"), (5000, "purple"), (10000, "red"), (16000, "deep_pink1")]
    elif hour < 12:
        return [(50, "blue"), (1000, "green"), (5000, "yellow"), (10000, "orange1"), (16000, "red")]
    elif hour < 18:
        return [(50, "sky_blue1"), (1000, "bright_green"), (5000, "gold1"), (10000, "red"), (16000, "deep_pink1")]
    else:
        return [(50, "dark_orange"), (1000, "orange3"), (5000, "red"), (10000, "deep_pink1"), (16000, "magenta")]

