# -*- coding: utf-8 -*-
"""LU Decomposition Implementation."""

import numpy as np


def lu_decomp(mat, epsilon=1.0e-15):
    """LU Decomposition with partial pivoting."""
    size = mat.shape[0]
    permutations = []

    for i in range(size):
        max_row = i
        for j in range(i + 1, size):
            if abs(mat[j, i]) > abs(mat[max_row, i]):
                max_row = j

        if abs(mat[max_row, i]) < epsilon:
            raise ValueError("Matrix may be singular.")

        if max_row != i:
            mat[[max_row, i]] = mat[[i, max_row]]
            permutations.append((max_row, i))

        for j in range(i + 1, size):
            factor = mat[j, i]
            mat[j, i:] -= factor * mat[i, i:]

    return permutations


def solve(mat, rhs, perms):
    """Solves the equation Ax = b where A is decomposed."""
    n = rhs.shape[0]

    for old_row, new_row in perms:
        rhs[[old_row, new_row]] = rhs[[new_row, old_row]]

    for i in range(1, n):
        for j in range(i):
            factor = mat[i, j]
            rhs[i] -= factor * rhs[j]

    for k in range(rhs.shape[1]):
        rhs[-1, k] /= mat[-1, -1]

    for i in range(n - 2, -1, -1):
        for j in range(i + 1, n):
            rhs[i, k] -= mat[i, j] * rhs[j, k]
        rhs[i, k] /= mat[i, i]

    return rhs


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

    perm_list = lu_decomp(A.copy())
    x = solve(A, b, perm_list)
    print("Found solution:", x)
    print("Verification Ax:", np.dot(A, x))
