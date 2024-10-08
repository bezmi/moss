# -*- coding: utf-8 -*-
"""Class-based LU Decomposition Solver."""

import numpy as np


class LUSolver:
    def __init__(self, matrix):
        self.matrix = matrix
        self.n = matrix.shape[0]
        self.permutations = []

    def decompose(self):
        for i in range(self.n):
            pivot_row = np.argmax(abs(self.matrix[i:, i])) + i
            if abs(self.matrix[pivot_row, i]) < 1e-15:
                raise ValueError("Matrix singular.")
            self.permutations.append((pivot_row, i))
            if pivot_row != i:
                self.matrix[[pivot_row, i]] = self.matrix[[i, pivot_row]]

            for j in range(i + 1, self.n):
                factor = self.matrix[j, i] / self.matrix[i, i]
                self.matrix[j, i:] -= factor * self.matrix[i, i:]

    def solve(self, rhs):
        n = rhs.shape[0]
        for old_row, new_row in self.permutations:
            rhs[[old_row, new_row]] = rhs[[new_row, old_row]]

        for i in range(1, n):
            for j in range(i):
                rhs[i] -= self.matrix[i, j] * rhs[j]

        for i in range(n - 1, -1, -1):
            rhs[i] = (
                rhs[i] - np.sum(self.matrix[i, i + 1 :] * rhs[i + 1 :])
            ) / self.matrix[i, i]

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

    solver = LUSolver(A.copy())
    solver.decompose()
    solution = solver.solve(b)
    print("Solution found:", solution)
