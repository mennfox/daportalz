import json
import time
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# ─── Glyph Blocks ───────────────────────────────────────────────────────────────
BLOCKS = "▁▂▃▄▅▆▇█"
GROW_ZONES = [(2, "blue"), (5, "green"), (8, "yellow"), (12, "orange1"), (16, "red"), (25, "magenta")]

# ─── Moisture Logic ─────────────────────────────────────────────────────────────
def grow_zone_color(week):
    for threshold, color in GROW_ZONES:
        if week <= threshold:
            return color
    return GROW_ZONES[-1][1]

def calc_progress(prop_date, repot_date=None):
    try:
        fmt = "%d/%m/%y"
        start = datetime.strptime(prop_date, fmt)
        now = datetime.now()
        total_weeks = 25
        elapsed_weeks = max(0, (now - start).days // 7)
        bar_len = min(elapsed_weeks, total_weeks)
        blocks = []
        for week in range(1, bar_len + 1):
            block_idx = min(int((week / total_weeks) * (len(BLOCKS) - 1)), len(BLOCKS) - 1)
            block = BLOCKS[block_idx]
            color = grow_zone_color(week)
            blocks.append(Text(block, style=color))
        bar = Text.assemble(*blocks)
        bar.append(f" {elapsed_weeks}w", style="bold white")
        return bar
    except Exception:
        return Text("[Invalid]", style="red")

def classify_soil(voltage):
    if voltage < 2.3:
        return "Saturated", "blue"
    elif voltage < 2.8:
        return "Moist", "green"
    else:
        return "Dry", "yellow"

def read_moisture_channels():
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1015(i2c, address=0x49)
        channels = [AnalogIn(ads, ADS.P0), AnalogIn(ads, ADS.P1), AnalogIn(ads, ADS.P2), AnalogIn(ads, ADS.P3)]
        return [chan.voltage for chan in channels]
    except Exception:
        return [None, None, None, None]

# ─── Watering Logic ─────────────────────────────────────────────────────────────
def hydration_urgency_bar(days_ago, max_days=10, width=20):
    color = "green" if days_ago < 2 else "yellow" if days_ago < 5 else "red"
    filled = min(int((days_ago / max_days) * width), width)
    bar = "█" * filled + " " * (width - filled)
    return Text(f"{days_ago:.1f}d ", style=color) + Text(bar, style=color)

def get_last_watering_info_by_plant():
    try:
        with open("watering_log.json", "r") as f:
            notes = json.load(f)
        if not notes:
            return {}
        latest_by_plant = {}
        for note in sorted(notes, key=lambda n: n["timestamp"], reverse=True):
            name = note.get("plant_name", "Unknown")
            if name not in latest_by_plant:
                days_ago = (time.time() - note["timestamp"]) / 86400
                date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(note["timestamp"]))
                latest_by_plant[name] = {
                    "text": f"{note['volume_ml']}ml via {note['method']} — {note['uptake']} uptake — {note['pot_size_l']}L pot",
                    "date": date_str,
                    "days_ago": days_ago
                }
        return latest_by_plant
    except Exception:
        return {}

# ─── Unified Grow Panel ─────────────────────────────────────────────────────────
def build_grow_dashboard(plants_path="plants.json"):
    try:
        with open(plants_path, "r") as f:
            plants_data = json.load(f)
    except Exception as e:
        return Panel(f"[red]Error loading plants.json: {e}[/red]", title="🌱 Grow Dashboard", border_style="red")

    moisture_values = read_moisture_channels()
    watering_data = get_last_watering_info_by_plant()

    table = Table(title="[bold green]Grow Dashboard[/bold green]")
    table.add_column("Name", style="bold green", justify="left", no_wrap=True)
    table.add_column("Type", style="cyan", justify="center")
    table.add_column("Breeder", style="cyan", justify="center")
    table.add_column("Propergated", style="magenta", justify="center")
    table.add_column("Re-Potted", style="yellow", justify="center")
    table.add_column("Progress", style="white", justify="left")
    table.add_column("Height", style="green", justify="center")
    table.add_column("Harvest", style="bold yellow", justify="center")
    table.add_column("Moisture", style="blue", justify="center")
    table.add_column("Watering", style="blue", justify="left")

    for idx, entry in enumerate(plants_data):
        name = entry["name"]
        type_ = entry.get("type", "Unknown")
        breeder = entry.get("breeder", "Unknown")
        prop_date = entry.get("propagation_date", "N/A")
        repot_date = entry.get("repot_date", "")
        repot = repot_date if repot_date else "[Pending]"
        progress = calc_progress(prop_date, repot_date)
        height_val = entry.get("height", 0.0)
        harvest_weight = entry.get("harvest_weight", 0.0)
        height_bar = f"{height_val:.1f}cm" if height_val else "[No data]"
        harvest = f"{harvest_weight:.1f}g" if harvest_weight else "[Pending]"

        # Moisture alignment by index
        if idx < len(moisture_values) and moisture_values[idx] is not None:
            voltage = moisture_values[idx]
            condition, color = classify_soil(voltage)
            moisture_str = Text(f"{voltage:.2f}V [{condition}]", style=color)
        else:
            moisture_str = Text("[No data]", style="grey50")

        # Watering info per plant
        water_info = watering_data.get(name)
        if water_info:
            urgency = hydration_urgency_bar(water_info["days_ago"])
            watering_str = Text(f"{water_info['date']} — {water_info['text']}\n", style="blue") + urgency
        else:
            watering_str = Text("[No data]", style="grey50")

        table.add_row(
            f"[link=]{name}[/link]", type_, breeder, prop_date, repot,
            progress, height_bar, harvest, moisture_str, watering_str
        )

    return Panel(table, border_style="grey37", title="🌱 Grow Tracker + Moisture + Watering")

# ─── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    panel = build_grow_dashboard()
    console.print(panel)
