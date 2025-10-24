from rich.panel import Panel
from rich.text import Text

from modules.zone_utils import zone_color
from statistics import mean

# Import shared histories and zones
from modules.sensor_histories import (
    temp_all_history, temp_spike_history,
    co2_history, hum_history, lux_history, pressure_history
)
from modules.zone_thresholds import (
    ZONES_TEMP, ZONES_CO2, ZONES_HUM, ZONES_LUX, ZONES_PRESSURE
)

BLOCKS = "▁▂▃▄▅▆▇█"
GRAPH_WIDTH = 30

def render_high_graph(data, threshold, max_value, width=GRAPH_WIDTH):
    graph = []
    for val in list(data)[-width:]:
        try:
            val = float(val)
        except:
            val = 0.0
        if val >= threshold:
            idx = min(int((val / max_value) * (len(BLOCKS) - 1)), len(BLOCKS) - 1)
            graph.append(BLOCKS[idx])
        else:
            graph.append(" ")
    return Text("".join(graph), style="bold green")

def label_graph(label, graph_text, style="bold cyan"):
    return Text(f"{label:<8} ─┬ ", style=style) + graph_text

def sensor_block(history, spike_history, zones, label, unit, threshold):
    try:
        current = mean(list(history)[-1:]) if history else 0.0
        max_val = max(spike_history) if spike_history else current
        breach_hours = sum(1 for val in history if val > threshold) * (1.0 / 3600)  # assuming 1s interval

        return [
            label_graph(label, render_high_graph(history, threshold, zones[-1][0]), style=f"bold {zone_color(current, zones)}"),
            Text(f"Max {label}: {max_val:.2f} {unit}", style="bold green"),
            Text(f"Breach: {breach_hours:.1f} hrs", style="yellow" if breach_hours > 0 else "dim")
        ]
    except Exception as e:
        return [Text(f"[red]{label} block error: {e}[/red]")]

def build_high_readings_panel():
    try:
        lines = []
        lines += sensor_block(temp_all_history, temp_spike_history, ZONES_TEMP, "Temp", "°C", 28.5)
        lines += sensor_block(co2_history, co2_history, ZONES_CO2, "CO₂", "ppm", 1500)
        lines += sensor_block(lux_history, lux_history, ZONES_LUX, "Lux", "Lux", 9000)
        lines += sensor_block(hum_history, hum_history, ZONES_HUM, "Rh", "%", 70)
        lines += sensor_block(pressure_history, pressure_history, ZONES_PRESSURE, "hPa", "hPa", 1020)
        lines.append(Text("Time → [Last 24h]", style="dim"))

        return Panel(Text("\n").join(lines), title="📊 High Sensor Readings", border_style="grey37")
    except Exception as e:
        return Panel(Text(f"[red]Sensor Graph Error: {e}[/red]"), title="📊 High Sensor Readings", border_style="red")

