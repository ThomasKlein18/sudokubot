
import numpy as np 
import math 
import time
from dancing_links import create_cover_instance, ExactCover

### utilities ###

example_sudoku = np.array([[0,0,0,0,0,0,0,0,0],
                           [0,2,0,5,0,0,0,9,4],
                           [0,0,1,0,0,0,0,0,7],
                           [0,0,0,4,0,6,0,0,5],
                           [2,0,8,0,0,0,0,0,0],
                           [0,0,0,0,5,3,0,0,0],
                           [4,0,9,0,0,0,0,2,0],
                           [5,0,0,6,0,2,0,8,0],
                           [0,6,0,0,9,0,3,0,0]])

"""
Solution:

 9  4  5 | 1  6  7 | 2  3  8 
 7  2  6 | 5  3  8 | 1  9  4 
 3  8  1 | 2  4  9 | 5  6  7 
-----------------------------
 1  9  3 | 4  2  6 | 8  7  5 
 2  5  8 | 9  7  1 | 6  4  3 
 6  7  4 | 8  5  3 | 9  1  2 
-----------------------------
 4  1  9 | 3  8  5 | 7  2  6 
 5  3  7 | 6  1  2 | 4  8  9 
 8  6  2 | 7  9  4 | 3  5  1 
"""

def print_sudoku(sudoku):
    """
    Prints a Sudoku in a somewhat visually appealing way.
    """
    for i in range(9):
        line = ""
        for j in range(9):
            line = line + " {} ".format(sudoku[i,j])
            if j % 3 == 2 and j != 8: 
                line = line + "|"
        print(line)
        if i % 3 == 2 and i != 8:
            print("------------------------------")


### brute force backtracking ###

def get_vals_in_neighbourhood(i,j, sudoku):
    """
    Obtains the values in the neighbourhood of a a sudoku cell, that is:
    The values in the row, column and respective block of the cell we are looking at.

    returns: a list of all the values that are obviously impossible for this cell.
    """
    row = list(sudoku[:,j])
    col = list(sudoku[i,:])
    block = list(sudoku[(i//3)*3:(i//3)*3+3, (j//3)*3:(j//3)*3+3].flatten())
    res = list(set(row) | set(col) | set(block))
    res.remove(0)
    return res

def solve_bruteforce(sudoku):
    """
    Solves any Sudoku using a simple Backtracking algorithm:
    Find the next empty cell, get all obviously impossible values and try the first
    possible one. If no value is possible, backtrack. 

    returns: The solved Sudoku
    """
    for i in range(9):
        for j in range(9):
            if(sudoku[i,j] == 0):
                neighbourhood = get_vals_in_neighbourhood(i,j, sudoku)
                for m in [n for n in range(1,10) if not n in neighbourhood]:
                    sudoku[i,j] = m 
                    res = solve_bruteforce(sudoku)
                    if( not res is None):
                        return res
                else:
                    sudoku[i,j] = 0
                    return None
    return sudoku


### DLX ###

def setup_exact_cover(sudoku):
    """
    Creates the large sparse matrix that contains all the constraints for a Sudoku.
    There are four types of constraints: 
    1. cell constraint: Every cell needs to contain exactly one value
    2. row constraint: Every row needs to contain every number from 1-9 (0-8 actually) exactly once
    3. column constraint: Every column needs to contain every number from 1-9 (0-8 actually) exactly once
    4. block constraint: Every 3x3 block of the sudoku needs to contain every number from 1-9 (0-8 actually) exactly once
    """

    ec = np.zeros((729,324))
    for i in range(9): # row
        for j in range(9): # column

            if sudoku[i, j] == 0:
                for k in range(9): # number

                    row = i*81+j*9+k

                    # cell constraint
                    ec[row, i*9+j] = 1 

                    # row constraint
                    ec[row, 81+i*9+k] = 1

                    # column constraint
                    ec[row,162+(9*j+k)%81] = 1

                    # block constraint
                    ec[row, 243+k+9*int((j/3))+27*int((i/3))] = 1
            else:
                k = sudoku[i,j]-1 #because the input will use numbers 1 to 9 instead of 0 to 8
                row = i*81+j*9+k

                # cell constraint
                ec[row, i*9+j] = 1 

                # row constraint
                ec[row, 81+i*9+k] = 1

                # column constraint
                ec[row,162+(9*j+k)%81] = 1

                # block constraint
                ec[row, 243+k+9*int((j/3))+27*int((i/3))] = 1

    return ec 


def solve_dancinglinks(sudoku):
    """
    Solves any Sudoku using the DLX algorithm as invented by Donald Knuth. 
    This views sudoku as an instance of the exact cover problem. ECPs can be thought of as
    a sparse matrix, i.e. a matrix that is mostly empty and contains some 1s here and there.
    The challenge is to select a subset of the rows, so that every column is covered by exactly
    one 1.

    The underlying idea is to use Algorithm X, which is:
    1. if the matrix is empty, return
    2. otherwise, select a column deterministically (specifically: select the column with fewest ones)
    3. choose a row (nondeterministically) that satisfies this column and add it to the solution
    4. remove this row and 
        all the columns that it satisfies and
        all other rows that satisfy these columns
    5. repeat this algorithm recursively 

    Algorithm X can be implemented very efficiently using Dancing Links, see https://arxiv.org/pdf/cs/0011047.pdf
    """

    matr = setup_exact_cover(sudoku) # creating the sparse matrix
    root = create_cover_instance(matr) # transforming it into double-linked lists
    cover = ExactCover(root) # solving it using dancing links
    res = cover.search(0)

    if res:
        
        selected_rows = cover.get_solution() # all the rows that are part of the solution

        for elem in selected_rows: # decoding what a row actually is
            row = int(elem / 81)
            residue = int(elem % 81)
            column = int(residue / 9)
            number = int(residue % 9)
            sudoku[row, column] = int(number+1) # filling out the sudoku

        return sudoku.astype(int)
    else:
        print("Sudoku not solvable!")
        return sudoku

        

if __name__ == "__main__":
    
    # running a speedtest on one example, just to illustrate how much faster it is

    second = example_sudoku.copy()

    start = time.time()
    print_sudoku(solve_bruteforce(example_sudoku))
    end = time.time()
    print("Brute Force Backtracking:",end - start)

    start = time.time()
    print_sudoku(solve_dancinglinks(second))
    end = time.time()
    print("Algorithm X with Dancing Links (DLX):",end - start)
    
