import numpy as np
import matplotlib.pyplot as plt


def enthalpy_func(temp):
    return 259.8 * (
        3.782 * temp - (2.997e-3 * temp**2) / 2 + (9.847e-6 * temp**4) / 4 - 1.064e3
    )


temperature_points = np.arange(0, 550, 5)
enthalpies = [enthalpy_func(temp) for temp in temperature_points]


def compute_derivative(x, x_vals, y_vals):
    deriv_sum = 0.0
    n = len(x_vals)

    for i in range(n):
        li_term = 1
        for j in range(n):
            if i != j:
                li_term *= (x - x_vals[j]) / (x_vals[i] - x_vals[j])

        dli_sum = sum(
            li_term / (x - x_vals[j])
            for j in range(n)
            if i != j and abs(x - x_vals[j]) >= 1e-10
        )
        deriv_sum += y_vals[i] * dli_sum

    return deriv_sum


heat_capacities = [
    compute_derivative(t, temperature_points, enthalpies) for t in temperature_points
]
heat_capacity_at_500_temp = compute_derivative(500, temperature_points, enthalpies)
print(heat_capacity_at_500_temp)
