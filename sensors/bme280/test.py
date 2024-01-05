import smbus2
import bme280
import plotext as plt


port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

# the sample method will take a single reading and return a
# compensated_reading object
data = bme280.sample(bus, address, calibration_params)

y1 = 234
y2 = 111

plt.plot(y1, xside= "lower", yside = "left", label = "lower left")
plt.plot(y2, xside= "upper", yside = "right", label = "upper right")

plt.title("Multiple Axes Plot")
plt.show()
# the compensated_reading class has the following attributes
# print(data.id)
# print(data.timestamp)
# print(data.temperature)
# print(data.pressure)
# print(data.humidity)

