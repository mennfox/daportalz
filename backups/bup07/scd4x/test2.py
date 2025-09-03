import plotext as plt

plt.date_form('d/m/Y')

start = plt.string_to_datetime('11/04/2022')
end = plt.today_datetime()

prices = 123

plt.plot(prices)

plt.title("Google Stock Price")
plt.xlabel("Date")
plt.ylabel("Stock Price $")
plt.show()
