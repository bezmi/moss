"""
Week 3 Exercise
Tim.f
"""

from numpy import linspace, arange
from pylab import plot, show, legend, xlabel, ylabel, figure


enthalpys = []
def enthalpy(T):
    h = 259.8 * (3.782 * T - 2.997 * (10 ** (-3)) * (T ** 2) / 2 + 9.847 * (10 ** (-6)) * (T ** 4) / 4 + 3.243 * (10 ** -12) * (T ** 5) / 5 - 1.064 * 10 ** 3)
    enthalpys.append(h)

temperatures = list(range(0, 550, 5))

for temp in temperatures:
    enthalpy(temp)

#differential function
def dlpoly(x, xdata, ydata, n, start=0):
    df = 0.0
    for i in range(start, n):
        li = 1.0
        dli = 0.0
        for j in range(start, n):
            if i == j:
                continue
            li *= (x - xdata[j]) / (xdata[i] - xdata[j])
        for j in range(start, n):
            if i == j:
                continue
            if abs(x - xdata[j]) < 1e-10:
                continue
            dli += li / (x - xdata[j])
        df += ydata[i] * dli
    return df


heat= []
for x in temperatures:
    heat.append(dlpoly(x, temperatures, enthalpys, len(temperatures), 0))


Cp = dlpoly(500, temperatures, enthalpys, len(temperatures), 0)
print(Cp)

"""
PART B

"""

#unfinished
def c2(T):
    return 259.8 * (3.782 - 2.997e-3 * T + 9.847e-6 * T**2 - 9.681e-9 * T**3 + 3.243e-12 * T**4)
