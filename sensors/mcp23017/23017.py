# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
#
# SPDX-License-Identifier: MIT
 
# Simple demo of reading and writing the digital I/O of the MCP2300xx as if
# they were native CircuitPython digital inputs/outputs.
# Author: Tony DiCola
import time
 
import board
import busio
import digitalio
 
 
from adafruit_mcp230xx.mcp23017 import MCP23017
 
 
# Initialize the I2C bus:
i2c = busio.I2C(board.SCL, board.SDA)
 
# Create an instance of either the MCP23008 or MCP23017 class depending on
# which chip you're using:
mcp = MCP23017(i2c)  # MCP23017
 
# Optionally change the address of the device if you set any of the A0, A1, A2
# pins.  Specify the new address with a keyword parameter:
# mcp = MCP23017(i2c, address=0x21)  # MCP23017 w/ A0 set
 
# Now call the get_pin function to get an instance of a pin on the chip.
# This instance will act just like a digitalio.DigitalInOut class instance
# and has all the same properties and methods (except you can't set pull-down
# resistors, only pull-up!).  For the MCP23008 you specify a pin number from 0
# to 7 for the GP0...GP7 pins.  For the MCP23017 you specify a pin number from
# 0 to 15 for the GPIOA0...GPIOA7, GPIOB0...GPIOB7 pins (i.e. pin 12 is GPIOB4).
pin8 = mcp.get_pin(8)
pin9 = mcp.get_pin(9)
pin10 = mcp.get_pin(10)
pin11 = mcp.get_pin(11)
pin12 = mcp.get_pin(12)
pin13 = mcp.get_pin(13)
pin14 = mcp.get_pin(14)
pin15 = mcp.get_pin(15)
 
# Setup pin0 as an output that's at a high logic level.
pin8.switch_to_output(value=True)
pin9.switch_to_output(value=True)
pin10.switch_to_output(value=True)
pin11.switch_to_output(value=True)
pin12.switch_to_output(value=True)
pin13.switch_to_output(value=True)
pin14.switch_to_output(value=True)
pin15.switch_to_output(value=True)

# Now loop blinking the pin 0 output and reading the state of pin 1 input.
while True:
    # Blink pin 0 on and then off.
    pin8.value = True
    time.sleep(0.5)
    pin9.value = True
    time.sleep(0.5)
    pin10.value = True
    time.sleep(0.5)
    pin11.value = True
    time.sleep(0.5)
    pin12.value = True
    time.sleep(0.5)
    pin13.value = True
    time.sleep(0.5)
    pin14.value = True
    time.sleep(0.5)
    pin15.value = True
    time.sleep(0.5)
    pin8.value = False
    time.sleep(0.5)
    pin9.value = False
    time.sleep(0.5)
    pin10.value = False
    time.sleep(0.5)
    pin11.value = False
    time.sleep(0.5)
    pin12.value = False
    time.sleep(0.5)
    pin13.value = False
    time.sleep(0.5)
    pin14.value = False
    time.sleep(0.5)
    pin15.value = False
    time.sleep(0.5)
    exit()
