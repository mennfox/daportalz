from time import sleep
import board
import busio
from adafruit_as7341 import AS7341
 
i2c = busio.I2C(board.SCL, board.SDA)
sensor = AS7341(i2c)
 
while True:
 
    print('Violet,',sensor.channel_415nm)
    print('Indigo,',sensor.channel_445nm)
    print('Blue,',sensor.channel_480nm)
    print('Cyan,',sensor.channel_515nm)
    print('Green,',sensor.channel_555nm)
    print('Yellow,',sensor.channel_590nm)
    print('Orange,',sensor.channel_630nm)
    print('Red,',sensor.channel_680nm)
    sleep(1)
