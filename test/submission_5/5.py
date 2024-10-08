import numpy as np
import matplotlib.pyplot as plt


def compute_enthalpy(temp):
    return 259.8 * (
        3.782 * temp - (2.997e-3 * temp**2) / 2 + (9.847e-6 * temp**4) / 4 - 1.064e3
    )


temp_values = np.arange(0, 550, 5)
enthalpy_values = [compute_enthalpy(temp) for temp in temp_values]


def get_derivative(x, x_data, y_data):
    total = 0.0
    n = len(x_data)

    for i in range(n):
        li = 1
        for j in range(n):
            if i != j:
                li *= (x - x_data[j]) / (x_data[i] - x_data[j])

        dli = sum(
            li / (x - x_data[j])
            for j in range(n)
            if i != j and abs(x - x_data[j]) >= 1e-10
        )
        total += y_data[i] * dli

    return total


heat_cap = [get_derivative(t, temp_values, enthalpy_values) for t in temp_values]
Cp_at_500 = get_derivative(500, temp_values, enthalpy_values)
print(Cp_at_500)
