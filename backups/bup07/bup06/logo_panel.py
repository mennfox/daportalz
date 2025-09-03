from rich.panel import Panel
from rich.text import Text

LOGO = """
██████╗  █████╗ ██████╗  ██████╗ ██████╗  █████╗ ██╗     ███████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝ ██╔══██╗██╔══██╗██║     ██╔════╝██╔════╝
██████╔╝███████║██████╔╝██║  ███╗██████╔╝███████║██║     █████╗  ███████╗
██╔═══╝ ██╔══██║██╔═══╝ ██║   ██║██╔═══╝ ██╔══██║██║     ██╔══╝  ╚════██║
██║     ██║  ██║██║     ╚██████╔╝██║     ██║  ██║███████╗███████╗███████║
╚═╝     ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
"""

def build_logo_panel():
    logo_text = Text(LOGO, style="bold magenta", justify="center", overflow="ignore")
    return Panel(logo_text, border_style="bright_cyan", title="DaPortalZ", title_align="center")

