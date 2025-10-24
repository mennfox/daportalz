from rich.panel import Panel
from rich.text import Text
from statistics import mean
from modules.zone_utils import zone_color
from modules.sensor_histories import (
    temp_all_history, temp_spike_history,
    co2_history, hum_history, lux_history, pressure_history
)
from modules.zone_thresholds import (
    ZONES_TEMP, ZONES_CO2, ZONES_HUM, ZONES_LUX, ZONES_PRESSURE
)

