import smbus2
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

# the sample method will take a single reading and return a compensated_reading object
data = bme280.sample(bus, address, calibration_params)

# Round the temperature and pressure to two decimal places
temperature = round(data.temperature, 2)
pressure = round(data.pressure, 2)

print(f"Temperature: {temperature} °C")
print(f"Pressure: {pressure} hPa")

