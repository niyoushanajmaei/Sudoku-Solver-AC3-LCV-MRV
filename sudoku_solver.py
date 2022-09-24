# considering the board is solvable

class Sudoku:
    def __init__(self):
        self.n = 9
        self.board = [[[] for i in range(self.n)] for j in range(self.n)]
        self.possible_values = [[[] for i in range(self.n)] for j in range(self.n)]
        self.solved = False
        self.changed_pos = []
        self.possible_values_before = []

    # get minimum remaining value, break tie with least constraining value
    # forward check, if possible make move, other wise backtrack
    # do until board is solved
    def solve_ac3_lcv_mrv(self):
        while not self.solved :
            min_rem_values,min = self.get_min_rem_values()
            if min==0:
                # if no moves is available for a cell, backtrack
                self.backtrack()
            else:
                pos = self.degree_heuristic(min_rem_values)
                val = self.get_least_const_val(pos)
                self.forward_check(val, pos)
                # if everything was ok the val was placed and all possible values were updated in "forward"
                # if everything was not ok, no move was made, and nothing changed
        return self.board

    def read(self):
        for i in range(self.n):
            self.board[i] = input().split()
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j]!='.':
                    self.board[i][j] = int(self.board[i][j])
        self.get_possible_values()

    # gets the possible values for empty places, store in possible_values
    def get_possible_values(self):
        for i in range(self.n):
            for j in range(self.n):
                temp = [False] * self.n
                if self.board[i][j] == '.':
                    for k in range(self.n):
                        if self.board[i][k] != '.':
                            temp[self.board[i][k]-1] = True
                    for k in range(self.n):
                        if self.board[k][j] != '.':
                            temp[self.board[k][j] - 1] = True
                    square_index = self.get_square_index(i,j)
                    for k in square_index:
                        r = int(k/self.n)
                        c = k%self.n
                        if self.board[r][c] != '.':
                            temp[self.board[r][c] - 1] = True
                self.possible_values[i][j] = [i+1 for i in range(self.n) if not temp[i]]
        return

    # get the indices of cells that constitute the square of a pos (i,j)
    def get_square_index(self,i,j):
        l = list()
        for r in range(int(i / 3)*3, int(i / 3)*3 + 3):
            for c in range(int(j / 3)*3, int(j / 3)*3 + 3):
                l.append(r*self.n+ c)
        return l

    # returns the positions of variables with least remaining values
    def get_min_rem_values(self):
        min = None
        min_rem = list()
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == '.':
                    if min is None or (self.board[i][j] == '.' and len(self.possible_values[i][j]) < min):
                        min_rem = [i*self.n+j]
                        min = len(self.possible_values[i][j])
                    elif self.board[i][j] == '.' and len(self.possible_values[i][j]) == min:
                        min_rem.append(i*self.n+j)
        return min_rem,min

    # returns the position of the variable with the most constraints
    def degree_heuristic(self,arr):
        if len(arr) == 1:
            return arr[0]
        max_degree = None
        max_pos = None
        for pos in arr:
            tmp = self.get_degree(pos)
            if max_degree is None or tmp > max_degree:
                max_degree = tmp
                max_pos = pos
        return max_pos

    #  returns the number of empty neighboring cells
    def get_degree(self,pos):
        degree = 0
        r = int(pos/self.n)
        c = pos%self.n
        for i in range(min(0,r),max(r+2,self.n)):
            for j in range(min(0,c),max(c+2,self.n)):
                if i != r and j != c and self.board[r][c] == ".":
                    degree += 1
        return degree

    # returns the least constraining value, appears less in that row, col and square
    def get_least_const_val(self,pos):
        count = [0]*self.n
        r = int(pos/self.n)
        c = pos%self.n
        for k in range(self.n):
            if self.board[r][k]!='.':
                count[self.board[r][k]-1] += 1 # elements in the same row
        for k in range(self.n):
            if self.board[k][c]!='.':
                count[self.board[k][c]-1] += 1 # elements in the same column
        square_index = self.get_square_index(r,c)
        for k in square_index:
            i = int(k/self.n)
            j = k%self.n
            if self.board[i][j]!='.':
                count[self.board[i][j]-1] += 1 # elements in the same square
        # make sure that the values that are not in possible moves, don't get chosen, set count to 9
        for k in range(self.n):
            if k+1 not in self.possible_values[r][c]:
                count[k] = 9
        m = min(count)
        return [i+1 for i, j in enumerate(count) if j == m][0]

    # returns True if making the move doesn't make the board unsolvable, returns false otherwise
    # places the val at pos and updates the possible values of neighbors
    # checks if the board was solved
    def forward_check(self,val,pos):
        # get a copy of current attributes, revert in the end if the placement causes arc inconsistency
        solvable = self.place(val, pos)
        if not solvable:  # if not solvable, revert and undo the move
            undo_pos = self.changed_pos.pop()
            self.undo_move(undo_pos)
        else:
            self.solved = self.check_solved()  # check whether the placement solved the puzzle
        return solvable

    # returns True if there are no more '.'s on the board
    def check_solved(self):
        solved = True
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == '.':
                    solved = False
        return solved

    # places a value in the position, removes the value from possible values of pos
    # updates self.changed_pos
    # gets a copy of possible moves of all the board before placing and appends to self.possible_values_before
    # updates possible moves of neighbors
    # returns True if the board remains solvable
    def place(self, val, pos):
        r = int(pos/self.n)
        c = pos%self.n
        self.board[r][c] = val
        self.possible_values[r][c].remove(val)
        self.changed_pos.append(pos)
        # append a copy of possible values to possible values before
        self.possible_values_before.append(self.get_copy_of_curr())

        # update possible moves of cells in the same row
        for k in range(self.n):
            if self.board[r][k] == '.' and val in self.possible_values[r][k]:
                self.possible_values[r][k].remove(val)
                if len(self.possible_values[r][k]) == 0:
                    return False  # The board is not solvable
        # update possible moves of cells in the same column
        for k in range(self.n):
            if self.board[k][c] == '.' and val in self.possible_values[k][c]:
                self.possible_values[k][c].remove(val)
                if len(self.possible_values[k][c]) == 0:
                    return False  # The board is not solvable
        # update possible moves of cells in the same square
        square_index = self.get_square_index(r, c)
        for k in square_index:
            i = int(k/self.n)
            j = k%self.n
            if self.board[i][j] == '.' and val in self.possible_values[i][j]:
                self.possible_values[i][j].remove(val)
                if len(self.possible_values[i][j]) == 0:
                    return False  # The board is not solvable
        return True

    # change the position to '.'
    # removes the value from that variable's possible moves
    def undo_move(self,pos):
        r = int(pos/self.n)
        c = pos%self.n
        self.board[r][c] = '.'
        self.possible_values = self.possible_values_before.pop()
        return

    # undo last move, revert possible moves to previous state
    # val was previously removed from possible moves (in place)
    # Backtrack until there isn't a possible move
    def backtrack(self):
        possible_move = False
        while not possible_move:
            pos = self.changed_pos.pop()
            r = int(pos/self.n)
            c = pos%self.n
            self.board[r][c] = '.'
            # revert possible values of all board to what it was before placing
            self.revert(self.possible_values_before.pop())
            # whether board has move
            possible_move = self.board_has_moves()
        return

    # returns a copy of the possible values of the board
    def get_copy_of_curr(self):
        poss_val = [[[] for i in range(self.n)] for j in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                tmp = []
                for k in range(len(self.possible_values[i][j])):
                    tmp.append(self.possible_values[i][j][k])
                poss_val[i][j] = tmp
        return poss_val

    # reverts the board's possible values to a previous status
    def revert(self,copy):
        self.possible_values = copy
        return

    # returns True if val can be placed at pos, False otherwise
    def is_possible(self, val, pos):
        possible = True
        r = int(pos/self.n)
        c = pos%self.n
        # check whether val is used in the same row as pos
        for k in range(self.n):
            if self.board[r][k] == val:
                possible = False
                break
        # check whether val is used in the same column as pos, only if still possible
        if possible:
            for k in range(self.n):
                if self.board[k][c] == val:
                    possible = False
                    break
        # check whether val is used in the same square as pos, only if still possible
        if possible:
            square_index = self.get_square_index(r,c)
            for k in square_index:
                i = int(k/self.n)
                j = k%self.n
                if self.board[i][j] == val:
                    possible = False
                    break
        return possible

    # returns false if there is at least one variable with no move
    def board_has_moves(self):
        has_moves = True
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j]=='.' and len(self.possible_values[i][j])==0:
                    has_moves = False
        return has_moves

if __name__=="__main__":
    sudoku = Sudoku()
    sudoku.read()
    res = sudoku.solve_ac3_lcv_mrv()
    for i in range(sudoku.n):
        for j in range(sudoku.n):
            print(sudoku.board[i][j], end=" ")
        print()
