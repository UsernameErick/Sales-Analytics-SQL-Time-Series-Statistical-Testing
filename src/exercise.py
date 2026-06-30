from scipy.stats import ttest_ind
import numpy as np
import matplotlib.pyplot as plt

before = np.random.normal(loc=100, scale = 15, size=1000)
after = np.random.normal(loc=110, scale = 50, size=1000)
# сначала я поставил в after loc=101 -> p большой -> скорее всего рандом сыграл.
# потом я поставил в after loc=110 -> p резко низкий -> вероятнее всего скидка зарешала.
# и потом в after scale = 50 -> p довольно низкий, но не такой как в прошлом -> все равно вероятно что скидка зарешала, несмотря на повышенный шум(шум разбавил уверенность в неслучайности)

t, p = ttest_ind(before, after)

plt.hist(before, alpha=0.5, bins=50, label='Before(Низкий шум)', color = 'blue')
plt.hist(after, alpha=0.5, bins=50, label='After(Высокий шум)', color = 'orange')
plt.ylabel = ("money")
plt.xlabel = ("time")
plt.legend()
plt.show()

print("t: ", t)
print("p: ", p)