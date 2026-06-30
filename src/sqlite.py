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

# изучаю данные таблицы, выявляю зависимости
query = """
    select Category, sum(Sales) as total_sales
    from sales
    group by Category
    order by total_sales desc
"""
result = pd.read_sql_query(query, conn)
print(result)

query1 = """
    select * 
    from sales 
    limit 5
"""
query1_result = pd.read_sql_query(query1, conn) # показать верхушку sql-таблицы для проверки работоспособности
print(query1_result)

# графическое представление продаж по категориям 
plt.bar(result['Category'], result['total_sales'])
plt.title("Sales by Category")
plt.show()

# strftime - форматирование даты, %Y - год в виде двух цифр, %m - месяц в виде двух цифр. [Order Date] - столбец
query_most_sold_month = """
    select strftime('%Y-%m', [Order Date]) as month, sum(Sales) as total_sales
    from sales
    group by month
    order by month
"""
monthly_sales = pd.read_sql_query(query_most_sold_month, conn)
print("Продажи по месяцам:\n", monthly_sales.head())

plt.figure(figsize=(12, 6))
plt.plot(monthly_sales['month'], monthly_sales['total_sales'])
plt.xticks(rotation=45)
plt.title("Monthly Sales")
plt.show()

query_most_richest_region = """
    select Region, sum(Sales) as total_sales
    from Sales
    group by Region
    order by total_sales desc
"""
query_most_richest_region_result = pd.read_sql_query(query_most_richest_region, conn)
print("Самый богатый регион по общим продажам:\n", query_most_richest_region_result)

query_most_popular_category_by_region = """
    select Region, Category, sum(sales) as total_sales
    from sales
    group by Region, Category
    order by Region, total_sales desc
"""
query_most_popular_category_by_region_result = pd.read_sql_query(query_most_popular_category_by_region, conn)
print("Самые популярные категории по регионам:\n", query_most_popular_category_by_region_result)

best_categories = pd.read_sql(query_most_popular_category_by_region, conn)
best_categories_result = best_categories.loc[ # для каждого региона выбрать строку с максимальными продажами
    best_categories.groupby('Region')['total_sales'].idxmax() # idxmax() вернет индекс с максимальным значением total_sales для каждого Region. взять максимальный total_sales для каждого региона
]
print("Лучшие категории по регионам:\n", best_categories_result)

query_best_month_by_region = """
    select Region, strftime('%Y-%m', [Order Date]) as month, sum(Sales) as total_sales
    from sales
    group by Region, month
    order by Region, total_sales desc
"""
query_best_month_by_region_result = pd.read_sql_query(query_best_month_by_region, conn)
best_month_by_region = query_best_month_by_region_result.loc[ # для каждого региона выбрать строку с максимальными продажами
    query_best_month_by_region_result.groupby('Region')['total_sales'].idxmax()
]
print("Лучший месяц по продажам у каждого региона:\n", best_month_by_region)

query_peak_east_2018_11_category = """
    select Region, Category, strftime('%Y-%m', [Order Date]) as month, sum(Sales) as total_sales
    from sales
    group by Region, Category, month
    having Region = 'East' and month = '2018-11'
    order by total_sales desc
"""
query_peak_east_2018_11_category_result = pd.read_sql_query(query_peak_east_2018_11_category, conn) # в данном случае мы используем HAVING, так как нам нужно отфильтровать результаты после группировки, а не до нее. WHERE не может использоваться для фильтрации агрегированных данных, таких как суммы продаж по категориям и месяцам.
peak_east_2018_11_category_result = query_peak_east_2018_11_category_result.loc[ # без этого снова получится несколько категорий на East за ноябрь 2018, но теперь мы выберем только максимальную
    query_peak_east_2018_11_category_result.groupby('Region')['total_sales'].idxmax()
]
print("Самая продаваемая категория на ноябрь 2018 в регионе East:\n", peak_east_2018_11_category_result) 

query_top_products_west = """
    select [Product Name], sum(Sales) as total_sales
    from sales
    where Region = 'West'
    group by [Product Name]
    order by total_sales desc
    limit 10
"""
query_top_products_west_result = pd.read_sql_query(query_top_products_west, conn)
print("Самые продающиеся продукты на Западе:\n", query_top_products_west_result)

query_west_total = """
    select sum(Sales) as total_sales
    from sales
    where Region = 'West'
"""
query_west_total_result = pd.read_sql_query(query_west_total, conn)
print("Total products sales West:\n", query_west_total_result)

# теперь узнаем сколько % от всей прибыли Запада составляют топ-10 продуктов
top10_sum = query_top_products_west_result['total_sales'].sum()
print("Total Top-10 products sales West SUM:\n", top10_sum)
west_total = query_west_total_result['total_sales'][0]
percentage_top10_to_all_west = top10_sum/west_total*100
print("Top10 products generates ", f"{percentage_top10_to_all_west:.2f}%", "of all sales in West")

query_most_profitable_shipment = """
    select sum(Sales) as total_sales, [Ship Mode]
    from sales
    group by [Ship Mode]
    order by total_sales desc
"""
query_most_profitable_shipment_result = pd.read_sql_query(query_most_profitable_shipment, conn)
print("Самый прибыльный способ доставки:\n", query_most_profitable_shipment_result)

query_avg_money_for_order = """
    select [Ship Mode], AVG(total_sales) as avg_total_sales
    from (
        select [Order ID], [Ship Mode], sum(Sales) as total_sales
        from sales
        group by [Order ID], [Ship Mode]
    )
    group by [Ship Mode]
    order by avg_total_sales desc
"""
query_avg_money_for_order_result = pd.read_sql_query(query_avg_money_for_order, conn)
print("Средний размер заказа по Ship Mode:\n", query_avg_money_for_order_result)
 
query_check_distinct_shipmodes = """
    select [Order ID], count(distinct[Ship Mode]) as shipmodes
    from sales
    group by [Order ID]
    having shipmodes > 1
"""
query_check_distinct_shipmodes_result = pd.read_sql_query(query_check_distinct_shipmodes, conn)
print("Если Empty DataFrame - все OK:", query_check_distinct_shipmodes_result) # если выйдет пустая табличка, то это значит что 1 Order ID = 1 Ship Mode(я думал вдруг в 1 заказе будут разные доставки, такое бывает)

query_most_used_shipmode = """
    select [Ship Mode], count(distinct[Order ID]) as Number_of_use
    from sales
    group by [Ship Mode]
    order by Number_of_use desc
"""
query_most_used_shipmode_result = pd.read_sql_query(query_most_used_shipmode, conn)
print("Самый частый способ доставки:\n", query_most_used_shipmode_result)

query_check_distinct_shipdates = """
    select [Order ID], count(distinct[Ship Date]) as ship_dates_count
    from sales
    group by [Order ID]
    having ship_dates_count > 1
"""
query_check_distinct_shipdates_result = pd.read_sql_query(query_check_distinct_shipdates, conn) # на выходе таблица, где условно [Order ID] 1 --- кол-во различных дат привоза = 1(ship_dates_count)
print("Если Empty DataFrame - все OK -", query_check_distinct_shipdates_result) # значит что у 1 Order ID всегда 1 день доставки(всё заказанное приходит в 1 день, а не в разные) 
# Мы выяснили, что самый популярный и одновременно самый прибыльный способ доставки - Standard Class. При этом средний чек за заказ у каждого вида доставки слабо отличается.

query_avg_days_shipment_and_min_max = """
    select [Ship Mode], avg(julianday([Ship Date]) - julianday([Order Date])) as avg_delivery_day,
    min(julianday([Ship Date]) - julianday([Order Date])) as min_delivery_day,
    max(julianday([Ship Date]) - julianday([Order Date])) as max_delivery_day
    from sales
    where julianday([Ship Date]) - julianday([Order Date]) >= 0
    group by [Ship Mode]
    order by avg_delivery_day asc
"""
query_avg_days_shipment_and_min_max_result = pd.read_sql_query(query_avg_days_shipment_and_min_max, conn) # julianday превращает дату в число. можно вычислять кол-во дней между датами
print("Средние сроки доставки, минимальный срок, максимальный срок:\n", query_avg_days_shipment_and_min_max_result)
# мы выяснили, что у некоторых данных, а именно max_delivery_day, значения либо некорректны, либо они действительно доставляли заказ категории Same Day целый месяц и т.д.

query_median_days_shipment = """
    select [Ship Mode], julianday([Ship Date]) - julianday([Order Date]) as delivery_days
    from sales
"""
delivery_median_days_df = pd.read_sql_query(query_median_days_shipment, conn)
delivery_median_days_df.groupby('Ship Mode')['delivery_days'].median() # медиана устойчивее, потому что могут быть значения (1, 1, 1, 50). и тогда avg не даст точный результат. Найди медиану у delivery_days для каждого Ship Mode
print("Медиана по дням доставки:\n", delivery_median_days_df.groupby('Ship Mode')['delivery_days'].median())

query_shipment_region_dependancy = """
    select region, [Ship Mode], count(distinct[Order ID]) as total_orders
    from sales
    group by region, [Ship Mode]
    order by region, total_orders desc
"""
query_shipment_region_dependancy_result = pd.read_sql_query(query_shipment_region_dependancy, conn)
print("Какая доставка в каком регионе чаще используется:\n", query_shipment_region_dependancy_result)
# мы узнали, что западный регион заказывает чаще всех, но соотношение у всех везде примерно одинаковое

query_avg_days_per_region = """
    select region, [Ship Mode], avg(julianday([Ship Date]) - julianday([Order Date])) as avg_delivery_days
    from sales
    where julianday([Ship Date]) - julianday([Order Date]) between 0 and 29
    group by region, [Ship Mode]
    order by avg_delivery_days
"""
query_avg_days_per_region_result = pd.read_sql_query(query_avg_days_per_region, conn)
print("Среднее время доставки у каждого региона:\n", query_avg_days_per_region_result)
# мы узнали, что длительность доставки не сильно зависит от региона. а также почистили данные с помощью between и получили более реалистичные значения
