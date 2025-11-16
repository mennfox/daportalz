import os
import json
import time
from pathlib import Path
JSON_FOLDER = os.path.join(os.path.dirname(__file__), "..", "json")
JSON_FOLDER = os.path.abspath(JSON_FOLDER)  # Optional: resolves full path
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
    print(f"\n✅ Saved: {volume_ml}ml via {method}, {uptake} uptake in {response_time_hr}h\n")

def prompt_for_note():
    try:
        volume_ml = int(input("💧 Volume (ml): "))
        method = input("🪴 Method (tray/top splash/both): ").strip()
        pot_size_l = float(input("🪣 Pot size (L): "))
        interval_days = int(input("⏱ Interval (days): "))
        uptake = input("🌊 Uptake (full/partial/slow): ").strip()
        response_time_hr = float(input("⏳ Uptake time (hrs): "))
        leaf_status = input("🍃 Leaf status (perky/clawing/yellowing): ").strip()

        add_note(volume_ml, method, pot_size_l, interval_days, uptake, response_time_hr, leaf_status)
    except Exception as e:
        print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    print("🪴 Watering Log Entry Tool")
    while True:
        proceed = input("Log new watering entry? (y/n): ").strip().lower()
        if proceed != 'y':
            print("👋 Exiting watering log.")
            break
        prompt_for_note()

