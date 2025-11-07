from pyfiglet import Figlet
import os
import time
from rich.console import Console

console = Console()

def print_animated_banner(text="DaPortalZ", font="slant", delay=0.1):
    figlet = Figlet(font=font)
    banner_lines = figlet.renderText(text).splitlines()
    terminal_width = os.get_terminal_size().columns
    for line in banner_lines:
        padded_line = line.center(terminal_width)
        console.print(padded_line, style="bold cyan")
        time.sleep(delay)
