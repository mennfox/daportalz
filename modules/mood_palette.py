from datetime import datetime

def get_mood_lux_palette():
    hour = datetime.now().hour
    if hour < 6:
        return [
            (50, "grey23"),
            (1000, "dark_blue"),
            (5000, "purple"),
            (10000, "red"),
            (16000, "deep_pink1")
        ]
    elif hour < 12:
        return [
            (50, "blue"),
            (1000, "green"),
            (5000, "yellow"),
            (10000, "orange1"),
            (16000, "red")
        ]
    elif hour < 18:
        return [
            (50, "sky_blue1"),
            (1000, "bright_green"),
            (5000, "gold1"),
            (10000, "red"),
            (16000, "deep_pink1")
        ]
    else:
        return [
            (50, "dark_orange"),
            (1000, "orange3"),
            (5000, "red"),
            (10000, "deep_pink1"),
            (16000, "magenta")
        ]

