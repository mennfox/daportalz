# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
import time
import board
import adafruit_sht31d

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()
sensor = adafruit_sht31d.SHT31D(i2c, address=0x44)

while True:
    print(sensor.temperature,sensor.relative_humidity)
    time.sleep(1)
