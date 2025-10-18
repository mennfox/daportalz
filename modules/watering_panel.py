# watering_panel.py

from rich.panel import Panel
from rich.text import Text
import time
import json
from datetime import datetime
from statistics import mean

# Optional: move these to a shared config if needed
BLOCKS = "▁▂▃▄▅▆▇█"

def hydration_urgency_bar(days_ago, max_days=10, width=30):
    color = "green" if days_ago < 2 else "yellow" if days_ago < 5 else "red"
    filled = min(int((days_ago / max_days) * width), width)
    bar = "█" * filled + " " * (width - filled)
    return Text(f"{days_ago:.1f} days ago ", style=color) + Text(bar, style=color)

def watering_rhythm_sparkline():
    try:
        with open("watering_log.json", "r") as f:
            notes = sorted(json.load(f), key=lambda n: n["timestamp"])
        intervals = [
            (notes[i]["timestamp"] - notes[i - 1]["timestamp"]) / 86400
            for i in range(1, len(notes))
        ]
        return sparkline(intervals, max_value=10, color="cyan")
    except:
        return Text("No rhythm data", style="dim")

def sparkline(data, max_value=100, color="white"):
    blocks = BLOCKS
    safe_max = max_value if max_value > 0 else 1.0
    scaled = [min(int((val / safe_max) * (len(blocks) - 1)), len(blocks) - 1) for val in data]
    return Text("".join(blocks[i] for i in scaled), style=color)

def get_last_watering_info():
    try:
        with open("watering_log.json", "r") as f:
            notes = json.load(f)
        if not notes:
            return None
        last = max(notes, key=lambda n: n["timestamp"])
        days_ago = (time.time() - last["timestamp"]) / 86400
        date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(last["timestamp"]))
        return {
            "text": f"{last['volume_ml']}ml via {last['method']} — {last['uptake']} uptake — {last['pot_size_l']}L pot",
            "date": date_str,
            "days_ago": days_ago
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_weeks(prop_date_str):
    try:
        prop_date = datetime.strptime(prop_date_str, "%d/%m/%y")
        today = datetime.today()
        delta = today - prop_date
        return max(delta.days // 7, 0)
    except Exception:
        return 0

def get_growth_stage():
    try:
        with open("plants.json", "r") as f:
            plants = json.load(f)
        if not plants:
            return "Unknown"
        prop_date = plants[0].get("propagation_date", "")
        weeks = calculate_weeks(prop_date)
        if weeks < 2:
            return "Seedling"
        elif weeks < 5:
            return "Veg"
        elif weeks < 8:
            return "Early Flower"
        elif weeks < 12:
            return "Mid Flower"
        elif weeks < 16:
            return "Late Flower"
        else:
            return "Finish"
    except:
        return "Unknown"

def build_watering_panel(show_panel=True):
    if not show_panel:
        return Panel(Text("Watering panel hidden", style="dim"), title="🛴 Watering Panel", border_style="grey37")

    info = get_last_watering_info()
    if not info or "error" in info:
        return Panel(Text(f"Error: {info.get('error', 'No data')}", style="red"), title="🛴 Watering Panel")

    urgency = hydration_urgency_bar(info["days_ago"])
    growth_stage = get_growth_stage()
    rhythm_graph = watering_rhythm_sparkline()

    lines = [
        Text(f"Last watered: {info['date']} — {info['text']}", style="green"),
        Text(f"Growth stage: {growth_stage}", style="magenta"),
        Text("Hydration urgency:", style="bold"),
        urgency,
        Text("Watering rhythm:", style="bold"),
        rhythm_graph
    ]
    return Panel(Text("\n").join(lines), title="🛴 Watering Panel", border_style="grey37")

