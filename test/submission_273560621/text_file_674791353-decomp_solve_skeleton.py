# -*- coding: utf-8 -*-
"""
Matrix solve via LU decomposition as per Gerald and Wheatley section 2.2.
"""
from numpy import array, zeros, dot, hstack

def decomp(c,very_small_value=1.0e-15):
    """
    Params:
        c:  nxn matrix of coefficients
            The matrix is altered in place to store the upper-triangular
            reduced matrix and the multipliers used in the reduction.
        
    Returns:
        A list of row-permutation pairs.
    """
    nrows,ncols = c.shape
    if nrows != ncols:
        raise RuntimeError("should be square matrix")
    permuteList = []
    for j in range(0,nrows):
        # Select pivot
        p = j
        for i in range(j+1, nrows):
            if abs(c[i,j]) > abs(c[p,j]): p = i
        if abs(c[p,j]) < very_small_value:
            raise RuntimeError("matrix is probably singular")
        # Swap the rows (carefully)
        if p != j:
            c[p,:], c[j,:] = c[j,:].copy(), c[p,:].copy()
            permuteList.append([p,j])# Record swap in permute list
        # Do the elimination to get zeros in column j below diagonal
        # Don't disturb the previous multipliers stored to the left
        for i in range(j+1,nrows):
            multiplier = c[i,j]/c[j,j]     # TODO: Complete this
            c[i,j:] -= multiplier*c[j,j:]  # TODO: Complete this
            c[i,j] = multiplier
    return permuteList

def solve(c,rhs,permuteList):
    """
    Second stage of the linear solver.
    
    Params:
        c: decomposed matrix from stage 1
        rhs: on input, one column vector for the right-hand side
             on return, the solution vector
        permuteList: list of row-permutation pairs from the first stage.
    """
    nrows, c_ncols = c.shape
    rhs_nrows, rhs_ncols = rhs.shape
    if rhs_ncols < 1 or rhs_nrows != nrows:
        raise RuntimeError("nonconforming rhs")
    # Get the right-hand side rows into final order.
    for p,j in permuteList: # replay from permuteList:
        rhs[p,:], rhs[j,:] = rhs[j,:].copy(), rhs[p,:].copy()
    # Forward elimination, using the stored multipliers.
    for i in range(1,nrows):
        for j in range(0,i):
            multiplier = c[i,j]# TODO: Complete this
            rhs[i,:] -= multiplier * rhs[j,:] # TODO: Complete this
    # Back substitution to obtain the solution vector(s).
    for col in range(rhs_ncols):
        rhs[-1,col] /= c[-1,-1] #complete with first element of solution
        for i in range(rhs_nrows-2,-1,-1): #Loop backwards over remaining rows
            my_sum = rhs[i,col]# initialise sum
            for j in range(i+1,nrows): my_sum -= c[i,j]*rhs[j,col]# increment sum
            rhs[i,col] = my_sum/c[i,i]# TODO: Complete this
    return

if __name__ == "__main__":
    lecture_problem = 2
    if lecture_problem == 1:
        print("Begin decomp-solve test that doesnt require pivoting...")
        A = array([[4.0, -2.0, 1.0],
            [-3.0, -1.0, 4.0],
            [1.0, -1.0, 3.0]], float)
        Acopy = A.copy() # save copy for checking
        b = array([[15.0,8,13]]).transpose()

    if lecture_problem == 2:
        print("Begin decomp-solve test that DOES require pivoting...")
        A = array([[0.0, 2.0, 0.0, 1.0],
            [2.0, 2.0, 3.0, 2.0],
            [4.0, -3.0, 0.0, 1.0],
            [6.0, 1.0, -6.0, -5.0]], float)
        Acopy = A.copy() # save copy for checking
        b = array([[0.0, -2.0, -7.0, 6.0]]).transpose()
 
    print("A=", A)    
    print("b=", b)
    permuteList = decomp(A)
    print("A decomposed =", A)
    print("permuteList=", permuteList)
    solve(A,b,permuteList)
    print("solution=", b)
    print("check RHS=", dot(Acopy,b))