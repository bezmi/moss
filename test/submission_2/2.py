import numpy as np
import matplotlib.pyplot as plt


def enthalpy(T):
    A, B, C, D = 259.8, 3.782, -2.997e-3, 9.847e-6
    H = A * (B * T + C * T**2 / 2 + D * T**4 / 4 - 1.064e3)
    return H


T_vals = np.linspace(0, 550, num=111)
H_vals = [enthalpy(T) for T in T_vals]


def derivative_at(x, x_points, y_points):
    result = 0.0
    n = len(x_points)

    for i in range(n):
        term = 1.0
        for j in range(n):
            if i != j:
                term *= (x - x_points[j]) / (x_points[i] - x_points[j])

        d_term = sum(term / (x - x_points[j]) for j in range(n) if i != j)
        result += y_points[i] * d_term
    return result


C_p = [derivative_at(t, T_vals, H_vals) for t in T_vals]
Cp_at_500 = derivative_at(500, T_vals, H_vals)
print(Cp_at_500)
