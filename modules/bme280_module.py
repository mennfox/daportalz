import smbus2
import bme280

# I²C setup
bme_bus = smbus2.SMBus(1)
bme_address = 0x76
bme_calibration = bme280.load_calibration_params(bme_bus, bme_address)

def get_bme280_stats():
    try:
        data = bme280.sample(bme_bus, bme_address, bme_calibration)
        return {
            "Temperature": data.temperature,
            "Humidity": data.humidity,
            "Pressure": data.pressure
        }
    except Exception as e:
        return {"Sensor Error": str(e)}

