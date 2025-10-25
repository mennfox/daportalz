from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from rich.panel import Panel
from rich.text import Text
import threading
import time

# 🧪 Configuration for the Watchdog panel
@dataclass
class WatchdogConfig:
    log_dir: Path = Path("logs")
    log_file: Path = None
    scroll_window: int = 17
    filter_mode: bool = False
    scroll_index: int = 0
    last_loop_time: float = time.time()

    def __post_init__(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if not self.log_file:
            self.log_file = self.log_dir / "watchdog_latest.log"
        if not self.log_file.exists():
            self.log_file.touch()

# 🧪 Logging function to write entries to file
def log_watchdog(msg: str, config: WatchdogConfig):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with config.log_file.open("a") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception as e:
        print(f"Log write error: {e}")

# 🧪 Panel builder to display log entries
def build_watchdog_log_panel(config: WatchdogConfig) -> Panel:
    try:
        if not config.log_file.exists():
            return Panel(Text("No watchdog entries yet.", style="dim"), title="🧪 Watchdog Logs")

        with config.log_file.open("r") as f:
            lines = [line.strip() for line in f.readlines()]

        if config.filter_mode:
            lines = [line for line in lines if "⚠" in line or "❌" in line]

        total_lines = len(lines)
        if total_lines == 0:
            body = Text("Log file is empty.", style="dim")
        else:
            start = config.scroll_index % total_lines
            end = start + config.scroll_window
            visible = lines[start:end]
            config.scroll_index += 1
            body = Text("\n".join(visible), style="white")

        title = "🧪 Watchdog Logs"
        if config.filter_mode:
            title += " [Filtered]"

        return Panel(body, title=title, border_style="grey37")

    except Exception as e:
        return Panel(f"[red]Error reading watchdog log: {e}[/red]", title="🧪 Watchdog Logs", border_style="red")

# 🧪 Watchdog thread to monitor dashboard health
def watchdog_ping_loop(config: WatchdogConfig, console=None, stall_threshold=2.0, heartbeat_interval=300):
    while True:
        now = time.time()
        drift = now - config.last_loop_time - 1.0
        config.last_loop_time = now

        if drift > stall_threshold:
            log_watchdog(f"⚠️ Dashboard stalled! Drift: {drift:.2f}s", config)
            log_watchdog("Active threads:", config)
            for t in threading.enumerate():
                log_watchdog(f" - {t.name}", config)

        if console and hasattr(console, "last_exception"):
            log_watchdog(f"❌ Last Exception: {console.last_exception}", config)
        else:
            log_watchdog(f"✅ Dashboard healthy. Drift: {drift:.2f}s", config)

        if int(now) % heartbeat_interval == 0:
            log_watchdog("💓 Sentinel Echo heartbeat", config)

        time.sleep(1.0)

