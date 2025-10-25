import os
import json, time
JSON_FOLDER = os.path.join(os.path.dirname(__file__), "..", "json")
JSON_FOLDER = os.path.abspath(JSON_FOLDER)  # Optional: resolves full path
from pathlib import Path
from rich.text import Text

LOG_PATH = Path("watering_log.json")

def get_last_watered_text():
    try:
        with open(LOG_PATH, "r") as f:
            notes = json.load(f)
        if not notes:
            return Text("Last watered: [dim]No data[/dim]")
        last_entry = max(notes, key=lambda n: n["timestamp"])
        date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(last_entry["timestamp"]))
        return Text(f"Last watered: {date_str}", style="green")
    except Exception as e:
        return Text(f"[red]Error reading watering log: {e}[/red]")

