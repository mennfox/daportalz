from rich.console import Console
import random
import time

console = Console()

def render_dial_lines(value, label, max_value=100):
    pointer_pos = int((value / max_value) * 12)
    arc_top = "╭────────────╮"
    arc_mid = "│            │"
    arc_bot = "╰────────────╯"
    pointer = " " * pointer_pos + "▲"

    # Color zones
    if value < 33:
        color = "green"
    elif value < 66:
        color = "yellow"
    else:
        color = "red"

    return [
        f"[bold {color}]{label:^16}[/bold {color}]",
        f"[cyan]{arc_top}[/cyan]",
        f"[cyan]{arc_mid}[/cyan]",
        f"[cyan]{arc_bot}[/cyan]",
        f"[{color}]{pointer}  {value:>5.1f}%[/{color}]"
    ]

def run_dual_dials():
    try:
        while True:
            val1 = random.uniform(0, 100)
            val2 = random.uniform(0, 100)

            console.clear()
            lines1 = render_dial_lines(val1, "Drawdown Phase")
            lines2 = render_dial_lines(val2, "Crest Pressure")

            for l1, l2 in zip(lines1, lines2):
                console.print(f"{l1:<25} {l2}")

            console.print("\n[dim]⏳ Auto-updating every 10 seconds… Press Ctrl+C to exit.")
            time.sleep(10)
    except KeyboardInterrupt:
        console.print("\n[bold red]⛔ Ritual paused. Gauges disengaged.[/bold red]")

if __name__ == "__main__":
    run_dual_dials()

