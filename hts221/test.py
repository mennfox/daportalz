
import termplot

import time
import board
import busio
import adafruit_hts221
 
i2c = busio.I2C(board.SCL, board.SDA)
hts = adafruit_hts221.HTS221(i2c)
while True:
    termplot.plot([hts.temperature])
    time.sleep(1)
