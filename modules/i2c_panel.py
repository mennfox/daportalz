from datetime import datetime
import time
import smbus2
from rich.panel import Panel
from rich.text import Text

# 🔧 Global Cache
i2c_scan_cache = {"addresses": [], "timestamp": "Never"}

# 🔁 Background Scanner
def scan_i2c_loop(bus_id=1, interval=7200):
    global i2c_scan_cache
    while True:
        bus = smbus2.SMBus(bus_id)
        found = []
        for address in range(0x03, 0x77):
            try:
                bus.write_quick(address)
                found.append(f"0x{address:02X}")
            except OSError:
                continue
        bus.close()
        i2c_scan_cache["addresses"] = found
        i2c_scan_cache["timestamp"] = datetime.now().strftime("%H:%M:%S")
        time.sleep(interval)

# 🎨 Panel Builder
def build_i2c_panel():
    addresses = i2c_scan_cache.get("addresses", [])
    timestamp = i2c_scan_cache.get("timestamp", "Never")
    found = set(int(addr, 16) for addr in addresses)

    lines = [Text("🔌 I²C Port Map", style="bold cyan")]
    header = " " + " ".join(f"{x:X}" for x in range(16))
    lines.append(Text(header, style="bold white"))

    for row in range(0x00, 0x80, 0x10):
        line = f"{row:02X}:"
        for col in range(16):
            addr = row + col
            line += f" {addr:02X}" if addr in found else " --"
        lines.append(Text(line, style="white"))

    lines.append(Text(f"Last scan: {timestamp}", style="dim"))
    return Panel(Text("\n").join(lines), title="🧭 I²C Port Map", border_style="grey37")

