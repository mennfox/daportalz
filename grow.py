import json
import os
from datetime import datetime

PLANT_FILE = "/home/pi/plants.json"

def load_plants():
    if os.path.exists(PLANT_FILE):
        with open(PLANT_FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass
    return []

def save_plants(plants):
    with open(PLANT_FILE, "w") as f:
        json.dump(plants, f, indent=2)

def prompt_for_plants():
    plants = []
    i = 1
    print("🌱 Enter plant details. Leave name blank to finish.")
    while True:
        name = input(f"Plant #{i} name: ").strip()
        if not name:
            break

        type_ = input("Type (e.g., Auto): ").strip()
        prop_date = input("Propagation date (DD/MM/YY): ").strip()
        repot_date = input("Repot date (DD/MM/YY or 'none'): ").strip()
        height = input("Current height (inches): ").strip()

        # Normalize repot date
        repot_date = repot_date if repot_date.lower() != "none" else None

        plant = {
            "id": i,
            "name": name,
            "type": type_ or "Unknown",
            "propagation_date": prop_date or "Unknown",
            "repot_date": repot_date,
            "progress": None,
            "last_watered": None,
            "status": "Unknown",
            "height": float(height) if height else 0.0
        }
        plants.append(plant)
        i += 1
    return plants

def show_plants(plants):
    print("\n🌿 Grow Tracker Panel")
    for plant in plants:
        name = plant.get("name", "Unnamed")
        type_ = plant.get("type", "Unknown")
        height = plant.get("height", "N/A")
        print(f"{name} | Type: {type_} | Height: {height}\"")

def main():
    print("🪴 Grow Setup Utility")
    existing = load_plants()
    if existing:
        print(f"Found {len(existing)} existing plants. Overwrite? (y/N)")
        if input().lower() != "y":
            print("❌ Aborted. No changes made.")
            return

    new_plants = prompt_for_plants()
    if new_plants:
        save_plants(new_plants)
        print(f"✅ Saved {len(new_plants)} plants to {PLANT_FILE}")
        show_plants(new_plants)
    else:
        print("⚠️ No plants entered. File not updated.")

if __name__ == "__main__":
    main()

