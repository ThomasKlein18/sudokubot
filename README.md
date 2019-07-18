# sudokubot
Building a telegram bot that solves sudokus.

The first challenge was to implement a faster way of solving sudokus (Backtracking works fine, but can be rather slow for some sudokus, especially sparse ones).
This was solved using the go-to-method for solving sudokus with computers: DLX = Algorithm X and Dancing Links by Stanford-CS-Professor Donald Knuth. 
See https://arxiv.org/pdf/cs/0011047.pdf for a detailed explanation of DLX, including the pseudocode which I used to write this code. 

The second challenge is to set up a Teleram bot that accepts an image of a sudoku, transforms that to a sudoku matrix and returns a solution. 
