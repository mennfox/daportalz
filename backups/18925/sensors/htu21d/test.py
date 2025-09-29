# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
import plotext as plt

import time
import board
import busio
from adafruit_htu21d import HTU21D
 
# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = HTU21D(i2c)

y1 = sensor.temperature
y2 = sensor.relative_humidity

plt.plot(y1, xside= "lower", yside = "left", label = "lower left")
plt.plot(y2, xside= "upper", yside = "right", label = "upper right")

plt.title("Multiple Axes Plot")
plt.show() 
 

