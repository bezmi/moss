import numpy as np
import matplotlib.pyplot as plt


def calculate_enthalpy(temperature):
    coeffs = [259.8, 3.782, -2.997e-3, 9.847e-6, 3.243e-12]
    h = coeffs[0] * (
        coeffs[1] * temperature
        + coeffs[2] * temperature**2 / 2
        + coeffs[3] * temperature**4 / 4
        - 1.064e3
    )
    return h


temperatures = np.arange(0, 550, 5)
enthalpy_values = [calculate_enthalpy(t) for t in temperatures]


def numerical_derivative(x, x_data, y_data):
    derivative = 0.0
    n = len(x_data)
    for i in range(n):
        li = np.prod(
            [(x - x_data[j]) / (x_data[i] - x_data[j]) for j in range(n) if i != j]
        )
        dli = sum(
            li / (x - x_data[j])
            for j in range(n)
            if i != j and abs(x - x_data[j]) >= 1e-10
        )
        derivative += y_data[i] * dli
    return derivative


heat_capacity = [
    numerical_derivative(t, temperatures, enthalpy_values) for t in temperatures
]
Cp_value = numerical_derivative(500, temperatures, enthalpy_values)
print(Cp_value)
