# watering_log.py (module version)
import json, time
from pathlib import Path

LOG_PATH = Path("watering_log.json")

def load_watering_notes():
    if LOG_PATH.exists():
        with open(LOG_PATH, "r") as f:
            return json.load(f)
    return []

def save_watering_notes(notes):
    with open(LOG_PATH, "w") as f:
        json.dump(notes, f, indent=2)

def add_note(volume_ml, method, pot_size_l, interval_days, uptake, response_time_hr, leaf_status):
    note = {
        "timestamp": time.time(),
        "volume_ml": volume_ml,
        "method": method,
        "pot_size_l": pot_size_l,
        "interval_days": interval_days,
        "uptake": uptake,
        "response_time_hr": response_time_hr,
        "leaf_status": leaf_status
    }
    notes = load_watering_notes()
    notes.append(note)
    save_watering_notes(notes)
    return f"✅ Saved: {volume_ml}ml via {method}, {uptake} uptake in {response_time_hr}h"

def log_entry_interactive():
    try:
        volume_ml = int(input("💧 Volume (ml): "))
        method = input("🪴 Method (tray/top splash/both): ").strip()
        pot_size_l = float(input("🪣 Pot size (L): "))
        interval_days = int(input("⏱ Interval (days): "))
        uptake = input("🌊 Uptake (full/partial/slow): ").strip()
        response_time_hr = float(input("⏳ Uptake time (hrs): "))
        leaf_status = input("🍃 Leaf status (perky/clawing/yellowing): ").strip()

        return add_note(volume_ml, method, pot_size_l, interval_days, uptake, response_time_hr, leaf_status)
    except Exception as e:
        return f"❌ Error: {e}"

