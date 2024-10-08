# -*- coding: utf-8 -*-
"""LU Decomposition Solver."""

import numpy as np


def lu_decompose(matrix):
    """Decomposes a matrix into lower and upper."""
    n = matrix.shape[0]
    L = np.eye(n)
    U = matrix.copy()

    for j in range(n):
        for i in range(j + 1, n):
            if U[j, j] == 0:
                raise ValueError("Matrix is singular.")
            factor = U[i, j] / U[j, j]
            L[i, j] = factor
            U[i, j:] -= factor * U[j, j:]

    return L, U


def lu_solve(L, U, b):
    """Solves the matrix equation using L and U matrices."""
    n = b.shape[0]
    y = np.zeros_like(b)

    for i in range(n):
        y[i] = b[i] - np.sum(L[i, :i] * y[:i])

    x = np.zeros_like(b)
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - np.sum(U[i, i + 1 :] * x[i + 1 :])) / U[i, i]

    return x


if __name__ == "__main__":
    A_matrix = np.array([[4, 2], [3, 1]], dtype=float)
    b_vector = np.array([[8], [8]], dtype=float)

    L_matrix, U_matrix = lu_decompose(A_matrix.copy())
    solution = lu_solve(L_matrix, U_matrix, b_vector)
    print("Solution:", solution)
