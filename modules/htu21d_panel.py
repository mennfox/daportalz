# modules/htu21d_panel.py

from rich.panel import Panel
from rich.text import Text
from modules.sensor_core import (
    hts, ZONES_TEMP, ZONES_HUM,
    temp_all_history, temp_spike_history, hum_history, max_values
)

def sensor_zone_lines(value, zones, label, unit, max_val):
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

    return [
        format_zone_bar(value, zones, label=label, unit=unit),
        Text(f"Max {label}: {max_val:.2f} {unit}", style="bold green")
    ]

def get_htu21d_stats():
    try:
        temp = hts.temperature
        humidity = hts.relative_humidity
        temp_all_history.append(temp)
        for i, val in enumerate(temp_all_history):
            temp_spike_history[i] = max(temp_spike_history[i], val)
        hum_history.append(humidity)
        return {"Temperature": temp, "Humidity": humidity}
    except Exception as e:
        return {"Sensor Error": str(e)}

def build_htu21d_panel():
    data = get_htu21d_stats()
    if "Sensor Error" in data:
        body = f"[red]{data['Sensor Error']}[/red]"
    else:
        temp = data["Temperature"]
        hum = data["Humidity"]
        max_values["HTU21d"]["Temp"] = max(max_values["HTU21d"]["Temp"], temp)
        max_values["HTU21d"]["Hum"] = max(max_values["HTU21d"]["Hum"], hum)
        lines = []
        lines += sensor_zone_lines(temp, ZONES_TEMP, "Temp", "°C", max_values["HTU21d"]["Temp"])
        lines += sensor_zone_lines(hum, ZONES_HUM, "Humidity", "%", max_values["HTU21d"]["Hum"])
        body = Text("\n").join(lines)
    return Panel(body, title="💧 HTU21d Sensor", border_style="grey37")

