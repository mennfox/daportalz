# SPDX-FileCopyrightText: 2020 by Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import sys
import time
import board
import adafruit_scd4x
from cfonts import render, say

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
scd4x = adafruit_scd4x.SCD4X(i2c)
# print("Serial number:", [hex(i) for i in scd4x.serial_number])

# print("Waiting for first measurement....")

scd4x.start_periodic_measurement()

while True:
    if scd4x.data_ready:
        a = scd4x.temperature
        b = scd4x.CO2
        c = scd4x.relative_humidity
        a_float = a
        b_float = b
        c_float = c
        formatted0_float = "{:.2f}".format(a_float)
        formatted1_float = "{:.2f}".format(b_float)
        formatted2_float = "{:.2f}".format(c_float)

        out1 = render(formatted0_float, font='3d', line-height='50', colors=['blue', 'cyan'], align='left')
        out2 = render(formatted2_float, colors=['blue', 'cyan'], align='right')
        out3 = render(formatted1_float, colors=['blue', 'cyan'], align='center')
        print(out1,out2,out3)
        sys.exit()
