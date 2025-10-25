from rich.panel import Panel
from rich.table import Table
import subprocess

def get_top_processes_panel():
    try:
        # Get top 8 processes with extended info
        output = subprocess.getoutput(
            "ps -eo pid,comm,%cpu,%mem,tty,stat,start_time,etime,user --sort=-%cpu | head -n 8"
        )
        lines = output.strip().split("\n")[1:]  # Skip header

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("PID", justify="right")
        table.add_column("Name", justify="left")
        table.add_column("CPU %", justify="right")
        table.add_column("MEM %", justify="right")
        table.add_column("TTY", justify="center")
        table.add_column("Status", justify="center")
        table.add_column("Start", justify="center")
        table.add_column("Elapsed", justify="center")
        table.add_column("User", justify="left")  # ✅ New column

        for line in lines:
            parts = line.split(None, 8)
            if len(parts) == 9:
                pid, name, cpu, mem, tty, stat, start, elapsed, user = parts
                table.add_row(pid, name, cpu, mem, tty, stat, start, elapsed, user)

        return Panel(table, title="🧠 Process Bloom Scroll", border_style="grey37")

    except Exception as e:
        return Panel(f"[red]Process Panel Error: {e}[/red]", title="🧠 Top Processes", border_style="grey37")
