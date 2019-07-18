import numpy as np 
import math 


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
        if self.root.r == self.root:
            self.print_solution() #self.parse_solution()
            return True#set([obj.row for obj in self.solution_objects])
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
            return False #[obj.row for obj in self.solution_objects]
    
    def cover_column(self, col):
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

    def parse_solution(self):
        """
        The idea behind printing a solution is relatively simple if you choose a clever representation
        of rows. Here: Let a row be represented by the set of columns that it covers. 
        Therefore, we print the row for every data object that we selected.
        """
        list_of_rows = []
        for dataobject in self.solution_objects:
            list_of_column_names = []
            start = dataobject.c.n 
            print(start)
            list_of_column_names.append(start)
            right = dataobject.r
            while(start != right.c.n):
                print(right.c.n)
                list_of_column_names.append(right.c.n)
                right = right.r
            list_of_rows.append(list_of_column_names)
        return list_of_rows

    def print_solution_knuth(self):
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
        print("Printing solution:")
        for obj in self.solution_objects:
            print("Select row {}".format(obj.row))

    def get_solution(self):
        return [obj.row for obj in self.solution_objects]

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

    cols = [ColumnObject(0,name) for name in range(matr.shape[1]+1)]#["h"] + [chr(i+65) for i in range(matr.shape[1])]]

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
                #print("Working on {}, ones={}, ones.any={} result: {}".format(d.id, ones, len(ones),d))
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

    # for i in range(matr.shape[0]):
    #     for j in range(matr.shape[1]):
    #         print(new_matr[i][j])

    return cols[0]


def setup_exact_cover(sudoku):
    """
    Creates the large sparse matrix that contains all the constraints for sudokus.
    """

    ec = np.zeros((729,324))
    fulfilled = []
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
                fulfilled += [i*9+j, 81+i*9+k, 162+(9*j+k)%81, 243+k+9*int((j/3))+27*int((i/3))]
    
    ec = np.delete(ec, fulfilled, axis=1) #zeros[]
    zeros = np.where(np.sum(ec, axis=0) == 0)
    ec = np.delete(ec, zeros[0], axis=1)
    return ec 

def setup_sudoku(ec, sudoku):
    locations = [[i*81+9*j+k] for i,j in zip(np.where(sudoku)[0], np.where(sudoku)[1]) for k in range(9)]
    return np.delete(ec, locations, axis=0)