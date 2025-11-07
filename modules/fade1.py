# modules/fade1.py

from pyfiglet import Figlet
from rich.text import Text
from rich.console import Console

def fade1_logo(font="block", style="bold cyan"):
    """
    Returns a right-aligned vertical DaPortalZ glyph as a styled Text block.
    """
    figlet = Figlet(font=font)
    console = Console()
    terminal_width = console.width

    logo_text = Text()

    for letter in "DaPortalZ":
        rendered = figlet.renderText(letter).splitlines()
        for line in rendered:
            logo_text.append(line.rjust(terminal_width) + "\n", style=style)
        logo_text.append("\n")  # spacing between letters

    return logo_text
