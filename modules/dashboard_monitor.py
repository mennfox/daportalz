from datetime import datetime, timedelta
import threading
import time
import psutil
import os
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

console = Console()

# 🔧 Watchdog Config
WATCHDOG_CHECK_INTERVAL = 10.0
WATCHDOG_STALL_THRESHOLD = 5.0

# 🧠 Watchdog Thread (no logging)
def watchdog_ping_loop():
    while True:
        time.sleep(WATCHDOG_CHECK_INTERVAL)
        now = time.time()
        last_loop = getattr(console, "last_loop_time", None)
        if last_loop is None:
            console.last_loop_time = now
            continue
        drift = now - last_loop
        if drift > WATCHDOG_STALL_THRESHOLD:
            # Silent stall detection—no logging
            console.watchdog_alert = f"⚠️ Dashboard stalled! Drift: {drift:.2f}s"
        else:
            console.watchdog_alert = f"✅ Dashboard healthy. Drift: {drift:.2f}s"

# 📊 Runtime Monitor Panel
def build_dashboard_health_panel(refresh_interval=1.0):
    lines = []
    active_threads = threading.enumerate()
    now = time.time()
    expected_threads = ["update_scd4x_loop", "watchdog_ping_loop"]

    def format_thread_info(name):
        thread = next((t for t in active_threads if name in t.name), None)
        is_active = thread is not None
        symbol = "[green]✓[/green]" if is_active else "[red]✗[/red]"
        meta = console.thread_meta.get(name, {})
        if is_active:
            if "start_time" not in meta:
                meta["start_time"] = now
                meta["restarts"] = meta.get("restarts", 0) + 1
            uptime = timedelta(seconds=int(now - meta["start_time"]))
        else:
            uptime = "—"
        age_secs = (now - meta.get("start_time", now)) if is_active else 0
        age_color = "green" if age_secs < 60 else "yellow" if age_secs < 300 else "red"
        age_bar = "█" * min(int(age_secs / 10), 20)
        age_bar = Text(age_bar.ljust(20), style=age_color)
        try:
            process = psutil.Process(os.getpid())
            cpu = process.cpu_percent(interval=None)
            mem_mb = process.memory_info().rss / (1024 ** 2)
            usage = f"CPU: {cpu:.1f}% | Mem: {mem_mb:.1f}MB"
        except Exception:
            usage = "Usage: [red]Error[/red]"
        console.thread_meta[name] = meta
        return Group(
            Text.from_markup(f"[bold]{symbol} Thread: {name}[/bold]"),
            Text(f"Uptime: {uptime}", style="cyan"),
            Text(f"Restarts: {meta.get('restarts', 0)}", style="magenta"),
            Text("Age Bar: ") + age_bar,
            Text(usage, style="blue")
        )

    for name in expected_threads:
        lines.append(format_thread_info(name))

    lines.append(Text(f"Refresh Interval: {refresh_interval:.2f}s", style="cyan"))
    banner_flag = getattr(console, "banner_rendered", True)
    banner_status = "[green]✓[/green]" if banner_flag else "[yellow]Pending[/yellow]"
    lines.append(Text.from_markup(f"Banner Animation: {banner_status}"))

    last_exc = getattr(console, "last_exception", None)
    if last_exc:
        lines.append(Text(f"[red]Last Exception: {last_exc}[/red]"))

    try:
        last_frame = getattr(console, "last_frame_time", None)
        frame_delta = now - last_frame if last_frame else 0.0
        console.last_frame_time = now
        lines.append(Text(f"Frame Render Δ: {frame_delta:.3f}s", style="blue"))
    except Exception as e:
        lines.append(Text(f"Frame Timing Error: {str(e)}", style="red"))

    try:
        last_loop = getattr(console, "last_loop_time", None)
        drift = now - last_loop - refresh_interval if last_loop else 0.0
        console.last_loop_time = now
        drift_color = "green" if abs(drift) < 0.1 else "yellow" if abs(drift) < 0.5 else "red"
        lines.append(Text(f"Loop Drift: {drift:+.3f}s", style=drift_color))
    except Exception as e:
        lines.append(Text(f"Loop Drift Error: {str(e)}", style="red"))

    # 🧩 Show watchdog status (in-memory only)
    alert = getattr(console, "watchdog_alert", None)
    if alert:
        lines.append(Text(alert, style="magenta"))

    body = Group(*lines)
    return Panel(body, title="📊 Dashboard Runtime Monitor", border_style="grey37")

