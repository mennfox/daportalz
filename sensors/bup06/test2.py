import curses
import time

def type_line_with_cursor(stdscr, y, x, text, color_pair):
    for i, char in enumerate(text):
        for _ in range(3):  # Blink 3 times before typing each character
            stdscr.addstr(y, x + i, "_", curses.color_pair(color_pair))
            stdscr.refresh()
            time.sleep(0.03)
            stdscr.addstr(y, x + i, " ", curses.color_pair(color_pair))
            stdscr.refresh()
            time.sleep(0.03)
        stdscr.addstr(y, x + i, char, curses.color_pair(color_pair))
        stdscr.refresh()
        time.sleep(0.05)

def draw_log_panel(stdscr, log_entries):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    max_y, max_x = stdscr.getmaxyx()
    panel_height = max_y - 2

    while True:
        stdscr.clear()
        stdscr.border()
        stdscr.addstr(0, 2, "💧 Watering Log", curses.color_pair(1))

        # Display existing log entries except the newest
        for i, entry in enumerate(log_entries[-(panel_height - 2):-1]):
            stdscr.addstr(i + 1, 2, entry, curses.color_pair(2))

        stdscr.refresh()

        # Simulate new log entry
        time.sleep(0.01)
        timestamp = time.strftime("%H:%M:%S")
        new_entry = f"[{timestamp}] Watered zone 3 🌱"
        log_entries.append(new_entry)

        # Type out the new entry with blinking cursor
        type_line_with_cursor(stdscr, panel_height - 1, 2, new_entry, 2)

        # Exit on 'q'
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
        except:
            pass

def launch_terminal_log():
    curses.wrapper(init_curses)

def init_curses(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Title
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Log text

    log_entries = [
        "[08:00:01] Watered zone 1 🌿",
        "[08:30:15] Watered zone 2 🌾"
    ]
    draw_log_panel(stdscr, log_entries)

if __name__ == "__main__":
    launch_terminal_log()

