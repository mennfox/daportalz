import json
import os

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

def height_bar(height, max_height=36):
    filled = int((height / max_height) * 30)
    empty = 30 - filled

    # Color zones
    if height < 12:
        color = "cyan"
    elif height < 24:
        color = "green"
    elif height < 36:
        color = "yellow"
    else:
        color = "red"

    return f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"

def update_height(plants):
    print("📏 Update plant heights (inches). Press Enter to skip.")
    for plant in plants:
        current = plant.get("height", 0.0)
        print(f"\n{plant['name']} (current: {current}\" inches)")
        new_height = input("New height: ").strip()
        if new_height:
            try:
                plant["height"] = float(new_height)
            except ValueError:
                print("⚠️ Invalid number. Skipping.")

def display_growth(plants):
    print("\n🌱 Growth Overview")
    for plant in plants:
        name = plant.get("name", "Unnamed")
        height = plant.get("height", 0.0)
        print(f"\n{name} - {height}\"")
        print(height_bar(height))

def height_bar(height, max_height=24.0, width=20):
    zones = [(2, "blue"), (5, "green"), (8, "yellow"), (12, "orange1"), (16, "red"), (25, "magenta")]
    color = next((c for t, c in zones if height <= t), zones[-1][1])
    filled = min(int((height / max_height) * width), width)
    bar = "█" * filled + " " * (width - filled)
    return Text(bar, style=color)

def main():
    print("🌿 Height Tracker Module")
    plants = load_plants()
    if not plants:
        print("⚠️ No existing plants found.")
        return

    update_height(plants)
    save_plants(plants)
    display_growth(plants)
    print(f"\n✅ Height updated for {len(plants)} plants.")

if __name__ == "__main__":
    main()

