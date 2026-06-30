import pandas as pd
import matplotlib.pyplot as plt
import os
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

base_dir = os.path.dirname(__file__)
data_dir = os.path.join(base_dir, "..", "data", "train.csv")
df = pd.read_csv(data_dir)

# преобразование даты
df = df.rename(columns={'Order Date': 'date'})
df["date"] = pd.to_datetime(df["date"])
#сортировка по дате
df = df.sort_values('date')

# берем сумму продаж Sales за каждый день
daily_sales = df.groupby('date')['Sales'].sum()

# скользящее среднее (rolling mean) (легко увидеть спады и пики, сглаживает шум)
rolling_mean = daily_sales.rolling(30).mean() # 30 последних дней среднее

# визуализация продаж по дням
plt.figure(figsize=(15, 6))
plt.plot(daily_sales.index, daily_sales.values) # index - это даты, values - это сумма продаж за эти даты
plt.title("Original")
plt.plot(rolling_mean.index, rolling_mean.values) # index - это даты, values - это скользящее среднее
plt.title("Rolling Mean")
plt.xticks(rotation=30)
plt.ylabel("Money")
plt.legend(["Daily Sales", "Rolling Mean"])
plt.show()

# resample сжать данные по месяцам и сумма
monthly_sales = daily_sales.resample('M').sum()

plt.plot(monthly_sales.index, monthly_sales.values)
plt.ylabel("Money")
plt.title("Monthly Sales")
plt.xticks(rotation=30)
plt.show()

# декомпозиция временного ряда
decomposition = seasonal_decompose(monthly_sales)
decomposition.plot()
plt.show() # тренд, сезонность и остатки (шум) в данных. сезонность покажет закономерность, тренд - общий рост или падение, остатки - шум.

# ML предсказание ARIMA.
train = monthly_sales[:-12] # берем все, кроме последних 12 месяцев
test = monthly_sales[-12:] # берем последние 12 месяцев

# model = ARIMA(train, order=(1, 1, 1)) # настройка модели ARIMA, order=(p, d, q) - p - порядок авторегрессии, d - порядок интегрирования, q - порядок скользящего среднего
# model_fit = model.fit()

# forecast = model_fit.forecast(steps=12) # предсказание на 12 месяцев вперед

# plt.figure(figsize=(12, 6))
# plt.plot(train.index, train.values, label='Train')
# plt.plot(test.index, test.values, label='Test')
# plt.plot(forecast.index, forecast.values, label='Forecast') # index - это даты, values - это предсказанные значения
# plt.legend()
# plt.xticks(rotation=30)
# plt.show()

# ML SARIMAX. Sarima знает про сезонность, потому полезнее для цикличных данных.
model_sarimax = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)) # seasonal_order=(P, D, Q, s) - P - сезонный порядок авторегрессии, D - сезонный порядок интегрирования, Q - сезонный порядок скользящего среднего, s - длина сезонности (12 для месячных данных)
model_sarimax_fit = model_sarimax.fit()
forecast_sarimax = model_sarimax_fit.forecast(steps=12)

plt.figure(figsize=(12, 6))
plt.plot(train.index, train.values, label='Train')
plt.plot(test.index, test.values, label='Test')
plt.plot(forecast_sarimax.index, forecast_sarimax.values, label='Forecast')
plt.legend()
plt.xticks(rotation=30)
plt.show()
