# modules/scd4x_module.py
import time
from typing import Optional, Dict

try:
    import board
    import busio
    import adafruit_scd4x
except Exception:
    board = None
    busio = None
    adafruit_scd4x = None


class SCD4xGlyph:
    """
    Reliable wrapper around SCD4x that:
    - Initializes I2C and starts periodic measurement
    - Waits for warm-up with bounded retries
    - Caches the last valid reading for dashboard use
    - Returns safe placeholders if data not ready
    """

    def __init__(self, warmup_seconds: int = 5, max_retries: int = 10, retry_interval: float = 0.5):
        self._i2c = None
        self._scd = None
        self._initialized = False

        self._last: Dict[str, str] = {
            "co2": "Not ready",
            "temperature": "-",
            "humidity": "-"
        }
        self._last_ts: float = 0.0

        self._warmup_seconds = warmup_seconds
        self._max_retries = max_retries
        self._retry_interval = retry_interval

        self._init_sensor()

    def _init_sensor(self):
        try:
            if board is None or busio is None or adafruit_scd4x is None:
                return  # libs missing; stay uninitialized

            self._i2c = busio.I2C(board.SCL, board.SDA)
            self._scd = adafruit_scd4x.SCD4X(self._i2c)

            # Ensure we are in periodic mode
            try:
                self._scd.stop_periodic_measurement()
            except Exception:
                pass

            self._scd.start_periodic_measurement()
            self._initialized = True

            # Initial warm-up pause
            time.sleep(max(0, self._warmup_seconds))

        except Exception:
            # Leave _initialized False to signal dashboard to show placeholder
            self._initialized = False

    def _read_once(self) -> Optional[Dict[str, str]]:
        """Attempt a single read if data_ready; return formatted dict or None."""
        try:
            if not self._initialized or self._scd is None:
                return None

            if getattr(self._scd, "data_ready", False):
                co2, temp, hum = self._scd.measurement
                # Some drivers use read_measurement(); support both:
                try:
                    co2, temp, hum = self._scd.read_measurement()
                except Exception:
                    # If read_measurement not available, rely on measurement property
                    pass

                return {
                    "co2": f"{float(co2):.1f} ppm",
                    "temperature": f"{float(temp):.1f}°C",
                    "humidity": f"{float(hum):.1f}%"
                }
            return None
        except Exception:
            return None

    def update(self) -> Dict[str, str]:
        """
        Try up to max_retries to get a ready measurement.
        If successful, cache and return. Otherwise, return last good or 'Not ready'.
        """
        # If not initialized, return last cached (likely 'Not ready')
        if not self._initialized:
            return self.get_latest()

        for _ in range(self._max_retries):
            reading = self._read_once()
            if reading:
                self._last = reading
                self._last_ts = time.time()
                return self._last
            time.sleep(self._retry_interval)

        # No fresh reading; return last cached (do not zero-out)
        return self.get_latest()

    def get_latest(self) -> Dict[str, str]:
        """Return the last cached reading (valid or placeholder)."""
        return dict(self._last)

    def get_latest_numeric(self) -> Dict[str, float]:
        """
        Numeric version for gauges; falls back to 0.0 if not ready.
        """
        out = {"co2": 0.0, "temperature": 0.0, "humidity": 0.0}
        latest = self.get_latest()
        try:
            if "ppm" in latest["co2"]:
                out["co2"] = float(latest["co2"].split()[0])
            if latest["temperature"].endswith("°C"):
                out["temperature"] = float(latest["temperature"].replace("°C", ""))
            if latest["humidity"].endswith("%"):
                out["humidity"] = float(latest["humidity"].replace("%", ""))
        except Exception:
            pass
        return out

    def last_timestamp(self) -> float:
        return self._last_ts

