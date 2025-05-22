import tkinter as tk
import random

DIFFICULTIES = {
    "Easy":    {"rows": 9,  "cols": 12, "mines": 15},
    "Medium":  {"rows": 12, "cols": 22, "mines": 40},
    "Hard":    {"rows": 16, "cols": 30, "mines": 99}
}

CELL_SIZE = 36
COLORS = {
    1: "#1a39e6",
    2: "#2ea130",
    3: "#e01c24",
    4: "#1b1bb4",
    5: "#a12b2b",
    6: "#24beb1",
    7: "#2e2e2e",
    8: "#999999"
}
MINE_COLOR = "#e01c24"
SAFE_COLOR = "#e6e6e6"
REVEALED_COLOR = "#f8f8f8"
FLAG_COLOR = "#ff4500"
HOVER_COLOR = "#ffe39b"
SAFE_HIGHLIGHT_COLOR = "#7CFC8A"

class Minesweeper:
    def __init__(self, master):
        self.master = master
        self.master.title("Minesweeper")
        self.difficulty = "Easy"
        self.hints_left = 3
        self.safe_clicks = 3
        self.safe_highlight = None
        self.safe_highlight_id = None
        self.make_menu()

    def make_menu(self):
        self.clear()
        self.menu_frame = tk.Frame(self.master, bg="#bbbbbb")
        self.menu_frame.pack(padx=30, pady=30)
        tk.Label(self.menu_frame, text="Minesweeper", font=("Arial", 28, "bold"), bg="#bbbbbb").pack(pady=(0,24))
        tk.Label(self.menu_frame, text="Choose difficulty:", font=("Arial", 14), bg="#bbbbbb").pack(pady=(0,10))
        self.diff_var = tk.StringVar(value=self.difficulty)
        for diff in DIFFICULTIES:
            tk.Radiobutton(self.menu_frame, text=diff, variable=self.diff_var, value=diff,
                           font=("Arial", 12), bg="#bbbbbb").pack(anchor="w", padx=25)
        tk.Button(self.menu_frame, text="Start Game", font=("Arial", 14, "bold"),
                  command=self.start_game).pack(pady=18)

    def start_game(self):
        self.difficulty = self.diff_var.get()
        self.rows = DIFFICULTIES[self.difficulty]["rows"]
        self.cols = DIFFICULTIES[self.difficulty]["cols"]
        self.num_mines = DIFFICULTIES[self.difficulty]["mines"]
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        self.first_click = True
        self.timer_running = False
        self.time_elapsed = 0
        self.hints_left = 3
        self.safe_clicks = 3
        self.safe_highlight = None
        self.safe_highlight_id = None
        self.clear()
        self.frame = tk.Frame(self.master, bg="#bbbbbb")
        self.frame.pack()
        self.status_label = tk.Label(self.frame, text="🙂", font=("Arial", 22, "bold"), bg="#bbbbbb")
        self.status_label.grid(row=0, column=0, columnspan=self.cols, sticky="ew", pady=(5,0))
        self.mine_count_label = tk.Label(self.frame, text=f"Mines: {self.num_mines}", bg="#bbbbbb", font=("Arial", 12))
        self.mine_count_label.grid(row=1, column=0, columnspan=self.cols//2, sticky="w")
        self.flag_count_label = tk.Label(self.frame, text=f"Flags: 0", bg="#bbbbbb", font=("Arial", 12))
        self.flag_count_label.grid(row=1, column=self.cols//2, columnspan=self.cols//2, sticky="e")
        self.timer_label = tk.Label(self.frame, text="Time: 0", bg="#bbbbbb", font=("Arial", 12))
        self.timer_label.grid(row=2, column=0, columnspan=self.cols, sticky="ew")
        btn_frame = tk.Frame(self.frame, bg="#bbbbbb")
        btn_frame.grid(row=3, column=0, columnspan=self.cols)
        self.hint_button = tk.Button(btn_frame, text=f"Hint ({self.hints_left})", font=("Arial", 12),
                                     command=self.use_hint)
        self.hint_button.pack(side=tk.LEFT, padx=2, pady=(0,7))
        self.safe_button = tk.Button(btn_frame, text=f"Safe ({self.safe_clicks})", font=("Arial", 12),
                                     command=self.safe_click)
        self.safe_button.pack(side=tk.LEFT, padx=2, pady=(0,7))
        self.restart_button = tk.Button(btn_frame, text="Restart", font=("Arial", 12),
                                        command=self.restart_game)
        self.restart_button.pack(side=tk.LEFT, padx=2, pady=(0,7))
        self.menu_button = tk.Button(btn_frame, text="Back to Menu", font=("Arial", 12),
                                        command=self.back_to_menu)
        self.menu_button.pack(side=tk.LEFT, padx=2, pady=(0,7))
        self.board_frame = tk.Frame(self.frame, bg="#bbbbbb")
        self.board_frame.grid(row=4, column=0, columnspan=self.cols)
        self.create_game_board()
        self.master.bind("<Key-h>", lambda event: self.use_hint())
        self.master.bind("<Key-H>", lambda event: self.use_hint())
        self.master.bind("<Key-s>", lambda event: self.safe_click())
        self.master.bind("<Key-S>", lambda event: self.safe_click())

    def clear(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def create_game_board(self):
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                btn = tk.Button(
                    self.board_frame,
                    width=2, height=1,
                    bg=SAFE_COLOR,
                    relief=tk.RAISED,
                    font=("Arial", 15, "bold"),
                    command=lambda r=row, c=col: self.cell_clicked(r, c)
                )
                btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                btn.bind("<Button-3>", lambda event, r=row, c=col: self.toggle_flag(r, c))
                btn.bind("<Button-2>", lambda event, r=row, c=col: self.chord_reveal(r, c))
                btn.bind("<Shift-Button-1>", lambda event, r=row, c=col: self.toggle_flag(r, c))
                btn.bind("<Enter>", lambda event, r=row, c=col: self.highlight_cell(r, c, True))
                btn.bind("<Leave>", lambda event, r=row, c=col: self.highlight_cell(r, c, False))
                self.buttons[row][col] = btn

    def place_mines(self, safe_row, safe_col):
        self.mines.clear()
        forbidden = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = safe_row + dr, safe_col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    forbidden.add((nr, nc))
        while len(self.mines) < self.num_mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row, col) not in forbidden:
                self.mines.add((row, col))

    def calculate_numbers(self):
        self.numbers = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) in self.mines:
                    continue
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if (nr, nc) in self.mines:
                                self.numbers[row][col] += 1

    def cell_clicked(self, row, col):
        if (row, col) in self.flags or (row, col) in self.revealed:
            return
        if self.first_click:
            self.place_mines(row, col)
            self.calculate_numbers()
            self.first_click = False
            self.start_timer()
        self.reveal_cell(row, col)
        self.update_flag_count()

    def reveal_cell(self, row, col):
        if (row, col) in self.revealed or (row, col) in self.flags:
            return
        self.revealed.add((row, col))
        btn = self.buttons[row][col]
        btn.config(relief=tk.SUNKEN, state=tk.DISABLED, bg=REVEALED_COLOR)
        if (row, col) in self.mines:
            btn.config(text="💣", bg=MINE_COLOR)
            self.game_over(False, lose_cell=(row, col))
            return
        if self.numbers[row][col] > 0:
            color = COLORS.get(self.numbers[row][col], "#222")
            btn.config(text=str(self.numbers[row][col]), disabledforeground=color)
        else:
            self.reveal_neighbors(row, col)
        if len(self.revealed) == (self.rows * self.cols - self.num_mines):
            self.game_over(True)

    def reveal_neighbors(self, row, col):
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if (
                    0 <= nr < self.rows and 0 <= nc < self.cols and
                    (nr, nc) not in self.revealed and
                    (nr, nc) not in self.flags
                ):
                    self.reveal_cell(nr, nc)

    def toggle_flag(self, row, col):
        if (row, col) in self.revealed:
            return
        btn = self.buttons[row][col]
        if (row, col) in self.flags:
            self.flags.remove((row, col))
            btn.config(text="", bg=SAFE_COLOR)
        else:
            if len(self.flags) < self.num_mines:
                self.flags.add((row, col))
                btn.config(text="🚩", fg=FLAG_COLOR, bg=SAFE_COLOR, font=("Arial", 16, "bold"))
        self.update_flag_count()

    def highlight_cell(self, row, col, on):
        btn = self.buttons[row][col]
        if (row, col) in self.revealed:
            return
        if self.safe_highlight and (row, col) == self.safe_highlight:
            return  # Don't override safe highlight color
        if on:
            btn.config(bg=HOVER_COLOR)
        else:
            btn.config(bg=SAFE_COLOR)

    def chord_reveal(self, row, col):
        if (row, col) not in self.revealed or self.numbers[row][col] == 0:
            return
        flags_nearby = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if (nr, nc) in self.flags:
                        flags_nearby += 1
        if flags_nearby == self.numbers[row][col]:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = row + dr, col + dc
                    if (
                        0 <= nr < self.rows and 0 <= nc < self.cols and
                        (nr, nc) not in self.revealed and
                        (nr, nc) not in self.flags
                    ):
                        self.reveal_cell(nr, nc)

    def update_flag_count(self):
        self.flag_count_label.config(text=f"Flags: {len(self.flags)}")

    def game_over(self, won, lose_cell=None):
        self.stop_timer()
        self.disable_safe_hint_buttons()
        for row in range(self.rows):
            for col in range(self.cols):
                btn = self.buttons[row][col]
                if (row, col) in self.mines:
                    if (row, col) == lose_cell:
                        btn.config(text="💥", bg="#ff4444")
                    elif (row, col) in self.flags:
                        btn.config(text="🚩", bg=FLAG_COLOR)
                    else:
                        btn.config(text="💣", bg=MINE_COLOR)
                elif (row, col) in self.flags:
                    btn.config(bg="#bbbbbb")
                btn.config(state=tk.DISABLED)
        if won:
            message = "🎉 You Win!"
            self.status_label.config(text="😎")
        else:
            message = "💥 Game Over!"
            self.status_label.config(text="😵")
        self.show_message(message)

    def show_message(self, message):
        popup = tk.Toplevel(self.master)
        popup.title(message)
        popup.resizable(False, False)
        tk.Label(popup, text=message, font=("Arial", 18)).pack(pady=20)
        tk.Button(popup, text="Restart", font=("Arial", 13),
                  command=lambda: [popup.destroy(), self.restart_game()]).pack(pady=10)
        tk.Button(popup, text="Back to Menu", font=("Arial", 13), command=lambda: [popup.destroy(), self.back_to_menu()]).pack()
        tk.Button(popup, text="Quit", font=("Arial", 13), command=self.master.destroy).pack()
        popup.grab_set()

    def restart_game(self):
        if hasattr(self, "frame"):
            self.frame.destroy()
        self.start_game()

    def back_to_menu(self):
        if hasattr(self, "frame"):
            self.frame.destroy()
        self.make_menu()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.time_elapsed = 0
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.timer_label.config(text=f"Time: {self.time_elapsed}")
            self.time_elapsed += 1
            self.master.after(1000, self.update_timer)

    def stop_timer(self):
        self.timer_running = False

    def use_hint(self):
        if self.first_click:
            return
        if self.hints_left <= 0:
            return
        safe_cells = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in self.mines and (r, c) not in self.revealed and (r, c) not in self.flags
        ]
        if not safe_cells:
            return
        cell = random.choice(safe_cells)
        self.reveal_cell(*cell)
        self.hints_left -= 1
        self.hint_button.config(text=f"Hint ({self.hints_left})", state=tk.NORMAL if self.hints_left else tk.DISABLED)

    def safe_click(self):
        if self.first_click:
            return
        if self.safe_clicks <= 0:
            return
        safe_cells = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in self.mines and (r, c) not in self.revealed and (r, c) not in self.flags
        ]
        if not safe_cells:
            return
        cell = random.choice(safe_cells)
        self.highlight_safe_cell(cell)
        self.safe_clicks -= 1
        self.safe_button.config(text=f"Safe ({self.safe_clicks})", state=tk.NORMAL if self.safe_clicks else tk.DISABLED)

    def highlight_safe_cell(self, cell):
        r, c = cell
        btn = self.buttons[r][c]
        # Remove previous highlight if any
        if self.safe_highlight:
            pr, pc = self.safe_highlight
            prev_btn = self.buttons[pr][pc]
            if (pr, pc) not in self.revealed:
                prev_btn.config(bg=SAFE_COLOR)
        self.safe_highlight = (r, c)
        btn.config(bg=SAFE_HIGHLIGHT_COLOR)
        # Remove highlight after 1.2 seconds
        if self.safe_highlight_id:
            self.master.after_cancel(self.safe_highlight_id)
        self.safe_highlight_id = self.master.after(1200, self.remove_safe_highlight)

    def remove_safe_highlight(self):
        if self.safe_highlight:
            r, c = self.safe_highlight
            btn = self.buttons[r][c]
            if (r, c) not in self.revealed:
                btn.config(bg=SAFE_COLOR)
            self.safe_highlight = None
            self.safe_highlight_id = None

    def disable_safe_hint_buttons(self):
        self.hint_button.config(state=tk.DISABLED)
        self.safe_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()