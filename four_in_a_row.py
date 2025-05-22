import tkinter as tk
from tkinter import messagebox
import random
import copy

# Game constants
ROWS = 6
COLS = 7
CONNECT_N = 4

THEMES = {
    "Classic": {
        "bg": "#225",
        "board": "#334",
        "empty": "#eef",
        "p1": "#e63946",
        "p2": "#457b9d",
        "hl": "#f1fa3c",
        "txt": "#fafafa",
        "button_fg": "#222",
        "button_bg": "#eef",
        "button_activebg": "#e63946",
        "button_activefg": "#fafafa",
    },
    "Ocean": {
        "bg": "#023047",
        "board": "#219ebc",
        "empty": "#8ecae6",
        "p1": "#ffb703",
        "p2": "#219ebc",
        "hl": "#fb8500",
        "txt": "#fff",
        "button_fg": "#023047",
        "button_bg": "#8ecae6",    # Contrasting light blue
        "button_activebg": "#ffb703",
        "button_activefg": "#023047",
    },
    "Light": {
        "bg": "#b3b3b3",
        "board": "#c7c8cc",
        "empty": "#e2e2e2",
        "p1": "#b23b4e",
        "p2": "#3c6fa7",
        "hl": "#c9d163",
        "txt": "#222",
        "button_fg": "#222",
        "button_bg": "#e2e2e2",
        "button_activebg": "#c9d163",
        "button_activefg": "#222",
    }
}

BOT_DIFFICULTIES = ["Easy", "Medium", "Hard", "Impossible"]

class FourInARow:
    def __init__(self, root):
        self.root = root
        self.root.title("Four in a Row (Connect Four)")
        self.theme_name = "Classic"
        self.theme = THEMES[self.theme_name]
        self.bot_enabled = False
        self.stats = {"P1": 0, "P2": 0, "Draws": 0}
        self.move_stack = []
        self.replay_moves = []
        self.replay_index = 0
        self.replay_mode = False
        self.bot_difficulty = "Medium"
        self.create_menu()

    def apply_theme(self):
        self.theme = THEMES[self.theme_name]
        self.root.config(bg=self.theme["bg"])
        for widget in self.root.winfo_children():
            try:
                widget.config(bg=self.theme["bg"], fg=self.theme["txt"])
            except:
                try:
                    widget.config(bg=self.theme["bg"])
                except:
                    pass

    def create_menu(self):
        self.clear_window()
        self.replay_mode = False
        self.apply_theme()
        frame = tk.Frame(self.root, bg=self.theme["bg"])
        frame.pack(expand=True, fill="both")
        tk.Label(frame, text="Four in a Row", font=("Arial", 28, "bold"),
                 fg=self.theme["p1"], bg=self.theme["bg"]).pack(pady=16)
        tk.Button(frame, text="Player vs Player", font=("Arial", 15, "bold"), width=22,
                  bg=self.theme["board"], fg=self.theme["p1"],
                  activebackground=self.theme["p1"], activeforeground=self.theme["txt"],
                  command=lambda: self.start_game(bot=False)).pack(pady=10)
        bot_frame = tk.Frame(frame, bg=self.theme["bg"])
        bot_frame.pack(pady=(8, 0))
        tk.Label(bot_frame, text="Player vs Bot - Difficulty:", font=("Arial", 13),
                 fg=self.theme["txt"], bg=self.theme["bg"]).pack(side=tk.LEFT)
        self.bot_difficulty_var = tk.StringVar(value=BOT_DIFFICULTIES[1])
        for diff in BOT_DIFFICULTIES:
            tk.Radiobutton(bot_frame, text=diff, variable=self.bot_difficulty_var, value=diff,
                           bg=self.theme["bg"], fg=self.theme["txt"], selectcolor=self.theme["p2"],
                           font=("Arial", 11)).pack(side=tk.LEFT, padx=2)
        # Fix: Set Start Bot Game button colors for theme contrast
        tk.Button(
            frame, text="Start Bot Game", font=("Arial", 13, "bold"), width=22,
            bg=self.theme["button_bg"], fg=self.theme["button_fg"],
            activebackground=self.theme["button_activebg"], activeforeground=self.theme["button_activefg"],
            command=self.start_bot_game
        ).pack(pady=10)
        theme_frame = tk.Frame(frame, bg=self.theme["bg"])
        theme_frame.pack(pady=(15, 0))
        tk.Label(theme_frame, text="Theme:", font=("Arial", 12),
                 fg=self.theme["txt"], bg=self.theme["bg"]).pack(side=tk.LEFT)
        for name in THEMES:
            tk.Button(theme_frame, text=name, width=9, font=("Arial", 10),
                      bg=self.theme["board"], fg=self.theme["txt"],
                      activebackground=self.theme["hl"], activeforeground=self.theme["txt"],
                      command=lambda n=name: self.change_theme(n)).pack(side=tk.LEFT, padx=4)
        stats_txt = f"P1 Wins: {self.stats['P1']}   P2 Wins: {self.stats['P2']}   Draws: {self.stats['Draws']}"
        tk.Label(frame, text=stats_txt, font=("Arial", 13, "italic"),
                 fg=self.theme["txt"], bg=self.theme["bg"]).pack(pady=28)

    def start_bot_game(self):
        self.bot_difficulty = self.bot_difficulty_var.get()
        self.start_game(bot=True)

    def change_theme(self, name):
        self.theme_name = name
        self.theme = THEMES[self.theme_name]
        self.create_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_game(self, bot=False):
        self.bot_enabled = bot
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.move_stack = []
        self.move_count = 0
        self.current_player = 1
        self.winner = None
        self.win_line = []
        self.replay_moves = []
        self.replay_index = 0
        self.replay_mode = False
        self.clear_window()
        self.apply_theme()

        top = tk.Frame(self.root, bg=self.theme["bg"])
        top.pack(pady=(12, 0), fill=tk.X)
        tk.Label(top, text=f"{'Player vs Bot (' + self.bot_difficulty + ')' if bot else 'Player vs Player'}",
                 font=("Arial", 15, "bold"), fg=self.theme["p1"], bg=self.theme["bg"]).pack(side=tk.LEFT, padx=10)
        tk.Button(top, text="Back", command=self.create_menu, font=("Arial", 10, "bold"),
                  bg=self.theme["board"], fg=self.theme["txt"],
                  activebackground=self.theme["hl"], activeforeground=self.theme["txt"],
                  ).pack(side=tk.RIGHT, padx=10)

        self.turn_label = tk.Label(self.root, text="Red's turn (P1)", font=("Arial", 16, "bold"),
                                   fg=self.theme["p1"], bg=self.theme["board"])
        self.turn_label.pack(fill=tk.X, padx=0, pady=(0, 6))

        # Board with drop buttons above every tile
        self.board_frame = tk.Frame(self.root, bg=self.theme["board"])
        self.board_frame.pack(padx=10, pady=8)
        self.cell_buttons = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.drop_buttons = []

        grid_frame = tk.Frame(self.board_frame, bg=self.theme["board"])
        grid_frame.pack()

        # Create drop buttons on top of each column/tile
        for c in range(COLS):
            btn = tk.Button(grid_frame, text="⬇", font=("Arial", 14, "bold"),
                            bg=self.theme["hl"], fg=self.theme["button_fg"], width=3, height=1,
                            activebackground=self.theme["p1"], activeforeground=self.theme["txt"],
                            relief=tk.RAISED, command=lambda col=c: self.drop_piece(col))
            btn.grid(row=0, column=c, sticky="nsew", padx=1, pady=(2, 8))
            self.drop_buttons.append(btn)
            grid_frame.grid_columnconfigure(c, weight=1)

        for r in range(ROWS):
            for c in range(COLS):
                b = tk.Label(grid_frame, width=3, height=1, font=("Arial", 28, "bold"),
                             bg=self.theme["empty"], fg=self.theme["txt"], relief=tk.FLAT, borderwidth=2)
                b.grid(row=r+1, column=c, padx=2, pady=2, sticky="nsew")
                grid_frame.grid_rowconfigure(r+1, weight=1)
                self.cell_buttons[r][c] = b

        bottom = tk.Frame(self.root, bg=self.theme["bg"])
        bottom.pack(fill=tk.X, pady=(6, 0))
        tk.Button(bottom, text="Undo", font=("Arial", 11, "bold"),
                  bg=self.theme["board"], fg=self.theme["txt"],
                  activebackground=self.theme["hl"], activeforeground=self.theme["txt"],
                  command=self.undo_move).pack(side=tk.RIGHT, padx=8)
        tk.Button(bottom, text="Replay", font=("Arial", 11, "bold"),
                  bg=self.theme["board"], fg=self.theme["txt"],
                  activebackground=self.theme["hl"], activeforeground=self.theme["txt"],
                  command=self.start_replay).pack(side=tk.RIGHT, padx=8)
        self.stats_label = tk.Label(self.root,
            text=f"P1 Wins: {self.stats['P1']}   P2 Wins: {self.stats['P2']}   Draws: {self.stats['Draws']}",
            font=("Arial", 13, "italic"), fg=self.theme["txt"], bg=self.theme["bg"])
        self.stats_label.pack(pady=(7, 4))
        self.update_board_ui()
        self.enable_columns()
        if self.bot_enabled and self.current_player == 2:
            self.root.after(500, self.bot_move)

    def update_board_ui(self):
        for r in range(ROWS):
            for c in range(COLS):
                val = self.board[r][c]
                b = self.cell_buttons[r][c]
                if (r, c) in self.win_line:
                    b.config(bg=self.theme["hl"])
                elif val == 1:
                    b.config(bg=self.theme["p1"], text="●", fg=self.theme["txt"])
                elif val == 2:
                    b.config(bg=self.theme["p2"], text="●", fg=self.theme["txt"])
                else:
                    b.config(bg=self.theme["empty"], text="", fg=self.theme["txt"])

    def enable_columns(self):
        if self.winner or self.replay_mode:
            for btn in self.drop_buttons:
                btn.config(state=tk.DISABLED)
            return
        for c in range(COLS):
            if self.board[0][c] is None:
                self.drop_buttons[c].config(state=tk.NORMAL, cursor="hand2")
            else:
                self.drop_buttons[c].config(state=tk.DISABLED, cursor="arrow")
        if self.bot_enabled and self.current_player == 2:
            for btn in self.drop_buttons:
                btn.config(state=tk.DISABLED)

    def drop_piece(self, col):
        if self.winner or self.replay_mode:
            return
        row = self.get_drop_row(col)
        if row is None:
            return
        self.move_stack.append((copy.deepcopy(self.board), self.current_player, copy.deepcopy(self.win_line)))
        self.replay_moves.append(col)
        self.board[row][col] = self.current_player
        self.move_count += 1
        self.check_game_end(row, col)
        if not self.winner and not self.is_draw():
            self.current_player = 2 if self.current_player == 1 else 1
            self.turn_label.config(
                text=f"{'Red' if self.current_player == 1 else 'Blue'}'s turn (P{self.current_player})",
                fg=self.theme["p1"] if self.current_player == 1 else self.theme["p2"],
                bg=self.theme["board"]
            )
            self.update_board_ui()
            self.enable_columns()
            if self.bot_enabled and self.current_player == 2:
                self.root.after(600, self.bot_move)
        else:
            self.update_board_ui()
            self.enable_columns()

    def get_drop_row(self, col):
        for r in reversed(range(ROWS)):
            if self.board[r][col] is None:
                return r
        return None

    def check_game_end(self, last_row, last_col):
        winner, line = self.check_winner(last_row, last_col)
        self.win_line = line
        if winner:
            self.winner = winner
            self.turn_label.config(
                text=f"{'Red' if winner == 1 else 'Blue'} wins! (P{winner})",
                fg=self.theme["p1"] if winner == 1 else self.theme["p2"],
                bg=self.theme["board"]
            )
            self.stats["P1" if winner == 1 else "P2"] += 1
            self.stats_label.config(
                text=f"P1 Wins: {self.stats['P1']}   P2 Wins: {self.stats['P2']}   Draws: {self.stats['Draws']}")
            self.update_board_ui()
            self.show_end_screen(winner=winner)
        elif self.is_draw():
            self.turn_label.config(text="It's a draw.", fg=self.theme["txt"], bg=self.theme["board"])
            self.stats["Draws"] += 1
            self.stats_label.config(
                text=f"P1 Wins: {self.stats['P1']}   P2 Wins: {self.stats['P2']}   Draws: {self.stats['Draws']}")
            self.update_board_ui()
            self.show_end_screen(winner=None)

    def is_draw(self):
        return all(self.board[0][c] is not None for c in range(COLS)) and not self.winner

    def check_winner(self, last_row, last_col):
        color = self.board[last_row][last_col]
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            line = [(last_row, last_col)]
            # Negative direction
            r, c = last_row-dr, last_col-dc
            while 0<=r<ROWS and 0<=c<COLS and self.board[r][c]==color:
                line.insert(0, (r,c))
                r, c = r-dr, c-dc
            # Positive direction
            r, c = last_row+dr, last_col+dc
            while 0<=r<ROWS and 0<=c<COLS and self.board[r][c]==color:
                line.append((r,c))
                r, c = r+dr, c+dc
            if len(line) >= CONNECT_N:
                return color, line
        return None, []

    def show_end_screen(self, winner=None):
        if self.replay_mode:
            return
        msg = ""
        if winner == 1:
            msg = "🟥 Red wins!"
        elif winner == 2:
            msg = "🟦 Blue wins!"
        else:
            msg = "It's a draw!"
        def restart():
            self.start_game(bot=self.bot_enabled)
        def back():
            self.create_menu()
        msgbox = tk.Toplevel(self.root)
        msgbox.title("Game Over")
        msgbox.grab_set()
        msgbox.geometry("+%d+%d" % (self.root.winfo_rootx()+100, self.root.winfo_rooty()+100))
        tk.Label(msgbox, text=msg, font=("Arial", 20, "bold"),
                 fg=self.theme["p1"] if winner==1 else self.theme["p2"] if winner==2 else self.theme["txt"], pady=20).pack()
        tk.Button(msgbox, text="Play Again", width=15, font=("Arial", 12, "bold"),
                  bg=self.theme["board"], fg=self.theme["txt"],
                  activebackground=self.theme["hl"], activeforeground=self.theme["txt"],
                  command=lambda: [msgbox.destroy(), restart()]).pack(pady=7)
        tk.Button(msgbox, text="Back to Menu", width=15, font=("Arial", 12),
                  bg=self.theme["board"], fg=self.theme["txt"],
                  activebackground=self.theme["hl"], activeforeground=self.theme["txt"],
                  command=lambda: [msgbox.destroy(), back()]).pack(pady=(0,14))

    # ----------- BOT LOGIC WITH STRENGTHS --------------
    def bot_move(self):
        if self.winner or self.replay_mode:
            return
        difficulty = self.bot_difficulty
        if difficulty == "Easy":
            col = self.bot_easy()
        elif difficulty == "Medium":
            col = self.bot_medium()
        elif difficulty == "Hard":
            col = self.bot_hard()
        elif difficulty == "Impossible":
            col = self.bot_impossible()
        else:
            col = self.bot_medium()
        if col is not None:
            self.drop_piece(col)

    def bot_easy(self):
        valid_cols = [c for c in range(COLS) if self.board[0][c] is None]
        return random.choice(valid_cols)

    def bot_medium(self):
        valid_cols = [c for c in range(COLS) if self.board[0][c] is None]
        for c in valid_cols:
            r = self.get_drop_row(c)
            self.board[r][c] = 2
            if self.check_winner(r, c)[0] == 2:
                self.board[r][c] = None
                return c
            self.board[r][c] = None
        for c in valid_cols:
            r = self.get_drop_row(c)
            self.board[r][c] = 1
            if self.check_winner(r, c)[0] == 1:
                self.board[r][c] = None
                return c
            self.board[r][c] = None
        if 3 in valid_cols:
            return 3
        for c in [0,6,1,5,2,4]:
            if c in valid_cols:
                return c
        return random.choice(valid_cols) if valid_cols else None

    def bot_hard(self):
        valid_cols = [c for c in range(COLS) if self.board[0][c] is None]
        for c in valid_cols:
            r = self.get_drop_row(c)
            self.board[r][c] = 2
            if self.check_winner(r, c)[0] == 2:
                self.board[r][c] = None
                return c
            self.board[r][c] = None
        for c in valid_cols:
            r = self.get_drop_row(c)
            self.board[r][c] = 1
            if self.check_winner(r, c)[0] == 1:
                self.board[r][c] = None
                return c
            self.board[r][c] = None
        safe_cols = []
        for c in valid_cols:
            r = self.get_drop_row(c)
            self.board[r][c] = 2
            opp_wins = False
            for cc in valid_cols:
                if cc == c:
                    rr = r-1
                else:
                    rr = self.get_drop_row(cc)
                if rr is not None:
                    self.board[rr][cc] = 1
                    if self.check_winner(rr, cc)[0] == 1:
                        opp_wins = True
                    self.board[rr][cc] = None
            self.board[r][c] = None
            if not opp_wins:
                safe_cols.append(c)
        if safe_cols:
            if 3 in safe_cols:
                return 3
            for c in [0,6,1,5,2,4]:
                if c in safe_cols:
                    return c
            return random.choice(safe_cols)
        else:
            return self.bot_medium()

    def bot_impossible(self):
        col, _ = self.minimax(self.board, depth=5, alpha=-float('inf'), beta=float('inf'), maximizing=True)
        if col is None:
            return self.bot_hard()
        return col

    def minimax(self, board, depth, alpha, beta, maximizing):
        valid_cols = [c for c in range(COLS) if board[0][c] is None]
        is_terminal, winner = self.is_terminal_node(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if winner == 2:
                    return None, 100000
                elif winner == 1:
                    return None, -100000
                else:
                    return None, 0
            return None, self.score_position(board, 2)
        if maximizing:
            value = -float('inf')
            chosen_col = random.choice(valid_cols)
            for col in valid_cols:
                r = self.get_drop_row_board(board, col)
                temp_board = copy.deepcopy(board)
                temp_board[r][col] = 2
                _, score = self.minimax(temp_board, depth-1, alpha, beta, False)
                if score > value:
                    value = score
                    chosen_col = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return chosen_col, value
        else:
            value = float('inf')
            chosen_col = random.choice(valid_cols)
            for col in valid_cols:
                r = self.get_drop_row_board(board, col)
                temp_board = copy.deepcopy(board)
                temp_board[r][col] = 1
                _, score = self.minimax(temp_board, depth-1, alpha, beta, True)
                if score < value:
                    value = score
                    chosen_col = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return chosen_col, value

    def is_terminal_node(self, board):
        for c in range(COLS):
            r = self.get_drop_row_board(board, c)
            if r is not None:
                for player in [1,2]:
                    board[r][c] = player
                    winner, _ = self.check_winner_board(board, r, c)
                    board[r][c] = None
                    if winner:
                        return True, winner
        if all(board[0][c] is not None for c in range(COLS)):
            return True, None
        return False, None

    def score_position(self, board, player):
        opp = 1 if player == 2 else 2
        score = 0
        center = [board[r][COLS//2] for r in range(ROWS)]
        score += center.count(player) * 6
        for r in range(ROWS):
            for c in range(COLS-3):
                window = [board[r][c+i] for i in range(4)]
                score += self.evaluate_window(window, player, opp)
        for c in range(COLS):
            for r in range(ROWS-3):
                window = [board[r+i][c] for i in range(4)]
                score += self.evaluate_window(window, player, opp)
        for r in range(ROWS-3):
            for c in range(COLS-3):
                window = [board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, player, opp)
            for c in range(3, COLS):
                window = [board[r+i][c-i] for i in range(4)]
                score += self.evaluate_window(window, player, opp)
        return score

    def evaluate_window(self, window, player, opp):
        score = 0
        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3 and window.count(None) == 1:
            score += 5
        elif window.count(player) == 2 and window.count(None) == 2:
            score += 2
        if window.count(opp) == 3 and window.count(None) == 1:
            score -= 7
        return score

    def get_drop_row_board(self, board, col):
        for r in reversed(range(ROWS)):
            if board[r][col] is None:
                return r
        return None

    def check_winner_board(self, board, last_row, last_col):
        color = board[last_row][last_col]
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            line = [(last_row, last_col)]
            r, c = last_row-dr, last_col-dc
            while 0<=r<ROWS and 0<=c<COLS and board[r][c]==color:
                line.insert(0, (r,c))
                r, c = r-dr, c-dc
            r, c = last_row+dr, last_col+dc
            while 0<=r<ROWS and 0<=c<COLS and board[r][c]==color:
                line.append((r,c))
                r, c = r+dr, c+dc
            if len(line) >= CONNECT_N:
                return color, line
        return None, []

    # ---------------- UNDO -----------------------
    def undo_move(self):
        if not self.move_stack or self.replay_mode:
            return
        self.board, self.current_player, self.win_line = self.move_stack.pop()
        self.winner = None
        self.update_board_ui()
        self.enable_columns()
        self.turn_label.config(
            text=f"{'Red' if self.current_player == 1 else 'Blue'}'s turn (P{self.current_player})",
            fg=self.theme["p1"] if self.current_player == 1 else self.theme["p2"],
            bg=self.theme["board"]
        )

    # ---------------- REPLAY -----------------------
    def start_replay(self):
        if not self.replay_moves:
            messagebox.showinfo("Replay", "No game to replay yet!")
            return
        self.replay_index = 0
        self.replay_mode = True
        self.clear_window()
        self.apply_theme()
        top = tk.Frame(self.root, bg=self.theme["bg"])
        top.pack(pady=(15, 0), fill=tk.X)
        tk.Label(top, text="Replay Game", font=("Arial", 15, "bold"),
                 fg=self.theme["p1"], bg=self.theme["bg"]).pack(side=tk.LEFT, padx=10)
        tk.Button(top, text="Back", command=self.end_replay, font=("Arial", 10, "bold"),
                  bg=self.theme["board"], fg=self.theme["txt"],
                  activebackground=self.theme["hl"], activeforeground=self.theme["txt"],
                  ).pack(side=tk.RIGHT, padx=10)
        board_frame = tk.Frame(self.root, bg=self.theme["board"])
        board_frame.pack(pady=10)
        self.replay_cells = [[None for _ in range(COLS)] for _ in range(ROWS)]
        grid_frame = tk.Frame(board_frame, bg=self.theme["board"])
        grid_frame.pack()
        for c in range(COLS):
            tk.Label(grid_frame, text="", width=3, height=1, bg=self.theme["board"]).grid(row=0, column=c)  # spacer
        for r in range(ROWS):
            for c in range(COLS):
                b = tk.Label(grid_frame, width=3, height=1, font=("Arial", 28, "bold"),
                             bg=self.theme["empty"], fg=self.theme["txt"], relief=tk.FLAT, borderwidth=2)
                b.grid(row=r+1, column=c, padx=2, pady=2)
                self.replay_cells[r][c] = b
        control = tk.Frame(self.root, bg=self.theme["bg"])
        control.pack()
        tk.Button(control, text="⏮ Prev", command=self.prev_replay, font=("Arial", 12, "bold"),
                  bg=self.theme["board"], fg=self.theme["txt"],
                  activebackground=self.theme["hl"], activeforeground=self.theme["txt"],
                  ).pack(side=tk.LEFT, padx=8)
        tk.Button(control, text="⏭ Next", command=self.next_replay, font=("Arial", 12, "bold"),
                  bg=self.theme["board"], fg=self.theme["txt"],
                  activebackground=self.theme["hl"], activeforeground=self.theme["txt"],
                  ).pack(side=tk.LEFT, padx=8)
        self.replay_status = tk.Label(self.root, text="", font=("Arial", 13, "italic"),
                                      fg=self.theme["txt"], bg=self.theme["bg"])
        self.replay_status.pack(pady=8)
        self.show_replay_state()

    def end_replay(self):
        self.replay_mode = False
        self.create_menu()

    def show_replay_state(self):
        board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        current_player = 1
        win_line = []
        winner = None
        for idx in range(self.replay_index):
            col = self.replay_moves[idx]
            row = None
            for r in reversed(range(ROWS)):
                if board[r][col] is None:
                    board[r][col] = current_player
                    row = r
                    break
            if row is not None:
                w, line = self.check_winner_replay(board, row, col)
                if w:
                    winner = w
                    win_line = line
                    break
            current_player = 2 if current_player == 1 else 1
        for r in range(ROWS):
            for c in range(COLS):
                val = board[r][c]
                b = self.replay_cells[r][c]
                if (r, c) in win_line:
                    b.config(bg=self.theme["hl"])
                elif val == 1:
                    b.config(bg=self.theme["p1"], text="●", fg=self.theme["txt"])
                elif val == 2:
                    b.config(bg=self.theme["p2"], text="●", fg=self.theme["txt"])
                else:
                    b.config(bg=self.theme["empty"], text="", fg=self.theme["txt"])
                b.config(relief=tk.RAISED)
        if winner:
            for (r, c) in win_line:
                self.replay_cells[r][c].config(bg=self.theme["hl"], relief=tk.SUNKEN)
        self.replay_status.config(text=f"Move {self.replay_index}/{len(self.replay_moves)}")

    def next_replay(self):
        if self.replay_index < len(self.replay_moves):
            self.replay_index += 1
            self.show_replay_state()

    def prev_replay(self):
        if self.replay_index > 0:
            self.replay_index -= 1
            self.show_replay_state()

    def check_winner_replay(self, board, last_row, last_col):
        color = board[last_row][last_col]
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            line = [(last_row, last_col)]
            r, c = last_row-dr, last_col-dc
            while 0<=r<ROWS and 0<=c<COLS and board[r][c]==color:
                line.insert(0, (r,c))
                r, c = r-dr, c-dc
            r, c = last_row+dr, last_col+dc
            while 0<=r<ROWS and 0<=c<COLS and board[r][c]==color:
                line.append((r,c))
                r, c = r+dr, c+dc
            if len(line) >= CONNECT_N:
                return color, line
        return None, []

if __name__ == "__main__":
    root = tk.Tk()
    app = FourInARow(root)
    root.mainloop()