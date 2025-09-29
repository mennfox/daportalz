# Daportalz: Grow Tent Monitoring Dashboard

This project is a Linux-based dashboard designed to monitor and visualize environmental conditions inside a grow tent. Built for Raspberry Pi and similar systems, it integrates sensor data with a lightweight HTML interface for real-time feedback.

## 🌱 Features

- Live temperature, humidity, and light level monitoring
- Sensor integration via I2C and GPIO
- Modular Python backend with CSV logging
- Terminal-based UI using Rich and curses
- HTML frontend for remote viewing
- Graceful error handling and system recovery

## 🛠️ Technologies

- Python 3
- Raspberry Pi OS / Linux
- Rich, curses, Flask (optional)
- GitHub Actions (planned)
- HTML/CSS for dashboard interface

## 📦 Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/mennfox/daportalz.git
   cd daportalz
pip install -r requirements.txt
python dpz.py
🔒 Notes
This project is part of a personal automation system for grow tent management. It emphasizes modularity, transparency, and resilience — especially in sensor failure or system restarts.

📜 License
MIT License — feel free to fork, adapt, and contribute.
