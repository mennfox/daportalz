import time
import board
import busio
import adafruit_adt7410

i2c_bus = busio.I2C(board.SCL, board.SDA)
adt = adafruit_adt7410.ADT7410(i2c_bus, address=0x4b)
adt.high_resolution = True

while True:
        print(adt.temperature)
        time.sleep(0.5)
