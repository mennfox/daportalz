import json
from datetime import datetime

PLANT_FILE = "plants.json"

def load_plants():
    with open(PLANT_FILE, "r") as f:
        return json.load(f)

def save_plants(plants):
    with open(PLANT_FILE, "w") as f:
        json.dump(plants, f, indent=2)

def update_repot(name, new_date):
    plants = load_plants()
    updated = False

    for plant in plants:
        if plant["name"].lower() == name.lower():
            plant["repot_date"] = new_date
            updated = True
            break

    if updated:
        save_plants(plants)
        print(f"✅ Updated repot date for '{name}' to {new_date}")
    else:
        print(f"⚠️ No plant found with name '{name}'")

if __name__ == "__main__":
    name = input("Enter plant name to update: ").strip()
    new_date = input("Enter new repot date (DD/MM/YY): ").strip()
    update_repot(name, new_date)

