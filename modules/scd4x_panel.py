from modules.scd4x_module import SCD4xGlyph
from rich.panel import Panel

scd4x = SCD4xGlyph()

def build_scd4x_panel():
    scd4x.update()
    data = scd4x.get_latest()

    body = f"CO₂: {data['co2']}\nTemperature: {data['temperature']}\nHumidity: {data['humidity']}"
    return Panel(body, title="🌿 SCD4x Sensor", border_style="green")

