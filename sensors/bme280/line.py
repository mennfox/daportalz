import plotext as plt
# Live Chart
temps = ["Temperature", "Humidity"]
hts = [324,567]

plt.bar(temps, hts, orientation = "h", width = 0.3, marker = 'fhd', color = 'green')
plt.title("Live Temperature & Humidity")
plt.clc() # to remove colors
plt.plotsize(103, (2 * len(temps) - 1) + 4) # 4 = (1 for x numerical ticks + 2 for x axes + 1 for title)
plt.show()
