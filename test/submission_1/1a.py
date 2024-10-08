# -*- coding: utf-8 -*-
"""LU Decomposition using Functional Programming."""

import numpy as np


def pivot(matrix, col):
    """Selects pivot and swaps rows if necessary."""
    max_row = np.argmax(abs(matrix[col:, col])) + col
    if col != max_row:
        matrix[[col, max_row]] = matrix[[max_row, col]]
    return matrix


def lu(matrix):
    """Perform LU decomposition with partial pivoting."""
    n = matrix.shape[0]
    for col in range(n):
        matrix = pivot(matrix, col)
        if abs(matrix[col, col]) < 1e-15:
            raise ValueError("Matrix is singular.")
        for row in range(col + 1, n):
            factor = matrix[row, col] / matrix[col, col]
            matrix[row, col:] -= factor * matrix[col, col:]
            matrix[row, col] = factor
    return matrix


def solve(matrix, b):
    """Solves Ax = b for x."""
    n = b.shape[0]
    for i in range(n):
        for j in range(i):
            b[i] -= matrix[i, j] * b[j]

    x = np.zeros_like(b)
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - np.sum(matrix[i, i + 1 :] * x[i + 1 :])) / matrix[i, i]

    return x


if __name__ == "__main__":
    A = np.array(
        [
            [0.0, 2.0, 0.0, 1.0],
            [2.0, 2.0, 3.0, 2.0],
            [4.0, -3.0, 0.0, 1.0],
            [6.0, 1.0, -6.0, -5.0],
        ],
        float,
    )
    b = np.array([[0.0, -2.0, -7.0, 6.0]]).transpose()

    U = lu(A.copy())
    solution = solve(U, b)
    print("Solution:", solution)
