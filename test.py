import time
import csv
import os
from datetime import datetime
from modules.scd4x_module import SCD4x  # renamed import, no 'Glyph'

# ─── Initialize SCD4x ───────────────────────────────────────────────
scd4x = SCD4x()

# ─── CSV Setup ──────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
log_file = "logs/scd4x_test_log.csv"

def log_scd4x(temp, humidity, co2):
    """Append a row to CSV with timestamp + readings."""
    try:
        with open(log_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().isoformat(),
                f"{temp:.2f}",
                f"{humidity:.2f}",
                f"{co2:.0f}"
            ])
    except Exception as e:
        print(f"CSV Logging Error: {e}")

# ─── Main Loop ──────────────────────────────────────────────────────
def run_scd4x_logger():
    print("Starting SCD4x logger (20s interval)...")
    while True:
        scd4x.update()
        scd = scd4x.get_latest()

        # Parse values safely
        temp = float(scd["temperature"].split()[0]) if "°C" in scd.get("temperature", "") else None
        hum  = float(scd["humidity"].split()[0]) if "%" in scd.get("humidity", "") else None
        co2  = float(scd["co2"].split()[0]) if "ppm" in scd.get("co2", "") else None

        if temp and hum and co2:
            print(f"{datetime.now().isoformat()} | Temp: {temp:.2f} °C | Hum: {hum:.2f} % | CO₂: {co2:.0f} ppm")
            log_scd4x(temp, hum, co2)
        else:
            print(f"{datetime.now().isoformat()} | Invalid reading, skipping...")

        # Wait 20 seconds before next measurement
        time.sleep(20)

if __name__ == "__main__":
    run_scd4x_logger()

