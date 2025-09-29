import time
import statistics
from collections import defaultdict
from datetime import datetime, timedelta

class RuntimeHealthPanel:
    def __init__(self, panel_registry, sensor_inputs, watchdog_logs):
        self.panel_registry = panel_registry  # Dict of panel_name: render_times
        self.sensor_inputs = sensor_inputs    # Dict of sensor_name: [timestamps, values]
        self.watchdog_logs = watchdog_logs    # List of log entries
        self.last_restart = None
        self.exceptions = defaultdict(int)
        self.loop_drift_history = []

    def update_loop_drift(self, drift_value):
        self.loop_drift_history.append(drift_value)
        if len(self.loop_drift_history) > 1440:  # Keep last 24h at 1-min intervals
            self.loop_drift_history.pop(0)

    def log_exception(self, exc_type):
        self.exceptions[exc_type] += 1

    def set_restart(self, reason):
        self.last_restart = (datetime.now(), reason)

    def get_daily_summary(self):
        avg_drift = round(statistics.mean(self.loop_drift_history), 3) if self.loop_drift_history else 0
        total_exceptions = sum(self.exceptions.values())
        restart_info = f"{self.last_restart[0].isoformat()} - {self.last_restart[1]}" if self.last_restart else "None"
        return {
            "Loop Drift Avg": avg_drift,
            "Exceptions": dict(self.exceptions),
            "Total Exceptions": total_exceptions,
            "Last Restart": restart_info,
            "Watchdog Pings": self._watchdog_summary()
        }

    def _watchdog_summary(self):
        success = sum(1 for log in self.watchdog_logs if "OK" in log)
        fail = sum(1 for log in self.watchdog_logs if "FAIL" in log)
        return f"{success} OK / {fail} FAIL"

    def get_panel_profiler(self):
        profiler = {}
        for panel, times in self.panel_registry.items():
            if times:
                profiler[panel] = {
                    "min": round(min(times), 2),
                    "max": round(max(times), 2),
                    "avg": round(statistics.mean(times), 2),
                    "lag_spike": any(t > 100 for t in times),
                    "drift_contrib": round(sum(times) / len(times), 2)
                }
        return profiler

    def get_sensor_health_index(self):
        health_index = {}
        now = time.time()
        for sensor, (timestamps, values) in self.sensor_inputs.items():
            freshness = round(now - timestamps[-1], 1) if timestamps else float('inf')
            volatility = round(statistics.stdev(values), 2) if len(values) > 1 else 0
            staleness = all(v == values[0] for v in values) if values else True
            health_index[sensor] = {
                "freshness": freshness,
                "volatility": volatility,
                "staleness": staleness,
                "confidence": self._confidence_score(freshness, volatility, staleness)
            }
        return health_index

    def _confidence_score(self, freshness, volatility, staleness):
        score = 100
        if freshness > 300: score -= 30
        if volatility < 0.5: score -= 20
        if staleness: score -= 50
        return max(score, 0)

    def render_overlay(self):
        print("🧠 Runtime Health Panel")
        print("────────────────────────────")
        print("📊 Daily Summary:")
        for k, v in self.get_daily_summary().items():
            print(f"  {k}: {v}")
        print("\n🧮 Panel Profiler:")
        for panel, stats in self.get_panel_profiler().items():
            print(f"  {panel}: {stats}")
        print("\n🌡️ Sensor Health Index:")
        for sensor, health in self.get_sensor_health_index().items():
            print(f"  {sensor}: {health}")
        print("────────────────────────────\n")

# Example usage (plug into your loop)
# panel = RuntimeHealthPanel(panel_registry, sensor_inputs, watchdog_logs)
# panel.update_loop_drift(current_drift)
# panel.log_exception("ZeroDivisionError")
# panel.set_restart("Auto-recovery triggered")
# panel.render_overlay()

