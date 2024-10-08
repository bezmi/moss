import numpy as np
import matplotlib.pyplot as plt


def compute_enthalpy(temp):
    return 259.8 * (
        3.782 * temp - 2.997e-3 * temp**2 / 2 + 9.847e-6 * temp**4 / 4 - 1.064e3
    )


T_array = np.arange(0, 550, 5)
enthalpy_list = [compute_enthalpy(t) for t in T_array]


def calc_derivative(value, x_data, y_data):
    derivative_sum = 0.0
    for i in range(len(x_data)):
        term_product = 1.0
        for j in range(len(x_data)):
            if i != j:
                term_product *= (value - x_data[j]) / (x_data[i] - x_data[j])

        derivative_term = sum(
            term_product / (value - x_data[j])
            for j in range(len(x_data))
            if i != j and abs(value - x_data[j]) >= 1e-10
        )
        derivative_sum += y_data[i] * derivative_term

    return derivative_sum


heat_capacities = [calc_derivative(t, T_array, enthalpy_list) for t in T_array]
heat_capacity_at_500 = calc_derivative(500, T_array, enthalpy_list)
print(heat_capacity_at_500)
