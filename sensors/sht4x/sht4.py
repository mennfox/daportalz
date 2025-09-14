import time
import board
import adafruit_sht4x

i2c = board.I2C()  # uses board.SCL and board.SDA
sht4 = adafruit_sht4x.SHT4x(i2c)

sht4.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
# Can also set the mode to enable heater
# sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS

while True:
    sht4temperature, relative_humidity = sht4.measurements
    print(sht4temperature)
    # print(relative_humidity)
    time.sleep(1)
