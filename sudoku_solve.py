"""
This is a collection of sudoku-solving functions.
"""

import numpy as np 
import math 
from dancing_links import *


example_sudoku = np.array([[0,0,0,0,0,0,0,0,0],
                           [0,2,0,5,0,0,0,9,4],
                           [0,0,1,0,0,0,0,0,7],
                           [0,0,0,4,0,6,0,0,5],
                           [2,0,8,0,0,0,0,0,0],
                           [0,0,0,0,5,3,0,0,0],
                           [4,0,9,0,0,0,0,2,0],
                           [5,0,0,6,0,2,0,8,0],
                           [0,6,0,0,9,0,3,0,0]])

# this creates an exact cover template for sudoku, that is:
# a 729 x 324 matrix with all the general constraints for a sudoku.
# this is the same for all sudokus, clues will be taken into account
# by removing some of the constraints.
#ec_template = setup_exact_cover()

"""
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
    for i in range(9):
        line = ""
        for j in range(9):
            line = line + " {} ".format(sudoku[i,j])
            if j % 3 == 2: 
                line = line + "|"
        print(line)
        if i % 3 == 2 and i != 8:
            print("------------------------------")

def get_vals_in_neighbourhood(i,j, sudoku):
    row = list(sudoku[:,j])
    col = list(sudoku[i,:])
    cell = list(sudoku[(i//3)*3:(i//3)*3+3, (j//3)*3:(j//3)*3+3].flatten())
    res = list(set(row) | set(col) | set(cell))
    res.remove(0)
    return res

def solve_bruteforce(sudoku):
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


def solve_dancinglinks(sudoku):

    matr = setup_exact_cover(sudoku)
    #print(matr)
    root = create_cover_instance(matr)
    cover = ExactCover(root)
    res = cover.search(0)

    if res:

        selected_rows = cover.get_solution()

        for elem in selected_rows:
            row = int(elem / 81)
            residue = int(elem % 81)
            column = int(residue / 9)
            number = int(residue % 9)
            sudoku[row, column] = int(number+1) 

        return sudoku.astype(int)
    else:
        print("Sudoku not solvable!")
        return sudoku

if __name__ == "__main__":
    np.set_printoptions(threshold=10000000000, linewidth= 1000)
    #print(ec_template)
    print_sudoku(solve_dancinglinks(example_sudoku))
