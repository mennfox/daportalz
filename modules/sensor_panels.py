from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from modules.zone_utils import sensor_zone_lines
from dpz import (
    get_htu21d_stats,
    get_bme280_stats,
    get_ahtx0_stats,
    sht31,
    ZONES_TEMP,
    ZONES_TEMP_ROOM,
    ZONES_HUM,
    max_values
)

def build_htu21d_panel():
    data = get_htu21d_stats()
    if "Sensor Error" in data:
        return Panel(f"[red]{data['Sensor Error']}[/red]", title="💧 HTU21d Sensor", border_style="grey37")
    lines = sensor_zone_lines(data["Temperature"], ZONES_TEMP, "Temp", "°C", max_values["HTU21d"]["Temp"])
    lines += sensor_zone_lines(data["Humidity"], ZONES_HUM, "Humidity", "%", max_values["HTU21d"]["Hum"])
    return Panel(Text("\n").join(lines), title="💧 HTU21d Sensor", border_style="grey37")

def build_bme280_panel():
    data = get_bme280_stats()
    if "Sensor Error" in data:
        return Panel(f"[red]{data['Sensor Error']}[/red]", title="🌤 BME280 Sensor", border_style="grey37")
    lines = sensor_zone_lines(data["Temperature"], ZONES_TEMP, "Temp", "°C", max_values["BME280"]["Temp"])
    lines += sensor_zone_lines(data["Humidity"], ZONES_HUM, "Humidity", "%", max_values["BME280"]["Hum"])
    return Panel(Text("\n").join(lines), title="🌤 BME280 Sensor", border_style="grey37")

def build_ahtx0_panel():
    data = get_ahtx0_stats()
    if "Sensor Error" in data:
        return Panel(f"[red]{data['Sensor Error']}[/red]", title="🌀 Duct Sensor (AHTx0)", border_style="grey37")
    lines = sensor_zone_lines(data["Temperature"], ZONES_TEMP, "Duct Temp", "°C", max_values["AHTx0"]["Temp"])
    lines += sensor_zone_lines(data["Humidity"], ZONES_HUM, "Duct RH", "%", max_values["AHTx0"]["Hum"])
    return Panel(Text("\n").join(lines), title="🌀 Duct Sensor (AHTx0)", border_style="grey37")

def build_room_panel():
    try:
        temp = sht31.temperature
        humidity = sht31.relative_humidity
        lines = sensor_zone_lines(temp, ZONES_TEMP_ROOM, "Room Temp", "°C", max_values["Room"]["Temp"])
        lines += sensor_zone_lines(humidity, ZONES_HUM, "Room Hum", "%", max_values["Room"]["Hum"])
        return Panel(Text("\n").join(lines), title="🏠 Room Stats (SHT31)", border_style="grey37")
    except Exception as e:
        return Panel(f"[red]Sensor Error: {e}[/red]", title="🏠 Room Stats (SHT31)", border_style="grey37")

def build_environment_stack_panel():
    return Panel(
        Group(
            build_htu21d_panel(),
            build_bme280_panel(),
            build_ahtx0_panel(),
            build_room_panel()
        ),
        title="🌍 Environment Stack",
        border_style="grey37"
    )

