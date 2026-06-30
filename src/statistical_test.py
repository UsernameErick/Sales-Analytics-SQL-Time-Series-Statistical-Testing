import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

# создаем данные до promotion
before = np.random.normal(loc=100, scale=15, size=1000) # loc - среднее(mean), scale - разброс, size - кол-во значений

# после promotion
after = np.random.normal(loc=108, scale=15, size=1000)

# находим средние(mean)
print("Before mean:", before.mean())
print("After mean:", after.mean())

# t-test
t_stat, p_value = ttest_ind(before, after) # t-test - если бы акции не было, то была бы такая же разница, или же это просто случайность? (повлияли наши ИЗМЕНЕНИЯ ИЛИ всё же это ШУМ)
# t-stat - Test statistic - t-stat = разница/шум. большая разница и мало шума - t большая. Насколько сильные изменения. t = (avg1 - avg2)/шум. поэтому если продажи стали выше, то t отрицательный
# p-value - Probability - вероятность, что разница случайна. Чем больше, тем мы сами надумали
# разница - разница между avg, разброс/шум - на сколько "гуляют" значения (max-min) тоже считают до и после
# ЕСЛИ МНОГО ШУМА, ТО И ПОВЫШЕННЫЕ ПРОДАЖИ ПОСЛЕ АКЦИИ МОГУТ ПОСЧИТАТЬСЯ ЗА ШУМ, НЕПОНЯТНО ШУМ ЭТО ИЛИ НЕТ. Если всё +-стабильно, и данные повысились, то скорее всего сработала именно акция
# пределы P: 0 <= p <= 1. это вероятность

# результат
print("P-value:", p_value) # если p < 0.05, то изменение не случайность. если p > 0.05 то это вероятно случайность. Probability такого низкое - можно верить, что не случайно

if p_value < 0.05:
    print("Promotion likely changed sales")
else: 
    print("Difference may be random")
