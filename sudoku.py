from copy import deepcopy
from enum import Enum
from typing import List, Tuple, NamedTuple, Callable, Optional

Grid = List[List[int]]
Options = List[List[List[int]]]

GRID_SIZE: int = 9
SECTOR_SIZE: int = 3
VALUE_RANGE: int = 9
EMPTY = 0

# sample puzzles
puz1 = [[5,1,7,6,0,0,0,3,4],
         [2,8,9,0,0,4,0,0,0],
         [3,4,6,2,0,5,0,9,0],
         [6,0,2,0,0,0,0,1,0],
         [0,3,8,0,0,6,0,4,7],
         [0,0,0,0,0,0,0,0,0],
         [0,9,0,0,0,0,0,7,8],
         [7,0,3,4,0,0,5,6,0],
         [0,0,0,0,0,0,0,0,0]]

inp2  = [[5,1,7,6,0,0,0,3,4],
         [0,8,9,0,0,4,0,0,0],
         [3,0,6,2,0,5,0,9,0],
         [6,0,0,0,0,0,0,1,0],
         [0,3,0,0,0,6,0,4,7],
         [0,0,0,0,0,0,0,0,0],
         [0,9,0,0,0,0,0,7,8],
         [7,0,3,4,0,0,5,6,0],
         [0,0,0,0,0,0,0,0,0]]

inpd  = [[1,0,5,7,0,2,6,3,8],
         [2,0,0,0,0,6,0,0,5],
         [0,6,3,8,4,0,2,1,0],
         [0,5,9,2,0,1,3,8,0],
         [0,0,2,0,5,8,0,0,9],
         [7,1,0,0,3,0,5,0,2],
         [0,0,4,5,6,0,7,2,0],
         [5,0,0,0,0,4,0,6,3],
         [3,2,6,1,0,7,0,0,4]]

hard  = [[8,5,0,0,0,2,4,0,0],
         [7,2,0,0,0,0,0,0,9],
         [0,0,4,0,0,0,0,0,0],
         [0,0,0,1,0,7,0,0,2],
         [3,0,5,0,0,0,9,0,0],
         [0,4,0,0,0,0,0,0,0],
         [0,0,0,0,8,0,0,7,0],
         [0,1,7,0,0,0,0,0,0],
         [0,0,0,0,3,6,0,4,0]]

diff  = [[0,0,5,3,0,0,0,0,0],
         [8,0,0,0,0,0,0,2,0],
         [0,7,0,0,1,0,5,0,0],
         [4,0,0,0,0,5,3,0,0],
         [0,1,0,0,7,0,0,0,6],
         [0,0,3,2,0,0,0,8,0],
         [0,6,0,5,0,0,0,0,9],
         [0,0,4,0,0,0,0,3,0],
         [0,0,0,0,0,9,7,0,0]]


class GridLocation(NamedTuple):
    row: int
    column: int


class Sudoku():
    def __init__(self, initial_values: Grid = None, rows: int = GRID_SIZE, columns: int = GRID_SIZE ) -> None:
        self._rows: int = rows
        self._columns: int = columns
        if initial_values == None:
            self.grid: Grid = [[EMPTY for c in range(columns)] for r in range(rows)]
        elif len(initial_values) != rows:
            print(f"initial_values: {len(initial_values)} rows, should be {GRID_SIZE}.")
        elif not (all([len(r)==GRID_SIZE for r in initial_values])):
            print(f"initial_values: not all rows contain {GRID_SIZE} columns.")
        else:
            self.grid: Grid = initial_values.copy()
        self._options: Options = self.get_options()


    def __str__(self) -> str:
        first_row = True
        output: str = "["
        for row in self.grid:
            first_col = True
            if first_row:
                output += "["
                first_row = False
            else:
                output += " ["
            for col in row:
                if first_col:
                    output += str(col)
                    first_col = False
                else:
                    output += ", " + str(col)
            output += "],\n"
        output += "]\n"
        return output


    def is_valid(self) -> bool:
        """
        checks if sudoku constraints are satisfied
        """
        for r in range(self._rows):
            for c in range(self._columns):
                if self.grid[r][c] != EMPTY:
                    # check row
                    for j in range(self._columns):
                        if (c != j) & (self.grid[r][c] == self.grid[r][j]):
                            return False
                    # check column
                    for i in range(self._rows):
                        if (r != i) & (self.grid[r][c] == self.grid[i][c]):
                            return False
                    # check sector
                    sec_r = r // SECTOR_SIZE
                    sec_c = c // SECTOR_SIZE
                    for i in range(SECTOR_SIZE):
                        for j in range(SECTOR_SIZE):
                            si = SECTOR_SIZE*sec_r + i
                            sj = SECTOR_SIZE*sec_c + j
                            if (r != si) & (c != sj) & (self.grid[r][c] == self.grid[si][sj]):
                                return False
        return True


    def _init_domain(self) -> Options:
        """
        initializes a list array of 1 through 9 domain options for each cell
        """
        domain = []
        for r in range(self._rows):
            row = []
            for c in range(self._columns):
                row.append(list(range(1,VALUE_RANGE+1)))
            domain.append(row)
        return domain


    def get_options(self) -> Options:
        """
        given a sudoku puzzle grid with values entered, an array of options for each cell is returned  
        """
        opts = self._init_domain()
        for r in range(self._rows):
            for c in range(self._columns):
                if self.grid[r][c] != EMPTY:
                    opts[r][c] = []
                else:
                    # check row
                    for j in range(self._columns):
                        if self.grid[r][j] in opts[r][c]:
                            opts[r][c].remove(self.grid[r][j])
                    # check column
                    for i in range(self._rows):
                        if self.grid[i][c] in opts[r][c]:
                            opts[r][c].remove(self.grid[i][c])
                    # check sector
                    sec_r = r // SECTOR_SIZE
                    sec_c = c // SECTOR_SIZE
                    for i in range(SECTOR_SIZE):
                        for j in range(SECTOR_SIZE):
                            si = SECTOR_SIZE*sec_r + i
                            sj = SECTOR_SIZE*sec_c + j
                            if self.grid[si][sj] in opts[r][c]:
                                opts[r][c].remove(self.grid[si][sj])
        return opts


    def set_cell(self, rcv: Optional[Tuple[int, int, int]] ):
        """
        set a sudoku puzzle grid cell (r, c) to value (v)
        """
        if rcv:
            r, c, v = rcv
            self.grid[r][c] = v
            self._options: Options = self.get_options()
        else:
            print(f"in set_cell() rcv is {rcv}.")
        return self


    def print_num_options(self):
        """
        prints a grid conaining number of options for each cell
        """
        for r in range(self._rows):
            print([len(self._options[r][c]) for c in range(self._columns)])


    def num_options_all_zero(self) -> bool:
        """
        if any option counts greater than zero, returns False
        """
        for r in range(self._rows):
            for c in range(self._columns):
                if len(self._options[r][c]) > 0:
                    return False
        return True


    def get_first_option(self, num: int) -> Optional[Tuple[int, int, int]]:
        """
        find first cell with only num options
            return row , column and the single option
        otherwise return None
        """
        for r in range(self._rows):
            for c in range(self._columns):
                if len(self._options[r][c]) == num:
                    return (r, c, self._options[r][c][0])
        return None


    def fill_easy(self):
        """
        fill first cell with one option
        repeat until all cells with a single option are filled
        """
        d = True
        step_count = 0
        opt = self.get_first_option(1)
        while (opt is not None):
            self.set_cell(opt)
            step_count += 1
            #print(f"Step: {step_count}\n{self}")
            opt = self.get_first_option(1)
        return self


def sudoku_solver(sudoku: Sudoku) -> Optional[Sudoku]:
    solution = None
    sud1 = deepcopy(sudoku)
    sud1._options = sud1.get_options()
    sud1 = sud1.fill_easy()
    sud1._options = sud1.get_options()
    
    if sud1.num_options_all_zero() & sud1.is_valid():
        return sud1
    else:
        for n in range(2, VALUE_RANGE):
            opt = sud1.get_first_option(n)
            opt_list: List = sud1._options[opt[0]][opt[1]]
            for v in opt_list:
                sud1 = sud1.set_cell((opt[0],opt[1],v)).fill_easy()
                print("call solver")
                solution = sudoku_solver(sud1)
            if solution is not None:
                return solution
        return None


if __name__ == "__main__":
    s1 = Sudoku(puz1)
    print(sudoku_solver(s1))
