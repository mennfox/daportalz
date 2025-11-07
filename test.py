import time
import random
from pyfiglet import Figlet
from rich.console import Console
from rich.text import Text
from rich.live import Live

console = Console()

def fade_retro_da():
    figlet = Figlet(font="block")  # Try "block", "big", "slant", "bubble", "doom"
    styles = ["dim white", "white", "bold white", "bold cyan", "bold magenta"]
    duration = 20  # seconds
    start_time = time.time()

    with Live(console=console, refresh_per_second=5, screen=False) as live:
        while time.time() - start_time < duration:
            style = random.choice(styles)

            d_lines = figlet.renderText("D").splitlines()
            a_lines = figlet.renderText("A").splitlines()
            combined = d_lines + [""] + a_lines  # vertical stack

            styled_text = Text()
            for line in combined:
                styled_text.append(line.center(console.width) + "\n", style=style)

            live.update(styled_text)
            time.sleep(random.uniform(0.6, 1.2))  # slow fade

fade_retro_da()
