from rich.panel import Panel
from rich.text import Text
import psutil, os, time, threading
from datetime import datetime

REFRESH_INTERVAL = 1.0  # You can override this from main

def build_dashboard_health_panel(console, expected_threads=None):
    lines = []
    now = time.time()
    active_threads = threading.enumerate()
    expected_threads = expected_threads or ["update_scd4x_loop", "watchdog_ping_loop"]

    def format_thread_info(name):
        thread = next((t for t in active_threads if name in t.name), None)
        is_active = thread is not None
        symbol = "[green]✓[/green]" if is_active else "[red]✗[/red]"
        meta = console.thread_meta.get(name, {})
        if is_active:
            if "start_time" not in meta:
                meta["start_time"] = now
            meta["restarts"] = meta.get("restarts", 0) + 1
            uptime = datetime.timedelta(seconds=int(now - meta["start_time"]))
        else:
            uptime = "—"
        age_secs = (now - meta.get("start_time", now)) if is_active else 0
        age_color = "green" if age_secs < 60 else "yellow" if age_secs < 300 else "red"
        age_bar = Text("█" * min(int(age_secs / 10), 20), style=age_color).ljust(20)
        try:
            process = psutil.Process(os.getpid())
            cpu = process.cpu_percent(interval=None)
            mem_mb = process.memory_info().rss / (1024 ** 2)
            usage = f"CPU: {cpu:.1f}% | Mem: {mem_mb:.1f}MB"
        except Exception:
            usage = "Usage: [red]Error[/red]"
        console.thread_meta[name] = meta
        return Text.from_markup(f"{symbol} Thread: {name}\nUptime: {uptime}\nRestarts: {meta.get('restarts', 0)}\n{usage}")

    for name in expected_threads:
        lines.append(format_thread_info(name))

    try:
        lines.append(Text(f"Refresh Interval: {REFRESH_INTERVAL:.2f}s", style="cyan"))
    except NameError:
        lines.append(Text("Refresh Interval: [red]Not Defined[/red]"))

    banner_flag = getattr(console, "banner_rendered", True)
    banner_status = "[green]✓[/green]" if banner_flag else "[yellow]Pending[/yellow]"
    lines.append(Text.from_markup(f"Banner Animation: {banner_status}"))

    if hasattr(console, "last_exception"):
        lines.append(Text(f"[red]Last Exception: {console.last_exception}[/red]"))

    try:
        if not hasattr(console, "last_frame_time"):
            console.last_frame_time = now
        frame_delta = now - console.last_frame_time
        console.last_frame_time = now
        lines.append(Text(f"Frame Render Δ: {frame_delta:.3f}s", style="blue"))
    except Exception as e:
        lines.append(Text(f"Frame Timing Error: {str(e)}", style="red"))

    try:
        if not hasattr(console, "last_loop_time"):
            console.last_loop_time = now
        drift = now - console.last_loop_time - REFRESH_INTERVAL
        console.last_loop_time = now
        drift_color = "green" if abs(drift) < 0.1 else "yellow" if abs(drift) < 0.5 else "red"
        lines.append(Text(f"Loop Drift: {drift:+.3f}s", style=drift_color))
    except Exception as e:
        lines.append(Text(f"Loop Drift Error: {str(e)}", style="red"))

    return Panel(Text("\n").join(lines), title="📊 Dashboard Runtime Monitor", border_style="grey37")

