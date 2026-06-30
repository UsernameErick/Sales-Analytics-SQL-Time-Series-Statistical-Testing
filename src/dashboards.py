import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

base_dir = os.path.dirname(__file__)
data_dir = os.path.join(base_dir, "..", "data", "train.csv")
df = pd.read_csv(data_dir)

conn = sqlite3.connect('sales.db') # создаем базу данных sales.db

df['Order Date'] = pd.to_datetime(df['Order Date']) # преобразуем Order Date в формат даты, а не строки
df['Order Date'] = df['Order Date'].dt.strftime('%Y-%m-%d') # форматируем дату в виде "Y-m-d"

df['Ship Date'] = pd.to_datetime(df['Ship Date'])
df['Ship Date'] = df['Ship Date'].dt.strftime('%Y-%m-%d')

df.to_sql("sales", conn, if_exists='replace', index=False) # переносим df в sales. "sales" - название таблицы

# показываю графики и в общем визуализирую данные

query_sales_by_months = """
    select strftime('%Y-%m', [Order Date]) as month, sum(Sales) as total_sales
    from sales
    group by month
    order by month
"""
# продажи по месяцам

query_sales_by_region = """
    select Region, sum(Sales) as total_sales
    from sales
    group by Region
    order by total_sales desc
"""
# продажи по регионам

query_shipmode_usage = """
    select [Ship Mode], count(distinct([Order ID])) as shipment_amount
    from sales
    group by [Ship Mode]
    order by shipment_amount desc
"""
# использование видов доставок

query_avg_delivery_days = """
    select avg(julianday([Ship Date]) - julianday([Order Date])) as avg_days, [Ship Mode]
    from sales
    where julianday([Ship Date]) - julianday([Order Date]) between 0 and 29
    group by [Ship Mode]
    order by avg_days asc
"""
# средняя длительность доставки каждого вида

# загружаем в pd
sales_by_months = pd.read_sql_query(query_sales_by_months, conn)
sales_by_region = pd.read_sql_query(query_sales_by_region, conn)
shipmode_usage = pd.read_sql_query(query_shipmode_usage, conn)
avg_delivery_days = pd.read_sql_query(query_avg_delivery_days, conn)

# визуализация
fig, axes = plt.subplots(2, 2, figsize = (14, 10)) # сетка 2 на 2

# sales by month 
axes[0, 0].plot(sales_by_months['month'], sales_by_months['total_sales'])

axes[0, 0].set_title("Sales by months")
axes[0, 0].tick_params(axis='x', rotation=75, labelsize = 8) # axis - к какой оси применить rotation

# sales by region
axes[0, 1].bar(sales_by_region['Region'], sales_by_region['total_sales'])

axes[0, 1].set_title("Sales by Region")

# shipmode usage
axes[1, 0].bar(shipmode_usage['Ship Mode'], shipmode_usage['shipment_amount'])

axes[1, 0].set_title("Shipmode Usage")
axes[1, 0].tick_params(axis='x', rotation=0)

# avg_delivery_days
axes[1, 1].bar(avg_delivery_days['avg_days'], avg_delivery_days['Ship Mode'])

axes[1, 1].set_title("Average Delivery Days")
axes[1, 1].tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.show()