import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
 
# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
 
# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)
 
# create the mcp object
mcp = MCP.MCP3008(spi, cs)
 
# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)
chan1 = AnalogIn(mcp, MCP.P1)
chan2 = AnalogIn(mcp, MCP.P2)
chan3 = AnalogIn(mcp, MCP.P3)
chan4 = AnalogIn(mcp, MCP.P4)
chan5 = AnalogIn(mcp, MCP.P5)
chan6 = AnalogIn(mcp, MCP.P6)
chan7 = AnalogIn(mcp, MCP.P7)

while True: 
    print('Raw ADC Value: ', chan0.value)
    print('Raw ADC Value: ', chan1.value)
    print('Raw ADC Value: ', chan2.value)
    print('Raw ADC Value: ', chan3.value)
    print('Raw ADC Value: ', chan4.value)
    print('Raw ADC Value: ', chan5.value)
    print('Raw ADC Value: ', chan6.value)
    print('Raw ADC Value: ', chan7.value)
    time.sleep(5)
