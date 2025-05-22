import tkinter as tk
import random
import copy

GRID_SIZE = 9
BOX_SIZE = 3

DIFFICULTIES = {
    "Easy": 40,    # Number of revealed cells
    "Medium": 32,
    "Hard": 24
}

class Sudoku:
    def __init__(self, master):
        self.master = master
        self.master.title("Sudoku")
        self.selected_cell = None
        self.cells = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.entries = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.solution = None
        self.hints_left = 3
        self.create_menu()

    def create_menu(self):
        self.clear()
        menu = tk.Frame(self.master, bg="#e6e6e6")
        menu.pack(padx=40, pady=40)
        tk.Label(menu, text="Sudoku", font=("Arial", 28, "bold"), bg="#e6e6e6").pack(pady=(0, 24))
        tk.Label(menu, text="Choose difficulty:", font=("Arial", 14), bg="#e6e6e6").pack()
        self.diff_var = tk.StringVar(value="Easy")
        for diff in DIFFICULTIES:
            tk.Radiobutton(menu, text=diff, variable=self.diff_var, value=diff, font=("Arial", 12), bg="#e6e6e6").pack(anchor="w", padx=30)
        tk.Button(menu, text="Start Game", font=("Arial", 14, "bold"), command=self.start_game).pack(pady=18)

    def clear(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def start_game(self):
        self.clear()
        self.hints_left = 3
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.solution = None
        self.generate_full_solution()
        self.puzzle = copy.deepcopy(self.solution)
        self.remove_cells(DIFFICULTIES[self.diff_var.get()])
        self.build_board()
        self.create_buttons()

    def build_board(self):
        board_frame = tk.Frame(self.master, bg="#333")
        board_frame.pack(padx=12, pady=12)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = self.puzzle[r][c]
                e = tk.Entry(board_frame, width=2, font=("Arial", 20, "bold"), justify="center",
                             bd=2, relief=tk.RIDGE)
                e.grid(row=r, column=c, ipadx=6, ipady=8, padx=(2 if c % 3 == 0 else 0, 2), pady=(2 if r % 3 == 0 else 0, 2))
                if val != 0:
                    e.insert(0, str(val))
                    e.config(state='readonly', readonlybackground="#e2e2e2", fg="#222")
                else:
                    e.config(bg="#f9f9f9")
                    e.bind("<FocusIn>", lambda event, i=r, j=c: self.set_selected(i, j))
                    e.bind("<KeyRelease>", lambda event, i=r, j=c: self.check_entry(i, j))
                self.entries[r][c] = e
        self.status_label = tk.Label(self.master, text=f"Hints left: {self.hints_left}", font=("Arial", 12), bg="#e6e6e6")
        self.status_label.pack(pady=(2, 10))

    def create_buttons(self):
        btn_frame = tk.Frame(self.master, bg="#e6e6e6")
        btn_frame.pack()
        tk.Button(btn_frame, text="Check", font=("Arial", 12), command=self.check_board).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Hint", font=("Arial", 12), command=self.give_hint).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Solve", font=("Arial", 12), command=self.solve_board).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Restart", font=("Arial", 12), command=self.start_game).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Back to Menu", font=("Arial", 12), command=self.create_menu).pack(side=tk.LEFT, padx=4)

    def set_selected(self, r, c):
        self.selected_cell = (r, c)

    def check_entry(self, r, c):
        v = self.entries[r][c].get()
        if not (v.isdigit() and 1 <= int(v) <= 9):
            self.entries[r][c].delete(0, tk.END)

    def check_board(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                v = self.entries[r][c].get()
                if self.puzzle[r][c] == 0:
                    if not (v.isdigit() and int(v) == self.solution[r][c]):
                        self.entries[r][c].config(bg="#ffb3b3")
                    else:
                        self.entries[r][c].config(bg="#b3ffb3")
        if self.is_board_correct():
            self.status_label.config(text="Congratulations! You solved it!", fg="#1a8c1a")
        else:
            self.status_label.config(text="There are mistakes. Try again.", fg="#e01c24")

    def is_board_correct(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                v = self.entries[r][c].get()
                if self.puzzle[r][c] == 0:
                    if not (v.isdigit() and int(v) == self.solution[r][c]):
                        return False
        return True

    def give_hint(self):
        if self.hints_left <= 0:
            self.status_label.config(text="No hints left!", fg="#e01c24")
            return
        # Find an empty cell
        empties = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                   if self.puzzle[r][c] == 0 and (self.entries[r][c].get() == "" or self.entries[r][c].get() != str(self.solution[r][c]))]
        if not empties:
            self.status_label.config(text="No empty cells for hint!", fg="#e01c24")
            return
        r, c = random.choice(empties)
        self.entries[r][c].delete(0, tk.END)
        self.entries[r][c].insert(0, str(self.solution[r][c]))
        self.entries[r][c].config(bg="#b3e5ff")
        self.master.after(800, lambda: self.entries[r][c].config(bg="#f9f9f9"))
        self.hints_left -= 1
        self.status_label.config(text=f"Hints left: {self.hints_left}", fg="#333")

    def solve_board(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.entries[r][c].config(state=tk.NORMAL)
                self.entries[r][c].delete(0, tk.END)
                self.entries[r][c].insert(0, str(self.solution[r][c]))
                if self.puzzle[r][c] == 0:
                    self.entries[r][c].config(bg="#e9ffb3")
        self.status_label.config(text="Solved!", fg="#1a8c1a")

    # ------ Generator & Solver ------
    def generate_full_solution(self):
        self.solution = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self._solution_helper(0, 0, self.solution)

    def _solution_helper(self, row, col, grid):
        if row == GRID_SIZE:
            return True
        next_row, next_col = (row, col+1) if col < GRID_SIZE-1 else (row+1, 0)
        nums = list(range(1, 10))
        random.shuffle(nums)
        for num in nums:
            if self.is_safe(grid, row, col, num):
                grid[row][col] = num
                if self._solution_helper(next_row, next_col, grid):
                    return True
                grid[row][col] = 0
        return False

    def is_safe(self, grid, row, col, num):
        for i in range(GRID_SIZE):
            if grid[row][i] == num or grid[i][col] == num:
                return False
        box_row, box_col = row - row % 3, col - col % 3
        for i in range(BOX_SIZE):
            for j in range(BOX_SIZE):
                if grid[box_row + i][box_col + j] == num:
                    return False
        return True

    def remove_cells(self, given):
        # Remove cells to create the puzzle (given=number of nonzero cells to keep)
        empties = GRID_SIZE*GRID_SIZE - given
        positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        random.shuffle(positions)
        removed = 0
        for r, c in positions:
            if removed >= empties:
                break
            temp = self.puzzle[r][c]
            self.puzzle[r][c] = 0
            puzzle_copy = copy.deepcopy(self.puzzle)
            if not self.has_unique_solution(puzzle_copy):
                self.puzzle[r][c] = temp
            else:
                removed += 1

    def has_unique_solution(self, board):
        # Backtracking count to check uniqueness (stop after more than 1)
        count = [0]
        def solve(r=0, c=0):
            if r == GRID_SIZE:
                count[0] += 1
                return count[0] < 2
            next_r, next_c = (r, c+1) if c < GRID_SIZE-1 else (r+1, 0)
            if board[r][c] != 0:
                return solve(next_r, next_c)
            for num in range(1, 10):
                if self.is_safe(board, r, c, num):
                    board[r][c] = num
                    if not solve(next_r, next_c):
                        board[r][c] = 0
                        return False
                    board[r][c] = 0
            return True
        solve()
        return count[0] == 1

if __name__ == "__main__":
    root = tk.Tk()
    Sudoku(root)
    root.mainloop()