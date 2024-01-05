import RPi.GPIO as GPIO
import os
import digitalio
import glob
import sys
import digitalio
import subprocess
import smbus2
import datetime
from time import sleep
import time
import board
import busio
import adafruit_bh1750
import adafruit_hts221
import bme280
import adafruit_ahtx0
from adafruit_htu21d import HTU21D
import adafruit_lps35hw
from termcolor import colored, cprint
from ascii_graph import Pyasciigraph
from ascii_graph.colors import *
from ascii_graph.colordata import vcolor
from colorama import Fore, Back, Style
# from ascii_graph.colordata import hcolor
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# Degress Sign¢
ds = u'\xb0C' # degree sign 
p = '%'
h = 'hPa'

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)

# Clear Screen
os.system('clear')

# Headings
now = datetime.datetime.now()
cprint("|   CURRENT TIME    |                TEMPERATURE               |           HUMIDITY          |       PRESSURE      |   LUX    |", 'blue',  'on_white', attrs=['bold'])
cprint("|                   |    Ext   |   Mid    |   Plvl   |  Inta   |   Ext   |   Mid   |   Plvl  |   Ext   |   Int     |           ", 'white', 'on_blue', attrs=['underline'])

while True:
     # Module Parameters
     # M
     # BME280
     port = 1
     address = 0x76
     bus = smbus2.SMBus(port)
     calibration_params = bme280.load_calibration_params(bus, address)
     b280 = bme280.sample(bus, address, calibration_params)
     hts = adafruit_hts221.HTS221(i2c)
     htu = HTU21D(i2c)
     aht = adafruit_ahtx0.AHTx0(i2c)
     lps = adafruit_lps35hw.LPS35HW(i2c)
     bh = adafruit_bh1750.BH1750(i2c)

             
     # [Float Definitions]
     a = b280.temperature
     b = b280.humidity
     c = b280.pressure
     d = aht.temperature
     e = aht.relative_humidity
     f = htu.temperature
     g = htu.relative_humidity
     h = hts.temperature
     i = hts.relative_humidity
     j = lps.temperature
     k = lps.pressure
     l = bh.lux

     a_float = a
     b_float = b
     c_float = c
     d_float = d
     e_float = e
     f_float = f
     g_float = g
     h_float = h
     i_float = i
     j_float = j
     k_float = k
     l_float = l

     formatted0_float = "{:.2f}".format(a_float)
     formatted1_float = "{:.2f}".format(b_float)
     formatted2_float = "{:.0f}".format(c_float)
     formatted3_float = "{:.2f}".format(d_float)
     formatted4_float = "{:.2f}".format(e_float)
     formatted5_float = "{:.2f}".format(f_float)
     formatted6_float = "{:.2f}".format(g_float)
     formatted7_float = "{:.2f}".format(h_float)
     formatted8_float = "{:.2f}".format(i_float)
     formatted9_float = "{:.2f}".format(j_float)
     formatted10_float = "{:.0f}".format(k_float)
     formatted11_float = "{:.0f}".format(l_float)
     
     
     # Main GUI 
     now = datetime.datetime.now()
     print(now.strftime('%Y-%m-%d %H:%M:%S'),'|',formatted7_float,ds,'|',formatted0_float,ds,'|',formatted5_float,ds,'|         |',formatted8_float,'%','|',formatted1_float,'%','|',formatted6_float,'%','|',formatted10_float,'hPa','|',formatted2_float,'hPa  ','|',formatted11_float, end='\r')
     time.sleep(2) 

