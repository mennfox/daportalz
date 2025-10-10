from rich.panel import Panel
from rich.text import Text
from modules.utils import sensor_zone_lines, get_mood_lux_palette
from adafruit_mcp9808 import MCP9808
from adafruit_adt7410 import ADT7410
from bme280 import sample
from test import (
    bme_bus, bme_address, bme_calibration,
    max_values, ZONES_TEMP, ZONES_CO2, ZONES_PRESSURE,
    environment_data
)

def build_atmos_tent_panel(mcp9808: MCP9808, adt7410: ADT7410):
    try:
        # Tent sensors
        temp_mcp = mcp9808.temperature
        temp_adt = adt7410.temperature
        data_bme = sample(bme_bus, bme_address, bme_calibration)
        temp_bme = data_bme.temperature

        max_values["Tent"]["MCP9808"] = max(max_values["Tent"]["MCP9808"], temp_mcp)
        max_values["Tent"]["ADT7410"] = max(max_values["Tent"]["ADT7410"], temp_adt)
        max_values["Tent"]["BME280"] = max(max_values["Tent"]["BME280"], temp_bme)

        # Environment sensors
        co2_str = environment_data["CO₂"]
        pressure_str = environment_data["Pressure"]
        lux_str = environment_data.get("Lux", "Waiting...")

        co2_value = float(co2_str.split()[0]) if "ppm" in co2_str else 0.0
        pressure_value = float(pressure_str.split()[0]) if "hPa" in pressure_str else 0.0
        lux_value = float(lux_str.split()[0]) if "Lux" in lux_str else 0.0

        max_values["Environment"]["CO₂"] = max(max_values["Environment"]["CO₂"], co2_value)
        max_values["Environment"]["Pressure"] = max(max_values["Environment"]["Pressure"], pressure_value)
        max_values["Environment"]["Lux"] = max(max_values["Environment"]["Lux"], lux_value)

        # Build lines
        lines = []
        lines.append(Text("🌡 Tent Sensors", style="bold underline"))
        lines += sensor_zone_lines(temp_mcp, ZONES_TEMP, "MCP9808", "°C", max_values["Tent"]["MCP9808"])
        lines += sensor_zone_lines(temp_adt, ZONES_TEMP, "ADT7410", "°C", max_values["Tent"]["ADT7410"])
        lines += sensor_zone_lines(temp_bme, ZONES_TEMP, "BME280", "°C", max_values["Tent"]["BME280"])

        lines.append(Text("\n🌍 Environment Sensors", style="bold underline"))
        lines += sensor_zone_lines(co2_value, ZONES_CO2, "CO₂", "ppm", max_values["Environment"]["CO₂"])
        lines += sensor_zone_lines(pressure_value, ZONES_PRESSURE, "Pressure", "hPa", max_values["Environment"]["Pressure"])
        lines += sensor_zone_lines(lux_value, get_mood_lux_palette(), "Lux", "Lux", max_values["Environment"]["Lux"])

        body = Text("\n").join(lines)
    except Exception as e:
        body = Text(f"[red]Sensor Error: {e}[/red]")

    return Panel(body, title="🌡🌍 AtmosTent Panel", border_style="grey37")

