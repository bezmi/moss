# -*- coding: utf-8 -*-
"""LU decomposition and system solving."""

from numpy import array, zeros, dot


def perform_lu_decomposition(matrix, tolerance=1.0e-15):
    """Perform LU decomposition on a given matrix."""
    n = matrix.shape[0]
    if n != matrix.shape[1]:
        raise ValueError("Input must be a square matrix.")

    swaps = []

    for col in range(n):
        pivot_row = col
        for row in range(col + 1, n):
            if abs(matrix[row, col]) > abs(matrix[pivot_row, col]):
                pivot_row = row

        if abs(matrix[pivot_row, col]) < tolerance:
            raise ValueError("Matrix appears to be singular.")

        if pivot_row != col:
            matrix[[pivot_row, col]] = matrix[[col, pivot_row]]
            swaps.append((pivot_row, col))

        for row in range(col + 1, n):
            factor = matrix[row, col]
            matrix[row, col:] -= factor * matrix[col, col:]
            matrix[row, col] = factor

    return swaps


def solve_linear_system(matrix, rhs, swaps):
    """Solves the linear equation Ax = b where A is the matrix."""
    n = matrix.shape[0]

    for pivot, row in swaps:
        rhs[[pivot, row]] = rhs[[row, pivot]]

    for i in range(1, n):
        for j in range(i):
            factor = matrix[i, j]
            rhs[i] -= factor * rhs[j]

    for col in range(rhs.shape[1]):
        rhs[-1, col] /= matrix[-1, -1]

    for i in range(n - 2, -1, -1):
        for j in range(i + 1, n):
            rhs[i, col] -= matrix[i, j] * rhs[j, col]
        rhs[i, col] /= matrix[i, i]

    return rhs


if __name__ == "__main__":
    test_case = 0
    if test_case == 0:  # Test with no pivot needed
        A = array([[4.0, -2.0, 1.0], [-3.0, -1.0, 4.0], [1.0, -1.0, 3.0]], float)
        b = array([[15.0, 8.0, 13.0]]).transpose()
        lu_swaps = perform_lu_decomposition(A.copy())
        x = solve_linear_system(A, b, lu_swaps)
        print("Solution:", x)
        print("Check Ax:", dot(A, x))
