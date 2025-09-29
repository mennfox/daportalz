import json
import os
from rich.text import Text
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

def growth_stage_label(height):
    if height < 2:
        return "[grey50]Germination[/grey50]"
    elif height < 6:
        return "[blue]Seedling[/blue]"
    elif height < 12:
        return "[cyan]Early Veg[/cyan]"
    elif height < 20:
        return "[green]Veg[/green]"
    elif height < 28:
        return "[chartreuse3]Late Veg[/chartreuse3]"
    elif height < 36:
        return "[yellow]Early Flower[/yellow]"
    elif height < 46:
        return "[orange1]Flowering[/orange1]"
    elif height <= 55:
        return "[magenta]Ripening[/magenta]"
    else:
        return "[red]Harvest Ready[/red]"

from rich.text import Text

def height_bar(height, prev_height=0.0, max_height=55):
    filled = int((height / max_height) * 30)
    empty = 30 - filled
    percent = int((height / max_height) * 100)
    delta = height - prev_height

    # Stage label and color logic
    if height < 2:
        color = "grey50"
        stage = "[grey50]Germination[/grey50]"
    elif height < 6:
        color = "blue"
        stage = "[blue]Seedling[/blue]"
    elif height < 12:
        color = "cyan"
        stage = "[cyan]Early Veg[/cyan]"
    elif height < 20:
        color = "green"
        stage = "[green]Veg[/green]"
    elif height < 28:
        color = "chartreuse3"
        stage = "[chartreuse3]Late Veg[/chartreuse3]"
    elif height < 36:
        color = "yellow"
        stage = "[yellow]Early Flower[/yellow]"
    elif height < 46:
        color = "orange1"
        stage = "[orange1]Flowering[/orange1]"
    elif height <= 55:
        color = "magenta"
        stage = "[magenta]Ripening[/magenta]"
    else:
        color = "red"
        stage = "[red]Harvest Ready[/red]"

    # Growth delta string
    if delta > 0:
        delta_str = f"[green]+{delta:.1f}\"[/green]"
    elif delta < 0:
        delta_str = f"[red]{delta:.1f}\"[/red]"
    else:
        delta_str = "[dim]0.0\"[/dim]"

    # Final bar string
    bar_str = (
        f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim] "
        f"[bold white]{height:.1f}\"[/bold white] ({percent}%) {delta_str} {stage}"
    )
    return Text.from_markup(bar_str)


def update_height(plants):
    print("📏 Update plant heights (inches). Press Enter to skip.")
    for plant in plants:
        current = plant.get("height", 0.0)
        print(f"\n{plant['name']} (current: {current}\" inches)")
        new_height = input("New height: ").strip()
        if new_height:
            try:
                new_val = float(new_height)
                plant["prev_height"] = current  # store previous
                plant["height"] = new_val
            except ValueError:
                print("⚠️ Invalid number. Skipping.")

def display_growth(plants):
    print("\n🌱 Growth Overview")
    for plant in plants:
        name = plant.get("name", "Unnamed")
        height = plant.get("height", 0.0)
        print(f"\n{name} - {height}\"")
        print(height_bar(height))

def archive_grow(plants, archive_dir="/home/pi/grow_archive"):
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    archive_file = os.path.join(archive_dir, f"grow_{timestamp}.json")
    with open(archive_file, "w") as f:
        json.dump(plants, f, indent=2)
    print(f"📦 Archived grow data to {archive_file}")

def append_readable_archive(plants, archive_file="/home/pi/grow_archive/grow_archive.txt"):
    os.makedirs(os.path.dirname(archive_file), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open(archive_file, "a") as f:
        f.write(f"\n🗓️ Grow Completed: {timestamp}\n")
        f.write("-" * 40 + "\n")
        for plant in plants:
            name = plant.get("name", "Unnamed")
            height = plant.get("height", 0.0)
            stage = growth_stage_label(height)
            f.write(f"{name}: {height:.1f}\" - {stage}\n")
        f.write("-" * 40 + "\n")


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

