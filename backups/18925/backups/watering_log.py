# watering_log.py
import json, time
from pathlib import Path

LOG_PATH = Path("watering_log.json")

def load_watering_notes():
    if LOG_PATH.exists():
        with open(LOG_PATH, "r") as f:
            raw_notes = json.load(f)
            now = time.time()
            return [note for note in raw_notes if now - note["timestamp"] < 7 * 86400]
    return []

def save_watering_notes(notes):
    with open(LOG_PATH, "w") as f:
        json.dump(notes, f)

def add_note(text):
    notes = load_watering_notes()
    notes.append({"timestamp": time.time(), "text": text})
    save_watering_notes(notes)
    print(f"✅ Note saved: {text}")

if __name__ == "__main__":
    while True:
        note = input("💧 Enter watering note (or 'q' to quit): ")
        if note.lower() == 'q':
            break
        add_note(note)

