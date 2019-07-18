import numpy as np 
import math 
"""
My implementation of DLX, with some additional features I find helpful for debugging, such as 
the ability of a DataObject to print itself.

See https://arxiv.org/pdf/cs/0011047.pdf for a detailed explanation.
"""

class DataObject():
    
    def __init__(self):
        self.l = self
        self.r = self
        self.u = self
        self.d = self
        self.c = self

        self.id = None

        self.row = None

    def __repr__(self):
        return "DataObject {} with column: {}.\nLeft: {} Right: {} Up: {} Down: {}".format(self.id, self.c.id, self.l.id, self.r.id, self.u.id, self.d.id)


class ColumnObject(DataObject):

    def __init__(self, s, n):
        super(ColumnObject, self).__init__() 
        self.s = s 
        self.n = n
        self.id = n


class ExactCover():

    def __init__(self, root):
        self.root = root 
        self.solution_objects = []


    def search(self, k=0):
        """
        Solves the exact cover problem as described in the paper.
        
        returns: True once it found a solution, False if instance is unsolvable.

        The solution is then contained in self.solution_objects, which is a list of DataObjects.
        To acquire the corresponding rows, use get_solution() after running search().

        I adapted the algorithm to find and return only one solution instead of printing out all possible solutions.
        You can revert that change:
        Instead of returning true and passing that truth value upwards through the recursion levels, just 
        uncomment the print_solution statement and remove the if-clause to keep the algorithm running. 
        """
        if self.root.r == self.root:
            #self.print_solution()
            return True 
        else:
            col = self.choose_column()
            self.cover_column(col)
            r = col.d
            while(r != col):
                if len(self.solution_objects) > k:
                    self.solution_objects[k] = r
                else:
                    self.solution_objects.append(r)
                j = r.r 
                while(j != r):
                    self.cover_column(j.c)
                    j = j.r
                if self.search(k+1):
                    return True
                r = self.solution_objects[k] 
                col = r.c
                j = r.l 
                while(j != r):
                    self.uncover_column(j.c)
                    j = j.l 
                r = r.d
            self.uncover_column(col)
            return False 
    
    def cover_column(self, col):
        """
        Covers one column of the sparse matrix by removing it, 
        walking over all of the rows that satisfy it and removing those rows as well
        by removing all of the data-objects they consist of.
        """
        col.r.l = col.l 
        col.l.r = col.r
        i = col.d 
        while(i != col):
            j = i.r 
            while(j != i):
                j.d.u = j.u 
                j.u.d = j.d
                j.c.s -= 1
                j = j.r
            i = i.d

    def uncover_column(self, col):
        """
        Backtracking step: If we ended up with an unsolvable matrix, revert all of the deletion operations.
        """
        i = col.u
        while(i != col):
            j = i.l 
            while(j != i):
                j.c.s += 1
                j.d.u = j
                j.u.d = j
                j = j.l
            i = i.u
        col.r.l = col 
        col.l.r = col

    def print_solution_knuth(self):
        """
        This is only here for debugging reasons.
        """
        for obj in self.solution_objects:
            res = ""
            o = obj
            res += o.c.n
            o = o.r
            while(o != obj):
                res += o.c.n
                o = o.r
            print(res)
        print(True)

    def print_solution(self):
        """
        Prints a solution to the command line as a list of row numbers. It will give you duplicate entries if some exist.
        """
        print("Printing solution:")
        print([obj.row for obj in self.solution_objects])

    def get_solution(self):
        """
        Returns the found solution (this is not necessarily the only existing solution) as a set of row indices.
        """
        return [obj.row for obj in set(self.solution_objects)]

    def choose_column(self):
        """
        We could choose a column randomly, but there is a simple way of speeding things up,
        which is: select the column with the smallest number of entries, which results in a 
        search tree with a small branching factor at the top, which is obviously advantageous.
        """
        s = math.inf
        j = self.root.r 
        while(j != self.root):
            if(j.s < s):
                c = j 
                s = j.s 
            j = j.r
        return c



def create_cover_instance(matr):
    """
    This transforms a sparse matrix into a cover instance expressed as double-linked lists, by walking over
    the the sparse matrix and creating a data object for every "1" that is encountered, which is then woven into
    the web of double-linked lists.
    This might be very helpful, because it works for any kind of sparse matrix, irrespective of the semantics of the
    problem (so, not just for sudokus). However, there might be more efficient ways of creating the web, if the problem
    can be transformed into the web directly, without expressing it as a matrix first.
    """

    cols = [ColumnObject(0,name) for name in range(matr.shape[1]+1)]

    for idx in range(len(cols)-1):
        cols[idx].r = cols[idx+1]
        cols[idx+1].l = cols[idx]
    cols[-1].r = cols[0]
    cols[0].l = cols[-1]
        
    new_matr = [[None for x in range(matr.shape[1])] for x in range(matr.shape[0])]

    for i in range(matr.shape[0]):
        for j in range(matr.shape[1]):

            if matr[i,j] == 1:

                d = DataObject()
                d.id = str(i) + str(j)

                # setting column
                d.c = cols[j+1]
                d.row = i
                d.c.s += 1

                # setting down
                d.d = d.c

                # setting up
                ones = np.where(matr[0:i,j])[0]
                if len(ones) > 0:
                    up = new_matr[ones[-1]][j]
                    d.u = up
                    up.d = d
                else:
                    d.u = d.c 
                    d.c.d = d # necessarily happens at some point

                # for the latest data object, column.up automatically is this object
                d.c.u = d

                # setting left and right
                ones = np.where(matr[i,0:j])[0]
                if len(ones) > 0:
                    # setting right
                    right = new_matr[i][ones[0]]
                    d.r = right
                    right.l = d

                    #setting left
                    left = new_matr[i][ones[-1]]
                    d.l = left
                    left.r = d 

                new_matr[i][j] = d 

    return cols[0]
