import board
import busio
import time
import threading
from datetime import datetime
from adafruit_as7341 import AS7341

def init_as7341():
    i2c = busio.I2C(board.SCL, board.SDA)
    return AS7341(i2c)

def create_as7341_cache():
    return {
        "channels": {},
        "timestamp": "Never"
    }

def start_as7341_loop(sensor, cache, interval=3600):
    def loop():
        while True:
            try:
                channels = {
                    "Violet": sensor.channel_415nm,
                    "Indigo": sensor.channel_445nm,
                    "Blue": sensor.channel_480nm,
                    "Cyan": sensor.channel_515nm,
                    "Green": sensor.channel_555nm,
                    "Yellow": sensor.channel_590nm,
                    "Orange": sensor.channel_630nm,
                    "Red": sensor.channel_680nm
                }
                cache["channels"] = channels
                cache["timestamp"] = datetime.now().strftime("%H:%M:%S")
            except Exception as e:
                cache["channels"] = {"Error": str(e)}
            time.sleep(interval)
    threading.Thread(target=loop, name="as7341_loop", daemon=True).start()

