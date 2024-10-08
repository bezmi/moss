from numpy import linspace, arange
from pylab import plot, show, legend, xlabel, ylabel, figure

enthalpy_values = []


def calculate_enthalpy(temperature):
    h = 259.8 * (
        3.782 * temperature
        - 2.997 * (10 ** (-3)) * (temperature**2) / 2
        + 9.847 * (10 ** (-6)) * (temperature**4) / 4
        + 3.243 * (10**-12) * (temperature**5) / 5
        - 1.064 * 10**3
    )
    enthalpy_values.append(h)


temp_range = list(range(0, 550, 5))
for temp in temp_range:
    calculate_enthalpy(temp)


# differential function
def numerical_derivative(x_value, x_data, y_data, num_points, start_index=0):
    derivative = 0.0
    for i in range(start_index, num_points):
        li = 1.0
        dli = 0.0
        for j in range(start_index, num_points):
            if i == j:
                continue
            li *= (x_value - x_data[j]) / (x_data[i] - x_data[j])
        for j in range(start_index, num_points):
            if i == j:
                continue
            if abs(x_value - x_data[j]) < 1e-10:
                continue
            dli += li / (x_value - x_data[j])
        derivative += y_data[i] * dli
    return derivative


heat_capacity = []
for x in temp_range:
    heat_capacity.append(
        numerical_derivative(x, temp_range, enthalpy_values, len(temp_range), 0)
    )

Cp_value = numerical_derivative(500, temp_range, enthalpy_values, len(temp_range), 0)
print(Cp_value)

""" PART B """


# unfinished
def compute_c2(temperature):
    return 259.8 * (
        3.782
        - 2.997e-3 * temperature
        + 9.847e-6 * temperature**2
        - 9.681e-9 * temperature**3
        + 3.243e-12 * temperature**4
    )
