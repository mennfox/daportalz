from rich.panel import Panel
from rich.text import Text

from modules.scd4x_module import SCD4xGlyph
from modules.bme280_module import get_bme280_stats
from modules.zone_utils import format_zone_bar, sensor_zone_lines
from modules.mood_palette import get_mood_lux_palette

import adafruit_mcp9808
import adafruit_adt7410
import adafruit_bh1750
import board
import busio

# Initialize I2C and sensors
i2c = busio.I2C(board.SCL, board.SDA)
mcp9808 = adafruit_mcp9808.MCP9808(i2c)
adt7410 = adafruit_adt7410.ADT7410(i2c)
bh1750 = adafruit_bh1750.BH1750(i2c)
scd4x = SCD4xGlyph()

# Zone thresholds
ZONES_TEMP = [(18, "blue"), (25, "green"), (28.5, "yellow"), (32, "red")]
ZONES_HUM = [(30, "sky_blue1"), (50, "cyan"), (70, "deep_sky_blue1"), (85, "steel_blue")]
ZONES_CO2 = [(600, "blue"), (1000, "green"), (1500, "yellow"), (2000, "red")]
ZONES_PRESSURE = [(980, "blue"), (1013, "green"), (1030, "yellow"), (1050, "red")]

def build_tent_environment_panel():
    try:
        # Update and retrieve sensor data
        scd4x.update()
        scd = scd4x.get_latest()
        bme = get_bme280_stats()

        # Extract readings
        temp_mcp = mcp9808.temperature
        temp_adt = adt7410.temperature
        temp_bme = bme["Temperature"]
        hum_bme = bme["Humidity"]
        pressure = bme["Pressure"]
        co2 = float(scd["co2"].split()[0]) if "ppm" in scd["co2"] else 0.0
        lux = bh1750.lux

        # Compose visual lines
        lines = []
        lines += sensor_zone_lines(temp_mcp, ZONES_TEMP, "MCP9808 - UPPER", "°C", temp_mcp)
        lines += sensor_zone_lines(temp_adt, ZONES_TEMP, "ADT7410 - MID", "°C", temp_adt)
        lines += sensor_zone_lines(temp_bme, ZONES_TEMP, "BME280 - LOWER", "°C", temp_bme)
        lines += sensor_zone_lines(hum_bme, ZONES_HUM, "BME280 - lower hum", "%", hum_bme)
        lines += sensor_zone_lines(co2, ZONES_CO2, "CO₂", "ppm", co2)
        lines += sensor_zone_lines(pressure, ZONES_PRESSURE, "Pressure", "hPa", pressure)
        lines += sensor_zone_lines(lux, get_mood_lux_palette(), "Lux", "Lux", lux)

        return Panel(Text("\n").join(lines), title="🌍 Tent + Environment", border_style="grey37")

    except Exception as e:
        return Panel(f"[red]Sensor Error: {e}[/red]", title="🌍 Tent + Environment", border_style="red")

