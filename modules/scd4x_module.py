import time
import board
import busio
import adafruit_scd4x
from collections import deque

class SCD4xGlyph:
    def __init__(self, maxlen=60):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.scd4x = adafruit_scd4x.SCD4X(self.i2c)
        self.scd4x.start_periodic_measurement()

        self.history = {
            "co2": deque([0.0] * maxlen, maxlen=maxlen),
            "temperature": deque([0.0] * maxlen, maxlen=maxlen),
            "humidity": deque([0.0] * maxlen, maxlen=maxlen)
        }

        self.latest = {
            "co2": "Waiting...",
            "temperature": "Waiting...",
            "humidity": "Waiting..."
        }

        self.max_values = {
            "co2": float("-inf"),
            "temperature": float("-inf"),
            "humidity": float("-inf")
        }

    def update(self):
        try:
            if self.scd4x.data_ready:
                co2 = self.scd4x.CO2
                temp = self.scd4x.temperature
                hum = self.scd4x.relative_humidity

                self.history["co2"].append(co2)
                self.history["temperature"].append(temp)
                self.history["humidity"].append(hum)

                self.latest["co2"] = f"{co2:.0f} ppm"
                self.latest["temperature"] = f"{temp:.1f} °C"
                self.latest["humidity"] = f"{hum:.1f} %"

                self.max_values["co2"] = max(self.max_values["co2"], co2)
                self.max_values["temperature"] = max(self.max_values["temperature"], temp)
                self.max_values["humidity"] = max(self.max_values["humidity"], hum)
            else:
                self.latest = {
                    "co2": "Not ready",
                    "temperature": "-",
                    "humidity": "-"
                }
        except Exception as e:
            self.latest = {
                "co2": "Error",
                "temperature": "-",
                "humidity": "-"
            }
            print(f"[SCD4x Error] {e}")

    def get_latest(self):
        return self.latest

    def get_max(self):
        return self.max_values

    def get_history(self):
        return self.history

