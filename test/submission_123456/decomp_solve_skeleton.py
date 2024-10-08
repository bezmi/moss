# -*- coding: utf-8 -*-
"""Matrix solve via LU decomposition as per Gerald and Wheatley section 2.2."""

from numpy import array, zeros, dot, hstack


def lu_decomposition(matrix, small_value=1.0e-15):
    """
    Params:
    matrix: nxn matrix of coefficients
    The matrix is altered in place to store the upper-triangular reduced matrix and the multipliers used in the reduction.
    Returns:
    A list of row-permutation pairs.
    """
    num_rows, num_cols = matrix.shape
    if num_rows != num_cols:
        raise RuntimeError("should be square matrix")
    perm_list = []

    for col in range(0, num_rows):
        # Select pivot
        pivot = col
        for row in range(col + 1, num_rows):
            if abs(matrix[row, col]) > abs(matrix[pivot, col]):
                pivot = row
        if abs(matrix[pivot, col]) < small_value:
            raise RuntimeError("matrix is probably singular")

        # Swap the rows (carefully)
        if pivot != col:
            matrix[pivot, :], matrix[col, :] = (
                matrix[col, :].copy(),
                matrix[pivot, :].copy(),
            )
            perm_list.append([pivot, col])  # Record swap in permute list

        # Do the elimination to get zeros in column col below diagonal
        # Don't disturb the previous multipliers stored to the left
        for row in range(col + 1, num_rows):
            multiplier = matrix[row, col]  # Calculate the multiplier
            matrix[row, col:] -= multiplier * matrix[col, col:]  # Update the row
            matrix[row, col] = multiplier  # Store the multiplier

    return perm_list


def solve_system(matrix, rhs_vector, perm_list):
    """
    Second stage of the linear solver.
    Params:
    matrix: decomposed matrix from stage 1
    rhs_vector: on input, one column vector for the right-hand side on return,
    the solution vector
    perm_list: list of row-permutation pairs from the first stage.
    """
    num_rows, matrix_cols = matrix.shape
    rhs_rows, rhs_cols = rhs_vector.shape

    if rhs_cols < 1 or rhs_rows != num_rows:
        raise RuntimeError("nonconforming rhs")

    # Get the right-hand side rows into final order.
    for pivot, row in perm_list:  # replay from permuteList
        rhs_vector[pivot, :], rhs_vector[row, :] = (
            rhs_vector[row, :].copy(),
            rhs_vector[pivot, :].copy(),
        )

    # Forward elimination, using the stored multipliers.
    for i in range(1, num_rows):
        for j in range(0, i):
            multiplier = matrix[i, j]  # Calculate the multiplier
            rhs_vector[i, :] -= (
                multiplier * rhs_vector[j, :]
            )  # Update the right-hand side

    # Back substitution to obtain the solution vector(s).
    for column in range(rhs_cols):
        rhs_vector[-1, column] /= matrix[
            -1, -1
        ]  # Complete with first element of solution
        for i in range(rhs_rows - 2, -1, -1):  # Loop backwards over remaining rows
            sum_value = rhs_vector[i, column]  # Initialize sum
            for j in range(i + 1, num_rows):
                sum_value -= matrix[i, j] * rhs_vector[j, column]  # Increment sum
            rhs_vector[i, column] = sum_value / matrix[i, i]  # Complete this

    return


if __name__ == "__main__":
    test_case = 2
    if test_case == 1:
        print("Begin decomp-solve test that doesn't require pivoting...")
        matrix_a = array([[4.0, -2.0, 1.0], [-3.0, -1.0, 4.0], [1.0, -1.0, 3.0]], float)
        matrix_copy = matrix_a.copy()  # save copy for checking
        rhs_vector = array([[15.0, 8, 13]]).transpose()
    if test_case == 2:
        print("Begin decomp-solve test that DOES require pivoting...")
        matrix_a = array(
            [
                [0.0, 2.0, 0.0, 1.0],
                [2.0, 2.0, 3.0, 2.0],
                [4.0, -3.0, 0.0, 1.0],
                [6.0, 1.0, -6.0, -5.0],
            ],
            float,
        )
        matrix_copy = matrix_a.copy()  # save copy for checking
        rhs_vector = array([[0.0, -2.0, -7.0, 6.0]]).transpose()

    print("A =", matrix_a)
    print("b =", rhs_vector)
    perm_list = lu_decomposition(matrix_a)
    print("A decomposed =", matrix_a)
    print("permuteList =", perm_list)
    solve_system(matrix_a, rhs_vector, perm_list)
    print("solution =", rhs_vector)
    print("check RHS =", dot(matrix_copy, rhs_vector))
